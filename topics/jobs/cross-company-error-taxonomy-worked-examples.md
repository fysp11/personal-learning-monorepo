# Domain-Specific Error Taxonomies — Worked Examples

Saved: 2026-04-11

## Context

The cross-company deep patterns document identifies error taxonomies as a transferable concept. This file provides **concrete worked examples** for both Finom and Delphyr, turning the abstract pattern into interview-ready material.

---

## Why Error Taxonomies Matter

Generic error handling ("something went wrong") is useless for correctness-sensitive AI. You need to know:
1. **What kind of error** — to route the right fix
2. **How severe** — to prioritize response
3. **Whether it's AI or system** — to route to the right team
4. **Whether it's recoverable** — to decide auto-retry vs escalate

---

## Finom Error Taxonomy: Transaction Processing Pipeline

### Layer 1: Pipeline Stage Errors

```
Pipeline Error
├── Ingestion Errors
│   ├── DocumentParseFailure (PDF/image extraction failed)
│   ├── DuplicateDocument (already processed this invoice)
│   └── UnsupportedFormat (file type not handled)
│
├── Extraction Errors
│   ├── AmountExtractionFailure (couldn't parse monetary value)
│   ├── DateExtractionFailure (ambiguous or missing date)
│   ├── VendorExtractionFailure (merchant name unclear)
│   └── LineItemExtractionFailure (individual items not parseable)
│
├── Categorization Errors
│   ├── WrongCategory (Office → Marketing)
│   ├── AmbiguousCategory (could be Travel or Entertainment)
│   ├── UnknownCategory (no matching account in chart)
│   └── CrossMarketConfusion (DE category applied to FR transaction)
│
├── Tax Calculation Errors
│   ├── WrongVatRate (standard applied instead of reduced)
│   ├── MissedReverseCharge (B2B intra-EU not detected)
│   ├── WrongTaxPeriod (booked to wrong reporting period)
│   └── ExemptionMissed (tax-exempt transaction taxed)
│
└── Booking Errors
    ├── WrongAccount (debit/credit swapped)
    ├── DoubleBooking (transaction entered twice)
    ├── OrphanEntry (booking with no source document)
    └── ReconciliationMismatch (bank statement doesn't match)
```

### Layer 2: Severity Classification

| Severity | Definition | Response Time | Example |
|----------|-----------|---------------|---------|
| **Critical** | Affects tax filing correctness | Immediate | WrongVatRate, MissedReverseCharge |
| **High** | Affects financial statements | Same day | WrongCategory (material amount), DoubleBooking |
| **Medium** | Requires correction but doesn't affect reporting | 48 hours | WrongCategory (small amount), DateExtractionFailure |
| **Low** | Cosmetic or preference | Next batch | VendorExtractionFailure (name slightly wrong) |

### Layer 3: Root Cause Classification

| Root Cause | Fix Pathway | Example |
|-----------|-------------|---------|
| **AI confidence** | Threshold adjustment | Category at 0.83 was wrong; tighten to 0.88 |
| **Missing training data** | Add to fine-tuning set | New vendor type never seen before |
| **Rule gap** | Update deterministic rules | New tax regulation not in rule engine |
| **Data quality** | Input validation | Blurry receipt image, OCR failed |
| **Integration** | System fix | Bank API returned wrong format |

### Worked Example: "PrintShop GmbH classified as Office Supplies"

```
Error: WrongCategory
  Actual: Marketing materials (4600 Werbekosten)
  Predicted: Office supplies (4930 Bürobedarf)
  Confidence: 0.87 (above auto-book threshold)
  Severity: Medium (small amount, €230)
  Root cause: AI confidence (merchant name contains "print" → office association)

Resolution:
  1. Immediate: Merchant override → PrintShop GmbH = Marketing
  2. Evaluation: Add test case for printing/marketing merchants
  3. Calibration: Check if 0.87 predictions have lower accuracy for this category
  4. Prevention: Consider adding "marketing" keyword rules
```

---

## Delphyr Error Taxonomy: Clinical AI Pipeline

### Layer 1: Pipeline Stage Errors

