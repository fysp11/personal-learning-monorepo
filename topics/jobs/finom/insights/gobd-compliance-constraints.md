# GoBD Compliance Constraints for AI-Generated Bookings

Saved: 2026-04-17

GoBD (Grundsätze zur ordnungsmäßigen Führung und Aufbewahrung von Büchern, Aufzeichnungen und Unterlagen in elektronischer Form sowie zum Datenzugriff) is the German BMF directive governing digital bookkeeping. It was updated in November 2019 to explicitly address AI and automated systems.

This matters for Finom's AI pipeline because the pipeline is *making bookings* — not just suggestions. Every AUTO_BOOKED transaction is a GoBD-governed accounting record.

---

## What GoBD Actually Requires

### 1. Vollständigkeit (Completeness)
Every business transaction must be recorded. No transaction may be silently lost.

**AI implication:** The `LifecycleRegistry` and `find_stranded()` pattern is a GoBD control. A transaction stuck in CATEGORIZING for > 30 seconds without reaching a terminal state is a GoBD violation in the making. The pipeline must guarantee every transaction reaches exactly one terminal state.

### 2. Richtigkeit (Correctness)
Records must accurately reflect the underlying transaction.

**AI implication:** This is why confidence routing matters legally, not just technically. An AUTO_BOOKED transaction the user didn't review is a GoBD-compliant record *if and only if the confidence threshold has been validated*. An uncalibrated model with ECE > 0.10 booking at "85% confidence" produces legally suspect records. Platt scaling and the ECE gate are compliance controls, not just accuracy metrics.

### 3. Zeitgerechtheit (Timeliness)
Records must be made promptly — for bank transactions, this effectively means the accounting period in which the transaction occurred.

**AI implication:** A 30-day backlog of PROPOSAL_SENT transactions waiting for user confirmation can push bookings into the wrong accounting period. The pipeline needs a "pending review aging" alert — if a proposal sits > 7 days unconfirmed, escalate before the month-end close.

### 4. Ordnung (Order/Organization)
Records must be systematically organized and traceable.

**AI implication:** The trace_id in `observability.py` is not optional for GoBD compliance. Every booking must be traceable to the exact inputs that produced it: transaction data, prompt version, model version, confidence score, retrieval evidence. The `BookingEntry` must store the trace_id as a foreign key.

### 5. Unveränderbarkeit (Immutability)
Once recorded, an entry must not be modified without creating an audit trail of the change.

**AI implication:** If the model makes a wrong booking and the user corrects it, the correction must be a *new* entry with a reference to the original — not an in-place edit. This means the pipeline needs a `create_correction()` function, not an `update_booking()` function. The wrong booking stays in the ledger, marked as amended.

### 6. Nachvollziehbarkeit (Traceability)
An informed third party (e.g., tax auditor) must be able to trace every entry from raw transaction to booking.

**AI implication:** The tax auditor can ask "why was this €5000 payment booked to 6825 professional fees?" The answer must be in the system: "LLM categorization v2.0.0 (hash=abc123) with confidence 0.91, evidence: 'consulting service → professional fees', retrieved from transaction h6 (human-verified similar transaction)." This is the interview answer to "how does your pipeline handle audits?"

---

## What GoBD Does NOT Say

GoBD does not prohibit AI-generated bookings. The 2019 update explicitly acknowledges automated systems. What it requires is:
- The automated system must be *documented* (which model, which version, which rules)
- The automated system must be *verifiable* (auditor can trace any record)
- The automated system must be *controlled* (not a black box; thresholds must be documented and validated)

This is why the `AUTO_BOOK_THRESHOLD = 0.85` in the code should be a documented configuration parameter with a rationale comment, not a magic number.

---

## Concrete GoBD-Compliant Pipeline Requirements

### BookingEntry must include:
```python
@dataclass
class BookingEntry:
    # ... existing fields ...
    trace_id: str              # links to span tree in observability store
    prompt_version: str        # e.g. "v2.0.0"
    prompt_content_hash: str   # sha256 of prompt template
    model_id: str              # e.g. "claude-haiku-4-5-20251001"
    confidence_score: float    # the exact score at time of booking
    ece_at_booking: float      # ECE of the model at time this threshold was validated
    booked_at: datetime        # ISO 8601 with timezone
    amended_by: Optional[str]  # tx_id of correction if this was later amended
```

### Required audit trail queries:
```sql
-- "What model version booked all transactions in March?"
SELECT DISTINCT model_id, prompt_version, COUNT(*)
FROM bookings
WHERE booked_at BETWEEN '2026-03-01' AND '2026-03-31'
GROUP BY model_id, prompt_version;

-- "Show me every booking that was later corrected"
SELECT b.id, b.account_code, b.model_id, b.confidence_score,
       c.corrected_account_code, c.corrected_by, c.correction_reason
FROM bookings b
JOIN corrections c ON b.id = c.original_booking_id;

-- "What was the auto-book rate in Q1 vs Q4?"
SELECT QUARTER(booked_at), routing_status, COUNT(*) / total.n
FROM bookings;
```

### Retention:
- GoBD requires 10-year retention for accounting records (§238 HGB)
- This means the prompt versions and model IDs referenced in bookings must be stored for 10 years
- "We switched models last year and can't reproduce the reasoning" is not GoBD-compliant

---

## The Revisionssicherheit Test

A GoBD-compliant system must pass this test:
1. Take any booking from the last 10 years
2. Retrieve the trace_id
3. Find the span tree in the observability store
4. Find the prompt version + content hash
5. Find the model ID
6. Find the input transaction data
7. Reproduce the categorization decision (or explain why it can't be exactly reproduced)

Items 1-6 are engineering constraints. Item 7 is the honest acknowledgment that LLMs are not deterministic — which is why the *documented confidence score at time of booking* matters more than the ability to replay the exact output.

---

## What to Say in an Interview

When asked "how does your pipeline handle GoBD compliance?":

> "GoBD requires completeness, correctness, timeliness, order, immutability, and traceability. Each maps to a specific pipeline control. Completeness is the LifecycleRegistry — no transaction can be silently lost. Correctness is the calibration gate — the ECE threshold is a GoBD control, not just an accuracy metric. Immutability means corrections are new entries, not edits. Traceability means every BookingEntry stores the trace_id, prompt version, content hash, and confidence score. The 2019 update explicitly permits automated bookings — it doesn't prohibit AI, it requires documentation and verifiability. So our compliance posture is: we can answer any auditor question about any booking in the last 10 years."

The phrase "each maps to a specific pipeline control" is the signal. It shows you understand GoBD as an engineering specification, not just a legal obligation.

---

## GoBD and the Confidence Threshold Decision

The question "why 0.85 and not 0.90?" is a GoBD question as much as a product question.

The threshold must be:
1. **Documented** — in configuration, with a rationale comment
2. **Validated** — ECE < 0.05 at the time the threshold was set
3. **Reviewed** — after model updates, the threshold validation must be re-run

If someone asks "how did you decide on 0.85?", the GoBD-compliant answer is:
"The threshold was set after Platt scaling showed ECE = 0.031 on the holdout set. At that calibration level, 0.85 confidence corresponds to approximately 85% accuracy on the held-out set. The threshold is in configuration with a comment referencing the calibration run date and ECE measurement. It's reviewed after every model or prompt update."
