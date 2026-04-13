# Interview 3 — Live Round Scenario Playbook

Saved: 2026-04-11

These are the most likely exercise shapes for the 60-minute live coding round, with step-by-step execution plans. The goal is not to pre-solve every problem — it is to have clear decomposition reflexes so you can start scoping immediately rather than freezing.

---

## Scenario A: "Design and implement expense categorization for German SMBs"

**Most likely opening.** Maps directly to Finom's core AI Accountant product.

### Scoping phase (5 min)

Ask/clarify:
- Is the input a raw bank transaction, an uploaded receipt, or both?
- Should this handle only Germany or be multi-market from the start?
- What is the expected output: a proposed booking entry, just a category label, or a full accounting record?
- Should it auto-book high-confidence results or always propose?

### Architecture sketch (5 min)

```
Transaction Event
  → Stage 1: Feature Extraction (AI) — merchant name, amount, date from raw text
  → Stage 2: Category Proposal (AI) — match to SKR03/SKR04 account code
  → Stage 3: VAT Calculation (Deterministic) — apply DE rules based on category
  → Stage 4: Confidence Router (Deterministic) — auto-book / propose / reject
  → Stage 5: Booking Entry (Deterministic) — create accounting record
```

### Key design decisions to state out loud

1. "VAT calculation is deterministic — too risky for LLM"
2. "Category proposal is the AI step — merchant text is genuinely ambiguous"
3. "Confidence routing gives us earned autonomy — high confidence auto-books, medium proposes for approval, low rejects"
4. "The trace captures every stage decision for auditability"
5. "I want one operator metric from the start — review rate or minutes of review per 100 transactions — so we can prove this compresses work instead of moving it around"

### Implementation order (50 min)

1. Define typed interfaces: `TransactionInput`, `CategoryProposal`, `VatCalculation`, `BookingEntry`, `WorkflowOutcome` (10 min)
2. Implement deterministic VAT calculation with market config (10 min)
3. Implement categorization function (mock AI with keyword matching) (10 min)
4. Wire the orchestrator with confidence routing (10 min)
5. Add trace/observability and test cases (10 min)

### What to say if they probe further

- "For production, the categorization function would call an LLM with structured output (Zod schema or JSON mode)"
- "I'd add a learning loop: user overrides feed back into the model or update keyword rules"
- "For France, I'd parameterize the market config — same workflow shape, different account codes and VAT rates"

---

## Scenario B: "Refactor this single-agent workflow into controllable stages"

**They give you a big messy function.** Your job is to decompose it.

### Approach

1. Read the code. Identify what it does in sequence.
2. Draw stage boundaries: where does input parsing end? Where does policy start? Where is the LLM call?
3. Extract each stage into a function with typed input/output.
4. Add confidence at each AI boundary.
5. Add a routing decision after the AI stages.
6. Wire stages through a simple orchestrator.
7. Add a trace array that captures each stage result.

### What to say while working

- "I'm looking for where policy decisions are hidden inside the prompt — those should be deterministic code"
- "This merge of extraction and classification should be two stages because they fail differently"
- "I'm adding typed contracts between stages so each one is independently testable"

### Anti-patterns to call out

- Tax rules baked into the LLM prompt → extract to deterministic function
- Single confidence threshold for the whole pipeline → per-stage confidence
- No trace/audit trail → add structured logging
- Auto-action on low-confidence → add proposal mode

---

## Scenario C: "Build a minimal evaluation harness for a categorization agent"

### Architecture

```
EvalRunner
  ├── TestCaseLoader — reads test cases from file or inline array
  ├── AgentUnderTest — the categorization function to evaluate
  ├── FieldComparator — per-field accuracy (category, VAT rate, amount)
  ├── SeverityWeighter — critical errors (VAT) >> cosmetic errors (description)
  ├── CalibrationChecker — confidence vs actual accuracy
  └── ReportGenerator — per-market breakdown, regression detection
```

### Implementation order

1. Define `TestCase` and `EvalResult` types (5 min)
2. Build inline test suite: 5-8 transactions covering standard, reverse charge, exempt, mixed VAT (10 min)
3. Implement field-level comparison (10 min)
4. Add severity-weighted scoring (10 min)
5. Generate summary report (10 min)
6. Show calibration: are high-confidence results actually correct more often? (10 min)

### Key talking points

- "Severity-weighted accuracy is more meaningful than raw accuracy — a wrong VAT rate is worse than a wrong description"
- "Calibration tells us whether the model's confidence is trustworthy, which directly affects routing thresholds"
- "I'd run this eval suite in CI against every model or prompt change"

