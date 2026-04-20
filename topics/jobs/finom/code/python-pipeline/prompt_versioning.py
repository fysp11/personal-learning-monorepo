"""
Prompt Versioning & Experiment Tracking — Production Pattern

Demonstrates the discipline required for iterating safely on prompts in production:

  1. Prompt registry: every prompt is versioned, immutable after deployment
  2. Experiment: a named comparison between two prompt versions on shared eval set
  3. Metrics: accuracy delta, ECE delta, token cost delta, latency delta
  4. Promotion gate: only promote if all gates pass (same gates as model rollout)
  5. Rollback: revert to last known-good prompt version in < 30 seconds

Why prompts need the same discipline as model weights:
  - A prompt change can degrade categorization accuracy as badly as a bad model update
  - "Just tweak the wording" ships without eval → silent accuracy regression
  - Prompts embed business rules (account codes, VAT thresholds) that must be auditable
  - Compliance teams ask: "what prompt was running when this transaction was booked?"

Run:
    python3 prompt_versioning.py
"""

import hashlib
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pipeline import Transaction, CategoryProposal, MERCHANT_PATTERNS


# ─────────────────────────────────────────
# Prompt registry
# ─────────────────────────────────────────

@dataclass
class PromptVersion:
    version: str            # semantic: "1.0.0", "1.1.0", "2.0.0"
    template: str           # the actual prompt text
    author: str
    created_at: float = field(default_factory=time.monotonic)
    deprecated: bool = False

    @property
    def content_hash(self) -> str:
        """SHA-256 of template — detects silent drift if someone edits in place."""
        return hashlib.sha256(self.template.encode()).hexdigest()[:12]


class PromptRegistry:
    """
    Immutable registry: once deployed, a prompt version cannot be edited.
    Audit requirement: every booking must reference the prompt version that produced it.
    """
    def __init__(self) -> None:
        self._versions: dict[str, PromptVersion] = {}
        self._active: Optional[str] = None

    def register(self, pv: PromptVersion) -> None:
        if pv.version in self._versions:
            raise ValueError(f"version {pv.version} already registered — create a new version")
        self._versions[pv.version] = pv

    def activate(self, version: str) -> None:
        if version not in self._versions:
            raise KeyError(f"version {version} not registered")
        self._active = version

    def get_active(self) -> PromptVersion:
        if not self._active:
            raise RuntimeError("no active prompt version")
        return self._versions[self._active]

    def get(self, version: str) -> PromptVersion:
        return self._versions[version]

    def list_versions(self) -> list[PromptVersion]:
        return sorted(self._versions.values(), key=lambda p: p.created_at)

    def rollback(self) -> PromptVersion:
        """Rollback to second-most-recent non-deprecated version."""
        candidates = [p for p in self.list_versions() if not p.deprecated]
        if len(candidates) < 2:
            raise RuntimeError("nothing to roll back to")
        previous = candidates[-2]
        self._active = previous.version
        return previous


# ─────────────────────────────────────────
# Mock categorizers using different prompt versions
# ─────────────────────────────────────────

def categorize_v1(tx: Transaction) -> CategoryProposal:
    """
    v1.0 prompt: straightforward keyword matching, conservative confidence.
    Accurate but misses some patterns (no consulting, no airline expansion).
    """
    merchant_lower = tx.merchant.lower()
    desc_lower = tx.description.lower()
    for keyword, (de_code, fr_code, conf, evidence) in MERCHANT_PATTERNS.items():
        if keyword in merchant_lower or keyword in desc_lower:
            code = de_code if tx.market == "DE" else fr_code
            return CategoryProposal(account_code=code, confidence=conf, evidence=f"[v1] {evidence}")
    return CategoryProposal(account_code="4990", confidence=0.30, evidence="[v1] no match")


def categorize_v2(tx: Transaction, rng: random.Random) -> CategoryProposal:
    """
    v2.0 prompt: expanded patterns + higher base confidence.
    Improvement: added "bahn", "easyjet", "ryanair" for travel.
    Regression: inflated confidence on unknown merchants (overconfident).
    """
    EXTRA_PATTERNS = {
        "bahn":    ("4670", "6251", 0.88, "train travel → business travel"),
        "easyjet": ("4670", "6251", 0.89, "airline → business travel"),
        "ryanair": ("4670", "6251", 0.88, "airline → business travel"),
    }
    merchant_lower = tx.merchant.lower()
    desc_lower = tx.description.lower()

    combined = {**MERCHANT_PATTERNS, **EXTRA_PATTERNS}
    for keyword, (de_code, fr_code, conf, evidence) in combined.items():
        if keyword in merchant_lower or keyword in desc_lower:
            code = de_code if tx.market == "DE" else fr_code
            # v2 regression: slight confidence inflation on known patterns
            inflated_conf = min(0.97, conf + rng.uniform(0.02, 0.08))
            return CategoryProposal(account_code=code, confidence=round(inflated_conf, 3),
                                   evidence=f"[v2] {evidence}")

    # v2 regression: unknown merchants get inflated confidence too (overconfident fallback)
    inflated_fallback = 0.45 + rng.uniform(0, 0.10)   # should be 0.30
    return CategoryProposal(account_code="4990", confidence=round(inflated_fallback, 3),
                           evidence="[v2] no match (overconfident fallback)")


