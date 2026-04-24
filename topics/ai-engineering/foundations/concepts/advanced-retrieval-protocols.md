# Entity: Advanced Retrieval Protocols

type: concept
aliases:
  - retrieval protocols
  - advanced retrieval
tags:
  - ai-engineering
  - retrieval
  - architecture
relationships:
  - hybrid-search
  - query-rewriting
  - reranking
confidence: high

## Facts
- The source material treats retrieval as a staged system rather than a single vector lookup.
- The retrieval stack includes filtering, candidate generation, and context selection before generation.

## Why it matters
- This is the control surface that determines what context the model can safely use.

## Open questions
- Where should the final routing threshold live?
