# Entity: Expected Calibration Error

type: methodologies
aliases:
  - ECE
  - Expected Calibration Error (ECE)
tags:
  - evaluation
  - confidence
  - model-reliability
relationships:
  - confidence-routing
  - proposal-mode-vs-action-mode
confidence: high
generated_by: scripts/extract-entities.ts
generated_at: 2026-04-13T03:25:20.523Z

## Evidence
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:66) — matched `Expected Calibration Error`: - **Confidence calibration**: Expected Calibration Error (ECE) measuring whether confidence scores are trustworthy
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:102) — matched `ECE`: `confidence-calibration.ts` — Demonstrates the math behind confidence-based routing: ECE calculation, Platt scaling, per-market calibration, and threshold analysis.
- [topics/jobs/finom/code/README.md](/Users/fysp/personal/learning/topics/jobs/finom/code/README.md:107) — matched `ECE`: - **ECE/MCE calculation**: Expected and Maximum Calibration Error — the key metrics for trusting confidence scores
- [topics/jobs/finom/insights/agent-safety-transaction-semantics.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/agent-safety-transaction-semantics.md:274) — matched `ECE`: - `code/confidence-calibration.ts` — ECE and threshold analysis
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:27) — matched `Expected Calibration Error`: ### Expected Calibration Error (ECE)
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:32) — matched `ECE`: ECE = Σ (|bin_count / total|) × |accuracy_in_bin - confidence_in_bin|
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:36) — matched `ECE`: - ECE < 0.05: Well-calibrated, threshold-based routing is reliable
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:37) — matched `ECE`: - ECE 0.05-0.15: Moderate — thresholds work but need safety margins
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:38) — matched `ECE`: - ECE > 0.15: Poorly calibrated — confidence scores are misleading
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:97) — matched `ECE`: ece: number;
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:101) — matched `ECE`: When ECE drifts above threshold → alert → refit calibration parameters → optionally tighten routing thresholds until recalibrated.
- [topics/jobs/finom/insights/confidence-calibration-deep-dive.md](/Users/fysp/personal/learning/topics/jobs/finom/insights/confidence-calibration-deep-dive.md:111) — matched `ECE`: → measure new ECE
