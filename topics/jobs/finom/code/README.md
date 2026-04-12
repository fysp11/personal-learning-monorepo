# Finom Code Examples

## 1. Multi-Agent System (MAS) Coordination Demo

`accounting-mas-pipeline.ts` — Demonstrates the orchestration and coordination patterns for a distributed multi-agent accounting system matching Finom's public AI Accountant architecture.

### What it shows

- **Typed agent boundaries**: Each agent (classification, extraction, reconciliation, categorization) has explicit input/output contracts via Zod schemas
- **Confidence propagation**: Agents return confidence levels (high/medium/low) that propagate through the pipeline
- **Circuit breaking**: The orchestrator halts processing when upstream confidence drops below threshold
- **Escalation routing**: Low-confidence cases route to human review instead of auto-completing
- **End-to-end observability**: WorkflowTrace captures per-agent timing, confidence, and events with correlation IDs

### What it does NOT show

- LLM calls — this is a structural demo, not an AI demo
- Production error handling, retry logic, or persistence
- Real document processing or OCR

### Why this architecture

Finom publicly describes its AI Accountant as a "distributed AI multi-agent system (MAS) that consists of multiple autonomous AI agents that collaborate within a shared environment." This demo makes the coordination layer concrete and discussable.

### Run

```bash
bun run demo
```

### Interview talking point

"I've worked with production multi-agent pipelines that follow this exact pattern — typed boundaries between agents, confidence propagation for quality control, circuit breaking when upstream quality drops, and end-to-end trace observability. The key insight is that the coordination layer is where reliability lives, not inside any single agent."

---

## 2. Live Round Rehearsal

`live-round-rehearsal.ts` — A compact, self-contained orchestrator for the interview live-coding warm-up.

### What it shows

- **Deterministic vs AI split**: VAT calculation is deterministic; categorization simulates AI
- **Market configuration**: Germany (SKR03) and France (PCG) with different account codes and VAT rates
- **Confidence-based routing**: auto-book / propose / reject based on confidence thresholds
- **Proposal mode**: medium-confidence cases produce structured proposals for human approval
- **Trace per stage**: every stage logs its decision and duration

### Run

```bash
bun run rehearsal
```

---

## 3. Evaluation Harness

`eval-harness.ts` — Production-grade evaluation framework for financial agent accuracy.

### What it shows

- **Field-level accuracy**: per-field comparison (account code, VAT rate, amounts, mechanism)
- **Severity-weighted scoring**: critical errors (wrong VAT, missed reverse charge) weigh 4x more than low-severity
- **Per-market breakdown**: separate accuracy metrics for DE and FR
- **Confidence calibration**: Expected Calibration Error (ECE) measuring whether confidence scores are trustworthy
- **Realistic failure modes**: simulated agent that misses reverse charge and mixed-VAT cases
- **Regression detection**: compares against a stored baseline to catch cases that were passing but now fail
- **Threshold analysis**: sweeps auto-book confidence thresholds to find the optimal safety/automation tradeoff

### Why this matters

Before any categorization agent goes to production, you need to know: Is it accurate enough? Are its confidence scores calibrated? Where does it fail? Did we break anything that was working? What's the right auto-book threshold? This harness answers all five.

### Test cases cover

| Case | Severity | What it tests |
|------|----------|---------------|
| Standard office supplies (DE) | Low | Happy path |
| SaaS subscription (DE) | Low | Software category matching |
| Reverse charge B2B (DE) | Critical | Cross-border VAT mechanism |
| Train ticket (FR) | Medium | French reduced VAT rate |
| Business dinner (DE) | Low | Entertainment categorization |
| Mixed VAT receipt (DE) | High | Multi-rate handling |
| Mobile plan (FR) | Low | French telecom |
| Kleinunternehmer §19 (DE) | Critical | VAT exemption detection |

### Run

```bash
bun run eval
```

### Interview talking point

