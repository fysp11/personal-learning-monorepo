# Finom — 2nd Round Interview Simulation

Practice questions for the technical deep-dive with Dmitry's colleague. Based on signals from the CTO call — expect system design, MCP architecture, and production agent reliability questions.

---

## Category 1: System Design

### Q1: "Design a system that automatically categorizes bank transactions for German SMBs."

**Answer — walk through on whiteboard:**

> **Requirements clarification:**
> - Input: bank transaction (merchant, amount, date, description) + optional uploaded receipt
> - Output: SKR03 account code, VAT rate, booking entry ready for approval
> - Scale: ~100-500 transactions/month per SMB, 200K+ accounts = tens of millions per month
> - Latency: <5 seconds from transaction to suggested categorization
> - Accuracy: >90% category accuracy, >97% VAT accuracy (compliance-critical)
>
> **Architecture:**
>
> ```
> Bank Transaction Webhook (event)
>     │
>     ├─ Receipt Matcher (if receipt uploaded)
>     │   - Semantic search: match by amount ± tolerance + date range
>     │   - OCR + LLM extraction: merchant, line items, VAT breakdown
>     │
>     ├─ Feature Assembly
>     │   - Merchant name normalization
>     │   - Transaction history (how was this merchant categorized before?)
>     │   - Receipt content (if matched)
>     │   - MCC code (Merchant Category Code from payment network)
>     │
>     ├─ Categorization (LLM with structured output)
>     │   - Input: assembled features
>     │   - Output: { skr03_code, category_name, confidence }
>     │   - Model: fine-tuned or few-shot with German accounting examples
>     │
>     ├─ VAT Calculation (DETERMINISTIC rule engine, NOT LLM)
>     │   - Input: category + country + merchant type + counterparty
>     │   - Rules: standard 19%, reduced 7%, exempt, reverse charge
>     │   - Handles: Kleinunternehmerregelung, intra-EU, third-country
>     │
>     ├─ Confidence Routing
>     │   - High (>0.90): auto-book, show in feed
>     │   - Medium (0.70-0.90): auto-book but flag for review before tax filing
>     │   - Low (<0.70): queue for user decision with explanation
>     │
>     └─ Booking Entry
>         - Double-entry: debit expense account, credit bank account
>         - VAT split: separate Vorsteuer (input VAT) entry
>         - Staged until user confirms or auto-approved at month-end
> ```
>
> **Key design decisions:**
> 1. **VAT is deterministic**: This is the most important decision. Tax calculation CANNOT be LLM-based — wrong VAT = compliance violation. The rule engine is tested with 100% branch coverage for each country's tax rules.
> 2. **Merchant history as strongest signal**: If we've seen this merchant 10 times and it was always "Office Supplies," that's more reliable than any LLM inference.
> 3. **Confidence routing**: The system should know what it doesn't know. Better to ask the user than to silently miscategorize.
> 4. **Learning from corrections**: User corrections become training data. Over time, each user's personalized history makes the system more accurate for their specific business.
>
> **Non-functional concerns:**
> - **Idempotency**: Processing the same transaction twice must not create duplicate bookings
> - **Audit trail**: Every categorization decision is logged with reasoning
> - **Observability**: Langfuse traces for every agent run, Prometheus metrics for accuracy/latency
> - **GDPR**: Transaction data stays in EU, encrypted at rest

**Key phrase**: "The core insight is separating judgment from compliance — let the LLM make judgment calls on categorization, but use deterministic rules for tax. You can tolerate a wrong category (user corrects it), but you can't tolerate wrong VAT."

---

### Q2: "How would you structure MCP servers for Finom's multi-agent accounting platform?"

**Answer:**

