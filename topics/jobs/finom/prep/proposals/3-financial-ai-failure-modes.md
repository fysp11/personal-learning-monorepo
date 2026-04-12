# Financial AI Workflow — Failure Modes Encyclopedia

Saved: 2026-04-11 (Iteration 4)

## Purpose

A catalog of specific, named failure modes in financial AI automation workflows. Use in the interview when asked about risk, reliability, evaluation, or production incidents. Each entry follows the same structure: what it is, how you detect it, root cause, mitigation, Finom example.

This document complements the eval harness (severity weighting, regression detection) and the MCP architecture (confidence routing, deterministic policy). Those tools *prevent* these failures; this catalog *names* them.

---

## Taxonomy Overview

| Category | Failure modes |
|----------|--------------|
| **Extraction failures** | OCR drift, currency confusion, date ambiguity |
| **Categorization failures** | Overconfident miscategorization, distribution shift, ghost categories |
| **VAT/Tax failures** | Vorsteuer rate error, reverse charge miss, mixed-rate split error |
| **Confidence failures** | Confidence inflation, threshold ossification, calibration drift |
| **Routing failures** | Auto-book creep, escalation storm, silent reject |
| **Orchestration failures** | Stage leak, partial trace, idempotency violation |
| **Market expansion failures** | Config collision, silent rule override, missing locale hook |

---

## Extraction Failures

### FM-01: OCR Drift

**What it is:** The extraction model correctly parsed documents during training/fine-tuning, but document formats in production are different enough that extraction accuracy degrades without triggering any alert.

**Symptom:** Gradually increasing user correction rate on amounts and dates. No hard errors — numbers are extracted, but they're wrong (e.g., reading "19,00" as "1900" due to German number formatting).

**Root cause:** German uses "." as thousands separator and "," as decimal separator (€1.234,56 = one thousand two hundred thirty-four euros and 56 cents). English-format OCR pipelines misparse this. Also: bold totals, rotated text in scanned invoices, handwritten annotations.

**Mitigation:**
- Locale-aware number normalization as a post-extraction step (deterministic)
- Test suite with German-format invoices from real-world scans
- Extraction confidence score that is penalized when the extracted amount doesn't match a known pattern (e.g., amount doesn't multiply: net × (1 + rate) ≠ gross)

**Finom example:** An AWS invoice shows "1.234,56 EUR" — a pipeline trained on English invoices extracts "1234.56" but if the locale normalization is wrong it becomes "1.23456". The Vorsteuer claim is off by 1000x. The sum check (net × rate = gross) should catch this before booking.

---

### FM-02: Date Ambiguity (Supply/Invoice Date Confusion)

**What it is:** An invoice has multiple dates — the service period, the invoice issue date, and possibly a payment due date. The extraction agent picks the wrong one as the "booking date."

**Symptom:** Transactions appear in the wrong tax period. A March invoice booked to February means the UStVA for February is overstated and March is understated.

**Root cause:** German invoices legally require both the Leistungsdatum (service date) and the Rechnungsdatum (invoice date). VAT is owed in the period when the service was rendered (for accrual-basis taxpayers), not when the invoice was issued. An extraction agent that just picks the first date it sees will be wrong for invoices with multi-day service periods.

**Mitigation:**
- Explicitly extract all date fields with typed labels (issue_date, service_date, due_date)
- Default to invoice date for EÜR users (cash-basis is simpler)
- Flag when service date and invoice date are in different tax periods — require human confirmation

---

### FM-03: Currency Confusion in Multi-Currency Accounts

**What it is:** A transaction is in a foreign currency, but the extraction agent uses the face amount without applying the exchange rate, producing a VAT claim in the wrong currency.

**Symptom:** A USD 100 charge from an American vendor appears as "€100 Vorsteuer claimed at 19%" — but €19 VAT was never actually paid.

**Root cause:** Most German SMEs are EUR-only, but freelancers working with US clients receive USD payments. Currency conversion is required before VAT treatment.

**Mitigation:** Detect non-EUR amounts in the extraction step. Apply the Bundesbank reference exchange rate for the invoice date. Flag multi-currency invoices for human review in the first 90 days of deployment for a new user.

---

## Categorization Failures

### FM-04: Overconfident Miscategorization

**What it is:** The categorization model assigns a wrong account code with high confidence (>0.85), causing it to bypass human review and auto-book incorrectly.

**Symptom:** Low override rate in aggregate (looks good), but periodic audits reveal systematic errors for specific merchant types. The user only notices at annual tax time.

