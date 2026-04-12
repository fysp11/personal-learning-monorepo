# MDT Evaluation Benchmark Framework

Saved: 2026-04-11

## Context

Delphyr's MDT (Multi-Disciplinary Team) preparation agent is their highest-value future product surface — automating the 30-60 minutes of case prep per patient that clinicians currently do manually. This insight designs a concrete evaluation framework for benchmarking MDT briefing quality.

---

## What an MDT Briefing Agent Produces

For each patient case, the agent generates a structured briefing:

```
MDT Briefing: Patient [ID]
─────────────────────────────
1. Clinical Timeline (structured chronology of events)
2. Current Status (latest labs, imaging, symptoms)
3. Relevant Guidelines (matched from clinical guideline database)
4. Decision Points (what the MDT needs to decide)
5. Prior MDT Decisions (if any, what was decided before)
6. Supporting Evidence (citations to source records)
```

Every element must be **traced to a source document**. The agent retrieves and structures — it never diagnoses or recommends.

---

## Evaluation Dimensions

### Dimension 1: Completeness

**Question:** Did the briefing include all clinically relevant information?

**Metric:** Recall against a gold-standard reference briefing.

```
completeness_score = |relevant_facts_found| / |relevant_facts_in_reference|
```

**Sub-dimensions:**
- **Timeline completeness:** Are all significant clinical events included?
- **Lab/imaging completeness:** Are recent results present?
- **Medication completeness:** Is the current medication list accurate?
- **History completeness:** Is relevant past medical history surfaced?

