# Audio Overview Prompt — Episode 2: The Guardrails Pipeline

**Episode Type:** Deep Dive  
**Duration:** 10-15 minutes  
**Target Characters:** ~4000-4500 (within NotebookLM limits)

---

## Episode Structure

### [1-2 min] Why Single-Stage Guardrails Fail in Medical AI

Open by establishing why the naive approach (one moderation filter before the LLM) is dangerous in healthcare:

- Normal content filters catch toxicity, but not medical prompt injection, scope drift, or unsupported clinical claims
- Medical failures are often subtle: the system following "helpful" instructions that drift into diagnosis or treatment recommendations
- Single-stage checks can't catch retrieval contamination, generation hallucinations, or output contradictions
- Delphyr's explicit finding: one-turn checks were not enough; full conversational context mattered

Set up the core insight: **medical guardrails must be a staged pipeline, not a single gate.**

---

### [4-5 min] The Full Pipeline Architecture

Walk through the complete guardrail pipeline that serious medical AI systems implement:

**Stage 1: Input Validation**
- Intent classification: what is the user actually asking for?
- Scope enforcement: is this within the system's intended use?
- Patient scoping: is there a valid patient context?
- Prompt injection detection: subtle attempts to override safety instructions
- Topic drift detection: is the request staying in the medical domain?

**Stage 2: Retrieval Constraints**
- What the system is allowed to retrieve
- Patient-specific filtering (only see data for the scoped patient)
- Source authorization (EHR vs guidelines vs external)
- Metadata-based filtering (date, type, author)

**Stage 3: Generation Rules**
- Claim-level support requirements: every factual claim must cite evidence
- Domain boundaries: what the system is permitted to answer
- Confidence calibration: expressing uncertainty when evidence is weak
- Abstention rules: when to refuse rather than guess

**Stage 4: Output Validation**
- Support verification: does each claim actually match the cited evidence?
- Contradiction detection: does the answer contradict itself or the retrieved evidence?
- Impossible value detection: physiologically implausible numbers
- Overconfidence detection: clinical language that overstates certainty
- Severity classification: is this a minor issue or a critical safety risk?

**Stage 5: Human Escalation**
- When to route to clinician review
- Escalation paths and queues
- Logging for later evaluation and red-team testing

---

### [4-5 min] Real-World Patterns from Delphyr, AWS, and Hippocratic AI

**Delphyr's Multi-Stage Safety Architecture**
- Three risk buckets: security, accuracy, and focus
- Security: prompt injection, malicious instructions
- Accuracy: false medical content, unsupported claims, copied EHR mistakes
- Focus: topic drift, scope creep, going beyond retrieval into diagnosis
- The key insight: safety checks must happen before, during, and after generation
- Full conversational context matters, not just single-turn checks

**AWS Component-Level Evaluation**
- Evaluate extraction separately from RAG response generation
- Extraction metrics: accuracy, completeness, adjusted recall/capture rate, precision
- RAG metrics: response relevancy, context precision, faithfulness
- LLM-as-a-judge approaches: pairwise comparison, single-answer grading, reference-guided grading
- The evaluation philosophy: "the app works" is not an evaluation plan

**Hippocratic AI's Safety Pipeline**
- Real-world error management as a core competency
- Output testing in realistic scenarios (not just benchmarks)
- Human clinical supervision at scale
- Escalation paths and cross-validation
- Their public positioning: real-world error management and feedback loops are necessary for safe deployment

---

### [2 min] Key Principles for Designing Medical Guardrails

Close with actionable principles:

1. **Guardrails are a pipeline, not a filter** — multiple stages with different checks at each stage

2. **Distrust the model by default** — the system should earn the right to answer by passing validation, not be trusted by default

3. **Layer controls for scope, support, and clinical risk** — each requires different checks

4. **Design for abstention** — sometimes the right answer is "I can't determine that from the available evidence"

5. **Log everything** — adversarial testing and continuous improvement require comprehensive logging

6. **Keep humans in the loop for high-risk actions** — diagnosis, prognosis, prescribing, treatment recommendations

---

## Optimized Prompt for NotebookLM

Copy and paste this into NotebookLM:

```
Create a 10-15 minute educational podcast episode exploring "The Guardrails Pipeline in Medical AI."

Structure:
[1-2 min] Why single-stage guardrails fail - normal content filters miss medical-specific failures like prompt injection, scope drift, unsupported clinical claims. Why one moderation call before the LLM isn't enough.

[4-5 min] The full pipeline architecture: input validation (intent classification, scope enforcement, patient scoping, prompt injection detection), retrieval constraints (authorized sources, patient-specific filtering), generation rules (claim-level support, domain boundaries, abstention), output validation (support verification, contradiction detection, impossible values), human escalation paths.

[4-5 min] Real-world patterns: Delphyr's three risk buckets (security, accuracy, focus) with checks before/during/after generation, AWS's component-level evaluation (extraction vs RAG metrics), Hippocratic AI's output testing, human supervision, and escalation patterns.

[2 min] Key principles: guardrails as pipeline not filter, distrust model by default, layer controls for scope/support/risk, design for abstention, log everything, keep humans in loop for high-risk actions.

Tone: educational, technical but accessible. Include specific company examples. Mention Delphyr is a Dutch healthcare AI startup, AWS provides healthcare prescriptive guidance, and Hippocratic AI focuses on safety at scale.
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
    "custom_prompt": "Two hosts - one explaining the architecture, one providing clinical context. Make the pipeline stages concrete with examples."
  },
  "tips": [
    "Use the 'wrong way vs right way' framing for impact",
    "Name specific failure modes each stage prevents",
    "Emphasize that this is about patient safety, not just technical quality"
  ]
}
```
