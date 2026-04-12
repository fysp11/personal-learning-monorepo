# Confidence Calibration Deep Dive — From Numbers to Trust

Saved: 2026-04-11

## Why Calibration Matters at Finom

Finom's transaction categorization pipeline produces confidence scores. But a confidence score is worthless unless it's **calibrated** — meaning "when the model says 85% confident, it should be right ~85% of the time."

Miscalibrated confidence leads to:
- **Over-confident:** Auto-booking bad categories → accounting errors → audit risk
- **Under-confident:** Sending too many transactions to human review → defeating the automation goal

This is the mathematical foundation for the "earned autonomy" pattern Ivo described.

---

## Core Concepts

### Calibration Curve (Reliability Diagram)

The calibration curve plots **predicted confidence** (x-axis) vs **actual accuracy** (y-axis).

- **Perfect calibration:** a diagonal line (0.8 predicted → 0.8 actual)
- **Over-confident:** curve bends below the diagonal (says 0.9, is actually 0.7)
- **Under-confident:** curve bends above the diagonal (says 0.6, is actually 0.8)

### Expected Calibration Error (ECE)

The single-number summary of calibration quality:

```
ECE = Σ (|bin_count / total|) × |accuracy_in_bin - confidence_in_bin|
```

Practical interpretation:
- ECE < 0.05: Well-calibrated, threshold-based routing is reliable
- ECE 0.05-0.15: Moderate — thresholds work but need safety margins
- ECE > 0.15: Poorly calibrated — confidence scores are misleading

### Platt Scaling (Post-Hoc Calibration)

When a model's raw confidence is miscalibrated, Platt scaling fits a logistic regression on a held-out set to map raw scores to calibrated probabilities:

```
calibrated = 1 / (1 + exp(-(a × raw_score + b)))
```

This is a lightweight fix that doesn't require retraining the model.

---

## How This Applies to Finom's Architecture

### Transaction Categorization Pipeline

```
Raw Transaction → LLM Categorization (raw confidence: 0.92)
                                       ↓
                  Platt Calibration Layer (calibrated: 0.87)
                                       ↓
                  Confidence Router:
                    ≥ 0.85 → auto-book
                    0.50-0.85 → human review
                    < 0.50 → reject
```

The calibration layer sits **between** the AI output and the routing decision. This is a deterministic transformation — it doesn't call the LLM again.

### Per-Market Calibration

Different markets have different calibration characteristics:
- **Germany (mature):** High training data, well-calibrated, can use aggressive thresholds
- **France (new):** Lower training data, likely over-confident, needs conservative thresholds
- **Italy (future):** Zero training data, start with maximum conservatism

**Interview talking point:** "When we expand to a new market, we don't just change the chart of accounts — we reset the calibration. The model might have seen Italian vendors during pretraining, which gives it false confidence. We need market-specific calibration on actual transaction data before we trust the thresholds."

---

## Calibration Monitoring in Production

### Sliding Window Calibration

Don't just calibrate once — monitor calibration drift over time:

```typescript
// Conceptual: track calibration per rolling window
interface CalibrationWindow {
  startDate: Date;
  endDate: Date;
  bins: Array<{
    confidenceRange: [number, number];
    predictedAccuracy: number;  // center of bin
    actualAccuracy: number;     // from human corrections
    count: number;
  }>;
  ece: number;
}
```

When ECE drifts above threshold → alert → refit calibration parameters → optionally tighten routing thresholds until recalibrated.

### Feedback Loop Design

```
Auto-booked transactions
  ↓ (sampled: 5% audited by human)
  → correction signal
  → recalibrate Platt parameters
  → update routing thresholds if needed
  → measure new ECE
  → repeat
```

The 5% audit rate is the cost of maintaining trust. As calibration improves, audit rate can decrease — another form of earned autonomy.

---

## Connection to Other Prep

- **Confidence routing code:** `code/live-round-rehearsal.ts` lines 216-227 — the THRESHOLDS and routeByConfidence function
- **Cross-company pattern:** `../cross-company-insights-deep-patterns.md` — Pattern 1 (Confidence-Based Routing)
- **Gap mitigation:** `insights/gap-mitigation.md` — addresses "how do you measure if your AI is trustworthy enough"
- **Delphyr parallel:** Clinical confidence calibration has even higher stakes — miscalibrated clinical AI can cause harm, not just accounting errors

---

## Interview-Ready One-Liner

> "Confidence is just a number until you calibrate it against outcomes. The auto-book threshold isn't a parameter you tune once — it's a contract between the model and the business that you verify continuously."
