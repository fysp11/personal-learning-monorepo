# Audio Overview Plans - Medical RAG & Guardrails

Date: 2026-04-02

## Overview
6 long-duration audio overview prompts (10-15 min each), max 5000 characters per prompt.

---

## Episode 1 — Deep Dive: Medical RAG: Beyond Vector Search
**Sources:** Delphyr, Google Cloud, Abridge  
**Focus:** Claim-level citations, patient scoping, verification systems, no-source-no-claim  

**Prompt Structure:**
- 1-2 min: Why medical RAG is different from general RAG
- 4-5 min: Core concepts (claim-level grounding, exact snippet citations, patient-specific scoping)
- 4-5 min: How Delphyr, Google Cloud, and Abridge handle it
- 2 min: Practical takeaways for building medical RAG systems

---

## Episode 2 — Deep Dive: The Guardrails Pipeline
**Sources:** Delphyr, AWS, Hippocratic AI  
**Focus:** Multi-stage safety architecture — input → retrieval → generation → output validation  

**Prompt Structure:**
- 1-2 min: Why single-stage guardrails fail in medical AI
- 4-5 min: The full pipeline (input validation, retrieval constraints, generation rules, output validators)
- 4-5 min: Real-world patterns from Delphyr, AWS, Hippocratic AI
- 2 min: Key principles for designing medical guardrails

---

## Episode 3 — Debate: RAG vs Fine-tuning for Medical Knowledge
**Sources:** Abridge, Delphyr, John Snow Labs  
**Format:** Balanced trade-offs — neither side "wins"  

**Prompt Structure:**
- 1 min: Frame the debate (retrieve vs memorize)
- 4 min: Strengths of RAG approach
- 4 min: Strengths of fine-tuning approach
- 2 min: Decision framework — when to use which

---

## Episode 4 — Debate: Closed Source vs Open Source Medical AI
**Sources:** Hippocratic AI, John Snow Labs, AWS  
**Format:** Balanced trade-offs — proprietary vs open models  

**Prompt Structure:**
- 1 min: Frame the debate
- 4 min: Case for closed source (reliability, compliance, support)
- 4 min: Case for open source (transparency, customization, cost)
- 2 min: Decision framework for healthcare deployments

---

## Episode 5 — Critique: Big Models vs Small Domain Models
**Sources:** John Snow Labs, Hippocratic AI, AWS  
**Format:** Balanced trade-offs — scale vs domain fit  

**Prompt Structure:**
- 1 min: Frame the critique
- 4 min: Why bigger models seem better (capability ceiling, generalization)
- 4 min: Why smaller domain models can win (latency, cost, domain fit, control)
- 2 min: Practical recommendations for different use cases

---

## Episode 6 — Critique: Evaluation Frameworks in Medical AI
**Sources:** Abridge, Hippocratic AI, AWS, Google Cloud  
**Format:** Critique of benchmarks vs real-world testing  

**Prompt Structure:**
- 1 min: Frame the critique — why current benchmarks are insufficient
- 4 min: Limitations of offline benchmarks and LLM-as-a-judge
- 4 min: What real-world evaluation looks like (clinician review, scenario testing, safety monitoring)
- 2 min: Building a practical evaluation stack

---

## Character Guidelines
- Target ~4000-4500 characters per prompt
- Leave buffer for NotebookLM formatting
- Include specific company examples and real-world patterns

---

## Sources Summary
| Company | Key Topics |
|---------|------------|
| Delphyr | Claim-level citations, multi-stage guardrails, patient context |
| Abridge | Factuality taxonomy, unsupported claim detection, fine-tuning |
| Hippocratic AI | Real-world evals, safety at scale, clinician supervision |
| AWS | Component-level evaluation, extraction metrics, RAG metrics |
| Google Cloud | Patient scoping, intended-use boundaries, FHIR retrieval |
| John Snow Labs | Small domain models, healthcare RAG, practical deployments |
