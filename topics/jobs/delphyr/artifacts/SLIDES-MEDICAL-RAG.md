# Slide Deck Plans - Medical RAG Only

Date: 2026-04-03

## Overview
3 slide deck prompts for NotebookLM, focused on Medical RAG systems (no guardrails or evals).

---

## Slide Deck 1: Medical RAG Architecture
**Location:** `notebooklm-studio/slide-deck/medical-rag-architecture/PROMPT.md`

**Topic:** Core technical architecture of Medical RAG systems

**Slides:**
1. Title Slide
2. What Makes Medical RAG Different
3. System Overview
4. The Citation Problem
5. Patient Context Layer
6. Structured + Unstructured Data
7. Generation with Grounding
8. The Verification Pipeline
9. Key Design Principles
10. Summary

**Sources:** Delphyr, Google Cloud, Abridge

---

## Slide Deck 2: Retrieval & Grounding
**Location:** `notebooklm-studio/slide-deck/retrieval-grounding/PROMPT.md`

**Topic:** How Medical RAG finds and cites the right context

**Slides:**
1. Title Slide
2. The Retrieval Challenge
3. Citation Quality Levels
4. Hybrid Retrieval Architecture
5. Source Verification Pipeline
6. The No-Source-No-Claim Principle
7. Context Precision
8. Handling Multiple Sources
9. Patient-Specific Retrieval
10. Key Takeaways

**Sources:** Delphyr, Abridge, AWS

---

## Slide Deck 3: Patient Context & Clinical Boundaries
**Location:** `notebooklm-studio/slide-deck/patient-context-boundaries/PROMPT.md`

**Topic:** Patient scoping and intended-use boundaries

**Slides:**
1. Title Slide
2. Why Patient Context Matters
3. Single-Patient Retrieval Scope
4. FHIR Resource Handling
5. The Intended Use Problem
6. Bounded Task Design
7. Topic Drift Prevention
8. Clinical vs Non-Clinical Queries
9. Human Review Requirements
10. Summary: Safe Boundaries

**Sources:** Google Cloud, Delphyr, AWS

---

## Usage
1. Open NotebookLM
2. Create new Source and add sources from the web
3. Generate Slide Deck using the PROMPT.md content
4. Export to Google Slides

## Sources to Add to NotebookLM
- Delphyr blog posts on citations and guardrails
- AWS Prescriptive Guidance on healthcare RAG evaluation
- Google Cloud healthcare search documentation
- Abridge science of hallucination elimination
