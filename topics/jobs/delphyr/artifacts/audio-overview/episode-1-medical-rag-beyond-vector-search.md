# Audio Overview Prompt — Episode 1: Medical RAG: Beyond Vector Search

**Episode Type:** Deep Dive  
**Duration:** 10-15 minutes  
**Target Characters:** ~4000-4500 (within NotebookLM limits)

---

## Episode Structure

### [1-2 min] Why Medical RAG Is Different from General RAG

Open by establishing what makes medical retrieval fundamentally different from standard enterprise RAG:

- In general RAG, a wrong answer is inconvenient. In medical RAG, a wrong answer can harm patients.
- General RAG optimizes for relevance. Medical RAG must optimize for verification, traceability, and bounded confidence.
- Standard RAG can tolerate "probably" and "might." Medical RAG requires "this specific snippet supports this specific claim."
- The stakes are different: retrieval errors in healthcare can propagate into clinical decisions.

Set up the core tension: **medical RAG is not about finding relevant documents—it's about producing verifiable, patient-scoped answers with exact evidence.**

---

### [4-5 min] Core Concepts

Walk through the key technical concepts that distinguish medical-grade retrieval:

**Claim-Level Grounding**
- Explain the difference between document-level citations and claim-level citations
- Why "this came from guideline X" is weak—versus "this sentence is supported by this exact snippet from page Y"
- Delphyr's approach: inline citation generation during response generation, not post-hoc attachment

**Exact Snippet Citations**
- The technical challenge: generating citations at the same time as the answer, not after
- Why this matters for verification: clinicians need to check the specific evidence, not hunt through source documents
- The verification contract: every factual claim must cite its evidence

**Patient-Specific Scoping**
- Why retrieval must be scoped to a specific patient, not general medical knowledge
- Google Cloud's pattern: requiring patient ID, patient-specific search scope
- The risk of cross-patient contamination in retrieval results
- How Delphyr handles patient context: knowing the context of a patient

**No-Source-No-Claim Behavior**
- The critical design principle: if evidence doesn't support a claim, the system must refuse or express uncertainty
- Abridge's factuality taxonomy: directly supported, reasonable inference, questionable inference, unmentioned, contradiction
- Why this is a safety feature, not just a quality feature

---

### [4-5 min] How Delphyr, Google Cloud, and Abridge Handle It

**Delphyr's Approach**
- Inline citation generation during response generation
- Multiple safety checks before, during, and after generation
- Security, accuracy, and focus as the three guardrail buckets
- Patient context as a first-class concern
- The design philosophy: slower answers with deterministic verification over faster answers with ambiguous support

**Google Cloud's Healthcare Search**
- Bounded intended use: retrieve and summarize existing medical information, not diagnose or treat
- Outputs are drafts requiring clinical review
- Patient ID requirement and patient-specific scope
- FHIR-based retrieval over Composition, DiagnosticReport, DocumentReference
- Recommendation to avoid inference-heavy queries

**Abridge's Factuality System**
- Taxonomy-based hallucination detection: not binary, but multi-level
- Categories: directly supported, reasonable inference, questionable inference, unmentioned, contradiction
- Severity ratings: minimal, moderate, major (separate from support quality)
- Multiple models in the pipeline: task-specific unsupported-claim detector + automated correction
- 50,000+ training examples for unsupported-claim detection
- Clinician review required before notes enter EHR

---

### [2 min] Practical Takeaways

Close with actionable principles for building medical RAG systems:

1. **Treat RAG as a verification system, not a retrieval system** — retrieve evidence, generate only grounded claims, attach precise evidence, validate support before release

2. **Patient scope is non-negotiable** — one patient at a time, clear task boundaries, no cross-patient leakage

3. **Citation quality is a safety feature** — claim-level evidence beats document-level references

4. **Design for abstention** — the system should refuse or express uncertainty when support is weak

5. **Separate support quality from clinical severity** — a weakly supported claim that's clinically harmless is different from one that's dangerous

---

## Optimized Prompt for NotebookLM

Copy and paste this into NotebookLM:

```
Create a 10-15 minute educational podcast episode exploring "Medical RAG: Beyond Vector Search."

Structure:
[1-2 min] Why medical RAG is fundamentally different from general RAG - the stakes, the verification requirements, why "good enough" isn't acceptable in healthcare.

[4-5 min] Core concepts: claim-level grounding vs document-level citations, exact snippet citations, patient-specific scoping, no-source-no-claim behavior. Explain why each matters for clinical safety.

[4-5 min] How three companies approach this: Delphyr's inline citation generation and multi-stage safety checks, Google Cloud's patient-scoped FHIR retrieval with intended-use boundaries, Abridge's factuality taxonomy with support levels and severity ratings.

[2 min] Practical takeaways: treating RAG as verification not retrieval, patient scope as non-negotiable, citation quality as safety, designing for abstention, separating support quality from clinical severity.

Tone: educational, technical but accessible. Include specific company examples and real-world patterns. Mention that Delphyr is a Dutch healthcare AI startup, Abridge focuses on clinical note documentation, and Google Cloud provides healthcare-specific search APIs.
```

---

## Settings Recommendation

```json
{
  "artifact_type": "audio-overview",
  "settings": {
    "duration": "long",
    "tone": "educational",
    "hosts": "auto",
    "custom_prompt": "Use two hosts - one technical, one clinical perspective. Make it accessible but precise."
  },
  "tips": [
    "Emphasize the safety rationale behind each technical choice",
    "Name specific companies when discussing patterns",
    "Connect concepts back to patient safety stakes"
  ]
}
```
