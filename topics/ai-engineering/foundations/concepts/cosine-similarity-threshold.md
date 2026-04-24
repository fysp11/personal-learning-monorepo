# Entity: Cosine Similarity Threshold

type: concept
aliases:
  - cosine threshold
  - similarity threshold
tags:
  - ai-engineering
  - retrieval
  - deduplication
relationships:
  - minhash
  - hybrid-search
  - reranking
confidence: high

## Facts
- A cosine similarity threshold is used to reject semantically redundant context.
- The repo's source material uses thresholds as a practical deduplication control, not as a theoretical abstraction.

## Why it matters
- This is a simple, auditable gate for pruning noisy retrieval results.

## Open questions
- What threshold is safe across different content types?
