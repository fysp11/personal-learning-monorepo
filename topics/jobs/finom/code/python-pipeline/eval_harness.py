"""
Financial AI Workflow — Python Evaluation Harness

Demonstrates production-grade evaluation patterns for accounting AI:
- Field-level accuracy with severity weighting
- Confidence calibration (ECE)
- Per-market breakdown
- Regression detection against a stored baseline
- Threshold sweep to find the right auto-book cutoff

This is the eval infrastructure a central AI team owns.
Run it in CI on every model, prompt, or pipeline change.

Run:
    python3 eval_harness.py          # full eval against mock agent
    python3 eval_harness.py --show-details  # include per-case breakdown
"""

import argparse
import math
from dataclasses import dataclass, field
from typing import Literal, Optional

# Import the pipeline under test
from pipeline import (
    Transaction, RoutingStatus,
    categorize, calculate_vat, route,
)


# ─────────────────────────────────────────
# Schema: test case + agent output
# ─────────────────────────────────────────

Severity = Literal["critical", "high", "medium", "low"]
Mechanism = Literal["standard", "reduced", "reverse_charge", "exempt"]

SEVERITY_WEIGHTS: dict[Severity, int] = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


@dataclass
class ExpectedOutput:
    account_code: str
    vat_rate: float
    vat_amount: float
    net_amount: float
    mechanism: Mechanism


@dataclass
class TestCase:
    id: str
    market: str
    description: str
    severity: Severity
    merchant: str
    amount: float
    tx_description: str
    is_b2b: bool
    expected: ExpectedOutput


@dataclass
class FieldResult:
    field: str
    expected: str | float
    actual: str | float
    correct: bool
    delta: Optional[float] = None  # numeric fields only


@dataclass
class CaseResult:
    test_case_id: str
    market: str
    severity: Severity
    passed: bool
    fields: list[FieldResult]
    confidence: float
    severity_weight: int
    weighted_score: float  # severity_weight if passed else 0


# ─────────────────────────────────────────
# Test suite
# ─────────────────────────────────────────

TEST_CASES: list[TestCase] = [
    TestCase(
        id="TC-OFFICE-DE",
        market="DE",
        description="Standard office supply purchase — standard VAT, SKR03",
        severity="medium",
        merchant="Office World",
        amount=119.0,
        tx_description="stationery and printer paper",
        is_b2b=False,
        expected=ExpectedOutput(
            account_code="4930",
            vat_rate=0.19,
            vat_amount=round(119.0 * 0.19 / 1.19, 2),
            net_amount=round(119.0 - 119.0 * 0.19 / 1.19, 2),
            mechanism="standard",
        ),
    ),
    TestCase(
        id="TC-AWS-DE",
        market="DE",
        description="Cloud infrastructure — IT cost account, standard VAT",
        severity="medium",
        merchant="AWS",
        amount=238.0,
        tx_description="EC2 instance monthly charges",
        is_b2b=False,
        expected=ExpectedOutput(
            account_code="4940",
            vat_rate=0.19,
            vat_amount=round(238.0 * 0.19 / 1.19, 2),
            net_amount=round(238.0 - 238.0 * 0.19 / 1.19, 2),
            mechanism="standard",
        ),
    ),
    TestCase(
        id="TC-RESTAURANT-DE",
        market="DE",
        description="Meal expense — reduced VAT applies (7%)",
        severity="high",
        merchant="Lieferando",
        amount=35.70,
        tx_description="team lunch delivery",
        is_b2b=False,
        expected=ExpectedOutput(
            account_code="4650",
            vat_rate=0.07,
            vat_amount=round(35.70 * 0.07 / 1.07, 2),
            net_amount=round(35.70 - 35.70 * 0.07 / 1.07, 2),
            mechanism="reduced",
        ),
    ),
    TestCase(
        id="TC-REVERSE-CHARGE",
        market="DE",
        description="B2B intra-EU service — reverse charge §13b UStG (CRITICAL: wrong here = penalty)",
        severity="critical",
        merchant="Acme Consulting Ltd",
        amount=5000.0,
        tx_description="advisory services",
        is_b2b=True,
        expected=ExpectedOutput(
            account_code="6825",  # professional fees
            vat_rate=0.0,
            vat_amount=0.0,
            net_amount=5000.0,
            mechanism="reverse_charge",
        ),
    ),
    TestCase(
        id="TC-TRAVEL-DE",
        market="DE",
        description="Business travel — Uber ride, reduced VAT",
        severity="medium",
        merchant="Uber",
        amount=45.0,
        tx_description="airport transfer",
        is_b2b=False,
        expected=ExpectedOutput(
            account_code="4670",
            vat_rate=0.07,
            vat_amount=round(45.0 * 0.07 / 1.07, 2),
            net_amount=round(45.0 - 45.0 * 0.07 / 1.07, 2),
            mechanism="reduced",
        ),
    ),
    TestCase(
        id="TC-TRAVEL-FR",
        market="FR",
        description="Business travel in France — PCG code, FR reduced VAT (10%)",
        severity="medium",
        merchant="Uber",
        amount=48.0,
        tx_description="business travel Paris",
        is_b2b=False,
        expected=ExpectedOutput(
            account_code="6251",
            vat_rate=0.10,
            vat_amount=round(48.0 * 0.10 / 1.10, 2),
            net_amount=round(48.0 - 48.0 * 0.10 / 1.10, 2),
            mechanism="reduced",
        ),
    ),
    TestCase(
        id="TC-LUFTHANSA-DE",
        market="DE",
        description="Airline ticket — business travel, reduced VAT",
        severity="medium",
        merchant="Lufthansa",
        amount=320.0,
        tx_description="Frankfurt to Amsterdam flight",
        is_b2b=False,
        expected=ExpectedOutput(
            account_code="4670",
            vat_rate=0.07,
            vat_amount=round(320.0 * 0.07 / 1.07, 2),
            net_amount=round(320.0 - 320.0 * 0.07 / 1.07, 2),
            mechanism="reduced",
        ),
    ),
    TestCase(
        id="TC-LEGAL-DE",
        market="DE",
        description="Legal/notary fees — professional services, standard VAT",
        severity="high",
        merchant="Notary Berlin GbR",
        amount=595.0,
        tx_description="notarial deed",
        is_b2b=False,
        expected=ExpectedOutput(
            account_code="6825",
            vat_rate=0.19,
            vat_amount=round(595.0 * 0.19 / 1.19, 2),
            net_amount=round(595.0 - 595.0 * 0.19 / 1.19, 2),
            mechanism="standard",
        ),
    ),
]


