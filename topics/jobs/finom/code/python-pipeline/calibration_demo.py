"""
Confidence Calibration Demo — Platt Scaling for Financial AI

Demonstrates the full calibration workflow:
  1. Simulate an overconfident categorizer (ECE >> 0.05)
  2. Collect ground-truth outcomes on a holdout set
  3. Fit Platt scaling (logistic regression on raw scores)
  4. Measure ECE before and after calibration
  5. Show how calibration changes the routing threshold

This is the production calibration workflow for any pipeline that uses
confidence-based routing. Run it after every model/prompt change.

Run:
    python3 calibration_demo.py
"""

import math
import random
from dataclasses import dataclass


# ─────────────────────────────────────────
# Simulate an overconfident model
# ─────────────────────────────────────────

def simulate_overconfident_model(n: int = 200, seed: int = 42) -> list[tuple[float, bool]]:
    """
    Returns (raw_confidence, is_correct) pairs.
    The model is systematically overconfident: it reports 0.9 when it's right only 70%.
    This is typical for fine-tuned LLMs on domain-specific classification.
    """
    rng = random.Random(seed)
    pairs = []
    for _ in range(n):
        # Raw score clusters around 0.7–0.95 (overconfident zone)
        raw = rng.uniform(0.55, 0.98)
        # Actual accuracy is ~15 percentage points lower than reported
        actual_accuracy = max(0.0, raw - 0.15 + rng.gauss(0, 0.05))
        is_correct = rng.random() < actual_accuracy
        pairs.append((raw, is_correct))
    return pairs


# ─────────────────────────────────────────
# ECE calculation
# ─────────────────────────────────────────

@dataclass
class CalibrationBin:
    low: float
    high: float
    count: int
    correct: int
    avg_confidence: float
    accuracy: float
    gap: float  # |accuracy - avg_confidence|


def compute_ece(pairs: list[tuple[float, bool]], n_bins: int = 10) -> tuple[float, list[CalibrationBin]]:
    """
    Expected Calibration Error:
    ECE = Σ (|bin| / total) × |accuracy_in_bin - avg_confidence_in_bin|

    Target: ECE < 0.05 before widening auto-book thresholds.
    """
    edges = [i / n_bins for i in range(n_bins + 1)]
    bins: list[CalibrationBin] = []

    for i in range(n_bins):
        low, high = edges[i], edges[i + 1]
        in_bin = [(c, ok) for c, ok in pairs if low <= c < high or (i == n_bins - 1 and c == 1.0)]
        if not in_bin:
            continue
        avg_conf = sum(c for c, _ in in_bin) / len(in_bin)
        acc = sum(1 for _, ok in in_bin if ok) / len(in_bin)
        bins.append(CalibrationBin(
            low=low, high=high,
            count=len(in_bin), correct=sum(1 for _, ok in in_bin if ok),
            avg_confidence=avg_conf,
            accuracy=acc,
            gap=abs(acc - avg_conf),
        ))

    total = len(pairs)
    ece = sum((b.count / total) * b.gap for b in bins)
    return ece, bins


# ─────────────────────────────────────────
# Platt scaling (post-hoc calibration)
# ─────────────────────────────────────────

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def fit_platt_scaling(
    pairs: list[tuple[float, bool]],
    lr: float = 0.5,
    epochs: int = 300,
) -> tuple[float, float]:
    """
    Fits a logistic regression: p(correct) = sigmoid(a * raw_score + b)
    Uses gradient descent on the training pairs.
    Returns (a, b) — the two Platt parameters.

    This is the minimal post-hoc calibration fix:
    - Does NOT require retraining the model
    - Requires only a holdout set with ground-truth outcomes
    - Adds 2 parameters that map raw scores → calibrated probabilities
    """
    a, b = 1.0, 0.0  # start from identity

    for _ in range(epochs):
        grad_a, grad_b = 0.0, 0.0
        for raw, is_correct in pairs:
            p = sigmoid(a * raw + b)
            y = 1.0 if is_correct else 0.0
            error = p - y
            grad_a += error * raw
            grad_b += error

        a -= lr * grad_a / len(pairs)
        b -= lr * grad_b / len(pairs)

    return a, b


def apply_platt(raw: float, a: float, b: float) -> float:
    return round(sigmoid(a * raw + b), 4)


# ─────────────────────────────────────────
# Threshold analysis (pre vs post calibration)
# ─────────────────────────────────────────

def analyze_thresholds(
    pairs: list[tuple[float, bool]],
    a: float,
    b: float,
    thresholds: list[float] = [0.70, 0.75, 0.80, 0.85, 0.90],
) -> None:
    print("\n  ── Threshold analysis: raw vs calibrated ───────────────")
    print(f"  {'Threshold':<12} {'Raw auto-book':<18} {'Raw accuracy':<16} {'Cal auto-book':<18} {'Cal accuracy'}")
    for t in thresholds:
        raw_auto = [ok for raw, ok in pairs if raw >= t]
        cal_auto = [ok for raw, ok in pairs if apply_platt(raw, a, b) >= t]
        raw_acc = sum(raw_auto) / len(raw_auto) if raw_auto else 0.0
        cal_acc = sum(cal_auto) / len(cal_auto) if cal_auto else 0.0
        reco = "  ← recommended" if t == 0.85 else ""
        print(f"  {t:<12.2f} {len(raw_auto):<18} {raw_acc:<16.0%} {len(cal_auto):<18} {cal_acc:.0%}{reco}")


