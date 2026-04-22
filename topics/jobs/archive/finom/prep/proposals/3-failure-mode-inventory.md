# Finom Interview 3 — Failure Mode Inventory

Saved: 2026-04-22

Complete reference for every named failure mode in the Finom accounting AI pipeline. Codes are used across prep materials — this file is the authoritative definition source.

Use this to answer the Q9 "production pain points" question and any hostile follow-up about how the system breaks. Say the codes by name — it signals systematic thinking.

---

## How to Use in the Interview

> "I maintain a failure mode inventory for production AI systems — each mode has a name, a detection signal, and a response strategy. Let me walk through the ones most likely to surface in a financial AI workflow..."

Then name 3-4 from different categories. Never say "it could go wrong" — say "FM-07 is reverse charge miss, and the detection signal is..."

---

## Extraction Layer (FM-01 to FM-03)

### FM-01: OCR Drift
**What**: Scanned document quality degrades over time — camera blur, poor lighting, old scanner hardware. The extraction model was trained on clean docs; performance degrades silently.  
**Signal**: Confidence distribution P50 drops for `extraction` stage while input volume holds steady. Review queue rises with "extraction failed" labels.  
**Response**: Alert when P50 drops >2σ below 30-day baseline. Reject low-quality docs at ingestion with a user-visible message ("document too blurry — re-upload or enter manually").  
**Severity**: High — downstream stages inherit the error; VAT can't be correct if the amount is wrong.  
**Prevention**: Per-stage confidence; reject before routing downstream.

### FM-02: Vendor Name Ambiguity
**What**: Same vendor string means different things across markets. "Amazon" in Germany is likely AWS (reverse charge), in France could be consumer marketplace (standard VAT).  
**Signal**: Override rate rises on a specific merchant cluster in one market but not others.  
**Response**: Market-scoped vendor classification; add market flag to the categorization prompt or retrieval context. Never classify vendor intent globally.  
**Severity**: Medium — wrong category, possibly wrong VAT treatment.  
**Prevention**: Market-specific categorization config; vendor override list per market.

### FM-03: Missing Context
**What**: Transaction has no description, vendor name is a bank code, or document is unreadable. AI has no signal to categorize.  
**Signal**: Extraction stage returns empty or null fields; confidence drops below proposal threshold.  
**Response**: Route to `requires_review` with a structured prompt: "No vendor name detected — please categorize manually." Never auto-categorize blank transactions.  
**Severity**: Medium — should fail loudly, not silently.  
**Prevention**: Guard at extraction: if required fields are empty, short-circuit to `requires_review` before calling the categorization stage.

---

## Categorization Layer (FM-04 to FM-06)

### FM-04: Overconfident Miscategorization
**What**: Model returns high confidence (0.92+) but the category is wrong. Calibration error — raw scores don't match actual accuracy.  
**Signal**: ECE rises above 0.05; override rate on auto-booked transactions climbs above 2%.  
**Response**: Platt scaling to recalibrate raw scores. Tighten auto-book threshold. Do not widen confidence thresholds in new markets until ECE is verified.  
**Severity**: High — auto-booked wrong categorizations bypass human review.  
**Prevention**: Calibration check before enabling auto-book. ECE < 0.05 is the gate condition for advancing on the maturity ladder.

### FM-05: Category-Tax Mismatch
**What**: Correct category, wrong downstream tax treatment. Example: "Restaurant meal" is categorized correctly as entertainment, but the deterministic VAT mapper applies 19% standard instead of the applicable rate for that context.  
**Signal**: VAT correction rate rises for specific category × market combinations.  
**Response**: Per-category tax treatment tests; regression suite covering each category code → VAT rate mapping.  
**Severity**: High — deterministic stage should catch this, but only if the mapping is correct and tested.  
**Prevention**: Comprehensive category-to-tax mapping unit tests; run in CI on every config change.

### FM-06: Amount Parsing Error
**What**: Wrong decimal separator in foreign invoices (e.g., French "1.234,56" parsed as "1.234" instead of "1234.56"). Amount is structurally extracted but value is wrong.  
**Signal**: Amount delta between extracted and corrected value in review queue; override rate on amount field specifically.  
**Response**: Market-specific amount parsers. Validate extracted amounts against invoice total where available.  
**Severity**: Critical — wrong amount means wrong VAT amount, wrong booking, wrong ledger.  
**Prevention**: Locale-aware number parsing; test each market's decimal separator format explicitly.

---

## VAT / Policy Layer (FM-07 to FM-09)

### FM-07: Reverse Charge Miss
**What**: Cross-border B2B service (AWS Ireland, Google Ireland) auto-booked without applying §13b UStG reverse charge. Standard VAT applied instead.  
**Signal**: VAT amount present on bookings where `vendor_country != DE` AND `is_b2b = true`. Compliance audit catches it; detection by the time it's caught is expensive.  
**Response**: Reverse charge detection must be deterministic, not AI. Maintain a vendor list + VAT ID check. Any vendor triggering the rule **always** routes to `requires_review` regardless of confidence.  
**Severity**: Critical — §13b violation. Tax audit liability; formal Berichtigte Voranmeldung required.  
**Prevention**: Compliance override in the router: reverse charge vendors hard-route to `requires_review`. This override fires before any confidence check.

