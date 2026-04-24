# Entity: Expected Calibration Error

type: concept
aliases:
  - ECE
  - calibration error
tags:
  - ai-engineering
  - evaluation
  - confidence
relationships:
  - confidence-routing
  - thresholding
  - model-evaluation
confidence: high

## Facts
- Expected Calibration Error measures whether stated confidence matches observed correctness.
- In the Finom prep material, it is used as the metric behind threshold-based routing.

## Why it matters
- It tells you whether the system can safely auto-act or should defer to review.

## Open questions
- What ECE is acceptable for each workflow stage?
