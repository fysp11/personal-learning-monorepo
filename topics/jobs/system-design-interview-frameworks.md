# System Design Interview Answer Frameworks

## Purpose

Both Finom and Delphyr will likely ask "design X" questions in technical rounds. This document provides structured answer frameworks for the most probable prompts.

---

## General Framework: CLEAR

Use this structure for any system design question:

1. **C**larify — ask 2-3 scoping questions before designing
2. **L**ayout — describe the high-level architecture (3-5 components)
3. **E**valuate — explain how you'd measure quality and correctness
4. **A**dversarial — identify failure modes and edge cases
5. **R**ollout — describe the staged deployment plan

**Time allocation (45-minute interview):**
- Clarify: 3-5 min
- Layout: 10-15 min
- Evaluate: 5-10 min
- Adversarial: 5-10 min
- Rollout: 5 min

---

## Finom Design Prompts

### Prompt 1: "Design a German SMB transaction categorization system"

#### Clarify
- "What's the accuracy bar? Is this for draft categorization (human reviews) or auto-filing?"
- "What's the throughput — how many transactions per day?"
- "Do we have labeled historical data, or are we starting cold?"

#### Layout

```
Transaction Input
     │
     ▼
┌────────────────┐
│ Pre-Processing  │ ← Normalize merchant names, parse amounts, extract dates
└────────┬───────┘
         │
         ▼
┌────────────────┐    ┌──────────────┐
│ Rule Engine     │───→│ SKR03/04     │ ← Known mappings (e.g., "Deutsche Bahn" → Reisekosten)
│ (fast path)     │    │ Account Codes │
└────────┬───────┘    └──────────────┘
         │ unmatched
         ▼
┌────────────────┐
│ ML Classifier   │ ← Multi-class: Betriebsausgabe, Reisekosten, Bewirtung, etc.
│ + Confidence    │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Confidence      │ ← High: auto-categorize / Medium: draft / Low: escalate
│ Router          │
└────────┬───────┘
         │
         ▼
┌────────────────┐
│ Tax Logic       │ ← Apply VAT rules, deductibility, Finanzamt requirements
│ (deterministic) │
└────────────────┘
```

**Key design decisions:**
- **Rule engine first:** Known merchant-to-category mappings don't need ML. Rules are fast, interpretable, and deterministic.
- **ML for the long tail:** Novel merchants, ambiguous descriptions, multi-category transactions.
- **Confidence routing:** Never auto-categorize when uncertain. Draft mode for medium confidence.
- **Tax logic is deterministic:** Once categorized, tax implications (VAT rate, deductibility) follow rules, not ML.

#### Evaluate
- **Category accuracy:** Against human-labeled ground truth, per category
- **Confidence calibration:** Does 90% confidence mean 90% accuracy?
- **Coverage:** What % of transactions are auto-categorized vs. requiring review?
- **Per-business-type performance:** Freelancer vs. GmbH vs. UG — different category distributions
- **Long-tail accuracy:** Rare categories (Anlagevermögen, Durchlaufende Posten) are hardest

#### Adversarial
- **Merchant name variation:** "DB" vs "Deutsche Bahn" vs "DB Fernverkehr AG"
- **Multi-category transactions:** A restaurant receipt could be Bewirtung (entertainment) or Betriebsausgabe
- **Foreign transactions:** Non-German merchants, non-EUR currencies
- **Seasonal patterns:** Year-end tax purchases, quarterly VAT submissions
- **Adversarial manipulation:** Someone categorizing personal expenses as business expenses

#### Rollout
1. **Shadow mode:** Categorize silently, compare against human decisions
2. **Draft mode:** Show suggested category, human confirms
3. **Auto-categorize high confidence:** Top 60-70% of transactions by volume
4. **Expand gradually:** Lower confidence threshold as calibration improves

---

### Prompt 2: "Design a credit scoring pipeline for SME invoice financing"

#### Clarify
- "Are we scoring the business or the specific invoice?"
- "What data sources do we have beyond Finom transaction history?"
- "What's the latency requirement — real-time or batch?"

#### Layout

