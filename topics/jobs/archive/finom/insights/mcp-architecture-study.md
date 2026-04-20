# Finom — MCP Architecture & Multi-Agent Accounting Study

## MCP in Production: How Finom Uses It

### Architecture Overview
From Dmitry's interview: "The whole platform is going to be stitched with MCP-based interfaces. Connecting new skills is going to be really easy."

This reveals Finom is building a **skill-based agent architecture** where:
- Each business capability is exposed as an MCP tool/resource
- AI agents discover and invoke skills through MCP
- New capabilities are added by deploying new MCP servers
- The system is composable and decoupled

### MCP Architecture for Financial Services

```
┌─────────────────────────────────────────────────────────┐
│                    AI Orchestrator Layer                  │
│    (coordinates agent workflows, manages state)          │
├─────────────────────────────────────────────────────────┤
│                   MCP Client Pool                        │
│  (maintains connections to all registered MCP servers)   │
├─────────────────────────────────────────────────────────┤
│                   MCP Servers (Skills)                    │
│                                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Receipt OCR  │ │ Transaction  │ │ VAT          │    │
│  │ Server       │ │ Categorizer  │ │ Calculator   │    │
│  │ Python       │ │ Python       │ │ C#/.NET      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Invoice      │ │ Cash Flow    │ │ Compliance   │    │
│  │ Generator    │ │ Analyzer     │ │ Checker      │    │
│  │ C#/.NET      │ │ Python       │ │ C#/.NET      │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Bank Account │ │ Tax Filing   │ │ Report       │    │
│  │ Service      │ │ Service      │ │ Generator    │    │
│  │ C#/.NET      │ │ C#/.NET      │ │ Python       │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────┤
│              Core Platform (C#/.NET)                     │
│   PostgreSQL │ Event Store │ Cache │ Message Bus         │
└─────────────────────────────────────────────────────────┘
```

### Why MCP Fits Financial Services

1. **Auditability**: Every tool call through MCP is a structured, loggable event
   - Who called what, with what parameters, what was returned
   - Critical for financial compliance and debugging
2. **Authorization**: MCP servers can enforce access controls
   - Agent X can read transactions but not modify them
   - Agent Y can propose tax entries but not file them
3. **Composability**: New skills added without changing orchestration
   - "Add Spanish tax rules" = deploy a new MCP server
   - No changes to existing agents or orchestrator
4. **Language agnostic**: C# core services and Python AI services both expose MCP
   - Unified interface regardless of implementation language
5. **Human-in-the-loop**: MCP supports confirmation flows naturally
   - Tool describes its action → agent proposes → user confirms → execute

### MCP vs. Alternatives

| Approach | Pros | Cons | Fit for Finom |
|----------|------|------|---------------|
| **MCP** | Standard, composable, typed tools | Newer, less battle-tested | Strong ✓ |
| **Custom REST APIs** | Battle-tested, familiar | Tight coupling, manual discovery | Partial |
| **gRPC** | High perf, typed contracts | Language-specific clients, complex | Good for internal |
| **GraphQL** | Flexible queries, schema-first | Overkill for tool calls | Weak |
| **Function calling (raw)** | Simple, built into LLM APIs | No standardization, no discovery | Weak |

Finom's bet on MCP makes strategic sense: it's the emerging standard, Anthropic backs it, and the composability model fits their multi-market, multi-agent vision.

## Multi-Agent Accounting: Deep Dive

### Agent Workflow: Monthly Close for German SMB

```
Trigger: Month-end (or user request)
    │
    ├─ 1. Transaction Collector Agent
    │      - Pulls all month's bank transactions
    │      - Identifies unprocessed items
    │      - MCP tools: bank_account.list_transactions, bank_account.get_balance
    │
    ├─ 2. Receipt Matching Agent
    │      - Matches transactions to uploaded receipts/invoices
    │      - Uses semantic search + amount/date heuristics
    │      - MCP tools: receipt_store.search, receipt_store.get, receipt_ocr.extract
    │
    ├─ 3. Categorization Agent
    │      - Assigns SKR03/SKR04 account codes
    │      - Uses transaction history, merchant data, receipt content
    │      - Confidence-scored output
    │      - MCP tools: categorizer.classify, merchant_db.lookup
    │
    ├─ 4. VAT Agent
    │      - Calculates VAT per transaction (19%/7%/exempt/reverse charge)
    │      - Handles intra-EU B2B detection
    │      - MCP tools: vat_calculator.compute, eu_vat.check_id
    │
    ├─ 5. Booking Agent
    │      - Creates double-entry bookkeeping records
    │      - Stages entries for review
    │      - MCP tools: ledger.create_entry, ledger.stage_batch
    │
    ├─ 6. Validation Agent
    │      - Cross-checks totals, balance sheet, trial balance
    │      - Flags anomalies (unusual amounts, missing entries)
    │      - MCP tools: ledger.get_trial_balance, validator.check_consistency
    │
    └─ 7. Report Agent
           - Generates monthly summary
           - Prepares UStVA (VAT advance return) data
           - MCP tools: report.generate, tax_filing.prepare_ustva
```

### Coordination Patterns

