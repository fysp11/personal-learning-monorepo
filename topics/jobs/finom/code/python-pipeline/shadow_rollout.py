"""
Shadow Mode & Gradual Rollout — Production AI Deployment Pattern

Demonstrates the full maturity ladder for safely deploying a new model version:

  Stage 0: Shadow     — new model runs in parallel, output not used (comparison only)
  Stage 1: Canary     — new model used for N% of traffic, metrics compared vs baseline
  Stage 2: Ramping    — percentage increases as gates pass (5% → 25% → 50% → 100%)
  Stage 3: Full       — new model is baseline; old model retired

Promotion gates (must pass before advancing stage):
  - Accuracy delta ≥ 0 (new model not worse than baseline)
  - ECE delta ≤ +0.01 (calibration not significantly worse)
  - Critical regression count = 0 (no new critical misses)
  - Minimum sample count met for statistical significance

This is the interview answer to "how would you deploy a new model safely?" made
concrete. The key principle: autonomy is earned through data, not granted by default.

Run:
    python3 shadow_rollout.py
"""

import random
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable

from pipeline import Transaction, CategoryProposal, MERCHANT_PATTERNS


# ─────────────────────────────────────────
# Maturity stages
# ─────────────────────────────────────────

class RolloutStage(Enum):
    SHADOW   = "shadow"    # 0% traffic to new model; runs in parallel for comparison only
    CANARY   = "canary"    # 5% traffic to new model
    RAMPING  = "ramping"   # 5% → 25% → 50% → 100% as gates pass
    FULL     = "full"      # 100% traffic to new model; old model retired


STAGE_TRAFFIC_PCT: dict[RolloutStage, float] = {
    RolloutStage.SHADOW:  0.00,
    RolloutStage.CANARY:  0.05,
    RolloutStage.RAMPING: 0.25,  # starting point; gate-driven promotion increases this
    RolloutStage.FULL:    1.00,
}


# ─────────────────────────────────────────
# Model comparison record
# Each transaction processed during rollout generates one record.
# ─────────────────────────────────────────

@dataclass
class ComparisonRecord:
    transaction_id: str
    baseline_proposal: CategoryProposal
    new_proposal: CategoryProposal
    ground_truth: Optional[str]   # None until user confirms/overrides
    used_new_model: bool           # was the new model's result actually served?
    stage: RolloutStage


# ─────────────────────────────────────────
# Promotion gate results
# ─────────────────────────────────────────

@dataclass
class GateResult:
    gate_name: str
    passed: bool
    value: float
    threshold: float
    detail: str


@dataclass
class PromotionAssessment:
    current_stage: RolloutStage
    target_stage: RolloutStage
    gates: list[GateResult] = field(default_factory=list)
    can_promote: bool = False
    block_reason: Optional[str] = None
    sample_count: int = 0
    min_samples: int = 50


# ─────────────────────────────────────────
# Mock model implementations
# baseline_model: current production model
# new_model: candidate — slightly better on most cases but has one regression
# ─────────────────────────────────────────

def baseline_model(tx: Transaction) -> CategoryProposal:
    """Current production model. Well-calibrated, ECE ~ 0.04."""
    merchant_lower = tx.merchant.lower()
    desc_lower = tx.description.lower()

    for keyword, (debit, credit, conf, evidence) in MERCHANT_PATTERNS.items():
        if keyword in merchant_lower or keyword in desc_lower:
            return CategoryProposal(account_code=debit, confidence=conf, evidence=evidence)

    return CategoryProposal(account_code="4990", confidence=0.30,
                           evidence="no pattern match — manual review")


def new_model(tx: Transaction, rng: random.Random) -> CategoryProposal:
    """
    Candidate new model. Generally better confidence calibration but:
    - Has a regression: 'consulting' merchants → returns 4990 instead of 6825
    - Slightly higher confidence overall (good, if well-calibrated)
    """
    merchant_lower = tx.merchant.lower()
    desc_lower = tx.description.lower()

    # Intentional regression: new model misses consulting keyword
    if "consult" in merchant_lower or "consult" in desc_lower:
        return CategoryProposal(account_code="4990", confidence=0.35,
                               evidence="[new model regression] consulting not in v2 patterns")

    for keyword, (debit, credit, conf, evidence) in MERCHANT_PATTERNS.items():
        if keyword in merchant_lower or keyword in desc_lower:
            # New model: slightly higher confidence on known patterns
            new_conf = min(0.97, conf + rng.uniform(0.01, 0.05))
            return CategoryProposal(account_code=debit, confidence=round(new_conf, 3),
                                   evidence=f"[v2] {evidence}")

    return CategoryProposal(account_code="4990", confidence=0.28,
                           evidence="[new model] no pattern match")


# ─────────────────────────────────────────
# Rollout controller
# ─────────────────────────────────────────

