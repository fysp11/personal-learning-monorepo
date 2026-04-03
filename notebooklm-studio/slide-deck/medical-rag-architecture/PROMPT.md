# Slide Deck: Medical RAG Architecture

Create a presentation covering the core architecture of Medical RAG systems:

## Slides (10-15 slides)

1. **Title Slide**
   - Medical RAG: Beyond Vector Search
   - Subtitle: How healthcare AI systems retrieve and cite clinical knowledge

2. **What Makes Medical RAG Different**
   - General RAG vs Medical RAG requirements
   - Stakes: errors can harm patients
   - Need for exact citations, not just relevance

3. **System Overview**
   - High-level architecture diagram
   - Components: retrieval, generation, citation, validation

4. **The Citation Problem**
   - "This came from guideline X" is weak
   - "This sentence is supported by this exact snippet" is stronger
   - Citation quality as safety feature

5. **Patient Context Layer**
   - Why patient-specific context matters
   - Single-patient retrieval scope
   - EHR integration patterns

6. **Structured + Unstructured Data**
   - Handling both clinical notes and guidelines
   - FHIR resources (Composition, DiagnosticReport, DocumentReference)
   - Hybrid retrieval approaches

7. **Generation with Grounding**
   - Inline citation generation during response
   - Not post-hoc source attachment
   - Deterministic verification over fast answers

8. **The Verification Pipeline**
   - Claim-level support checking
   - Contradiction detection against retrieved evidence
   - Abstention when support is weak

9. **Key Design Principles**
   - Patient-scoped, source-grounded, clinically bounded
   - Traceability, abstention, severity-aware failure

10. **Summary**
    - Medical RAG is a verification system
    - Citations are safety features
    - Patient context is non-negotiable

## Style
- Academic/technical presentation
- Clean, professional slides
- Include speaker notes for each slide
