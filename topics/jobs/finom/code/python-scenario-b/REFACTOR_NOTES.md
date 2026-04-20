# Scenario B — Refactoring Analysis

This is what you say **before touching the keyboard** in a live round.
Spend 3-4 minutes on this analysis. The interviewer is watching you read and diagnose, not just code.

---

## What's Wrong — Name These Out Loud

### 1. AI and policy are merged (critical)

```python
def fake_ai_call(merchant, amount, description, is_b2b):
    vat = round(amount * 0.19 / 1.19, 2)  # VAT rate hardcoded here
    return {"category": "IT_COSTS", "account": "4940", "vat": vat, ...}
```

The AI call is computing VAT inside the same function that proposes the category.
**Problem:** VAT is law, not prediction. If the AI function is ever wrong about the category, it will also return a wrong VAT amount with no way to separate which part failed.
**Fix:** Extract VAT calculation as a pure deterministic function called *after* the AI stage.

**What to say:** "The AI stage should return a category proposal with a confidence score. VAT calculation should be a separate deterministic function that receives the confirmed category."

---

### 2. No confidence score from the model

```python
confidence = random.uniform(0.5, 1.0)  # THIS IS WRONG
```

The confidence value is random — not derived from the AI output.
**Problem:** The routing decision downstream is completely meaningless. A system that warns on low confidence but proceeds anyway is strictly worse than no confidence check at all, because it creates false safety.
**Fix:** The AI stage must return a numeric confidence in `[0, 1]` derived from model output (logprob, calibrated classifier score, or self-evaluated certainty). The router uses this score with calibrated thresholds.

**What to say:** "Confidence must come from the model or a calibrated post-processor. Random confidence is misleading — it trains engineers to ignore the warning."

---

### 3. Low confidence → warning and continue (never acceptable in finance)

```python
if confidence < 0.6:
    print(f"WARNING: low confidence — but booking anyway")
```

This is the worst possible outcome: the system knows it's uncertain and books anyway.
**Problem:** In financial workflows, low confidence must route to human review or rejection. A warning that doesn't change the output is not a safety mechanism — it's debt masquerading as safety.
**Fix:** Three-way router: confidence ≥ 0.85 → auto-book, 0.55–0.85 → proposal for human review, < 0.55 → reject and queue.

**What to say:** "The router's job is to give every transaction a deterministic terminal state. Warning-and-continue means there's no terminal state for uncertain cases — the system is making a choice it didn't earn."

---

### 4. Reverse charge is buried and silent

```python
if is_b2b:
    result["mechanism"] = "reverse_charge"
    result["vat"] = 0.0
```

The compliance rule is applied **after** the AI call and **before** routing, without any logging.
**Problem:** (1) Reverse charge overrides the category without explaining why. (2) There's no audit trail for the override. (3) Reverse charge should always force human review in v1 — it's a compliance decision, not a confidence decision.
**Fix:** Add a pre-routing compliance check: if `is_b2b=True`, force `mechanism=reverse_charge` and route to `REQUIRES_REVIEW` regardless of confidence. Log the override with the original AI output preserved.

**What to say:** "Compliance overrides must be logged explicitly. The fact that something was reverse-charge should appear in the trace as a named decision, not a silent mutation of the AI result."

---

### 5. No typed contracts

The function returns a plain dict with no schema. Downstream code doesn't know what fields to expect.
**Problem:** Dict-based contracts break silently. A missing `"vat"` key causes a `KeyError` somewhere else, not at the source. Typed Pydantic models make failures visible at the boundary.
**Fix:** Define `CategoryProposal`, `VatCalculation`, `RoutingStatus`, `WorkflowOutcome` as Pydantic models or dataclasses before any logic.

---

### 6. No trace / no observability

The function returns the booking entry only — no record of what happened at each stage.
**Problem:** When a transaction is miscategorized in production, the support team has no way to answer "what did the model propose, what was the confidence, and why did this end up in the review queue?" — the answer is lost.
**Fix:** Add a `trace` list to `WorkflowOutcome` that captures per-stage name, duration, decision, and confidence.

---

### 7. Single terminal state (always books)

The function always returns a booking dict. There is no path to "requires_review" or "rejected".
**Problem:** A downstream system that receives this dict assumes the transaction was confidently categorized. There's no mechanism for the workflow to ask a human for help.
**Fix:** `WorkflowOutcome.status` must be a discriminated enum: `AUTO_BOOKED | PROPOSAL_SENT | REQUIRES_REVIEW | REJECTED`. Every transaction reaches exactly one terminal state.

---

## Refactoring Order (for the live round)

1. **Define typed contracts** (5 min): `CategoryProposal`, `VatCalculation`, `RoutingStatus`, `WorkflowOutcome`
2. **Extract deterministic stages** (10 min): `calculate_vat()`, `route()`, `create_booking()`
3. **Clean up the AI stage** (5 min): make `categorize()` return a `CategoryProposal` with real confidence
4. **Add compliance check** (3 min): reverse-charge detection before routing
5. **Wire orchestrator with trace** (5 min): chain stages, capture timing and decisions
6. **Run test cases** (5 min): at least one auto-book, one review, one reverse-charge

See `good_pipeline.py` for the clean implementation.

---

## One-Sentence Diagnosis (for the live round opener)

> "This function merges AI judgment with deterministic policy, replaces calibrated confidence with a random number, warns on low confidence but acts anyway, has no typed contracts, and always books — there's no path to human review. I'll extract the stages, add real confidence routing, and make every terminal state explicit."
