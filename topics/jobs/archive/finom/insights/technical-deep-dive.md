# Finom — Technical Deep-Dive Preparation (2nd Round)

## 1. MCP (Model Context Protocol) Architecture for Multi-Agent Systems

### What MCP Is
Anthropic's open protocol for connecting AI systems to data sources and tools. Think of it as a USB-C port for AI — a standardized way for models to access external capabilities.

### MCP in Finom's Architecture
From the interview, Dmitry revealed:
- "The whole platform is going to be stitched with MCP-based interfaces"
- "Connecting new skills are going to be really easy"
- Skills = agent capabilities exposed via MCP

### MCP Architecture Pattern for Fintech
```
┌─────────────────────────────────────────┐
│              Agent Orchestrator          │
│         (coordinates multi-agent flows)  │
├─────────────────────────────────────────┤
│                MCP Layer                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │ Receipt  │ │ Tax      │ │ Cash     ││
│  │ OCR Skill│ │ Calc Skil│ │ Flow Skil││
│  └──────────┘ └──────────┘ └──────────┘│
│  ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │ Invoice  │ │ Expense  │ │ Report   ││
│  │ Match    │ │ Category │ │ Generator││
│  └──────────┘ └──────────┘ └──────────┘│
├─────────────────────────────────────────┤
│          C#/.NET Core Services          │
│    (banking, invoicing, compliance)     │
├─────────────────────────────────────────┤
│     PostgreSQL / Event Store / Cache    │
└─────────────────────────────────────────┘
```

### Key Design Questions for Interview
1. **Skill discovery**: How do agents find and select the right skills?
2. **Skill composition**: Can skills be chained? Who orchestrates the chain?
3. **Error handling**: What happens when a skill fails mid-chain?
4. **Versioning**: How do you version skills independently?
5. **Testing**: How do you test skill integration?

---

## 2. Multi-Agent Accounting Workflows

### Transaction Categorization Agent
```
Event: New bank transaction received
  ↓
Receipt Matching Agent
  - Searches for uploaded receipts matching amount/date/merchant
  - Confidence score for match
  ↓
Categorization Agent
  - Determines accounting category (e.g., office supplies, travel, SaaS)
  - Uses merchant data, receipt content, transaction history
  - Market-specific rules (German SKR03/SKR04, French PCG)
  ↓
Tax Calculation Agent
  - Applies VAT rules based on category + country
  - Handles reverse charge, exempt supplies, reduced rates
  ↓
Compliance Check Agent
  - Validates against regulatory requirements
  - Flags suspicious patterns
  ↓
Booking Agent
  - Creates accounting entry
  - Stages for user approval OR auto-books if high confidence
```

### Tax Filing Agent (The "Killer Feature")
From interview: Agent sees it's time to create tax record → prepares → user approves → files to government.

This is high-stakes agentic AI:
- **Correctness is non-negotiable**: Wrong tax filing = penalties
- **Timeliness matters**: Tax deadlines are hard deadlines
- **Audit trail required**: Every decision must be traceable
- **Rollback complexity**: Filed taxes require amendment process, not simple undo

---

## 3. EU Tax Regime Complexity

### Market-Specific Challenges

| Market | Tax System | VAT Rates | Chart of Accounts | Filing |
|--------|-----------|-----------|-------------------|--------|
| **Germany** | USt (Umsatzsteuer) | 19% / 7% | SKR03 or SKR04 | Monthly/quarterly UStVA |
| **France** | TVA | 20% / 10% / 5.5% / 2.1% | PCG (Plan Comptable Général) | Monthly/quarterly CA3 |
| **Italy** | IVA | 22% / 10% / 5% / 4% | Piano dei Conti | Monthly liquidation |
| **Spain** | IVA | 21% / 10% / 4% | PGC (Plan General Contable) | Quarterly Modelo 303 |
| **Netherlands** | BTW | 21% / 9% / 0% | RGS (optional) | Quarterly OB |

### Architecture Decision: Shared vs. Per-Country Agents
Two approaches:
1. **Shared architecture + localization layers**: One categorization engine with country-specific rule sets
   - Pros: Code reuse, easier maintenance, consistent UX
   - Cons: Complex rule engine, harder to test edge cases
2. **Per-country specialized agents**: Each market has dedicated agents
   - Pros: Simpler per-agent, country experts can own their domain
   - Cons: Code duplication, harder to scale to new markets

**Likely Finom approach**: Shared core + localization (based on "scaling out across the entire platform" language)

---

## 4. C#/.NET + Python Polyglot Architecture

### Why This Matters
Finom's stack:
- **C#/.NET**: Core banking/invoicing services (performance, type safety, ecosystem)
- **Python**: AI/LLM services (library ecosystem, rapid prototyping)