> I'd organize MCP servers along **domain boundaries**, not technical boundaries. Each server owns a coherent piece of business logic:
>
> **Core MCP Servers (C#/.NET):**
> - `banking-service` — account info, transaction listing, balance queries
> - `ledger-service` — create/read/update booking entries, trial balance, journal
> - `invoice-service` — create/read invoices, match to transactions
> - `tax-engine` — deterministic VAT calculation, tax filing preparation, deadline tracking
> - `compliance-service` — regulatory checks, AML screening, reporting
>
> **AI MCP Servers (Python):**
> - `document-understanding` — OCR, receipt parsing, invoice data extraction
> - `categorization` — transaction classification with confidence scoring
> - `cashflow-analysis` — trend detection, forecasting, anomaly alerts
> - `report-generator` — natural language financial summaries
>
> **Cross-cutting:**
> - `user-preferences` — learned categorization preferences, custom rules per user
> - `market-config` — country-specific settings (chart of accounts, tax rates, filing requirements)
>
> **Why this structure:**
> 1. **Independent deployment**: Update the categorization model without touching the ledger
> 2. **Language-appropriate**: Tax rules in C# (type-safe, tested), AI inference in Python (library ecosystem)
> 3. **New market expansion**: Add Spain = deploy `market-config` for ES + train categorization on Spanish data. No changes to core architecture.
> 4. **Permission boundaries**: The AI categorization agent can READ transactions but can only WRITE through the ledger service, which validates before committing
>
> **Skill discovery pattern:**
> The orchestrator agent gets a tool manifest from each MCP server. For a task like "process this receipt," it plans:
> 1. Call `document-understanding.extract_receipt`
> 2. Call `banking-service.find_matching_transaction`
> 3. Call `categorization.classify`
> 4. Call `tax-engine.calculate_vat`
> 5. Call `ledger-service.create_entry`

---

## Category 2: Agent Reliability in Production

### Q3: "How do you ensure an AI agent doesn't make errors that compound in financial systems?"

**Answer:**

> Financial errors compound in two ways: **data corruption** (wrong bookings propagate into reports/filings) and **trust erosion** (users stop trusting the system). I address both:
>
> **Prevention:**
> - **Confidence-based routing**: Never auto-commit low-confidence decisions
> - **Deterministic guardrails**: Tax calculations, balance checks, and regulatory validations are NEVER LLM-based
> - **Schema validation**: Every agent output is validated against a strict Pydantic schema before it touches the database
> - **Idempotency**: Every operation has a unique key — retries don't create duplicates
>
> **Detection:**
> - **Balance sheet validation**: After every booking, verify debits equal credits. If not, something is wrong — halt and alert.
> - **Anomaly detection**: Flag transactions that deviate significantly from the user's historical pattern
> - **Drift monitoring**: Track categorization accuracy weekly. If the model starts declining (e.g., due to a new merchant type), catch it early
> - **Shadow mode for new models**: Run new model alongside current, compare outputs, only switch when accuracy is validated
>
> **Recovery:**
> - **Correction cascade**: If a user corrects a categorization, the system must also update the VAT and the booking entry — not just the category
> - **Amendable filings**: For tax filings already submitted, generate a corrected filing (Berichtigte Voranmeldung in Germany)
> - **Audit trail**: Every decision is logged. If a regulator asks "why was this categorized as X?", we have the full reasoning chain
>
> **From my experience:** In my document processing pipeline (30-60K docs/day), we had a similar problem — errors in classification would propagate into downstream enrichment. The solution was exactly this layered approach: prevent what you can, detect what you can't prevent, and make recovery fast and traceable.

---

### Q4: "How do you monitor and debug multi-agent systems in production?"

**Answer:**

> Multi-agent systems are hard to debug because failures are distributed. My approach:
>
> **Observability stack:**
> - **Langfuse / OpenTelemetry**: Full execution traces — every agent call, every tool invocation, every LLM inference, with timing and token costs
> - **Structured logging**: Every agent emits structured JSON logs with correlation IDs that tie the entire workflow together
> - **Prometheus + Grafana**: Real-time dashboards for success rates, latency p50/p95/p99, cost per transaction, accuracy metrics
>
> **Debugging workflow:**
> When something goes wrong, I work from the trace:
> 1. **Find the trace**: Using the transaction ID, pull the full execution trace
> 2. **Identify the failing step**: Which agent in the chain produced wrong output?
> 3. **Inspect inputs/outputs**: What did the agent receive? What did it produce? Was the input bad (upstream problem) or was the agent's logic wrong?
> 4. **Replay**: Take the exact inputs and replay the agent call in isolation. Is the failure reproducible?
> 5. **Root cause**: Usually one of: bad prompt, missing context in retrieval, model degradation, edge case in business rules
>
> **Alerts I'd set up for accounting agents:**
> - Category accuracy drops below 85% over rolling 24h window
> - VAT accuracy drops below 95% (P0 — immediate investigation)
> - Agent latency p95 exceeds 10s
> - Error rate exceeds 5%
> - Cost anomaly (spending 2x normal — possible infinite loop or retry storm)
>
> **Key principle**: In financial systems, a silent error is worse than a loud failure. I'd rather the system refuse to categorize (and queue for human review) than silently miscategorize.

---

## Category 3: Architecture & Scale

### Q5: "How would you approach expanding the AI accounting system to a new EU market — say, Italy?"

**Answer:**

> Italy is particularly interesting because of **Fatturazione Elettronica** — mandatory electronic invoicing through SDI (Sistema di Interscambio). This is both a challenge and an advantage.
>
> **Phase 1 — Configuration (1-2 weeks):**
> - Add Italian market config: VAT rates (22%, 10%, 5%, 4%), Piano dei Conti (chart of accounts)
> - Configure Italian tax rules in the deterministic engine
> - Set up SDI integration for e-invoicing (XML FatturaPA format)
>
> **Phase 2 — Data & Training (2-4 weeks):**
> - Collect Italian transaction samples (from beta users or synthetic)
> - Fine-tune or few-shot the categorization model with Italian merchant names and categories
> - Build Italian-specific evaluation dataset (100+ labeled transactions)
> - Validate VAT calculation rules with 100% test coverage
>
> **Phase 3 — Integration (2-3 weeks):**
> - SDI integration: send/receive e-invoices in FatturaPA XML format
> - Monthly VAT liquidation preparation (Italian-specific filing)
> - Handle Regime Forfettario (Italian flat-rate tax regime for small businesses)
>
> **Architecture advantage of MCP:**
> - The `categorization` MCP server just needs Italian training data — no architecture change
> - The `tax-engine` MCP server gets Italian rules added — tested independently
> - A new `italy-sdi` MCP server handles e-invoicing — completely new capability, plugs in via MCP
> - The orchestrator doesn't change at all — it calls the same tools, just with `country: "IT"`
>
> **The SDI advantage**: Since all Italian invoices are structured XML through SDI, we get clean, structured data for free. This actually makes Italian categorization EASIER than German (where receipts are photos/PDFs).

---

### Q6: "What's your experience with polyglot architectures? How do you handle C# + Python services?"

**Answer:**

> I haven't worked extensively in C#, but I've worked in polyglot environments (Python + Node + Go). The principles are the same:
>
> **Service boundary design:**
> - C# for what it's good at: type-safe domain logic, high-performance transaction processing, deterministic business rules
> - Python for what it's good at: LLM integration, rapid AI prototyping, rich ML library ecosystem
> - The boundary should be clean: **shared schema definitions** (Protobuf, OpenAPI, or JSON Schema)
>
> **Communication:**
> - gRPC for performance-critical, strongly-typed service-to-service calls
> - HTTP/REST for simpler, less frequent interactions
> - Message bus (Kafka/RabbitMQ) for async event-driven flows (transaction events, receipt uploads)
> - MCP for AI agent → service interactions (this is the layer you're betting on)
>
> **Practical concerns:**
> - **Distributed tracing**: OpenTelemetry spans must propagate across language boundaries — this is non-negotiable for debugging
> - **Shared schema evolution**: Breaking changes in a C# service's API must be caught before Python callers break. Schema validation in CI.
> - **Separate CI/CD**: .NET and Python have different build/test/deploy pipelines, but should deploy together for integration testing
>
> **My honest gap**: I'd need to ramp up on C#/.NET idioms — but I'm confident in the patterns (dependency injection, async/await, strong typing). The architecture thinking transfers. And the AI-heavy work where I'd spend most of my time is Python anyway.

---

## Category 4: Culture & Product Thinking

### Q7: "How do you think about building AI features for a product like Finom?"

**Answer:**

> Dmitry's phrase stuck with me: "Building product-focused engineering orgs from zero." I think about AI features through a product lens:
>
> **Start with the user's job-to-be-done:**
> - A German freelancer doesn't WANT accounting — they want "tax stuff handled, don't fine me"
> - The AI's job isn't "categorize transactions" — it's "make sure I never worry about bookkeeping again"
>
> **Progressive automation:**
> - **Level 1**: Suggest a category, user confirms → builds trust + training data
> - **Level 2**: Auto-categorize high-confidence, queue low-confidence → saves time
> - **Level 3**: Auto-book everything, prepare tax filing, user reviews before submission → almost hands-free
> - **Level 4**: File taxes automatically with user consent → full autonomy
>
> Each level requires earning user trust at the previous level. You can't jump to Level 4.
>
> **Measurement:**
> - "How many transactions did the user have to manually categorize?" → should trend toward zero
> - "How long from receipt upload to booked entry?" → should be <10 seconds
> - "How many corrections did the user make?" → accuracy metric from the user's perspective
> - NOT "how many API calls did we make" or "what was our model accuracy" — those are internal metrics
>
> **The AIC4 vision**: What excites me about your platform is that it's not a chatbot — it's proactive. The system DOES things for you without being asked. "I see it's time to prepare your monthly VAT advance return" → prepares it → presents for approval. That's a fundamentally different product than "ask me questions about your finances."

---

### Q8: "Why Finom? Why this role?"

**Answer:**

> Three things converge:
>
> 1. **The technical challenge**: Multi-agent systems for high-stakes, domain-specific workflows with real consequences — this is the hardest and most interesting problem in applied AI right now. Not chatbots, not demos — production agents that handle real money.
>
> 2. **The architecture bet on MCP**: You're making the right bet by building a composable, skill-based agent platform. Most companies are still wiring agents with custom glue code. MCP as the interface layer means you can scale to new markets and new capabilities without rearchitecting. I want to build this.
>
> 3. **Practical alignment**: I run my own entity (Fysp Tech), deal with multi-country invoicing and tax compliance firsthand. I feel the SMB accounting pain as a user. I know what "the receipt is in my camera roll and I'll deal with it later" feels like. Building the thing that eliminates that pain is deeply motivating.
>
> And honestly — the conversation with Dmitry was one of the most technically engaging interviews I've had. The fact that the CTO is hands-on enough to get excited about DSPy and has opened ClickHouse PRs tells me this is an engineering-first culture.

---

## Pre-Interview Checklist

- [ ] Review Finom's public product (sign up for free tier if possible, explore the UI)
- [ ] Know SKR03 basics: top 10 most common account codes for freelancers/SMBs
- [ ] Understand German UStVA (VAT advance return) filing process
- [ ] Be ready to whiteboard the transaction categorization pipeline
- [ ] Have MCP server example ready to discuss (from experiment)
- [ ] Know Finom's competitors: Qonto (AI features?), Revolut Business, N26 Business
- [ ] Prepare a question about their event-driven architecture (Kafka? RabbitMQ? Azure Service Bus?)
- [ ] Have the polyglot C#/.NET + Python integration story ready
