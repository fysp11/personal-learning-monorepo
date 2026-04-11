# System Design Answer Template — Correctness-Sensitive AI

Saved: 2026-04-11

## Purpose

A reusable template for answering system design questions in interviews at companies that need correctness-sensitive AI systems. Works for both Finom (financial) and Delphyr (clinical) contexts, and any similar role.

---

## The 7-Step Framework (5 minutes to present, 10 minutes to discuss)

### Step 1: Clarify the Scope (30 seconds)

Before designing, confirm:
- **Input format:** What arrives? (transaction, document, audio, patient record)
- **Output format:** What do we produce? (structured data, decision, document)
- **Correctness bar:** What's the cost of a wrong output? (audit penalty, patient harm, wasted time)
- **Latency requirement:** Real-time or batch? (seconds vs minutes)
- **Scale:** How many per day/month?

**Template sentence:**
> "Before I start — I want to make sure I understand the constraints. The input is [X], the output is [Y], and a wrong output costs [Z]. Is that right?"

### Step 2: Identify AI vs Deterministic Boundaries (1 minute)

The most important architectural decision: **what should the AI decide, and what should be rules?**

**Principle:** AI handles ambiguity (categorization, extraction, summarization). Deterministic code handles policy (tax rates, drug interactions, compliance rules).

| AI Boundary | Deterministic Boundary |
|-------------|----------------------|
| "What category is this?" | "What tax rate for this category?" |
| "What does this note say?" | "Is this drug interaction dangerous?" |
| "What's the key finding?" | "Should we cite guideline X or Y?" |

**Template sentence:**
> "The boundary I'd draw is: [AI task] uses an LLM because it involves judgment. [Deterministic task] is rules because it's policy — and policy shouldn't be probabilistic."

### Step 3: Design the Pipeline (2 minutes)

Draw the stages. Each stage has:
- **Input contract:** What it receives (typed)
- **Output contract:** What it produces (typed)
- **Confidence:** Does this stage produce a confidence score?
- **Failure mode:** What happens when this stage fails?

**Generic pipeline:**

```
Input → Extraction (AI) → Validation (rules) → Classification (AI)
    → Policy Application (rules) → Confidence Router → Output
```

**Template sentence:**
> "The pipeline has [N] stages. Let me walk through each one and where the AI boundary sits."

### Step 4: Add Confidence Routing (30 seconds)

Every AI-powered stage produces a confidence score. Route by confidence:

```
High confidence → Auto-execute (measured trust)
Medium confidence → Human review queue (proposal mode)
Low confidence → Reject / escalate (safety boundary)
```

**Template sentence:**
> "The router is the most important 10 lines. Everything upstream produces confidence; everything downstream depends on this routing decision."

### Step 5: Add Observability (30 seconds)

Every pipeline run gets a trace:
- **Correlation ID:** Links all stages for this run
- **Per-stage:** Input, output, confidence, duration, decision
- **Outcome tracking:** What happened downstream (auto-executed? reviewed? corrected?)

**Template sentence:**
> "When something goes wrong three weeks from now, the first question is 'what did each stage decide?' Without the trace, debugging is archaeology."

### Step 6: Address Scale and Extension (30 seconds)

- **Caching:** For repeated inputs (same merchant, same patient query), cache the classification
- **Batch vs stream:** High-volume → batch with async notification; low-latency → stream with timeout
- **Multi-market/domain:** Config-driven, not code-driven. Adding a new market/specialty = new config, zero code changes

**Template sentence:**
> "At scale, the key optimization is [caching/batching]. For extension to new [markets/specialties], the config is data, not code."

### Step 7: Discuss Failure Modes (30 seconds)

Name the top 3 failure modes and how the design handles each:

| Failure | Detection | Response |
|---------|-----------|----------|
| AI gets it wrong (high confidence) | Post-hoc correction rate monitoring | Tighten threshold, add to eval suite |
| AI uncertain (low confidence) | Confidence router | Route to human review |
| System failure (timeout, crash) | Health checks, circuit breaker | Retry with backoff, then escalate |

**Template sentence:**
> "The design handles three failure modes: [wrong + confident], [uncertain], and [system failure]. Each routes differently."

---

## Finom Instantiation

**Problem:** "Design a transaction categorization system for German SMBs"

| Step | Finom-Specific |
|------|----------------|
| Scope | Input: bank transaction + optional receipt. Output: SKR03 code + VAT + booking entry. Cost of error: wrong tax filing. |
| AI boundary | Categorization = AI (ambiguous). VAT calculation = rules (law). |
| Pipeline | Extraction → Categorization → VAT Calculation → Confidence Router → Booking |
| Confidence | 0.85+ auto-book, 0.50-0.85 review, <0.50 reject |
| Observability | Correlation ID per transaction, trace through all stages |
| Scale | Merchant-level caching for top-80% merchants. Batch processing for month-end. |
| Failures | Wrong category: correction → eval suite. Wrong VAT: critical alert. System down: queue with retry. |

## Delphyr Instantiation

**Problem:** "Design an MDT briefing preparation system"

| Step | Delphyr-Specific |
|------|-----------------|
| Scope | Input: patient records (notes, labs, imaging, meds). Output: structured MDT briefing. Cost of error: wrong clinical decision. |
| AI boundary | Summarization/extraction = AI (judgment). Drug interactions, guideline rules = deterministic. |
| Pipeline | Retrieval → Extraction → Synthesis → Citation Verification → Confidence Router → Briefing |
| Confidence | Per-section: high confidence sections auto-include, low confidence flagged for clinician review |
| Observability | Patient-scoped trace, every claim linked to source document |
| Scale | Patient-scoped caching (data doesn't change between MDT reviews). Specialty-specific retrieval profiles. |
| Failures | Hallucination: citation verification blocks unsupported claims. Omission: completeness check flags missing sections. System down: degrade to raw record list. |

---

## The One Sentence That Ties It Together

> "The design separates AI judgment from deterministic policy, routes by measured confidence, and traces every decision for debugging. The AI earns more autonomy as calibration is verified."

This sentence works for financial AI, clinical AI, legal AI, or any domain where correctness matters more than speed.

---

## Common Interview Follow-Up Patterns

| They ask... | You redirect to... |
|------------|-------------------|
| "How do you handle edge cases?" | "The confidence router catches them — edge cases are medium-confidence by definition" |
| "What about adversarial inputs?" | "Input validation is stage 1 — separate from classification, runs deterministic rules" |
| "How does this scale?" | "Caching for repeated patterns, batch for volume, config for new markets" |
| "How do you evaluate this?" | "Correction-driven eval suite: every human correction becomes a test case" |
| "What would you build first?" | "The confidence router and trace — everything else is less valuable without observable routing" |
| "What's the biggest risk?" | "Over-confident auto-execution before calibration is verified — the earned autonomy ratchet prevents this" |