# ─────────────────────────────────────────
# Agent under test: wraps the pipeline
# ─────────────────────────────────────────

@dataclass
class AgentOutput:
    account_code: str
    vat_rate: float
    vat_amount: float
    net_amount: float
    mechanism: str
    confidence: float


def run_agent(tc: TestCase) -> AgentOutput:
    """
    Runs the pipeline under test against a test case.
    In CI, swap this for an API call to the real agent.
    """
    tx = Transaction(
        id=tc.id,
        merchant=tc.merchant,
        amount=tc.amount,
        description=tc.tx_description,
        is_b2b=tc.is_b2b,
        market=tc.market,
    )
    category = categorize(tx)
    vat = calculate_vat(category, tx)
    return AgentOutput(
        account_code=category.account_code,
        vat_rate=vat.rate,
        vat_amount=vat.amount,
        net_amount=vat.net_amount,
        mechanism=vat.mechanism,
        confidence=category.confidence,
    )


# ─────────────────────────────────────────
# Field-level comparison
# ─────────────────────────────────────────

def compare_fields(expected: ExpectedOutput, actual: AgentOutput) -> list[FieldResult]:
    results = []

    results.append(FieldResult(
        field="account_code",
        expected=expected.account_code,
        actual=actual.account_code,
        correct=(expected.account_code == actual.account_code),
    ))
    results.append(FieldResult(
        field="vat_rate",
        expected=expected.vat_rate,
        actual=actual.vat_rate,
        correct=abs(expected.vat_rate - actual.vat_rate) < 0.001,
        delta=abs(expected.vat_rate - actual.vat_rate),
    ))
    results.append(FieldResult(
        field="vat_amount",
        expected=expected.vat_amount,
        actual=actual.vat_amount,
        correct=abs(expected.vat_amount - actual.vat_amount) < 0.01,
        delta=abs(expected.vat_amount - actual.vat_amount),
    ))
    results.append(FieldResult(
        field="net_amount",
        expected=expected.net_amount,
        actual=actual.net_amount,
        correct=abs(expected.net_amount - actual.net_amount) < 0.01,
        delta=abs(expected.net_amount - actual.net_amount),
    ))
    results.append(FieldResult(
        field="mechanism",
        expected=expected.mechanism,
        actual=actual.mechanism,
        correct=(expected.mechanism == actual.mechanism),
    ))
    return results


def evaluate_case(tc: TestCase) -> CaseResult:
    actual = run_agent(tc)
    fields = compare_fields(tc.expected, actual)
    passed = all(f.correct for f in fields)
    weight = SEVERITY_WEIGHTS[tc.severity]
    return CaseResult(
        test_case_id=tc.id,
        market=tc.market,
        severity=tc.severity,
        passed=passed,
        fields=fields,
        confidence=actual.confidence,
        severity_weight=weight,
        weighted_score=weight if passed else 0,
    )


