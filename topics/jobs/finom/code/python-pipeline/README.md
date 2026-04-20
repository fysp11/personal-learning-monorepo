# Python Pipeline — Transaction Categorization (Production Patterns)

Canonical Python implementation of the multi-stage fintech AI pipeline. All files use stdlib only — no external dependencies — so each runs immediately in any interview environment.

```bash
python3 pipeline.py             # core pipeline, 6 test cases
python3 pipeline.py --async     # async bounded-concurrency batch
python3 eval_harness.py         # severity-weighted eval with regression detection
python3 calibration_demo.py     # Platt scaling: fix overconfident model
python3 multi_market_drill.py   # DE + FR + IT side-by-side
python3 rag_categorizer.py      # RAG pipeline: retrieval + evidence gate
python3 resilience_patterns.py  # 5 production failure mode controls
python3 model_cascading.py      # 3-tier inference: cost-optimized routing
python3 shadow_rollout.py       # shadow mode → data-gated promotion → canary
python3 async_streaming.py      # webhook ingestion + SSE progress streaming
python3 prompt_versioning.py    # immutable prompt registry + experiment gates
python3 structured_output.py    # LLM JSON reliability: 5-stage parse stack
python3 observability.py        # span tracing, P99 metrics, audit chain
```

---

## File Reference

### [`pipeline.py`](pipeline.py) — Core Pipeline

The base pipeline. Every other file imports or extends it.

```
Transaction → categorize (AI) → calculate_vat (rules) → route (thresholds) → booking (math)
```

Four terminal states — every transaction must reach exactly one:
```
AUTO_BOOKED       confidence ≥ 0.85 + no compliance flag
PROPOSAL_SENT     confidence ∈ [0.55, 0.85)
REQUIRES_REVIEW   reverse charge B2B, or compliance trigger
REJECTED          confidence < 0.55
```

Key invariants:
- `categorize()` is the only AI call — returns `CategoryProposal(account_code, confidence, evidence)`
- `calculate_vat()` is a pure function — wrong VAT = amended filing, never in the model
- `route()` is 10 lines — intentionally minimal; all business logic is in the pipeline stages before it
- Reverse charge always → `REQUIRES_REVIEW`, regardless of confidence (compliance gate beats routing gate)

---

### [`eval_harness.py`](eval_harness.py) — Severity-Weighted Evaluation

Production eval pattern: raw accuracy is misleading for financial AI.

```python
SEVERITY_WEIGHTS = {Severity.CRITICAL: 4, Severity.HIGH: 3, Severity.MEDIUM: 2, Severity.LOW: 1}
```

What it measures:
- Severity-weighted accuracy (4× penalty for wrong VAT or missed reverse charge)
- ECE per market (calibration health)
- Regression detection against `BASELINE` dict
- Threshold sweep: accuracy at [0.70, 0.75, 0.80, 0.85, 0.90]

`"Test passed" !== "Production safe"` — a high raw pass rate can mask a single critical miss.

---

### [`calibration_demo.py`](calibration_demo.py) — Platt Scaling

Demonstrates the full calibration workflow: ECE measurement → Platt scaling → per-market policy.

Core principle: `AUTO_BOOK_THRESHOLD = 0.85` is only reliable when `ECE < 0.05`. Widen thresholds only after confirming calibration.

```python
a, b = fit_platt_scaling(train_pairs)   # 2 params, no retraining
calibrated = sigmoid(a * raw_score + b)
```

Per-market calibration state (example):
```
DE:  18 months, ECE=0.031, threshold=0.85   ✓ auto-book enabled
FR:   4 months, ECE=0.087, threshold=0.95   ⚠ calibration weak
IT:   1 month,  n=120,     shadow mode only  (< 500 labeled samples)
```

---

### [`multi_market_drill.py`](multi_market_drill.py) — Market Config as Data

Proof point: adding Italy requires exactly one config block and one merchant pattern dict. The orchestrator is unchanged.

```python
EXTENDED_MARKET_CONFIG = {
    **BASE_CONFIG,
    "IT": {
        "standard_vat": 0.22,           # Italy: higher than DE/FR
        "reduced_vat": 0.10,            # ristorante, travel
        "chart": "Piano dei Conti",
        "einvoicing_required": True,    # SDI mandatory since 2024
    }
}
```

Same `process_multi_market()` orchestrator handles DE/FR/IT — market config drives behavior.

---

### [`rag_categorizer.py`](rag_categorizer.py) — RAG Categorization

Why RAG for categorization: "Amazon" = account 4940 for a dev shop, 4800 for a law firm. The correct mapping is in the business's own transaction history, not in static rules.

```
Query rewrite → retrieve (cosine similarity) → re-rank (human-verified flag) → LLM → evidence gate
```

Evidence gate:
```python
def can_auto_book(proposal: CategoryProposal) -> bool:
    return proposal.confidence >= AUTO_BOOK_THRESHOLD and proposal.retrieval_support
```

