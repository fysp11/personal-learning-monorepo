# Slide Deck: Patient Context & Clinical Boundaries

Create a **7-slide** interview-prep presentation for **myself** on patient scoping, intended use, and safe task boundaries in clinical AI.

## Slides

1. **Title: Patient Context & Clinical Boundaries**
   - Why “one patient, one task, one evidence boundary” matters

2. **Why Patient Context Is the Safety Boundary**
   - Clinical output is only useful if it is tied to the right patient record
   - Cross-patient leakage is a high-severity failure
   - Good anchor phrase: one patient at a time

3. **What Should Be in Context**
   - Notes, labs, imaging, medications, correspondence
   - Structured + unstructured artifacts together
   - Only authorized sources should be available to the retriever

4. **Allowed vs Unsafe Query Examples**
   - Allowed: “Summarize the latest anemia workup”
   - Allowed: “Show current medications and renal labs”
   - Unsafe: “What diagnosis explains everything?”
   - Unsafe: “What should I prescribe next?”

5. **Intended Use, in Plain English**
   - Safe systems retrieve and summarize existing information
   - They can surface evidence and draft output
   - They should not silently become diagnosis or treatment engines

6. **How Boundaries Show Up in Product Design**
   - Require patient ID or scoped chart context
   - Detect topic drift and override attempts
   - Narrow broad requests before answering
   - Route high-risk requests to human review

7. **What I’d Say in the Interview**
   - “Safe systems narrow the task before they scale it.”
   - “Patient scope, intended use, and refusal behavior are architecture decisions, not just policy text.”

## Style
- Practical and easy to remember
- Use concrete query examples generously
- Keep it focused on workflow-safe design, not compliance jargon
- Make it useful as a quick reminder during the interview