**Root cause:** The model was trained on a large dataset where "Uber" → travel (4670). But a freelancer using Uber Eats for a business lunch should be Repräsentationskosten (4650) with a different deductibility limit. The model saw "Uber" and confidently assigned travel.

**Mitigation:**
- Train on per-merchant-type examples, not just merchant name
- Include transaction description text and amount range as features
- Post-hoc audit: sample 2% of auto-booked transactions and compare to what an accountant would say
- Never trust a single high-confidence signal — require consistent confidence across multiple feature dimensions

**Finom example:** "Uber Eats" auto-booked as travel expense for 1,000 users. At year-end, each user's EÜR claims full deductibility on meals that were only 70% deductible. A €2M aggregate Vorsteuer overclaim across the user base.

---

### FM-05: Distribution Shift (New Merchant Categories)

**What it is:** A category of merchants that didn't exist (or wasn't common) in the training set starts appearing — the model routes them to the nearest familiar category, which is wrong.

**Example:** AI tool subscriptions (ChatGPT, Midjourney) started appearing in 2023. A model trained on 2021–2022 data had no examples of this merchant category. It might categorize them as "advertising" (4900), "office supplies" (4930), or "software" (4920) depending on what pattern matched. Only one of those is correct for most use cases.

**Symptom:** Unknown merchant flags cluster around the same time period. Override rate spikes for a specific category.

**Mitigation:**
- Track "first seen" date for merchant categories
- When override rate for a merchant rises above threshold, flag for retraining
- Add explicit "unknown vendor" category with 100% human review routing
- Periodically audit the top-50 new merchants and add targeted training examples

---

### FM-06: Ghost Category Assignment

**What it is:** The model assigns a valid-looking SKR03 account code that doesn't actually exist in the user's specific chart of accounts configuration, or that exists but is reserved for a different entity type.

**Symptom:** The booking goes through validation but is rejected by the downstream accounting system. Or the code appears in reports but isn't aggregated into the correct tax line.

**Mitigation:** Validate all extracted account codes against the user's configured chart of accounts before routing. The valid set must be a runtime constraint, not assumed from training.

---

## VAT/Tax Failures

### FM-07: Reverse Charge Miss

**What it is:** A German business receives a service from an EU vendor (e.g., AWS Ireland, Google Ireland, Microsoft Netherlands). The invoice shows 0% VAT with the note "Reverse charge." The Finom pipeline categorizes it as a zero-VAT purchase and doesn't record the self-assessed VAT.

**Impact:** The German business should have recorded both Vorsteuer (input VAT) and Umsatzsteuer (output VAT) for this transaction — under §13b UStG the tax is self-assessed. Missing this means:
- Underreported Umsatzsteuer → penalty exposure
- Unclaimed Vorsteuer → overpayment to Finanzamt

**Root cause:** The reverse charge indicator is buried in invoice text ("Steuerschuldnerschaft des Leistungsempfängers" or just "Reverse charge"). An extraction agent that doesn't explicitly look for this phrase and cross-reference the vendor country will miss it.

**Detection:** Every vendor with an Irish, Dutch, French, or other non-German EU VAT ID should trigger a reverse charge check. This is deterministic once the vendor VAT ID format is known.

**Mitigation:**
- Extract vendor VAT ID as a required field for invoices above €100
- Parse the country prefix (IE = Ireland, NL = Netherlands, FR = France)
- If vendor is EU non-DE and invoice shows 0% VAT → always apply reverse charge logic
- Test suite must include at least one reverse charge case per supported EU country

---

### FM-08: Mixed VAT Rate Invoice

**What it is:** An invoice contains line items at different VAT rates (e.g., a catering invoice with food at 7% and alcohol at 19%). The extraction agent extracts only a single overall amount and applies one rate to the whole invoice.

**Symptom:** Vorsteuer claim is wrong for the invoice — either overclaimed or underclaimed.

**German examples:**
- Restaurant: food 7%, drinks 19% (on-premise)
- Hotel: accommodation 7%, minibar 19%
- Supermarket: most food 7%, cleaning supplies 19%

**Mitigation:**
- Line-item extraction as a required stage for retail/hospitality invoices
- Validate: sum of (line_net × line_rate) = invoice total VAT
- Flag invoices where a single extracted rate doesn't produce the stated VAT amount

---

### FM-09: Kleinunternehmer Transition Error