# ─────────────────────────────────────────
# Confidence calibration (ECE)
# ─────────────────────────────────────────

@dataclass
class CalibrationBin:
    low: float
    high: float
    count: int
    correct: int
    accuracy: float


def compute_calibration(results: list[CaseResult]) -> tuple[list[CalibrationBin], float]:
    """
    ECE (Expected Calibration Error): weighted average gap between
    predicted confidence and observed accuracy per bin.
    Target: ECE < 0.05 before widening auto-book thresholds.
    """
    edges = [0.0, 0.2, 0.4, 0.6, 0.8, 1.01]
    bins: list[CalibrationBin] = []

    for i in range(len(edges) - 1):
        low, high = edges[i], edges[i + 1]
        in_bin = [r for r in results if low <= r.confidence < high]
        correct = sum(1 for r in in_bin if r.passed)
        accuracy = correct / len(in_bin) if in_bin else 0.0
        bins.append(CalibrationBin(
            low=low, high=min(high, 1.0),
            count=len(in_bin), correct=correct, accuracy=accuracy,
        ))

    total = len(results)
    ece = sum(
        (b.count / total) * abs(b.accuracy - (b.low + b.high) / 2)
        for b in bins if b.count > 0
    ) if total > 0 else 0.0

    return bins, ece


# ─────────────────────────────────────────
# Regression detection
# ─────────────────────────────────────────

# Simulates a stored baseline from a previous eval run (e.g., CI artifact)
BASELINE: dict[str, str] = {
    "TC-OFFICE-DE": "pass",
    "TC-AWS-DE": "pass",
    "TC-RESTAURANT-DE": "pass",
    "TC-REVERSE-CHARGE": "pass",
    "TC-TRAVEL-DE": "pass",
    "TC-TRAVEL-FR": "pass",
    "TC-LUFTHANSA-DE": "pass",
    "TC-LEGAL-DE": "pass",
}


@dataclass
class Regression:
    test_case_id: str
    severity: Severity
    baseline: str
    current: str


def detect_regressions(results: list[CaseResult]) -> list[Regression]:
    regressions = []
    for r in results:
        baseline = BASELINE.get(r.test_case_id)
        if baseline is None:
            continue
        current = "pass" if r.passed else "fail"
        if baseline == "pass" and current == "fail":
            regressions.append(Regression(
                test_case_id=r.test_case_id,
                severity=r.severity,
                baseline=baseline,
                current=current,
            ))
    return regressions


# ─────────────────────────────────────────
# Threshold sweep
# ─────────────────────────────────────────

@dataclass
class ThresholdAnalysis:
    threshold: float
    auto_book_count: int
    review_count: int
    auto_book_accuracy: float
    critical_errors_in_auto: int


def analyze_thresholds(results: list[CaseResult]) -> list[ThresholdAnalysis]:
    """
    Sweeps auto-book threshold to find the right precision/coverage tradeoff.
    Key invariant: critical errors in auto-book path must be zero.
    """
    analysis = []
    for threshold in [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]:
        auto = [r for r in results if r.confidence >= threshold]
        review = [r for r in results if r.confidence < threshold]
        auto_correct = sum(1 for r in auto if r.passed)
        critical_in_auto = sum(
            1 for r in auto if not r.passed and r.severity == "critical"
        )
        analysis.append(ThresholdAnalysis(
            threshold=threshold,
            auto_book_count=len(auto),
            review_count=len(review),
            auto_book_accuracy=auto_correct / len(auto) if auto else 0.0,
            critical_errors_in_auto=critical_in_auto,
        ))
    return analysis


# ─────────────────────────────────────────
# Report
# ─────────────────────────────────────────