**Target:** ≥ 95% (missing a relevant fact in an MDT briefing can change the team's decision)

**Why 95% not 100%:** Some facts in the reference may be tangentially relevant. The goal is to never miss a critical fact, while accepting occasional omission of low-relevance details.

### Dimension 2: Citation Accuracy

**Question:** Can every claim in the briefing be traced to a source document?

**Metric:** Proportion of claims with valid citations.

```
citation_accuracy = |claims_with_valid_citations| / |total_claims|
```

**Verification levels:**
- **Exact match:** Citation directly supports the claim
- **Partial match:** Citation supports the claim but requires inference
- **Unsupported:** No citation or citation doesn't support the claim
- **Fabricated:** Citation points to a document that doesn't exist

**Target:** ≥ 98% exact or partial match; 0% fabricated citations

### Dimension 3: Factual Accuracy

**Question:** Are the facts in the briefing correct?

**Metric:** Precision of extracted facts.

```
factual_accuracy = |correct_facts| / |total_facts_in_briefing|
```

**Error taxonomy:**
- **Value error:** Wrong lab value, wrong date, wrong medication dose
- **Attribution error:** Fact assigned to wrong patient visit or provider
- **Temporal error:** Events placed in wrong chronological order
- **Negation error:** "No diabetes" reported as "diabetes"

**Target:** ≥ 99% (factual errors in clinical briefings are the highest-severity failure)

### Dimension 4: Hallucination Rate

**Question:** Does the briefing contain information not present in any source?

**Metric:** Proportion of claims with no grounding in source documents.

```
hallucination_rate = |claims_not_in_any_source| / |total_claims|
```

**Hallucination types:**
- **Invented facts:** Patient never had this condition/test/medication
- **Confabulated connections:** Linking unrelated findings into a narrative
- **Temporal hallucination:** Fabricating a timeline that doesn't match records
- **Guideline hallucination:** Citing a guideline that doesn't exist or says something different

**Target:** < 1% (ideally 0%, but measurement noise means ~1% is the practical floor)

### Dimension 5: Omission Detection

**Question:** Did the briefing fail to surface something critical?

**Metric:** False negative rate on critical clinical facts.

```
critical_omission_rate = |critical_facts_missed| / |critical_facts_in_reference|
```

**What makes a fact "critical":**
- Active allergies
- Current medications (especially interactions)
- Recent significant test results
- Prior MDT decisions that constrain current options
- Active safety alerts

**Target:** < 2% for critical facts (stricter than general completeness)

### Dimension 6: Guideline Relevance

**Question:** Are the matched clinical guidelines actually relevant to this patient's case?

**Metric:** Precision and recall of guideline matching.

```
guideline_precision = |relevant_guidelines_matched| / |total_guidelines_matched|
guideline_recall = |relevant_guidelines_matched| / |relevant_guidelines_available|
```

**Target:** Precision ≥ 90% (irrelevant guidelines waste MDT time); Recall ≥ 85% (missing a relevant guideline is a safety concern)

---

## Benchmark Dataset Design

### Case Categories

A robust benchmark needs cases across multiple axes:

| Axis | Categories |
|------|-----------|
| **Complexity** | Simple (single condition), Moderate (2-3 conditions), Complex (multimorbid) |
| **Data volume** | Sparse (few records), Normal (typical patient), Dense (long history) |
| **Specialty** | Oncology, Cardiology, Psychiatry, General internal medicine |
| **Data quality** | Clean (structured), Messy (free-text notes, abbreviations), Mixed |
| **Language** | Dutch, Dutch+English mixed, Dutch+Latin medical terminology |

### Minimum Viable Benchmark

For a startup like Delphyr, start with:
- **20 cases** across complexity levels (5 simple, 10 moderate, 5 complex)
- **Gold-standard briefings** written by clinicians (not AI-generated)
- **Annotated claims** with source document links
- **Critical facts labeled** for omission detection

**Cost:** ~2-3 days of clinician time to create the gold standard. This is the most expensive part but also the most valuable.

### Evaluation Pipeline

```
For each test case:
  1. Feed patient records to MDT briefing agent
  2. Capture generated briefing + citations
  3. Compare against gold standard:
     - Fact extraction → completeness score
     - Citation verification → citation accuracy
     - Fact checking → factual accuracy
     - Hallucination detection → hallucination rate
     - Critical fact check → omission detection
     - Guideline match verification → guideline relevance
  4. Aggregate scores per dimension
  5. Flag any critical failures (hallucination, critical omission)
```

---

## Severity-Weighted Scoring

Not all errors are equal in clinical AI. A severity-weighted composite score:

| Error Type | Severity Weight | Rationale |
|-----------|----------------|-----------|
| Fabricated citation | 10x | Undermines trust in the entire system |
| Factual error (medication/dose) | 10x | Can cause patient harm |
| Critical omission | 8x | Missing info the MDT needed |
| Negation error | 8x | Inverts the clinical meaning |
| Temporal error | 5x | Misleads about disease progression |
| Minor omission | 2x | Inconvenient but not dangerous |
| Irrelevant guideline | 1x | Wastes time but doesn't mislead |

```
weighted_score = 1 - (Σ severity × error_count) / (Σ severity × max_possible_errors)
```

**Target:** Weighted score ≥ 0.95 before deployment to clinical users.

---

## Connection to Existing Work

| Existing Asset | How It Connects |
|---------------|-----------------|
| `code/citation-verification.ts` | Core of Dimension 2 (citation accuracy) — extend with clinical source types |
| `code/medical-extraction-agent.ts` | Extraction pipeline feeds into Dimension 1 (completeness) evaluation |
| `experiments/agent-safety-harness/` | Dimension 4 (hallucination) and 5 (omission) are safety harness triggers |
| `prep/rag-guardrail-architecture-design.md` | The 4-stage guardrail maps to pre/post evaluation gates |
| `insights/agentic-mdt-workflow-deep-dive.md` | Defines what the agent should produce; this file defines how to measure it |
| `research-medical-agentic-evaluations.md` | Literature grounding for agent-based evaluation approaches |

---

## Interview Follow-Up Angle

> "One thing I've been thinking about since our conversation is how you'd evaluate MDT briefing quality at scale. You can't have a clinician review every output, but you need confidence that the system isn't hallucinating or missing critical facts. I've sketched out a 6-dimension evaluation framework that separates different failure modes by clinical severity — I'd love to discuss whether that aligns with how you're thinking about quality assurance."

---

## Transferable to Finom

The same framework structure applies to Finom's transaction categorization evaluation:
- Completeness → all line items extracted
- Citation accuracy → booking traces to source document
- Factual accuracy → amounts, dates, VAT rates correct
- Hallucination → categories not supported by transaction data
- Omission → missed transactions or line items
- Severity weighting → tax-relevant errors weighted higher than cosmetic ones

This cross-domain applicability is exactly the "correctness-sensitive AI engineer" positioning.