`retrieval_support = False` caps confidence at 0.55 regardless of model output — "the model felt sure" is not evidence.

---

### [`resilience_patterns.py`](resilience_patterns.py) — Production Failure Mode Controls

5 patterns, each mapped to a named failure mode:

| Pattern | Failure Mode | What It Prevents |
|---------|-------------|-----------------|
| `LifecycleRegistry` | FM-15: Silent Reject | Transactions stuck in non-terminal state |
| `IdempotencyRegistry` | FM-16: Stage Leak | Double-booking on retry (SHA-256 content-addressable cache) |
| `RetryWithBackoff` | FM-12: Transient Failure | Lost transactions from rate-limit errors |
| `CircuitBreaker` | FM-14: Escalation Storm | Queue backup when confidence collapses (financial-AI variant) |
| `BatchAnomalyDetector` | FM-04: Confidence Inflation | P50 leading indicator before accuracy degrades |

The pipeline isn't reliable because the model is good. It's reliable because each failure mode has a named control.

---

### [`model_cascading.py`](model_cascading.py) — Tiered Inference

3-tier routing for cost-optimized categorization:

```
Tier 1 (Rule)   pattern_score ≥ 0.95   $0.00/tx   ~0ms    — no LLM needed
Tier 2 (Fast)   pattern_score ≥ 0.75   $0.0002/tx ~50ms   — single-category merchants
Tier 3 (Full)   pattern_score < 0.75   $0.003/tx  ~300ms  — ambiguous, description needed
```

Production target split: ~45% / ~35% / ~20% → 76% cost reduction vs all-Tier-3, accuracy parity on high-confidence segments.

Amount-aware routing in Tier 3: `MediaMarkt €799 → 4940 (IT)`, `MediaMarkt €899 → 0680 (capital asset)`.

Pattern scores are learned from override rates in `LifecycleRegistry`, not hardcoded.

---

### [`shadow_rollout.py`](shadow_rollout.py) — Shadow Mode & Gradual Rollout

Full maturity ladder: shadow (0%) → canary (5%) → ramping (25%) → full (100%). Promotion gated by accuracy delta, regression count, and calibration gap — not by model confidence.

Key: a single regression (control correct, treatment wrong) blocks promotion regardless of overall accuracy improvement.

---

### [`async_streaming.py`](async_streaming.py) — Async Streaming Pipeline

Webhook ingestion pattern with bounded concurrency (`Semaphore(3)`), SSE-format event streaming per stage, and graceful shutdown. Demonstrates 2.5× speedup over serial processing.

Without the semaphore: 50 concurrent bank-sync transactions → 50 simultaneous LLM calls → rate-limit cascade → lost transactions.

---

### [`prompt_versioning.py`](prompt_versioning.py) — Prompt Versioning

Prompts need the same deployment discipline as model weights: immutable after deploy, content-hashed, same promotion gates (accuracy delta, regressions, ECE), rollback in < 30 seconds. Every booking references the prompt version + content hash for compliance audit.

---

### [`structured_output.py`](structured_output.py) — LLM Output Parsing

Full reliability stack for LLM JSON responses:

```
strict → repair (Python bools, trailing commas, unquoted keys, buried JSON) → regex fallback → partial → failed
```

A `FAILED` parse that swallows the exception silently = wrong booking with no error. The parse outcome hierarchy maps to the routing hierarchy: failed parse → manual review queue.

---

### [`observability.py`](observability.py) — Pipeline Observability

OpenTelemetry-style span tracing per stage. Trace ID stored on `BookingEntry` creates a full audit chain: every booking links to the spans that produced it.

P99 categorize latency > 2s is a leading indicator of LLM provider degradation, detectable before users file complaints.

---

## Core Design Principles

| Principle | Implementation |
|-----------|---------------|
| AI does categorization, determinism does compliance | `categorize()` → AI; `calculate_vat()` → pure function |
| Confidence requires calibration before trust | ECE < 0.05 before widening thresholds |
| Evidence gate beats confidence alone | `retrieval_support` flag in RAG pipeline |
| Market rules are data, not code | `MARKET_CONFIG` dict — orchestrator unchanged per market |
| Each failure mode has a named control | 5 patterns in `resilience_patterns.py` |
| Cost optimization doesn't trade accuracy | Tier 1/2 only fire above high-signal threshold |

## Thresholds (from calibration, not intuition)

- `AUTO_BOOK_THRESHOLD = 0.85` — reliable only when ECE < 0.05
- `PROPOSAL_THRESHOLD = 0.55` — below this, signal too weak for a proposal
- Tier 1 pattern threshold: `0.95` — high enough that description context never changes the answer
- Tier 2 pattern threshold: `0.75` — still mostly single-category, fast model sufficient
- Circuit breaker confidence floor: `0.70` — below this, model output is noise
- Batch anomaly alert delta: `0.08` — P50 drop greater than this triggers on-call