#### Pattern 1: Pipeline (Sequential)
```
Transaction → Receipt Match → Categorize → Tax → Book → Validate
```
- Simple, predictable, easy to debug
- Slow — each step waits for previous
- Error handling: rollback entire pipeline

#### Pattern 2: Fan-Out/Fan-In (Parallel)
```
Transaction → ┌─ Receipt Match ─┐
              ├─ Categorize ────┤ → Merge → Book → Validate
              └─ Tax Pre-calc ──┘
```
- Faster — parallel where possible
- More complex state management
- Error handling: partial results, retry individual branches

#### Pattern 3: Event-Driven (Reactive)
```
Event: "transaction.received" → Categorization Agent reacts
Event: "receipt.uploaded" → Matching Agent reacts
Event: "month_end.approaching" → Tax Filing Agent prepares
```
- Most decoupled and scalable
- Harder to track end-to-end workflow state
- Best for independent, asynchronous operations

**Likely Finom approach**: Hybrid — event-driven for triggers, pipeline for within-workflow steps, fan-out for parallelizable sub-tasks.

### Error Handling in Financial Agent Systems

#### Categorization Error Recovery
```
1. Agent categorizes transaction as "Marketing" (confidence: 0.72)
2. User corrects to "Office Supplies"
3. System:
   a. Updates this transaction
   b. Adjusts VAT (if different rate applies)
   c. Rebalances ledger entries
   d. Stores correction as training signal
   e. Re-evaluates similar transactions from same merchant
```

#### Tax Filing Error Recovery
```
1. Agent prepares UStVA with incorrect categorization
2. Filing already submitted to ELSTER
3. Recovery:
   a. Cannot simply "undo" — filed tax returns require formal amendment
   b. Prepare corrected UStVA (Berichtigte Voranmeldung)
   c. Submit correction to ELSTER
   d. Notify user of correction and any implications
```

This is why **confidence-based routing** is critical:
- High confidence (>0.95): Auto-book, eligible for auto-filing
- Medium confidence (0.75-0.95): Auto-book but flag for review before filing
- Low confidence (<0.75): Queue for user decision, do NOT auto-book

## Polyglot Architecture: C#/.NET + Python

### Service Boundary Design
```
C#/.NET Services (Core Platform):
  ├─ Banking API (account management, transfers, SEPA)
  ├─ Invoicing (create, send, track invoices)
  ├─ Ledger (double-entry bookkeeping, journal entries)
  ├─ Tax Engine (deterministic tax rules, filing)
  ├─ Compliance (regulatory checks, AML/KYC)
  └─ User Management (auth, permissions, multi-tenancy)

Python Services (AI Layer):
  ├─ Document Understanding (OCR, receipt parsing, invoice extraction)
  ├─ Transaction Categorization (LLM-based classification)
  ├─ Cash Flow Analysis (trend detection, forecasting)
  ├─ Anomaly Detection (unusual patterns, potential fraud)
  ├─ Agent Orchestrator (multi-agent coordination)
  └─ Evaluation & Monitoring (quality metrics, drift detection)
```

### Communication Patterns
- **Sync (gRPC/REST)**: Python AI services call C# services for real-time operations
- **Async (Message Bus)**: Events flow between services (transaction.received, receipt.uploaded)
- **MCP**: AI agents access both C# and Python services through unified MCP interface

### Key Technical Debt Risks
1. **Schema drift**: C# and Python services may diverge on data models
2. **Deployment complexity**: Two runtimes need different CI/CD pipelines
3. **Debugging across languages**: Distributed tracing is essential
4. **Team knowledge silos**: Some engineers only know one language

## Preparation: System Design Exercise

### Prompt: "Design the receipt-to-booking pipeline for German SMBs"

**Skeleton answer**:
```
Input: User uploads photo of restaurant receipt

1. Receipt Processing (Python)
   - Image → OCR → structured text
   - LLM extracts: merchant, date, total, VAT amount, line items
   - Structured output schema: ReceiptData { merchant, date, total, vat_amount, ... }

2. Transaction Matching (Python + C#)
   - Search recent transactions for matching amount ± tolerance and date range
   - MCP call to C# banking service: bank.search_transactions(amount, date_range)
   - Confidence-scored matches returned

3. Categorization (Python)
   - Input: merchant name + receipt line items + transaction history
   - LLM classifies to SKR03 account (e.g., 4650 Bewirtungskosten)
   - Business meal? → Bewirtungsbeleg rules apply (70% deductible)

4. VAT Calculation (C#)
   - Deterministic rule engine (NOT LLM)
   - Input: category, amount, merchant type
   - Output: VAT rate, VAT amount, net amount
   - Handles: standard 19%, reduced 7%, exempt, mixed-rate receipts

5. Booking Entry (C#)
   - Creates double-entry journal entry
   - Debit: expense account (SKR03 code)
   - Credit: bank account
   - With VAT split (Vorsteuer account)

6. Review & Approval
   - High confidence → auto-book, show in feed
   - Low confidence → queue for user review with explanation
   - User corrections → feedback loop to categorization model

Non-functional:
- Latency target: <5s from upload to suggested booking
- Accuracy target: >90% categorization accuracy for top-50 categories
- Audit trail: every step logged with reasoning
- GDPR: receipt images stored in EU, encrypted at rest
```