"I always build severity-weighted evaluation before trusting any agent in production. Raw accuracy hides the difference between a wrong description and a wrong VAT rate — but in compliance, that difference is everything. Calibration tells us whether the confidence scores are actually useful for routing decisions."

---

## 4. Confidence Calibration Experiment

`confidence-calibration.ts` — Demonstrates the math behind confidence-based routing: ECE calculation, Platt scaling, per-market calibration, and threshold analysis.

### What it shows

- **Calibration analysis**: Bins predictions by confidence level, compares predicted vs actual accuracy
- **ECE/MCE calculation**: Expected and Maximum Calibration Error — the key metrics for trusting confidence scores
- **Platt scaling**: Post-hoc calibration that maps over-confident raw scores to calibrated probabilities
- **Per-market comparison**: Simulates DE (mature), FR (new), IT (zero-shot) with increasing calibration bias
- **Threshold analysis**: Shows how auto-book accuracy changes at different thresholds before/after calibration
- **ASCII calibration chart**: Visual reliability diagram for quick interpretation

### Run

```bash
bun run calibration
```

### Interview talking point

> "Confidence is just a number until you calibrate it. In a new market, the model may say 90% but only be right 70% of the time — that's over-confidence. Platt scaling fixes the mapping without retraining. The earned autonomy ratchet: start conservative, calibrate, then widen thresholds as trust is measured."

---

## 5. Multi-Market Expansion Drill

`multi-market-expansion-drill.ts` — A 15-minute drill demonstrating data-driven market configuration: adding new countries without code changes.

### What it shows

- **Zod-validated market config**: Tax rates, chart of accounts, reduced rates, exemptions, invoice requirements
- **Composable tax rules**: Standard → reduced → exempt → reverse charge cascade
- **Same transaction across markets**: Shows how €100 software purchase is taxed differently in DE/FR/IT
- **Italy SDI complexity**: Market-specific post-processing hooks for electronic invoicing
- **Adding Netherlands**: Zero code changes — just one config object

### Run

```bash
bun run multi-market
```

### Interview talking point

> "Market config is data, not code. You shouldn't need a deploy to add Italy. The configuration schema validates the new market's data structure at startup — if a field is missing or a rule overlaps, validation catches it before any transaction is processed."

---

## 6. MCP Accounting Skills Server

`mcp-accounting-server.ts` — A Model Context Protocol skill server exposing accounting tools across 5 EU markets.

### What it shows

- **MCP tool contracts**: Three tools with Zod input/output schemas (categorize, VAT, booking)
- **Market policy modules**: DE (SKR03), FR (PCG), ES (PGC), IT (Piano dei Conti), NL (RGS) — all from a single `MarketPolicy` interface
- **Deterministic vs AI separation**: VAT and booking are pure functions; categorization is the AI step
- **End-to-end workflow**: Chains all three tools with confidence routing to demonstrate the composable MCP architecture
- **Multi-market scaling**: Adding a market = adding a policy config, not changing the pipeline

### Why this matters

Dmitry said "the whole platform is going to be stitched with MCP-based interfaces." This demo makes that architecture concrete. Each tool is stateless, independently testable, and composable. The orchestration lives in the client, not the tool server.

### Run

```bash
bun run mcp-server
```

### Interview talking point

"I built an MCP skill server with three accounting tools — categorization, VAT, and booking — across five EU markets. The key design decision was making VAT and booking deterministic while keeping categorization AI-powered. Adding a new market is just a policy config object — the workflow shape and tool contracts don't change. This maps directly to how Finom can scale from Germany to France without rewriting the pipeline."

---

## 7. Production Resilience Patterns

`production-resilience-patterns.ts` — Five production reliability patterns for financial AI workflows.

### What it shows