```
Clinical AI Error
├── Retrieval Errors
│   ├── WrongPatient (data from different patient surfaced)
│   ├── StaleData (outdated results shown as current)
│   ├── MissedDocument (relevant record not retrieved)
│   ├── IrrelevantRetrieval (unrelated records in context)
│   └── ScopeViolation (data from outside authorized scope)
│
├── Extraction Errors
│   ├── NegationError ("no diabetes" → "diabetes")
│   ├── ValueError (wrong lab value, wrong dose)
│   ├── TemporalError (events in wrong chronological order)
│   ├── AttributionError (finding assigned to wrong visit)
│   └── UnitError (mg vs mcg, mmol/L vs mg/dL)
│
├── Synthesis Errors
│   ├── Hallucination (claim not grounded in any source)
│   ├── Confabulation (invented connection between real facts)
│   ├── Omission (missing critical clinical information)
│   ├── Oversimplification (clinical nuance lost)
│   └── SpeculativeDiagnosis (AI suggests diagnosis instead of retrieving)
│
├── Citation Errors
│   ├── FabricatedCitation (source document doesn't exist)
│   ├── MisattributedCitation (source exists but doesn't support claim)
│   ├── MissingCitation (claim has no citation)
│   └── AmbiguousCitation (citation could support multiple interpretations)
│
└── Guideline Matching Errors
    ├── IrrelevantGuideline (matched guideline doesn't apply)
    ├── OutdatedGuideline (superseded version cited)
    ├── MissedGuideline (relevant guideline not surfaced)
    └── MisappliedGuideline (guideline applies differently than stated)
```

### Layer 2: Clinical Severity Classification

| Severity | Definition | Response | Example |
|----------|-----------|----------|---------|
| **Safety-Critical** | Could cause patient harm if undetected | System halt + alert | NegationError on allergy, Hallucination of medication |
| **High** | Changes clinical decision if undetected | Immediate flag to reviewing clinician | Omission of recent lab results, WrongPatient data |
| **Medium** | Incorrect but detectable by clinician | Visual flag in interface | TemporalError, MisattributedCitation |
| **Low** | Cosmetic or preference | Log for quality improvement | Oversimplification, Formatting issues |

### Layer 3: Safety Response Matrix

| Error Type | Detected Pre-Review | Detected During Review | Detected Post-Review |
|-----------|--------------------|-----------------------|---------------------|
| **NegationError** | Block output, re-extract | Clinician corrects, log | Incident report, root cause analysis |
| **Hallucination** | Block output, remove claim | Clinician deletes, log | Incident report, guardrail review |
| **WrongPatient** | Block entire output | Clinician rejects, escalate | Critical incident, mandatory investigation |
| **MissedGuideline** | Cannot detect automatically | Clinician notices gap | Feedback → eval suite improvement |

### Worked Example: "Patient's statin medication omitted from MDT briefing"

```
Error: Omission
  Missing: Atorvastatin 40mg (prescribed 2024-01-15, active)
  Available in: Patient medication record (EHR medication list)
  Severity: High (statins interact with multiple drugs; MDT considering new treatment)
  Root cause: Retrieval — medication list was in structured EHR field, not in
              free-text notes; retrieval query focused on clinical notes only

Resolution:
  1. Immediate: Add medication list query to retrieval pipeline
  2. Evaluation: Add test cases for structured EHR data retrieval
  3. Completeness check: Add mandatory "current medications" section to briefing template
  4. Monitoring: Track medication omission rate as a specific metric
  5. Prevention: Cross-reference extracted medications against EHR medication list
```

---

## Cross-Domain Comparison

| Dimension | Finom | Delphyr |
|-----------|-------|---------|
| **Worst-case error** | Wrong tax filing → audit penalty | Wrong patient data → treatment harm |
| **Error discovery** | End of month (accounting close) | During clinical decision (MDT meeting) |
| **Correction cost** | Amended filing, potential fine | Treatment revision, potential adverse event |
| **Regulatory exposure** | Tax authority audit | Medical device incident report |
| **Feedback cycle** | Monthly (accounting period) | Per-consultation (immediate) |
| **Deterministic boundary** | Tax rates, chart of accounts | Drug interactions, guideline rules |
| **AI boundary** | Category prediction, extraction | Summarization, guideline matching |

### Shared Pattern: The Error Response Escalation Ladder

```
Level 1: Auto-correct (deterministic fix available)
  → Finom: Merchant override table
  → Delphyr: Structured field cross-reference

Level 2: Flag for human review (uncertain fix)
  → Finom: Send to accountant review queue
  → Delphyr: Highlight for clinician review

Level 3: Block and escalate (safety-critical)
  → Finom: Halt booking, alert finance team
  → Delphyr: Block output, alert clinical safety team

Level 4: System-wide response (pattern detected)
  → Finom: Tighten auto-book thresholds for affected category
  → Delphyr: Enable human review for affected error type
```

---

## Interview Application

### Finom (Interview 3 — System Design Discussion)

When discussing error handling in the live round:

> "I'd structure errors by severity and root cause, not just by stage. A category error on a €50 office supply purchase is medium-severity, but a VAT rate error on a €10,000 invoice is critical — same pipeline stage, completely different response. The error taxonomy drives the escalation behavior."

### Delphyr (Follow-Up)

When discussing quality assurance:

> "In clinical AI, the error taxonomy needs a safety dimension that financial AI doesn't. A negation error — reporting 'diabetes' when the record says 'no diabetes' — is categorically different from a formatting error. The taxonomy should drive different detection mechanisms, different response speeds, and different audit requirements."
