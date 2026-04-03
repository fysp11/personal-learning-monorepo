# Slide Deck: Medical Guardrails Pipeline

Create an **8-slide** interview-prep presentation for **myself** on staged guardrails for medical AI systems. Phrase it like a strong interview answer, not like a research paper.

## Slides

1. **Title: Medical Guardrails Pipeline**
   - Why one filter is not enough in clinical AI

2. **Why Single-Stage Guardrails Fail**
   - Generic moderation misses prompt injection, topic drift, unsupported clinical claims
   - Medical failures are subtle: plausible but unsafe output is still a failure
   - One-turn checks miss conversational problems

3. **Input Guardrails**
   - Classify intent
   - Enforce intended use
   - Require patient context when needed
   - Mini examples: block “What should I prescribe?” but allow “Summarize the latest visit”

4. **Retrieval Guardrails**
   - Patient-scoped retrieval only
   - Authorized sources only
   - Prevent broad context dumps and cross-patient contamination
   - Good phrase: the model should only see allowed evidence

5. **Generation Guardrails**
   - No-source-no-claim behavior
   - Stay in domain and within the allowed task
   - Prefer uncertainty over confident unsupported synthesis

6. **Output Validators**
   - Unsupported claim
   - Invalid citation
   - Weak support
   - Contradiction, impossible values, overconfidence
   - Example: output says “denies chest pain,” but source says chest pain was reported

7. **Escalation + Delphyr’s Three Buckets**
   - **Security**: prompt injection, malicious instructions
   - **Accuracy**: unsupported or copied errors from the record
   - **Focus**: drift beyond the intended task
   - Escalate to human review or fallback to retrieval-only behavior

8. **What I’d Say in the Interview**
   - “I wouldn’t trust the model and filter around it. I’d build a staged pipeline: intent checks, retrieval constraints, grounded generation, output validation, then escalation.”
   - “In medical AI, the model should earn the right to answer.”

## Style
- Implementation-aware, but phrased in interview language
- Use mini examples on multiple slides
- Keep stages crisp and memorable
- Optimize for quick verbal explanation