- **CircuitBreaker**: Opens at configurable failure rate threshold, prevents FM-14 (Escalation Storm). Transitions CLOSED → OPEN → HALF_OPEN → CLOSED. Demo: three FAILING_VENDOR transactions trip the breaker at 60%, subsequent healthy transactions are blocked until recovery.
- **IdempotencyRegistry**: Input-hashed key per (txId, stageName). Prevents FM-16 (Stage Leak) and FM-18 (ELSTER double-submission). Demo: re-processing the same two transactions returns cached results with `[idempotency] HIT` log.
- **RetryWithBackoff**: Exponential backoff wrapper for transient LLM/API failures. Prevents silent drops from one-time network errors.
- **TransactionLifecycleRegistry**: Every transaction must reach an explicit terminal state (`auto_booked` / `proposal_sent` / `rejected_notified` / `error_logged`). `findStrandedTransactions()` queries for non-terminal transactions past SLA window. Prevents FM-15 (Silent Reject).
- **BatchAnomalyDetector**: Tracks rolling confidence distribution per batch (P10/P50/P90). Emits anomaly if current P50 is >2σ below historical — signals OCR drift (FM-01) or confidence inflation (FM-10) early.

### What it does NOT show

- LLM integration — categorization is simulated with deterministic responses
- Persistence — registry is in-memory for demo purposes
- Production retry budgets — backoff is simplified

### Run

```bash
bun run resilience
```

### Key output to recognize

```
[circuit:categorization] → OPEN (failure rate 60% > threshold 40%)
Found 1 stranded transaction(s): tx_stranded
Action: send to dead letter queue + alert ops (FM-15 prevention)
```

### Interview talking point

"Each pattern in this demo is named after a specific failure mode from the production failure catalog I maintain. The circuit breaker prevents escalation storms where a bad document batch floods the human review queue. The transaction lifecycle prevents silent rejects — transactions that were ingested but never reached a terminal state. These aren't abstract patterns; they're responses to specific failure modes I've thought through for financial AI workflows."

---

## 8. Autonomous Batch Processor

`autonomous-batch-processor.ts` — The "go do the task, then come back" agentic pattern Ivo Dimitrov described as the product goal.

### What it shows

- **Month-end autonomous close**: Processes a 15-transaction batch (Anna's March 2026) and returns a structured `MonthCloseReport` — not just a list of results
- **Three-tier output**: `autoProcessed` (no user action needed), `proposalsForApproval` (confirm or override), `requiresAttention` (genuinely ambiguous + all reverse-charge items)
- **Earned autonomy by category**: Known SaaS/travel/coworking → auto-book. Restaurants, new vendors → propose. Reverse charge (AWS Ireland, Google Ireland) → always surfaces regardless of confidence. Filing → always requires explicit user signature.
- **Draft UStVA**: Aggregates Zahllast from confirmed bookings only (conservative). Shows Kz 81, Kz 63 line items.
- **Natural-language summary**: "I processed 15 transactions… I'll wait for your signature." — the "come back" message.
- **Audit log**: Every routing decision with confidence, category, and reason.

### The architectural distinction

All other code demos process transactions one at a time. This demo takes a batch and owns the entire month-end close:

```
Input:  15 raw transactions for a user's accounting period
Output: {
  autoProcessed: 8 items,      → silent
  proposalsForApproval: 3,     → 30 seconds of user time
  requiresAttention: 4,        → includes 2 reverse-charge items
  draftUStVA: { zahllast: 1301.44, requiresUserSignature: true },
  summary: "I processed 15 transactions..."
}
```

### Run

```bash
bun run autonomous-batch
```

### Key output to recognize

```
── Summary ──
I processed 15 transactions for 2026-03. 8 were categorized and booked
automatically. 3 need your confirmation... 4 require your attention,
including 2 reverse-charge item(s)... Zahllast of €1301.44.
Review the flagged items and draft before I submit to ELSTER —
I'll wait for your signature.
```

### Interview talking point

"This is the distinction Ivo drew between a passive copilot and a proactive workflow agent. The batch processor doesn't ask the user to do the work — it does the work and comes back with the results, surfacing only what genuinely requires human judgment. The reverse-charge items always surface, and filing always requires explicit approval — the earned autonomy is selective, not blanket."