**What it is:** A user who was a Kleinunternehmer (exempt from VAT, revenue < €22K) crosses the revenue threshold mid-year but the system doesn't update their VAT treatment. Invoices continue to be issued without VAT when they should now include it.

**Impact:** The user is legally required to issue VAT-inclusive invoices and file UStVA from the month they crossed the threshold. Failure to do so creates back-VAT liability for all sales since crossing.

**Root cause:** The threshold check runs annually (at tax year setup) but not continuously during the year. The user's revenue crosses €22K in September but the system only checks in January.

**Mitigation:**
- Real-time revenue tracking with a warning at €18K (80% of threshold)
- Hard flag at €22K: switch accounting mode, notify user, require confirmation
- Generate backdated UStVA filings for the affected period

---

## Confidence Failures

### FM-10: Confidence Inflation (Overconfident Model)

**What it is:** The model consistently produces high confidence scores even for genuinely ambiguous cases. The calibration curve is far below the diagonal — a model saying 0.9 is only right 70% of the time.

**Consequence:** The confidence router auto-books too aggressively. The override rate looks low (good metric) but hidden error rate is high (bad outcome).

**Detection:** Expected Calibration Error (ECE) — compare confidence buckets to actual accuracy. If ECE > 0.10, confidence scores cannot be trusted for routing.

**Mitigation:**
- Calibrate with Platt scaling or temperature scaling after training
- Target ECE < 0.05 before enabling any auto-book behavior
- Re-measure ECE after any model or prompt change
- In new markets: start at 100% human review regardless of confidence, calibrate on first 1000 transactions

---

### FM-11: Threshold Ossification

**What it is:** The routing thresholds (0.85 auto-book, 0.5 proposal, below reject) were set once and never revisited. As the model improves, the thresholds become too conservative — more than necessary goes to human review. As the model degrades (drift), thresholds become too aggressive.

**Consequence:** Either unnecessary cost (too much human review) or silent error accumulation (auto-booking things that should be reviewed).

**Mitigation:**
- Treat thresholds as hyperparameters with a scheduled review (e.g., quarterly)
- Use the eval harness threshold sweep (0.70–0.95) to show the precision/recall tradeoff at each threshold
- A 5% change in override rate should trigger a threshold review

---

### FM-12: Per-Market Calibration Bias

**What it is:** A model calibrated on German transactions has poor calibration on French transactions because the category distribution and merchant name patterns are different. The same confidence score means different things in different markets.

**Consequence:** Auto-booking that works well in DE causes errors in FR at launch.

**Mitigation:** Per-market calibration data as a requirement before GA in any new market. Share the same model but apply market-specific calibration layers (Platt scaling fit per market).

---

## Routing Failures

### FM-13: Auto-Book Creep

**What it is:** Over time, the threshold for auto-booking gradually expands — either through explicit changes ("let's be more aggressive") or through implicit drift (model improves slightly, someone raises the threshold). Eventually a class of genuinely ambiguous transactions is being auto-booked that shouldn't be.

**Detection:** Monthly audit of auto-booked transactions that were subsequently corrected by users. A rising correction rate in auto-booked items is the signal.

**Mitigation:** Correction rate on auto-booked transactions as a red-line metric. If correction rate on auto-books exceeds 2%, threshold must be tightened.

---

### FM-14: Escalation Storm

**What it is:** A bad document batch (e.g., a new OCR failure mode) causes all transactions to fall below the confidence threshold, flooding the human review queue.

**Symptom:** Human review queue suddenly has 100x normal volume. Review SLA is blown. Users see delays.

**Root cause:** No circuit breaker on the reject/escalate path. The system treats "low confidence" as "needs human review" without asking whether the volume is anomalous.

**Mitigation:**
- Circuit breaker: if more than X% of transactions in a batch fail confidence, alert ops and pause auto-processing
- Batch anomaly detection: compare current confidence distribution to historical P10
- Queue capacity planning: max queue size triggers different routing (hold transactions, not escalate)

---

### FM-15: Silent Reject

**What it is:** A transaction is silently dropped or queued indefinitely because no downstream handler claims it after rejection. The user never sees the transaction in their accounting view. It's not booked, not in review, not flagged.

**Root cause:** The reject path returns a result but no subscriber picks it up. Or a queue consumer crashes without acknowledgment.

**Detection:** Balance check — sum of (ingested transactions) must equal sum of (booked + in-review + rejected with notification). Any gap is a silent reject.

