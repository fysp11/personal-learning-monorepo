# Entity: Selective Field Embedding

type: concept
aliases:
  - selective embeddings
  - embed selected fields
tags:
  - ai-engineering
  - retrieval
  - data-modeling
relationships:
  - vector-search
  - keyword-filters
  - structured-data
confidence: high

## Facts
- Quantitative or exact-match fields should not always be embedded.
- Semantic search is stronger for meaning, while exact filters remain better for arithmetic or structured lookups.

## Why it matters
- It avoids wasting vector space on fields that need precision, not similarity.

## Open questions
- Which fields should be semantic, exact, or hybrid by default?