# ─────────────────────────────────────────
# Experiment framework
# ─────────────────────────────────────────

class ExperimentStatus(Enum):
    RUNNING  = "running"
    COMPLETE = "complete"
    PROMOTED = "promoted"
    ROLLED_BACK = "rolled_back"


@dataclass
class ExperimentCase:
    tx: Transaction
    ground_truth: str
    control_proposal: CategoryProposal    # current production version
    treatment_proposal: CategoryProposal  # candidate new version


@dataclass
class ExperimentResult:
    name: str
    control_version: str
    treatment_version: str
    cases: list[ExperimentCase] = field(default_factory=list)
    status: ExperimentStatus = ExperimentStatus.RUNNING

    # Computed metrics
    control_accuracy: float = 0.0
    treatment_accuracy: float = 0.0
    accuracy_delta: float = 0.0
    control_avg_conf: float = 0.0
    treatment_avg_conf: float = 0.0
    control_ece: float = 0.0
    treatment_ece: float = 0.0
    ece_delta: float = 0.0
    regression_count: int = 0
    new_coverage_count: int = 0   # cases treatment got right but control missed

    def compute_metrics(self) -> None:
        n = len(self.cases)
        if n == 0:
            return

        ctrl_correct  = sum(1 for c in self.cases if c.control_proposal.account_code   == c.ground_truth)
        treat_correct = sum(1 for c in self.cases if c.treatment_proposal.account_code == c.ground_truth)

        self.control_accuracy   = ctrl_correct  / n
        self.treatment_accuracy = treat_correct / n
        self.accuracy_delta = self.treatment_accuracy - self.control_accuracy

        self.control_avg_conf   = sum(c.control_proposal.confidence   for c in self.cases) / n
        self.treatment_avg_conf = sum(c.treatment_proposal.confidence for c in self.cases) / n

        # Simplified ECE: |avg_confidence - accuracy|
        self.control_ece   = abs(self.control_avg_conf   - self.control_accuracy)
        self.treatment_ece = abs(self.treatment_avg_conf - self.treatment_accuracy)
        self.ece_delta = self.treatment_ece - self.control_ece

        # Regressions: control correct, treatment wrong
        self.regression_count = sum(
            1 for c in self.cases
            if c.control_proposal.account_code == c.ground_truth
            and c.treatment_proposal.account_code != c.ground_truth
        )
        # New coverage: treatment correct, control wrong
        self.new_coverage_count = sum(
            1 for c in self.cases
            if c.control_proposal.account_code != c.ground_truth
            and c.treatment_proposal.account_code == c.ground_truth
        )

    def promotion_gates(self) -> list[tuple[str, bool, str]]:
        """Returns (gate_name, passed, detail) for each promotion gate."""
        return [
            ("accuracy_delta ≥ 0",      self.accuracy_delta >= 0,
             f"treatment={self.treatment_accuracy:.0%} vs control={self.control_accuracy:.0%} (delta={self.accuracy_delta:+.0%})"),
            ("regressions = 0",          self.regression_count == 0,
             f"{self.regression_count} regression(s) — control correct but treatment wrong"),
            ("ECE delta ≤ +0.05",        self.ece_delta <= 0.05,
             f"control ECE={self.control_ece:.3f}, treatment ECE={self.treatment_ece:.3f} (delta={self.ece_delta:+.3f})"),
        ]

    def can_promote(self) -> bool:
        return all(passed for _, passed, _ in self.promotion_gates())


# ─────────────────────────────────────────
# Eval transactions with ground truth
# ─────────────────────────────────────────

EVAL_CASES: list[tuple[Transaction, str]] = [
    (Transaction(id="e01", merchant="AWS EMEA",        amount=119.0, description="EC2",            market="DE"), "4940"),
    (Transaction(id="e02", merchant="Lieferando",      amount=47.80, description="team lunch",     market="DE"), "4650"),
    (Transaction(id="e03", merchant="Uber",            amount=34.50, description="airport pickup", market="DE"), "4670"),
    (Transaction(id="e04", merchant="Deutsche Bahn",   amount=89.0,  description="Hamburg ICE",    market="DE"), "4670"),  # new in v2
    (Transaction(id="e05", merchant="Ryanair",         amount=65.0,  description="Berlin conference",market="DE"), "4670"),  # new in v2
    (Transaction(id="e06", merchant="Acme Consulting", amount=2500.0,description="advisory Q1",   market="DE"), "6825"),
    (Transaction(id="e07", merchant="Unknown GmbH",    amount=40.0,  description="misc",           market="DE"), "4990"),
    (Transaction(id="e08", merchant="Microsoft",       amount=12.50, description="Office 365",     market="DE"), "4940"),
]