**Mitigation:**
- Dead letter queues with alerting
- Transaction lifecycle state machine: every transaction must have an explicit terminal state (booked, rejected-notified, or error-logged)
- Daily reconciliation job: count transactions at each state, alert on unexplained gaps

---

## Orchestration Failures

### FM-16: Stage Leak

**What it is:** An intermediate stage writes a result to the database but then the next stage fails. On retry, the pipeline re-runs from scratch and creates a duplicate booking.

**Example:** Categorization succeeds and writes to DB. VAT calculation fails. On retry: categorization runs again, detects the record exists, but a bug means it creates a second booking entry. The user sees the same expense twice.

**Mitigation:**
- Idempotent operations at every stage: each stage must be safe to re-run
- Idempotency key per transaction per stage (hash of input)
- Stage output check before re-running: "does output already exist with this idempotency key?"

---

### FM-17: Partial Trace

**What it is:** The trace/audit log records only successful stages. When a transaction fails at stage 3, the trace shows stages 1 and 2 but gives no information about why stage 3 failed. Debugging is archaeology.

**Consequence:** Production incident requires reading raw logs instead of a structured trace. MTTR increases.

**Mitigation:**
- Trace must include failed stages with error information, not just successful ones
- Each trace entry: stage name, start time, end time, status (success/failure/skip), confidence score if applicable, output hash
- The trace is written before the next stage starts, not after

---

### FM-18: Idempotency Violation on ELSTER Submission

**What it is:** A UStVA is successfully submitted to ELSTER, but the Finom system doesn't receive the confirmation response (network timeout). The system retries. ELSTER receives and accepts the second submission — now two returns exist for the same period.

**Impact:** Duplicate VAT filing. German tax authority may issue a correction demand. The user's account shows an extra payment.

**Mitigation:**
- Check ELSTER submission status before retrying (ELSTER provides a query API)
- Store the external ELSTER confirmation number immediately upon receipt
- If no confirmation within N minutes, query ELSTER for the submission status — do NOT re-submit until confirmed missing

---

## Market Expansion Failures

### FM-19: Config Collision

**What it is:** A new market config object uses a key that conflicts with an existing market's config. For example, Spain (ES) and Estonia (EE) both map to the same internal identifier due to a typo. The Spanish tax rules silently override Estonian ones.

**Mitigation:**
- Market config keys validated at startup against a registry
- Market codes must be ISO 3166-1 alpha-2 and validated against an allowlist
- Unit test: load all market configs, assert no overlapping keys

---

### FM-20: Missing E-Invoicing Hook

**What it is:** Italy is added as a market but the SDI e-invoicing requirement is not implemented. Italian users can categorize and book transactions, but outgoing invoices are not transmitted to Sistema di Interscambio as required by Italian law. The invoices are legally non-compliant.

**Impact:** Every Italian user's outgoing invoices are invalid under Italian law. They can't be used for tax deductions by the recipient. Finom's AI Accountant would be creating compliance liability rather than reducing it.

**Mitigation:**
- Market config includes a required flag: `eInvoicingRequired: boolean`
- If true, the pipeline must include a post-booking SDI transmission step before the booking is considered complete
- GA in Italy requires SDI integration — not a "phase 2" feature

---

## How To Use This In The Interview

**If asked "what's the hardest reliability problem in accounting AI?"**
> "Confidence calibration drift — FM-10. The model's confidence scores are only meaningful if they're calibrated. If a 0.85 confidence score is actually right only 70% of the time, your routing thresholds are meaningless and you're silently auto-booking things that should be reviewed. ECE under 0.05 is the bar. Re-measure after every model change."

**If asked "what production incident keeps you up at night in this system?"**
> "The silent reject — FM-15. A transaction that was ingested but never booked, never reviewed, never flagged. From the user's perspective their money moved but their accounting doesn't reflect it. You'd only find it in a balance reconciliation. Prevention: every transaction must have an explicit lifecycle state with a required terminal."

**If asked "what's your design test for reverse charge?"**
> "Any vendor with a non-German EU VAT ID + zero-VAT invoice = mandatory reverse charge check. This is deterministic once you extract the VAT ID. I'd make it a blocking validation rule, not an AI judgment. And I'd put at least one test case per EU country in the eval suite."

**If asked about Italy expansion:**
> "Italy is the case I'd use to stress-test the multi-market architecture. SDI e-invoicing is async and mandatory — it's not just a config change, it's a pipeline extension. The market config flag `eInvoicingRequired` would gate that path. I'd design it so no market goes GA until its required hooks are implemented and tested."