```
Financing Request (Business + Invoice)
     │
     ├──────────────────────────────────┐
     ▼                                  ▼
┌────────────────┐            ┌────────────────┐
│ Business Score  │            │ Invoice Score   │
│                 │            │                 │
│ - Cash flow     │            │ - Counterparty  │
│   patterns      │            │   relationship  │
│ - Revenue       │            │ - Invoice       │
│   stability     │            │   pattern match │
│ - Payment       │            │ - Amount vs.    │
│   history       │            │   historical    │
│ - Account age   │            │ - Duplicate     │
│ - Category      │            │   detection     │
│   diversity     │            │                 │
└────────┬───────┘            └────────┬────────┘
         │                              │
         └──────────┬───────────────────┘
                    ▼
           ┌────────────────┐
           │ Combined Score  │ ← Weighted fusion
           │ + Explanation   │
           └────────┬───────┘
                    │
                    ▼
           ┌────────────────┐
           │ Decision Engine │
           │                 │
           │ Approve / Refer │
           │ / Decline       │
           │ + Terms         │
           └────────────────┘
```

**Key design decisions:**
- **Finom's data advantage:** We already have the real transaction history — no need to trust self-reported financials
- **Invoice-level scoring:** Not just "is this business creditworthy" but "is this specific invoice legitimate"
- **Explainability required:** EU regulation requires explanation of credit decisions
- **Fraud integration:** Ghost invoices, duplicate financing attempts, inflated amounts (see fraud-risk-architecture-playbook.md)

#### Evaluate
- **Calibration:** Does a 10% default prediction mean 10% actually default?
- **Discrimination:** AUC-ROC for separating good from bad loans
- **Fairness:** No bias by business type, geography, or demographic proxies
- **False positive cost:** Declining a good loan = lost revenue + customer friction
- **False negative cost:** Approving a bad loan = financial loss

#### Adversarial
- **Synthetic businesses:** Manufactured transaction history to qualify for financing
- **Invoice collusion:** Two businesses creating fake invoices between each other
- **Revenue inflation:** Artificially high transaction volume before application
- **Timing attacks:** Cleaning up transaction patterns just before applying

#### Rollout
1. **Human-only:** All decisions by credit team, model provides recommendation
2. **Model-assisted:** Model scores, human decides, track model vs. human agreement
3. **Auto-approve high-confidence:** Small amounts, strong businesses, verified invoices
4. **Expand:** Increase auto-approve threshold as calibration data accumulates

---

## Delphyr Design Prompts

### Prompt 3: "Design a clinical patient summary system"

#### Clarify
- "Summary for what context — MDT, handover, discharge, or general?"
- "What EHR systems are we integrating with?"
- "What's the latency tolerance — real-time or can it be pre-computed?"

#### Layout

```
Patient Query + Context
     │
     ▼
┌──────────────────┐
│ Patient Scope     │ ← Hard filter: only this patient's data
│ (privacy gate)    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Hybrid Retrieval  │ ← Dense + sparse, RRF fusion
│ (see hybrid-      │    (see hybrid-retrieval-architecture-deep-dive.md)
│  retrieval doc)   │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Clinical          │ ← Recency boost, document type weighting
│ Re-Ranking        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Generation        │ ← Structured output with claim-level citations
│ (M1/M2)           │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Output Guard      │
│ - Citation check  │ ← Every claim must cite a source
│ - Safety check    │ ← No treatment recommendations
│ - PHI check       │ ← Minimize unnecessary identifiers
│ - Completeness    │ ← Flag missing expected sections
└────────┬─────────┘
         │
         ▼
  Structured Summary + Confidence + Sources
```

**Key design decisions:**
- **Patient scope is a hard gate:** Infrastructure-level isolation, not model-level
- **Citation is non-negotiable:** Every factual claim must trace to a source document
- **No treatment recommendations:** The system summarizes, never advises
- **Confidence per section:** Some sections (lab values) are near-deterministic; others (clinical interpretation) are inherently uncertain

#### Evaluate
- **Faithfulness:** Are claims supported by source documents? (see citation-verification.ts)
- **Completeness:** Are all relevant findings included?
- **Temporal correctness:** Are we showing current state, not outdated information?
- **Safety:** No unsupported claims, no treatment advice, no cross-patient leakage
- **Clinician time saved:** Practical metric — does this actually reduce prep time?

#### Adversarial
- **Contradictory information:** Two notes disagree on an allergy — both must be surfaced
- **Temporal confusion:** "Current medication" must be the latest list, not a historical one
- **Missing data:** The system must flag what's missing, not hallucinate to fill gaps
- **Long patient history:** Context window limits require intelligent selection, not truncation