### FM-08: Exempt Category Misclassified
**What**: Medical service, educational subscription, or insurance premium misclassified as a standard-rate taxable purchase.  
**Signal**: VAT applied to transactions in exemption-eligible categories. Caught in manual review or tax audit.  
**Response**: Exemption list must be deterministic. Categories that map to exempt services must never have VAT applied by the AI stage.  
**Severity**: Critical — applying VAT to exempt services is a compliance violation; refund/correction required.  
**Prevention**: Category-to-exemption-status mapping in the policy module; explicit test cases for each exempt category.

### FM-09: Kleinunternehmer Treated as VAT-Liable
**What**: Freelancer or sole trader registered under §19 UStG (Kleinunternehmer — small business, VAT threshold below €22,000/year). System adds VAT to their outgoing invoices, which is illegal.  
**Signal**: VAT on invoices for Kleinunternehmer-registered accounts. Status is stored in user profile; detection requires linking categorization to account registration.  
**Response**: Account type must propagate into the pipeline context. Kleinunternehmer flag = zero VAT on all outgoing invoices, full stop.  
**Severity**: Critical — charging VAT as a Kleinunternehmer invalidates the §19 exemption for that tax year.  
**Prevention**: Account type lookup at pipeline entry; short-circuit VAT calculation for registered Kleinunternehmer accounts.

---

## Confidence/Calibration Layer (FM-10 to FM-11)

### FM-10: Confidence Inflation
**What**: Raw model scores are systematically too high across all categories. A model that says 0.9 is right only 0.7 of the time. Develops during fine-tuning or when training distribution shifts.  
**Signal**: ECE rises above 0.05; calibration reliability diagram shows a systematic curve below the diagonal.  
**Response**: Platt scaling — fit logistic regression on a held-out calibration set; remap raw scores to calibrated probabilities. Does not require model retraining.  
**Severity**: High — confidence-based routing becomes meaningless; auto-book threshold protects the wrong boundary.  
**Prevention**: Scheduled calibration checks; ECE monitoring per market per week.

### FM-11: Category Drift
**What**: Model categories shift over time as training distribution evolves. "SaaS" used to map to "software subscription"; now it maps to "professional services" in newer model versions.  
**Signal**: Regression tests fail on historical test cases; override rate rises on categories that previously auto-booked reliably.  
**Response**: Regression suite run in CI against every model or prompt change. Any new failure in a previously-passing case = P1 before deployment.  
**Severity**: Medium — systematic drift degrades accuracy without a clean trigger event.  
**Prevention**: Pinned model versions; regression testing before every model upgrade.

---

## Orchestration Layer (FM-12 to FM-16)

### FM-12: Multi-Rate Split Invoice
**What**: Invoice contains line items at different VAT rates (e.g., 19% equipment + 7% food). System applies a single rate to the full amount instead of splitting.  
**Signal**: VAT amount mismatch between system-calculated and user-corrected; specific error pattern on invoices with multiple line items.  
**Response**: Line-item-level extraction; separate VAT calculation per line item; aggregate to invoice total.  
**Severity**: High — incorrect VAT declaration.  
**Prevention**: Test suite with multi-rate invoices. Extraction stage must return line-item array, not just invoice total.

### FM-13: Credit Note Reversal Failure
**What**: Credit note from a vendor doesn't correctly reverse the original booking. Either the original booking is not found, or the reversal entries are wrong.  
**Signal**: Accounts with a booking + credit note but non-zero net balance where net should be zero.  
**Response**: Credit note must include reference to original booking ID. Reversal creates exact opposite double-entry of the original.  
**Severity**: High — incorrect account balances; tax period closing errors.  
**Prevention**: Credit note processor with reference resolution; test case for full booking + credit note cycle.

### FM-14: Escalation Storm
**What**: A bad batch (poor OCR quality, new merchant type, model confidence deflation) floods the human review queue. Queue grows faster than human reviewers can clear it; SLA breached.  
**Signal**: Review queue depth growing week-over-week; batch rejection rate spike; queue backlog alerts.  
**Response**: Circuit breaker on the escalation path. If review queue exceeds threshold, pause auto-escalation of new transactions and surface a system-level alert to ops.  
**Severity**: High — user experience degradation; manual backlog; SLA violation.  
**Prevention**: CircuitBreaker pattern on the review escalation path; batch anomaly detection to catch quality drops before they hit the queue.