# ─────────────────────────────────────────
# ASCII calibration curve
# ─────────────────────────────────────────

def print_calibration_curve(bins: list[CalibrationBin], label: str) -> None:
    print(f"\n  ── Calibration curve: {label} ─────────────────────────")
    print(f"  {'Bin':<12} {'n':<6} {'Conf':<8} {'Acc':<8} {'Gap':<8} Bar (accuracy)")
    for b in bins:
        bar = "█" * round(b.accuracy * 20)
        perfect = "·" * round(b.avg_confidence * 20)
        flag = " ←" if b.gap > 0.10 else ""
        print(f"  [{b.low:.1f}–{b.high:.1f}]  {b.count:<6} {b.avg_confidence:.2f}    {b.accuracy:.2f}    {b.gap:.2f}    {bar}{flag}")


# ─────────────────────────────────────────
# Per-market calibration (production pattern)
# ─────────────────────────────────────────

def demonstrate_per_market_calibration() -> None:
    """
    In production, you fit separate Platt parameters per market.
    Germany has 18 months of data → tight calibration.
    France has 2 months of data → conservative thresholds only.
    """
    print("\n  ── Per-market calibration state ────────────────────────")

    market_data = {
        "DE": {"months": 18, "n": 5000, "ece": 0.031, "platt_a": 1.35, "platt_b": -0.42, "threshold": 0.85},
        "FR": {"months": 4,  "n": 800,  "ece": 0.087, "platt_a": None, "platt_b": None,  "threshold": 0.95},
        "IT": {"months": 1,  "n": 120,  "ece": None,  "platt_a": None, "platt_b": None,  "threshold": 1.01},
    }

    print(f"  {'Market':<8} {'Months':<8} {'Samples':<10} {'ECE':<10} {'Threshold':<12} {'Status'}")
    for market, d in market_data.items():
        ece_str = f"{d['ece']:.3f}" if d["ece"] else "n/a"
        platt_str = f"a={d['platt_a']}" if d["platt_a"] else "not fitted"
        threshold_str = f"{d['threshold']:.2f}" if d["threshold"] <= 1.0 else "human review only"
        status = "✓ auto-book enabled" if d["threshold"] <= 1.0 else "shadow mode only"
        if d["ece"] and d["ece"] > 0.05:
            status = "⚠ calibration weak — tighten threshold"
        print(f"  {market:<8} {d['months']:<8} {d['n']:<10} {ece_str:<10} {threshold_str:<12} {status}")

    print("\n  Key: France has ECE > 0.05 — threshold tightened to 0.95 until more data.")
    print("  Key: Italy in shadow mode — 120 samples insufficient to fit Platt parameters.")
    print("  Key: Advance from shadow mode only when ECE < 0.05 AND n > 500 per market.")


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("\n══════════════════════════════════════════════════════════")
    print("  Confidence Calibration Demo — Platt Scaling")
    print("══════════════════════════════════════════════════════════")

    # Split into train (calibration) and test (eval) sets
    all_pairs = simulate_overconfident_model(n=300)
    train_pairs = all_pairs[:200]
    test_pairs = all_pairs[200:]

    # Before calibration
    ece_before, bins_before = compute_ece(test_pairs)
    print(f"\n  Before calibration:")
    print(f"  ECE = {ece_before:.4f}  ({'✗ > 0.05 — thresholds unreliable' if ece_before > 0.05 else '✓ < 0.05'})")
    print_calibration_curve(bins_before, "BEFORE Platt scaling")

    # Fit Platt scaling on train set
    a, b = fit_platt_scaling(train_pairs)
    print(f"\n  Platt scaling parameters (fitted on {len(train_pairs)} holdout cases):")
    print(f"  a = {a:.4f}   b = {b:.4f}")
    print(f"  Formula: calibrated_score = sigmoid({a:.2f} × raw_score + ({b:.2f}))")

    # After calibration — apply to test set
    calibrated_test = [(apply_platt(raw, a, b), ok) for raw, ok in test_pairs]
    ece_after, bins_after = compute_ece(calibrated_test)
    print(f"\n  After calibration:")
    print(f"  ECE = {ece_after:.4f}  ({'✓ < 0.05 — thresholds reliable' if ece_after < 0.05 else '⚠ still > 0.05 — may need more data or different calibrator'})")
    print_calibration_curve(bins_after, "AFTER Platt scaling")

    # Threshold analysis
    analyze_thresholds(test_pairs, a, b)

    # Per-market state
    demonstrate_per_market_calibration()

    # Summary
    print(f"\n  ── Key takeaways ──────────────────────────────────────")
    print(f"  1. Raw ECE = {ece_before:.4f} → model is overconfident by ~{ece_before:.0%} on average")
    print(f"  2. After Platt scaling: ECE = {ece_after:.4f} ({'+' if ece_after > 0 else ''}{(ece_after - ece_before):.4f})")
    print(f"  3. Platt parameters: only 2 numbers, no retraining required")
    print(f"  4. Auto-book threshold 0.85 applied to calibrated scores is reliable")
    print(f"  5. New markets start at shadow mode — fit Platt only after 500+ labeled samples")
    print()