if __name__ == "__main__":
    rng = random.Random(42)

    print("\n══ Prompt Versioning & Experiment Tracking Demo ══\n")

    # Set up registry
    registry = PromptRegistry()
    v1 = PromptVersion(
        version="1.0.0",
        template="Categorize the transaction using SKR03. Use account 4940 for IT, 4650 for meals, 4670 for travel...",
        author="ai-team",
    )
    v2 = PromptVersion(
        version="2.0.0",
        template="Categorize transaction using SKR03. Expanded patterns: Deutsche Bahn/Ryanair/EasyJet → 4670 travel...",
        author="ai-team",
    )
    registry.register(v1)
    registry.register(v2)
    registry.activate("1.0.0")

    print("  ── Prompt registry ──────────────────────────────────")
    for pv in registry.list_versions():
        active_flag = " ← ACTIVE" if registry.get_active().version == pv.version else ""
        print(f"  v{pv.version}  hash={pv.content_hash}  author={pv.author}{active_flag}")

    # Run experiment: v1 (control) vs v2 (treatment)
    experiment = ExperimentResult(
        name="travel-pattern-expansion",
        control_version="1.0.0",
        treatment_version="2.0.0",
    )

    print(f"\n  ── Experiment: {experiment.name} ──────────────────────")
    print(f"  Control:   v{experiment.control_version}")
    print(f"  Treatment: v{experiment.treatment_version}")
    print(f"  Eval set:  {len(EVAL_CASES)} labeled transactions\n")

    for tx, truth in EVAL_CASES:
        ctrl  = categorize_v1(tx)
        treat = categorize_v2(tx, rng)
        experiment.cases.append(ExperimentCase(
            tx=tx, ground_truth=truth,
            control_proposal=ctrl,
            treatment_proposal=treat,
        ))

    experiment.compute_metrics()

    print(f"  {'ID':<5} {'Merchant':<22} {'Truth':<6} {'v1':<6} {'v2':<6} {'v1 conf':<9} {'v2 conf':<9} {'Result'}")
    for c in experiment.cases:
        ctrl_ok  = c.control_proposal.account_code   == c.ground_truth
        treat_ok = c.treatment_proposal.account_code == c.ground_truth
        if ctrl_ok and treat_ok:
            result = "both ✓"
        elif not ctrl_ok and treat_ok:
            result = "v2 gains +"
        elif ctrl_ok and not treat_ok:
            result = "⚠ REGRESSION"
        else:
            result = "both ✗"
        print(f"  {c.tx.id:<5} {c.tx.merchant:<22} {c.ground_truth:<6} "
              f"{c.control_proposal.account_code:<6} {c.treatment_proposal.account_code:<6} "
              f"{c.control_proposal.confidence:.2f}     {c.treatment_proposal.confidence:.2f}     {result}")

    print(f"\n  ── Metrics ──────────────────────────────────────────")
    print(f"  accuracy:  control={experiment.control_accuracy:.0%}  treatment={experiment.treatment_accuracy:.0%}  delta={experiment.accuracy_delta:+.0%}")
    print(f"  ECE:       control={experiment.control_ece:.3f}      treatment={experiment.treatment_ece:.3f}      delta={experiment.ece_delta:+.3f}")
    print(f"  regressions:    {experiment.regression_count}")
    print(f"  new coverage:   {experiment.new_coverage_count}  (cases v2 gets right that v1 misses)")

    print(f"\n  ── Promotion gates ──────────────────────────────────")
    for gate_name, passed, detail in experiment.promotion_gates():
        icon = "✓" if passed else "✗"
        print(f"  {icon} {gate_name:<25} {detail}")

    verdict = "PROMOTE v2.0.0" if experiment.can_promote() else "BLOCK — fix issues first"
    icon = "→" if experiment.can_promote() else "⛔"
    print(f"\n  {icon} Verdict: {verdict}")

    if not experiment.can_promote():
        print(f"\n  ── What needs to change in v2 ───────────────────────")
        print(f"  1. ECE delta is too high: v2 inflates confidence on fallback cases")
        print(f"     Fix: cap fallback confidence at 0.30 (same as v1)")
        print(f"  2. Re-run experiment after fix → expect ECE delta ≤ 0")
        print(f"  3. If new coverage improves without regression: promote to canary")

    print(f"\n  ── Rollback demo ─────────────────────────────────────")
    print(f"  Scenario: v2.0.0 deployed to canary, ECE anomaly detected after 50 txns")
    print(f"  Action: emergency rollback")
    rolled_back = registry.rollback()
    print(f"  Rolled back to: v{rolled_back.version}  (takes effect in < 30s via config push)")
    print(f"  Active prompt:  v{registry.get_active().version}")
    print(f"  Audit log:      v2.0.0 was active for 47 transactions [08:23:01 – 08:31:44]")

    print(f"\n  ── Production patterns ───────────────────────────────")
    print(f"  content_hash:   detect silent prompt drift (someone edited in place)")
    print(f"  immutable after deploy: no edits, only new versions")
    print(f"  audit trail:    every booking references prompt version + content hash")
    print(f"  same gates as model rollout: accuracy, regressions, ECE")
    print(f"  rollback SLA:   < 30 seconds (config push, not code deploy)")
