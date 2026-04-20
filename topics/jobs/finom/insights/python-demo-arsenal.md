# Python Demo Arsenal — File-to-Question Map

Saved: 2026-04-17

All files in `code/python-pipeline/` run with `python3 <file>.py` — stdlib only, no setup.
Use this guide to pick the right demo for a given interview question in under 10 seconds.

---

## Quick-pick matrix

| Interview question | File to open | Key output to point at |
|-------------------|-------------|----------------------|
| "Walk me through your pipeline architecture" | `pipeline.py` | 4 terminal states, stage contracts |
| "How would you test this in production?" | `eval_harness.py` | Severity-weighted accuracy, regression gate |
| "How do you trust a model's confidence score?" | `calibration_demo.py` | ECE before/after Platt, per-market policy |
| "How would you scale to France/Italy?" | `multi_market_drill.py` | One config block, orchestrator unchanged |
| "How does RAG improve categorization?" | `rag_categorizer.py` | Evidence gate: retrieval_support flag |
| "How would you handle infrastructure failures?" | `resilience_patterns.py` | FM-15 through FM-04, named controls |
| "How do you optimize LLM costs?" | `model_cascading.py` | 3-tier routing, 55% cost reduction |
| "How would you deploy a new model safely?" | `shadow_rollout.py` | Shadow → gates → canary → full |
| "How does the pipeline fit real-time systems?" | `async_streaming.py` | SSE events, semaphore, 2.5× speedup |
| "What if the LLM returns bad JSON?" | `structured_output.py` | 5-stage parse stack, 8 failure modes |
| "How do you debug production incidents?" | `observability.py` | Span tracing, P99, full audit chain |
| "What's wrong with this agent code?" | `python-scenario-b/bad_agent.py` | 7 named sins + refactor |
| "How would you handle invoice financing risk?" | `python-credit-risk/risk_pipeline.py` | Policy-gates-before-AI-score |

---

## Per-file framing (2 sentences each)

### `pipeline.py`
"This is the core pattern: AI does categorization, pure functions do VAT, deterministic routing handles compliance. Every transaction reaches exactly one of four terminal states — the compiler-equivalent guarantee for a financial workflow."

### `eval_harness.py`
"Raw accuracy is misleading — a 90% pass rate with one wrong reverse-charge call is a compliance failure. This harness weights critical misses 4×, which forces the eval to reflect actual financial risk rather than test-count arithmetic."

### `calibration_demo.py`
"Confidence scores aren't probabilities unless you calibrate them. Platt scaling fits two parameters on a holdout set — no retraining — and gives you an ECE you can gate against before widening auto-book thresholds."

### `multi_market_drill.py`
"The principle is that market rules are data, not code branches. Adding Italy is one config dict and one merchant pattern map — the orchestrator imports both and runs unchanged, and Italy's SDI e-invoicing requirement becomes a post-booking async flag."

### `rag_categorizer.py`
"Static keyword rules can't know that 'Amazon' means IT costs for a dev shop and office supplies for a law firm — but the business's own transaction history can. The evidence gate here requires retrieval_support=True before auto-booking, so 'the model felt sure' never becomes a booking without evidence."

### `resilience_patterns.py`
"The pipeline isn't reliable because the model is good — it's reliable because each named failure mode has a named control. FM-15 is stranded transactions, FM-16 is double-booking on retry, FM-14 is the circuit breaker that trips on confidence collapse rather than just error rate."

### `model_cascading.py`
"Pattern score determines tier routing before any model is called — Tier 1 is free and fires on >95% certain merchants like Lieferando. Tier 3 handles genuine ambiguity like 'Amazon' where the description context determines whether it's 4940 or 4800, and whether the amount crosses the €800 capitalization threshold."

### `structured_output.py`
"The parse reliability stack (strict → repair → regex → partial → failed) maps directly to the routing hierarchy: a failed parse routes to manual review, just like a rejected categorization. The key discipline is never swallowing a ParseError — a silently-swallowed JSON decode error becomes a silent wrong booking, which is the worst possible failure mode in financial AI."

