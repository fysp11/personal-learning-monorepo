# Entity: Hallucination Mitigation Protocols

type: concept
aliases:
  - hallucination mitigation
tags:
  - ai-engineering
  - retrieval
  - trust
relationships:
  - citations
  - evidence-grounding
  - human-review
confidence: high

## Facts
- The repo's AI-engineering source material frames hallucination mitigation as a design problem, not a post-hoc cleanup step.
- The underlying pattern is to require citations and remove claims that cannot be grounded in source context.

## Why it matters
- This is a reusable trust layer for any AI workflow that needs defensible outputs.

## Open questions
- Which checks should be deterministic vs model-assisted?