class RolloutController:
    """
    Manages traffic splitting and comparison logging for model rollout.
    In production: backed by a feature flag service (LaunchDarkly, Unleash).
    """

    def __init__(self, stage: RolloutStage, traffic_pct: Optional[float] = None):
        self.stage = stage
        self.traffic_pct = traffic_pct or STAGE_TRAFFIC_PCT[stage]
        self.records: list[ComparisonRecord] = []

    def process(
        self,
        tx: Transaction,
        rng: random.Random,
    ) -> CategoryProposal:
        """
        Process one transaction through the rollout controller.
        - Always runs baseline model
        - Runs new model if stage != SHADOW or for comparison logging
        - Serves new model output only if traffic roll hits and stage allows
        """
        baseline = baseline_model(tx)
        new = new_model(tx, rng)

        use_new = (
            self.stage != RolloutStage.SHADOW
            and rng.random() < self.traffic_pct
        )

        record = ComparisonRecord(
            transaction_id=tx.id,
            baseline_proposal=baseline,
            new_proposal=new,
            ground_truth=None,   # set later when user confirms
            used_new_model=use_new,
            stage=self.stage,
        )
        self.records.append(record)

        return new if use_new else baseline

    def record_ground_truth(self, tx_id: str, correct_account: str) -> None:
        for r in self.records:
            if r.transaction_id == tx_id:
                r.ground_truth = correct_account
                break

    def assess_promotion(self, target_stage: RolloutStage, min_samples: int = 30) -> PromotionAssessment:
        """
        Evaluate whether the current stage has sufficient evidence to promote.
        Gates: accuracy delta, ECE delta, critical regression count, sample count.
        """
        labeled = [r for r in self.records if r.ground_truth is not None]
        assessment = PromotionAssessment(
            current_stage=self.stage,
            target_stage=target_stage,
            sample_count=len(labeled),
            min_samples=min_samples,
        )

        if len(labeled) < min_samples:
            assessment.block_reason = f"insufficient samples: {len(labeled)} < {min_samples}"
            return assessment

        # Gate 1: accuracy delta
        baseline_correct = sum(
            1 for r in labeled if r.baseline_proposal.account_code == r.ground_truth
        )
        new_correct = sum(
            1 for r in labeled if r.new_proposal.account_code == r.ground_truth
        )
        baseline_acc = baseline_correct / len(labeled)
        new_acc = new_correct / len(labeled)
        acc_delta = new_acc - baseline_acc

        assessment.gates.append(GateResult(
            gate_name="accuracy_delta",
            passed=acc_delta >= 0.0,
            value=round(acc_delta, 4),
            threshold=0.0,
            detail=f"new={new_acc:.2%} vs baseline={baseline_acc:.2%} (delta={acc_delta:+.2%})",
        ))

        # Gate 2: critical regressions — cases baseline got right but new model got wrong
        critical_regressions = [
            r for r in labeled
            if r.baseline_proposal.account_code == r.ground_truth
            and r.new_proposal.account_code != r.ground_truth
        ]
        assessment.gates.append(GateResult(
            gate_name="critical_regressions",
            passed=len(critical_regressions) == 0,
            value=float(len(critical_regressions)),
            threshold=0.0,
            detail=f"{len(critical_regressions)} cases where baseline was correct but new model failed",
        ))

        # Gate 3: confidence calibration (simplified — check avg confidence vs accuracy)
        new_avg_conf = sum(r.new_proposal.confidence for r in labeled) / len(labeled)
        calibration_gap = abs(new_avg_conf - new_acc)
        assessment.gates.append(GateResult(
            gate_name="calibration_gap",
            passed=calibration_gap <= 0.10,
            value=round(calibration_gap, 4),
            threshold=0.10,
            detail=f"|avg_conf({new_avg_conf:.2%}) - accuracy({new_acc:.2%})| = {calibration_gap:.2%}",
        ))

        assessment.can_promote = all(g.passed for g in assessment.gates)
        if not assessment.can_promote:
            failed = [g.gate_name for g in assessment.gates if not g.passed]
            assessment.block_reason = f"gates failed: {', '.join(failed)}"

        return assessment


# ─────────────────────────────────────────
# Simulate a rollout lifecycle
# ─────────────────────────────────────────

LABELED_GROUND_TRUTH: dict[str, str] = {
    "t01": "4940", "t02": "4650", "t03": "4670", "t04": "4920",
    "t05": "6825", "t06": "4940", "t07": "4670", "t08": "4990",
}

TEST_TRANSACTIONS = [
    Transaction(id="t01", merchant="AWS EMEA",      amount=119.0,  description="EC2 instance",       market="DE"),
    Transaction(id="t02", merchant="Lieferando",    amount=47.80,  description="team lunch",          market="DE"),
    Transaction(id="t03", merchant="Uber",          amount=34.50,  description="airport transfer",    market="DE"),
    Transaction(id="t04", merchant="Telekom",       amount=49.99,  description="mobile contract",     market="DE"),
    Transaction(id="t05", merchant="Acme Consulting GmbH", amount=2500.0, description="advisory Q1", market="DE"),
    Transaction(id="t06", merchant="Hetzner",       amount=12.0,   description="vServer monthly",     market="DE"),
    Transaction(id="t07", merchant="Deutsche Bahn", amount=89.0,   description="Hamburg ICE",         market="DE"),
    Transaction(id="t08", merchant="Unknown AG",    amount=40.0,   description="misc",                market="DE"),
]