### `observability.py`
"Every span carries the trace_id that gets stored on the BookingEntry — when compliance asks 'what happened to transaction X?', the trace answers it. Stage latency metrics matter because P99 categorize > 2s is a leading indicator of LLM provider degradation, detectable before users start filing complaints."

### `async_streaming.py`
"The bounded-concurrency semaphore is the single most important pattern for production LLM pipelines — without it, 50 concurrent bank-sync transactions become 50 simultaneous LLM calls, which immediately hits rate limits and loses transactions. The event sink queue decouples processing from streaming, so the browser client sees stage-by-stage progress in real-time without waiting for the full batch."

### `shadow_rollout.py`
"New models don't earn traffic by being confident — they earn it by passing gates. Shadow mode catches regressions before any user is affected; a single critical miss blocks promotion regardless of overall accuracy improvement."

### `python-scenario-b/bad_agent.py` → `good_pipeline.py`
"The bad version merges AI judgment with VAT calculation into one function, uses random confidence scores, and has no terminal states. The refactoring exercise isolates these into a compliance gate before routing, typed contracts between stages, and a per-stage trace for auditability."

### `python-credit-risk/risk_pipeline.py`
"Invoice financing has asymmetric failure costs — a false positive (approve bad invoice) is capital loss, a false negative (decline good invoice) is recoverable. Policy gates run before AI scoring: if a hard limit would decline anyway, don't pay for the model call, and don't create a situation where a strong AI score might be used to rationalize overriding policy."

---

## Live-round operating discipline

**First 90 seconds (scoping):**
"Before I write anything — the two decisions that shape everything: where does AI judgment end and deterministic policy begin, and what are the four terminal states? Let me sketch those first."

Draw: `Input → [AI stage] → [Compliance gate] → [Router] → {AUTO_BOOKED | PROPOSAL_SENT | REQUIRES_REVIEW | REJECTED}`

**When you get a skeleton to modify:**
1. Read it fully before touching it (30 seconds)
2. Name what's wrong: "I see three things — no terminal states, VAT in the AI function, no typed contracts"
3. Fix in order: contracts first, then compliance gate, then routing, then AI call

**When you get a blank file:**
1. Write the dataclasses first (30 seconds) — Transaction, CategoryProposal, VatCalculation, WorkflowOutcome
2. Write the routing constants (10 seconds) — AUTO_BOOK_THRESHOLD, PROPOSAL_THRESHOLD
3. Write categorize() stub → calculate_vat() stub → route() → then fill in
4. Run early, comment what's missing rather than leaving syntax errors

**When something breaks:**
"I see what's happening — [one sentence diagnosis]. Let me fix [specific thing] first, then verify with a print statement, then move to the next stage."

**When time is short:**
"I have the core pipeline working. The two things I'd add in production are [calibration gate before widening thresholds] and [idempotency registry on the categorize call to prevent double-booking on retry]. I can sketch either — which is more interesting to you?"

---

## Architecture vocabulary (minimum set)

These 8 terms need to come out fluently in any live round:

| Term | One-sentence definition |
|------|------------------------|
| ECE | Expected Calibration Error — measures whether confidence scores are accurate probabilities |
| Platt scaling | 2-parameter logistic fit on holdout set; calibrates overconfident models without retraining |
| Evidence gate | Auto-book requires retrieval_support=True, not just confidence ≥ threshold |
| Circuit breaker | Trips on confidence distribution collapse, not just error rate — financial AI variant |
| Idempotency registry | SHA-256 content-addressable cache per (tx_id, stage) — prevents double-booking on retry |
| Maturity ladder | Shadow → Canary → Ramping → Full; each stage gated by data, not by model confidence |
| Policy gate | Hard rule that runs before AI scoring and cannot be overridden by a model score |
| Severity weight | Critical misses weighted 4× in eval; raw accuracy is misleading for financial pipelines |
