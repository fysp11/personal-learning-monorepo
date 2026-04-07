# Multi-Agent System Architecture for Fintech AI

Saved: 2026-04-07

## Why This Matters

Finom publicly describes its AI Accountant as a **distributed multi-agent system (MAS)** — multiple autonomous AI agents collaborating within a shared environment. This is not generic "we use AI." It's an explicit architectural choice.

If Ivo asks about multi-agent systems, agent coordination, or how to design reliable distributed AI workflows, this is the conversation to be ready for.

---

## What A Fintech MAS Looks Like

### Agent Roles In An Accounting MAS

Based on Finom's public product description (document recognition, expense categorization, reconciliation, tax preparation, tax filing), the likely agent decomposition:

1. **Document Intake Agent** — receives and normalizes incoming documents (invoices, receipts, bank statements)
2. **Classification Agent** — categorizes documents by type, urgency, and workflow destination
3. **Extraction Agent** — pulls structured data from documents (amounts, dates, parties, line items)
4. **Reconciliation Agent** — matches extracted data against transaction history and accounts
5. **Categorization Agent** — assigns accounting categories and tax treatment
6. **Tax Preparation Agent** — assembles tax-relevant records and declarations
7. **Review/Approval Agent** — routes to human review when confidence is low or consequences are high
8. **Filing Agent** — submits approved records to tax authorities

### Why Multi-Agent Over Monolithic

The multi-agent approach makes sense for this domain because:
- **Failure isolation** — a bad extraction doesn't necessarily corrupt reconciliation if the system can detect and route the failure
- **Independent scaling** — document intake scales differently from tax preparation
- **Independent evaluation** — each agent can be tested, measured, and improved independently
- **Specialization** — different tasks benefit from different models, prompts, and tooling
- **Auditability** — each agent's decision is traceable and reviewable

### The Hard Parts

1. **Inter-agent communication** — how agents pass state, context, and confidence signals
2. **Coordination and ordering** — which agents depend on which, how to handle parallel vs sequential execution
3. **Shared state management** — transaction context, document state, workflow progress
4. **Error propagation** — how one agent's failure affects downstream agents
5. **Consistency** — ensuring all agents operate on the same version of the truth
6. **Observability** — tracing a request across multiple agent boundaries

---

## How To Talk About MAS In The Interview

### If asked "how would you design a multi-agent accounting system?"

**Structure your answer around three layers:**

**1. Agent layer** — individual agents with clear input/output contracts
- Each agent owns one stage of the workflow
- Typed interfaces between agents (not free-form text passing)
- Per-agent evaluation metrics

**2. Orchestration layer** — coordinates agent execution
- DAG-based or workflow-engine-based execution
- Handles sequencing, parallelism, retry, and fallback
- Manages shared state (e.g., document context, transaction history)
- Routes to human review when confidence drops below threshold

**3. Quality layer** — cross-cutting evaluation and observability
- Per-agent metrics (accuracy, latency, error rate)
- End-to-end workflow metrics (completion rate, override rate, time saved)
- Failure taxonomy and alerting
- Drift detection and regression testing

### If asked "what makes multi-agent systems hard in production?"

**Top 5 challenges:**

1. **Cascading failures** — Agent A's bad output becomes Agent B's bad input. Need confidence propagation and circuit-breaking.

2. **Observability across boundaries** — Tracing a single document through 5+ agents requires correlation IDs, structured logging, and trace visualization.

3. **Evaluation at multiple levels** — Component evals are necessary but insufficient. End-to-end workflow evals catch interaction effects that per-agent tests miss.

4. **State management** — Agents need shared context (which transaction, which document, which customer) without tight coupling. This usually means a shared context store or event bus.

5. **Version coordination** — When you update one agent, does it break downstream agents? Need integration testing across agent boundaries.

### If asked "how is this different from a pipeline?"

**The key difference is autonomy:**
- A pipeline is a fixed sequence: step 1 → step 2 → step 3
- A MAS allows agents to make independent decisions: retry, request more info, escalate, delegate to another agent
- In a fintech MAS, the reconciliation agent might decide to request re-extraction if the data quality is too low, rather than just passing bad data forward

**But don't over-claim autonomy:**
- In production fintech, most agent "autonomy" is bounded by policy
- The system is agentic within guardrails, not free-form autonomous
- This is a strength, not a limitation — bounded autonomy is safer and more auditable

---

## Mapping To Your Experience

### Direct experience to reference

- Multi-stage document processing pipelines (30-60K docs/day) — this IS a multi-agent system in practice, even if the terminology was different
- Confidence-based routing between stages — this is inter-agent coordination
- Per-stage evaluation and observability — this is MAS observability
- Human review routing for low-confidence cases — this is the approval agent pattern

### How to bridge

"My experience with multi-stage document pipelines is architecturally very similar to what you'd call a multi-agent system. Each stage had clear input/output contracts, independent evaluation metrics, confidence-based routing, and failure isolation. The main difference in a formal MAS is that agents can make more autonomous decisions within their scope — retry, escalate, request re-processing — but the foundational patterns of typed interfaces, per-component evaluation, and end-to-end observability are the same."

---

## Key Vocabulary To Use Naturally

- **Agent boundary** — where one agent's responsibility ends and another's begins
- **Confidence propagation** — passing certainty signals between agents, not just data
- **Circuit breaking** — stopping downstream agents when upstream quality drops below threshold
- **Shared context** — the common state all agents reference (document, transaction, customer)
- **Workflow trace** — end-to-end visibility across agent boundaries
- **Bounded autonomy** — agents decide within policy, not freely
- **Failure taxonomy** — categorized failure types per agent and per workflow

---

## One-Sentence Thesis

**A production MAS in fintech needs three things: typed agent boundaries for failure isolation, confidence propagation for quality control, and end-to-end observability for trust.**