def run_shadow_stage(rng: random.Random) -> RolloutController:
    print("\n  ── Stage 0: SHADOW ────────────────────────────────────")
    print("  New model runs on 100% of traffic but results are NOT served.")
    print("  Purpose: collect comparison data before any traffic is split.\n")

    controller = RolloutController(stage=RolloutStage.SHADOW)
    for tx in TEST_TRANSACTIONS:
        result = controller.process(tx, rng)
        r = controller.records[-1]
        match = "✓" if r.baseline_proposal.account_code == r.new_proposal.account_code else "≠"
        print(f"  {match} {tx.id} baseline={r.baseline_proposal.account_code} "
              f"new={r.new_proposal.account_code}  served=baseline")

    for tx_id, truth in LABELED_GROUND_TRUTH.items():
        controller.record_ground_truth(tx_id, truth)

    return controller


def run_promotion_assessment(controller: RolloutController, target: RolloutStage) -> PromotionAssessment:
    assessment = controller.assess_promotion(target, min_samples=len(TEST_TRANSACTIONS))
    print(f"\n  ── Promotion gate: {controller.stage.value} → {target.value} ─────────────")
    print(f"  Labeled samples: {assessment.sample_count} (min required: {assessment.min_samples})\n")

    for gate in assessment.gates:
        icon = "✓" if gate.passed else "✗"
        print(f"  {icon} {gate.gate_name:<25} {gate.detail}")

    verdict = "PROMOTE" if assessment.can_promote else f"BLOCK ({assessment.block_reason})"
    verdict_icon = "→" if assessment.can_promote else "⛔"
    print(f"\n  {verdict_icon} Verdict: {verdict}")
    return assessment


if __name__ == "__main__":
    rng = random.Random(42)

    print("\n══ Shadow Mode & Gradual Rollout Demo ══")
    print("  Demonstrates: earn autonomy through data, not by default\n")
    print("  Maturity stages:")
    for stage, pct in STAGE_TRAFFIC_PCT.items():
        print(f"  {stage.value:<10} → {pct:.0%} traffic to new model")

    # Stage 0: Shadow
    shadow_controller = run_shadow_stage(rng)

    # Promotion assessment from Shadow → Canary
    assessment = run_promotion_assessment(shadow_controller, RolloutStage.CANARY)

    # Show what the regression looks like
    labeled = [r for r in shadow_controller.records if r.ground_truth]
    regressions = [
        r for r in labeled
        if r.baseline_proposal.account_code == r.ground_truth
        and r.new_proposal.account_code != r.ground_truth
    ]

    if regressions:
        print(f"\n  ── Regression detail ──────────────────────────────────")
        for r in regressions:
            tx = next(t for t in TEST_TRANSACTIONS if t.id == r.transaction_id)
            print(f"  tx={r.transaction_id} merchant='{tx.merchant}'")
            print(f"    baseline: {r.baseline_proposal.account_code} ✓ (correct)")
            print(f"    new:      {r.new_proposal.account_code} ✗ (wrong — {r.new_proposal.evidence})")
            print(f"    impact: auto-booking would book to 'miscellaneous' instead of 'professional fees'")

    print(f"\n  ── What happens next ──────────────────────────────────")
    if not assessment.can_promote:
        print(f"  1. File a regression ticket against the new model team:")
        print(f"     'consulting' keyword missing from v2 merchant patterns")
        print(f"  2. New model stays in SHADOW until regression is fixed and re-evaluated")
        print(f"  3. After fix: re-run shadow stage → assess → promote to CANARY (5%)")
        print(f"  4. Gate check at each stage before widening traffic")
    else:
        print(f"  1. Promote to CANARY: set traffic_pct = 0.05")
        print(f"  2. Monitor: accuracy delta, override rate, ECE at canary scale")
        print(f"  3. Gate check after 500 canary transactions before ramping")

    print(f"\n  ── Maturity ladder principle ───────────────────────────")
    print(f"  Stage   Traffic  Gate to advance")
    print(f"  shadow    0%     accuracy_delta ≥ 0, regressions = 0, calibration_gap ≤ 0.10")
    print(f"  canary    5%     same gates + 500 live transactions")
    print(f"  ramping  25%     same gates + override_rate < 2% sustained 7 days")
    print(f"  full    100%     same gates + ECE < 0.05 confirmed on full traffic")
    print(f"\n  Key: 'high shadow confidence' is NOT a gate. Data is the gate.")
    print(f"  Key: a single critical regression blocks promotion regardless of overall accuracy.")