### Integration Patterns
1. **gRPC**: Type-safe, efficient, cross-language — likely for service-to-service communication
2. **REST/HTTP**: Simple, debuggable — for less performance-critical paths
3. **Message queue** (Kafka/RabbitMQ): Async event-driven communication
4. **MCP**: The new standard for AI tool access — Finom is betting on this

### Key Technical Considerations
- **Schema sharing**: Protobuf or OpenAPI specs shared between C# and Python services
- **Observability**: Distributed tracing across language boundaries (OpenTelemetry)
- **Testing**: Integration tests that span language boundaries
- **Deployment**: Both runtimes need to be managed (.NET 8+ and Python 3.11+)

---

## 5. Agent Observability & Reliability

### What Dmitry Cares About (from interview)
"You thought about the latency, you thought about observability" — he wants engineers who think about production, not just prototype.

### Observability Stack for Multi-Agent Systems
```
┌─────────────────────────────────────┐
│         Agent Observability          │
├─────────────────────────────────────┤
│ Traces: OpenTelemetry / Langfuse    │
│  - Agent execution spans            │
│  - Tool call durations              │
│  - LLM latency per call             │
│  - Token usage tracking             │
├─────────────────────────────────────┤
│ Metrics: Prometheus / Grafana       │
│  - Agent success/failure rates      │
│  - Categorization accuracy (daily)  │
│  - P95 latency per workflow         │
│  - Cost per transaction processed   │
├─────────────────────────────────────┤
│ Logs: Structured JSON               │
│  - Decision reasoning chains        │
│  - Confidence scores per step       │
│  - Input/output pairs for replay    │
├─────────────────────────────────────┤
│ Alerts: PagerDuty / OpsGenie        │
│  - Accuracy drop below threshold    │
│  - Latency spike                    │
│  - Error rate increase              │
│  - Cost anomaly                     │
└─────────────────────────────────────┘
```

### Reliability Patterns
1. **Circuit breaker**: Don't keep calling a failing LLM provider
2. **Fallback chains**: If GPT-4 fails, try Claude, then rule-based fallback
3. **Idempotency**: Financial operations MUST be idempotent
4. **Dead letter queue**: Failed agent runs get queued for retry/human review
5. **Canary deployments**: New agent versions rolled out to subset first

---

## 6. System Design Exercise Prep

### Prompt: "Design an agent that handles expense categorization for German SMBs"

**Requirements**:
- Process bank transactions in real-time
- Match with uploaded receipts
- Categorize using SKR03/SKR04
- Calculate VAT (19% or 7%)
- Handle edge cases (split VAT, exempt, intra-EU)

**Architecture answer**:
```
1. Event ingestion (transaction webhook from banking API)
2. Receipt matching (semantic search over uploaded receipts)
3. Feature extraction (merchant name, amount, date, receipt content)
4. Categorization model (fine-tuned classifier OR LLM with structured output)
5. Tax rule engine (deterministic rules, not LLM — too risky)
6. Confidence scoring (route low-confidence to human review)
7. Booking (create accounting entry, stage for approval)
8. Learning loop (user corrections feed back into model)
```

**Key talking points**:
- Why tax calculation should be DETERMINISTIC, not LLM-based
- How to handle the long tail of edge cases (mixed-rate receipts, foreign vendors)
- How user corrections improve the model over time
- Why idempotency matters for financial operations

---

## 7. Technical Experiments to Build

### Experiment 1: MCP Skill Server
Build a simple MCP server that exposes accounting skills:
- Receipt OCR tool
- Transaction categorization tool
- VAT calculation tool
- Test with Claude Desktop as client

### Experiment 2: Multi-Agent Accounting Pipeline
Build a prototype multi-agent workflow:
- Transaction event → Receipt matching → Categorization → Tax calc → Booking
- Use LangGraph or Agno for orchestration
- Add confidence-based routing
- Implement human-in-the-loop for low-confidence cases

### Experiment 3: Polyglot Service Integration
Build a minimal C#/.NET + Python service:
- C# service for transaction handling (domain logic)
- Python service for LLM-based categorization
- gRPC communication between them
- Shared schema definitions

---

## 8. Key Vocabulary to Know
| Term | Meaning |
|------|---------|
| AIC4 | Finom's AI platform for proactive agent experiences |
| MCP | Model Context Protocol — standard for AI tool access |
| SKR03/SKR04 | German standard chart of accounts |
| USt / UStVA | German VAT / VAT advance return |
| EMI | Electronic Money Institution (Finom's license type) |
| PSD2 | Payment Services Directive 2 (EU open banking) |
| SEPA | Single Euro Payments Area |
| Steuerberater | German tax advisor/accountant |
| Buchungssatz | German accounting entry/posting |
| Reverse charge | VAT mechanism for cross-border B2B transactions |