---

## Scenario D: "Add confidence scoring and human review to an existing workflow"

### Steps

1. Define confidence as a numeric score (0-1) returned alongside every AI output
2. Define thresholds: auto-act (≥0.85), propose (0.5-0.85), reject (<0.5)
3. Create a `ReviewQueue` type: holds the transaction, the proposal, and the reason for review
4. Route based on confidence after the AI stage
5. For "propose" cases, create a structured proposal that shows the user what the system would do and why
6. Add approval/rejection tracking for measuring override rates
7. Wire observability: log confidence distribution, override rates, and severe-error rates

### What makes this answer strong

- Connecting thresholds to business outcomes: "The auto-book threshold should be tuned based on the override rate we're willing to accept"
- Mentioning that thresholds are per-market: "Germany has more training data so thresholds can be tighter; France starts more conservative"
- Describing the feedback loop: "Overrides feed back into model training or rule updates"

---

## Scenario E: "Build a tool-calling wrapper / MCP skill server"

### Architecture

```
MCP Server
  ├── categorize_transaction — takes transaction, returns category proposal
  ├── calculate_vat — takes amount + market + category, returns VAT breakdown
  ├── create_booking — takes all prior results, returns accounting entry
  └── health_check — returns server status and model availability
```

### Implementation

1. Define tool schemas (JSON Schema or Zod) (10 min)
2. Implement each tool as a standalone function (15 min)
3. Wire MCP server (stdio or HTTP) (15 min)
4. Test with a simple client or curl (10 min)
5. Add error handling and timeout (10 min)

### What to say

- "Each tool is stateless and independently testable"
- "The orchestration lives in the client, not the tool server — tools are capabilities, not workflows"
- "This maps to Finom's MCP-based architecture where skills are composable building blocks"

---

## Scenario F: "Refactor a sync batch endpoint to async without breaking clients"

**High-value variation.** This lets you show execution discipline, interface ownership, and measurable performance improvement without hiding behind architecture slides.

### Scoping phase (3-4 min)

Ask/clarify:
- Which public endpoints or payloads are contractually frozen?
- Is the pain point latency, worker starvation, timeout rate, or all three?
- Can I change internals only, or also introduce a queue/job model?
- Do you want a code refactor, a design sketch, or both?

### Architecture sketch (3-4 min)

```
HTTP Contract (unchanged)
  → Request Validation (Deterministic)
  → Categorization Service Boundary (unchanged port)
  → Execution Model (changed)
      sync sequential loop
      → bounded async fan-out with semaphore
  → Structured Per-Item Outcome
  → Response Contract (unchanged)
```

### Key design decisions to state out loud

1. "I'm changing execution strategy, not API shape."
2. "Shared contracts come first so client integrations do not drift."
3. "Concurrency is bounded, not unbounded, because latency wins are useless if they create provider instability."
4. "I want explicit per-item errors so batch behavior is observable and debuggable."

### Implementation order (50 min)

1. Freeze the request/response models and endpoint paths (5 min)
2. Extract the categorization dependency behind a shared interface / port (10 min)
3. Replace the sequential batch loop with `asyncio.gather` plus semaphore-limited concurrency (15 min)
4. Preserve ordering and error shape in the batch response (10 min)
5. Add one contract-parity test and one latency/behavior test (10 min)

### What to say if they probe further

- "This is the same control principle as Finom workflows: keep the public contract deterministic, move ambiguity or waiting into a controlled execution layer."
- "I'd only move to queue-backed background processing if request-time SLA still fails after bounded concurrency."
- "The metric is not just p95 latency; it's p95 latency while preserving contract parity and keeping failure semantics explicit."

---

## Universal Moves (use in any scenario)

### Always do first
- State the workflow boundary before coding
- Separate AI-powered steps from deterministic steps
- Define typed contracts between stages
- Name the business/operator metric the slice is supposed to improve

### Always build
- Confidence propagation
- Trace/observability object
- At least one test case that escalates to human review
- One explicit terminal state for low-confidence or failed items

### Always say
- "This is where the AI adds value — the input is genuinely ambiguous"
- "This part stays deterministic — the failure cost is compliance-related"
- "I would measure [specific metric] to know this is actually reducing manual work"
- "I'm optimizing for a slice a domain team could actually adopt next week, not a demo-only architecture"

### Never do
- Start coding without scoping
- Let Claude Code invent the architecture
- Accept generated code without reading it
- Use "the model will figure it out" as a design decision
- Over-abstract when a simple function works