#### Rollout
1. **Read-only alongside:** Summary shown next to current workflow, clinician ignores if wrong
2. **Pre-populated drafts:** Summary pre-fills a form the clinician edits
3. **Trusted view:** Summary becomes the primary patient view with audit trail
4. **Proactive alerts:** System flags changes, missing items, or inconsistencies

---

### Prompt 4: "Design a clinical guideline retrieval system"

#### Clarify
- "Are guidelines structured (XML/HTML) or unstructured (PDF)?"
- "How many guidelines in scope — dozens or thousands?"
- "Do clinicians search explicitly, or does the system match automatically?"

#### Layout

```
Clinical Context (diagnosis + question)
     │
     ▼
┌──────────────────┐
│ Query Formulation │ ← Map clinical context to search terms
│                   │    Handle medical synonyms, abbreviations
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Guideline Index   │ ← Section-level chunking (not document-level)
│ (hybrid search)   │    Metadata: specialty, evidence level, publication date
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Section Ranker    │ ← Boost by: evidence level, recency, specialty match
│                   │    Penalize: withdrawn guidelines, superseded versions
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Context Assembly  │ ← Extract specific recommendations
│                   │    Attach evidence levels (IA, IB, IIA, etc.)
│                   │    Cite exact guideline section
└────────────────┘
```

**Key design decisions:**
- **Section-level indexing:** A guideline on renal cell carcinoma has 15+ sections — only 1-2 are relevant per query
- **Evidence levels matter:** IA evidence is not the same as expert opinion — the system must surface this
- **Guideline versioning:** Medical guidelines are updated regularly; outdated recommendations are dangerous
- **Multi-guideline synthesis:** A clinical question may be addressed by multiple guidelines (ESMO + NVvH + NHG) — need to surface all, not just one

---

## Cross-Company Prompt

### Prompt 5: "Design an evaluation framework for a production AI system"

This prompt works for either company. Adjust domain examples.

#### Layout

```
┌───────────────────────────────────────┐
│           Evaluation Layers            │
├───────────────────────────────────────┤
│                                       │
│  Layer 1: OFFLINE                     │
│  - Golden set evaluation              │
│  - Component metrics (per agent)      │
│  - End-to-end workflow metrics        │
│  - Regression tests                   │
│  - Run: on every model/prompt change  │
│                                       │
│  Layer 2: ONLINE                      │
│  - Production accuracy sampling       │
│  - Latency / throughput monitoring    │
│  - Confidence calibration tracking    │
│  - Override rate monitoring           │
│  - Run: continuously in production    │
│                                       │
│  Layer 3: REVIEW                      │
│  - Human expert audit (random sample) │
│  - Edge case review                   │
│  - Failure post-mortems               │
│  - Calibration rechecks               │
│  - Run: weekly/monthly cycle          │
│                                       │
└───────────────────────────────────────┘
```

**Per-layer details:**

| Layer | Finom Example | Delphyr Example |
|-------|--------------|-----------------|
| Offline golden set | 500 labeled transactions across all categories | 100 clinical notes with expert extractions |
| Component metric | Classification accuracy per SKR03 code | Extraction recall per clinical section |
| End-to-end metric | % of tax declarations correct | % of MDT briefs rated complete by clinician |
| Online sampling | Random 5% of auto-categorized transactions audited | Random 10% of summaries reviewed by clinician |
| Calibration | ECE tracking per confidence bin | ECE tracking per query type |
| Override rate | How often humans change the AI's category | How often clinicians edit the AI's summary |
| Expert audit | Accountant reviews edge cases weekly | Clinical lead reviews flagged cases weekly |
| Failure post-mortem | Why did this transaction get mis-categorized? | Why did this summary miss an allergy? |

**Interview talking point:**
> "I structure evaluation in three layers: offline golden sets catch regressions before deployment, online monitoring catches drift and calibration issues in production, and periodic human review catches the things automated metrics miss. The key metric to watch is the override rate — when humans consistently change the AI's output, that's a signal the model or threshold needs adjustment."

---

## How To Use This Document

1. **Before an interview:** Read the framework for the most likely prompt
2. **During the interview:** Use CLEAR structure, adapt examples to what's asked
3. **If asked something unexpected:** Fall back to the general CLEAR framework
4. **Always end with rollout:** Shows you think about production, not just design