def print_report(
    results: list[CaseResult],
    show_details: bool = False,
) -> None:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    total_weight = sum(r.severity_weight for r in results)
    weighted_correct = sum(r.weighted_score for r in results)

    # Per-market
    markets = sorted({r.market for r in results})
    per_market = {}
    for m in markets:
        in_m = [r for r in results if r.market == m]
        per_market[m] = {
            "count": len(in_m),
            "accuracy": sum(1 for r in in_m if r.passed) / len(in_m),
            "critical_errors": sum(1 for r in in_m if not r.passed and r.severity == "critical"),
        }

    # Per-field
    all_fields = [f for r in results for f in r.fields]
    field_names = list(dict.fromkeys(f.field for f in all_fields))
    per_field = {}
    for fn in field_names:
        subset = [f for f in all_fields if f.field == fn]
        per_field[fn] = sum(1 for f in subset if f.correct) / len(subset)

    bins, ece = compute_calibration(results)
    regressions = detect_regressions(results)
    threshold_analysis = analyze_thresholds(results)
    failures = [r for r in results if not r.passed]

    # ── Print ──
    print("\n══════════════════════════════════════════════════════════")
    print("  Financial AI Workflow — Evaluation Report")
    print("══════════════════════════════════════════════════════════\n")

    print(f"  Total cases:              {total}")
    print(f"  Overall accuracy:         {passed}/{total}  ({passed/total:.0%})")
    swa = weighted_correct / total_weight if total_weight else 0
    print(f"  Severity-weighted acc:    {swa:.2%}  ({'✓ PASS' if swa >= 0.90 else '✗ FAIL'})")
    print(f"  ECE (calibration):        {ece:.4f}  ({'✓ < 0.05' if ece < 0.05 else '✗ > 0.05 — threshold unreliable'})\n")

    print("  ── Per-market ─────────────────────────────────────────")
    for m, stats in per_market.items():
        critical_tag = f"  ← {stats['critical_errors']} CRITICAL ERROR(s)" if stats["critical_errors"] else ""
        print(f"  {m}:  {stats['accuracy']:.0%} accuracy ({stats['count']} cases){critical_tag}")

    print("\n  ── Per-field accuracy ─────────────────────────────────")
    for fn, acc in per_field.items():
        marker = "✓" if acc >= 0.90 else "✗"
        print(f"  {marker} {fn:<15} {acc:.0%}")

    print("\n  ── Confidence calibration (ECE) ───────────────────────")
    for b in bins:
        if b.count == 0:
            continue
        midpoint = (b.low + b.high) / 2
        gap = abs(b.accuracy - midpoint)
        bar = "█" * round(b.accuracy * 20)
        print(f"  [{b.low:.1f}–{b.high:.1f}] n={b.count:<3} acc={b.accuracy:.0%} conf≈{midpoint:.0%}  Δ={gap:.2f}  {bar}")

    print("\n  ── Threshold sweep (auto-book tradeoff) ───────────────")
    print(f"  {'Threshold':<12} {'Auto-book':<12} {'Review':<10} {'Auto-acc':<12} {'Crit-errors'}")
    for t in threshold_analysis:
        crit_flag = "  ← BLOCK" if t.critical_errors_in_auto > 0 else ""
        recommended = "  ← recommended" if t.threshold == 0.85 and t.critical_errors_in_auto == 0 else ""
        print(f"  {t.threshold:<12.2f} {t.auto_book_count:<12} {t.review_count:<10} {t.auto_book_accuracy:<12.0%} {t.critical_errors_in_auto}{crit_flag}{recommended}")

    if regressions:
        print("\n  ── ✗ REGRESSIONS DETECTED ─────────────────────────────")
        for reg in regressions:
            print(f"  [{reg.severity.upper()}] {reg.test_case_id}: was {reg.baseline}, now {reg.current}")
    else:
        print("\n  ── ✓ No regressions vs baseline ───────────────────────")

    if failures:
        print("\n  ── Failures ───────────────────────────────────────────")
        for r in failures:
            bad_fields = [f.field for f in r.fields if not f.correct]
            print(f"  [{r.severity.upper()}] {r.test_case_id}: failed fields → {', '.join(bad_fields)}")

    if show_details:
        print("\n  ── Per-case detail ────────────────────────────────────")
        for r in results:
            status = "✓" if r.passed else "✗"
            print(f"  {status} [{r.severity.upper():<8}] {r.test_case_id} (conf={r.confidence:.0%})")
            for f in r.fields:
                field_ok = "  " if f.correct else "✗ "
                delta_str = f"  Δ={f.delta:.4f}" if f.delta and not f.correct else ""
                if not f.correct:
                    print(f"       {field_ok}{f.field}: expected={f.expected}  got={f.actual}{delta_str}")

    print("\n══════════════════════════════════════════════════════════\n")

    # CI exit code: fail if regressions or critical errors
    has_critical = any(
        not r.passed and r.severity == "critical" for r in results
    )
    if regressions or has_critical:
        print("  ✗ EVAL FAILED — regression or critical error detected")
        print("  This run would block a CI pipeline.\n")
    else:
        print("  ✓ EVAL PASSED — no regressions, no critical errors\n")


# ─────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--show-details", action="store_true", help="Show per-case field breakdown")
    args = parser.parse_args()

    results = [evaluate_case(tc) for tc in TEST_CASES]
    print_report(results, show_details=args.show_details)