### FM-15: Silent Reject
**What**: Transaction is ingested, enters the pipeline, then never reaches a terminal state (`auto_booked`, `proposal_sent`, `rejected`, `requires_review`). It disappears — no user notification, no error log visible to ops.  
**Signal**: Transaction lifecycle registry detects non-terminal state past SLA window. Without the registry, this is invisible.  
**Response**: Dead-letter queue for stranded transactions; ops alert with transaction ID and last-known state; automatic escalation to `requires_review` after SLA window.  
**Severity**: High — financial data loss; silent system failure that is hard to detect without explicit instrumentation.  
**Prevention**: Transaction lifecycle registry; terminal state enforcement in the orchestrator; `findStrandedTransactions()` query running on a schedule.

### FM-16: Stage Leak (Double Processing)
**What**: Transaction is processed by a stage twice due to a retry, network timeout, or queue redelivery. The double entry creates incorrect booking records.  
**Signal**: Duplicate booking entries for the same transaction ID; idempotency violation.  
**Response**: Idempotency registry keyed on `(transaction_id, stage_name)`. If the key exists, return the cached result immediately — do not re-execute.  
**Severity**: High — duplicate financial records; incorrect account balances.  
**Prevention**: Idempotency key on every stage execution; hash input for deterministic key generation.

---

## Filing / Integration Layer (FM-17 to FM-18)

### FM-17: Stale Market Config
**What**: VAT rates or chart-of-account codes are updated by a tax authority (e.g., Germany changes a reduced rate), but the market config in the pipeline is not updated. Wrong rates applied from the effective date until the config is corrected.  
**Signal**: Tax authority change published; config version not bumped; test suite on new-effective-date transactions fails.  
**Response**: Config versioning with effective dates; automated CI test that loads the config for each date and validates against known test cases.  
**Severity**: Critical — systematic wrong VAT from effective date; affects all transactions in the period.  
**Prevention**: Treat market config like a versioned schema; changelog; CI test that runs with effective-date parameterization.

### FM-18: ELSTER Double-Submit
**What**: Tax filing (UStVA) submitted to ELSTER twice — once from automated flow, once from a manual retry. ELSTER rejects the second submission or creates a duplicate record requiring manual amendment.  
**Signal**: ELSTER submission response code indicates "already received"; ops alert on filing endpoint.  
**Response**: Idempotency key per filing ID (period + account + type). Check key before submitting; if key exists, return the previous submission confirmation without re-submitting.  
**Severity**: Critical — tax compliance event; requires formal amendment if duplicate is processed.  
**Prevention**: Filing idempotency registry; the filing step is always `requires_review` regardless of confidence — never auto-submit.

---

## Quick Reference Table

| Code | Name | Layer | Severity | Key Prevention |
|------|------|-------|----------|---------------|
| FM-01 | OCR Drift | Extraction | High | P50 confidence monitoring |
| FM-02 | Vendor Ambiguity | Extraction | Medium | Market-scoped vendor config |
| FM-03 | Missing Context | Extraction | Medium | Guard on empty fields |
| FM-04 | Overconfident Miscategorization | Categorization | High | ECE < 0.05 gate |
| FM-05 | Category-Tax Mismatch | Categorization | High | Category→VAT mapping tests |
| FM-06 | Amount Parsing Error | Extraction | Critical | Locale-aware parsers |
| FM-07 | Reverse Charge Miss | VAT/Policy | Critical | Deterministic compliance override |
| FM-08 | Exempt Misclassification | VAT/Policy | Critical | Exemption status in policy module |
| FM-09 | Kleinunternehmer Error | VAT/Policy | Critical | Account type propagation |
| FM-10 | Confidence Inflation | Calibration | High | Platt scaling + ECE monitoring |
| FM-11 | Category Drift | Calibration | Medium | Regression CI on model updates |
| FM-12 | Multi-Rate Split Invoice | Orchestration | High | Line-item extraction |
| FM-13 | Credit Note Reversal | Orchestration | High | Reference resolution in credit notes |
| FM-14 | Escalation Storm | Orchestration | High | CircuitBreaker on review path |
| FM-15 | Silent Reject | Orchestration | High | Transaction lifecycle registry |
| FM-16 | Stage Leak | Orchestration | High | Idempotency registry |
| FM-17 | Stale Market Config | Filing/Integration | Critical | Config versioning + effective dates |
| FM-18 | ELSTER Double-Submit | Filing/Integration | Critical | Filing idempotency key |

---

## Interview Anchor Phrase

> "My pipeline maintains three invariants: every transaction reaches a terminal state (FM-15 prevention), VAT calculation is deterministic code not model output (FM-07/FM-08/FM-09 prevention), and confidence scores are calibrated before routing thresholds are trusted (FM-04/FM-10 prevention). If any of these invariants breaks, I have a named failure mode and a specific detection signal."

---

## Severity Definitions

| Level | Definition | Example |
|-------|-----------|---------|
| Critical | Regulatory violation; audit liability; requires formal correction | Wrong VAT rate filed, Kleinunternehmer VAT error |
| High | Wrong financial data; user must correct; SLA impact | Miscategorization, duplicate booking |
| Medium | Correctable error; no compliance impact | Wrong description, ambiguous vendor |
| Low | Cosmetic; no financial or compliance impact | Wrong formatting, minor display error |
