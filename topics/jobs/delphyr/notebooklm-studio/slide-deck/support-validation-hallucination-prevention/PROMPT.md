# Slide Deck: Support Validation & Hallucination Prevention

Create a **7-slide** interview-prep presentation for **myself** on preventing unsupported claims in medical AI by validating support, severity, and evidence quality.

## Slides

1. **Title: Support Validation & Hallucination Prevention**
   - Why “hallucination” is too vague for medical systems

2. **Why Binary Labels Fail**
   - Medical errors vary by support quality and by clinical harm
   - Some unsupported claims are minor; others are dangerous
   - Best framing: support and severity are different axes

3. **Support Taxonomy, in Plain English**
   - Directly supported
   - Reasonable inference
   - Questionable inference
   - Unmentioned
   - Contradiction
   - Make each term easy to explain out loud

4. **Mini Examples I Can Remember**
   - Direct support: source clearly states the same medication and dose
   - Questionable inference: inferring atrial fibrillation only because Eliquis appears in the med list
   - Contradiction: note says “denies chest pain” while the transcript says the opposite

5. **Support vs Severity**
   - Weak support can be harmless or dangerous depending on context
   - The same validation framework should help triage review priority
   - Good phrase: not every bad claim is equally risky

6. **What the System Should Do When Support Fails**
   - Align/correct the draft when the source clearly supports a fix
   - Delete unsupported claims
   - Escalate when support is weak or risk is high
   - Keep validator reasoning/logs for review

7. **What I’d Say in the Interview**
   - “I’d score claims on support and severity, not just true/false.”
   - “In medicine, hallucination prevention is really claim validation plus risk handling.”

## Style
- Practical and memorable
- Example-heavy rather than theory-heavy
- Use short phrases I can quickly recall in conversation
- Keep Delphyr/Abridge-style thinking visible without sounding academic
