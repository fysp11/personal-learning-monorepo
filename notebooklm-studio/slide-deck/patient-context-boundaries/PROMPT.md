# Slide Deck: Patient Context & Clinical Boundaries

Create a presentation covering patient scoping and intended-use boundaries in Medical RAG:

## Slides (10-15 slides)

1. **Title Slide**
   - Patient Context & Clinical Boundaries
   - Subtitle: Designing systems that stay in scope

2. **Why Patient Context Matters**
   - Generic medical advice is dangerous
   - Patient-specific information changes everything
   - The cost of context confusion

3. **Single-Patient Retrieval Scope**
   - One patient at a time
   - Patient ID in every query
   - Avoiding cross-patient contamination

4. **FHIR Resource Handling**
   - Composition, DiagnosticReport, DocumentReference
   - Structured vs unstructured clinical data
   - Relevance ordering for clinical resources

5. **The Intended Use Problem**
   - Medical AI: retrieve and summarize, not diagnose
   - Outputs are drafts, not final decisions
   - Clear task boundaries reduce risk

6. **Bounded Task Design**
   - Simpler queries over complex inference
   - Break complex questions into simpler ones
   - Avoid inference-heavy responses

7. **Topic Drift Prevention**
   - Stay in domain
   - Recognize when queries go out of scope
   - Refusal vs narrowing the task

8. **Clinical vs Non-Clinical Queries**
   - Routing based on query type
   - Different retrieval for different tasks
   - Clear escalation paths

9. **Human Review Requirements**
   - Clinician review before EHR entry
   - Keeping humans in the loop for high-risk actions
   - Design for escalation, not automation

10. **Summary: Safe Boundaries**
    - Patient scoping is non-negotiable
    - Intended use defines the design
    - When in doubt, narrow the task

## Style
- Clinical/professional presentation
- Include speaker notes
