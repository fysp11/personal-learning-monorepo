"""
Feedback Loop — Learning From Human Corrections

Demonstrates how user decisions on PROPOSAL_SENT transactions feed back into:
  1. Override rate tracking per merchant pattern
  2. Custom merchant pattern updates (business-specific learning)
  3. RAG retrieval store updates (high-quality ground-truth examples)
  4. Threshold demotion: merchants with override_rate > 5% demoted from AUTO to PROPOSAL
  5. Threshold promotion candidates: merchants with confirm_rate > 98% for 30 days

This is the "earn autonomy through data" principle applied to the feedback direction:
  - Good feedback → wider thresholds for this merchant
  - Bad feedback → narrower thresholds or demoted to PROPOSAL
  - New merchant manually categorized → added to retrieval store as ground truth

Run:
    python3 feedback_loop.py
"""

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pipeline import Transaction, CategoryProposal, RoutingStatus, categorize, route, calculate_vat


# ─────────────────────────────────────────
# Feedback signal types
# ─────────────────────────────────────────

class FeedbackSignal(Enum):
    CONFIRM   = "confirm"    # user accepted the proposal exactly as suggested
    OVERRIDE  = "override"   # user changed to a different account
    MANUAL    = "manual"     # user manually categorized a REJECTED transaction


@dataclass
class OverrideReason(Enum):
    WRONG_ACCOUNT  = "wrong_account"
    WRONG_VAT_RATE = "wrong_vat_rate"
    WRONG_CATEGORY = "wrong_category"
    OTHER          = "other"


@dataclass
class FeedbackRecord:
    transaction_id: str
    merchant: str
    proposed_account: str
    confirmed_account: str
    signal: FeedbackSignal
    override_reason: Optional[str]   # populated when signal = OVERRIDE
    timestamp: float = field(default_factory=time.monotonic)


# ─────────────────────────────────────────
# Merchant feedback tracker
# Computes per-merchant override rate and promote/demote signals
# ─────────────────────────────────────────

@dataclass
class MerchantFeedbackStats:
    merchant_key: str
    confirms: int = 0
    overrides: int = 0

    @property
    def total(self) -> int:
        return self.confirms + self.overrides

    @property
    def override_rate(self) -> float:
        return self.overrides / self.total if self.total > 0 else 0.0

    @property
    def confirm_rate(self) -> float:
        return self.confirms / self.total if self.total > 0 else 0.0

    def demotion_signal(self) -> bool:
        """Merchant should be demoted from AUTO_BOOK to PROPOSAL if override rate > 5%."""
        return self.total >= 10 and self.override_rate > 0.05

    def promotion_candidate(self) -> bool:
        """Merchant is candidate for threshold widening if confirm rate > 98% over sufficient samples."""
        return self.total >= 30 and self.confirm_rate >= 0.98


class FeedbackStore:
    """
    Tracks feedback signals and drives merchant-level threshold adjustments.
    In production: backed by a database with time-windowing (30-day rolling).
    """
    def __init__(self) -> None:
        self._records: list[FeedbackRecord] = []
        self._stats: dict[str, MerchantFeedbackStats] = {}
        self._custom_patterns: dict[str, tuple[str, str]] = {}   # merchant → (account, evidence)
        self._rag_additions: list[dict] = []   # new ground-truth examples for retrieval store

    def record(self, feedback: FeedbackRecord) -> None:
        self._records.append(feedback)

        # Update per-merchant stats
        key = feedback.merchant.lower()
        if key not in self._stats:
            self._stats[key] = MerchantFeedbackStats(merchant_key=key)

        if feedback.signal == FeedbackSignal.CONFIRM:
            self._stats[key].confirms += 1
        elif feedback.signal == FeedbackSignal.OVERRIDE:
            self._stats[key].overrides += 1

        # Manual categorization from REJECTED queue → add to custom patterns + RAG store
        if feedback.signal == FeedbackSignal.MANUAL:
            self._custom_patterns[key] = (
                feedback.confirmed_account,
                f"manual categorization by user → {feedback.confirmed_account}",
            )
            self._rag_additions.append({
                "merchant": feedback.merchant,
                "account_code": feedback.confirmed_account,
                "human_verified": True,
                "source": "manual_correction",
            })

    def get_stats(self, merchant: str) -> Optional[MerchantFeedbackStats]:
        return self._stats.get(merchant.lower())

    def demotions_needed(self) -> list[str]:
        """Merchants whose override rate justifies demotion from AUTO_BOOK to PROPOSAL."""
        return [k for k, s in self._stats.items() if s.demotion_signal()]

    def promotion_candidates(self) -> list[str]:
        """Merchants with sufficient confirm data to consider widening thresholds."""
        return [k for k, s in self._stats.items() if s.promotion_candidate()]

    def custom_patterns_learned(self) -> dict:
        return dict(self._custom_patterns)

    def rag_additions(self) -> list[dict]:
        return list(self._rag_additions)

    def summary(self) -> dict:
        return {
            "total_feedback_records": len(self._records),
            "merchants_tracked": len(self._stats),
            "custom_patterns_learned": len(self._custom_patterns),
            "rag_additions": len(self._rag_additions),
            "merchants_needing_demotion": self.demotions_needed(),
            "promotion_candidates": self.promotion_candidates(),
        }


# ─────────────────────────────────────────
# Simulate user decisions
# ─────────────────────────────────────────

def simulate_user_decision(
    tx: Transaction,
    proposal: CategoryProposal,
    rng: random.Random,
    override_probability: float = 0.08,
) -> FeedbackRecord:
    """
    Simulate a user deciding on a proposal.
    override_probability: likelihood the user disagrees with the model.
    """
    if rng.random() < override_probability:
        # User overrides — pick a different account
        alternatives = ["4940", "4930", "6825", "4650", "4670", "4990"]
        correction = rng.choice([a for a in alternatives if a != proposal.account_code])
        return FeedbackRecord(
            transaction_id=tx.id,
            merchant=tx.merchant,
            proposed_account=proposal.account_code,
            confirmed_account=correction,
            signal=FeedbackSignal.OVERRIDE,
            override_reason=OverrideReason.WRONG_ACCOUNT.value,
        )
    else:
        return FeedbackRecord(
            transaction_id=tx.id,
            merchant=tx.merchant,
            proposed_account=proposal.account_code,
            confirmed_account=proposal.account_code,
            signal=FeedbackSignal.CONFIRM,
            override_reason=None,
        )


# ─────────────────────────────────────────
# Simulate a degraded merchant (high override rate)
# ─────────────────────────────────────────

def simulate_degraded_merchant(
    store: FeedbackStore,
    merchant_name: str,
    n: int,
    rng: random.Random,
) -> None:
    """
    Simulate a merchant where the model's account mapping has become wrong —
    e.g., company changed expense category policy, but the model still uses old mapping.
    This merchant will generate a high override rate and trigger demotion.
    """
    for i in range(n):
        tx = Transaction(
            id=f"deg-{merchant_name}-{i:03d}",
            merchant=merchant_name,
            amount=rng.uniform(50, 200),
            description="monthly subscription",
            market="DE",
        )
        proposal = categorize(tx)
        record = simulate_user_decision(tx, proposal, rng, override_probability=0.25)
        store.record(record)


# ─────────────────────────────────────────
# Main demo
# ─────────────────────────────────────────

DEMO_TRANSACTIONS = [
    Transaction("fb01", "AWS EMEA",      119.0,  "EC2 monthly",   market="DE"),
    Transaction("fb02", "AWS EMEA",       95.0,  "S3 storage",    market="DE"),
    Transaction("fb03", "Lieferando",     47.80, "team lunch",    market="DE"),
    Transaction("fb04", "Lieferando",     52.00, "sprint review", market="DE"),
    Transaction("fb05", "Lieferando",     38.50, "offsite lunch", market="DE"),
    Transaction("fb06", "Uber",           34.50, "airport",       market="DE"),
    Transaction("fb07", "Uber",           28.00, "client pickup", market="DE"),
]

MANUAL_CATEGORIZATIONS = [
    ("Unknown GmbH",  "4990", "Miscellaneous — no matching pattern"),
    ("Toolcraft GmbH","4940", "Software tooling → IT costs"),
]


if __name__ == "__main__":
    rng = random.Random(42)
    store = FeedbackStore()

    print("\n══ Feedback Loop Demo ══\n")
    print("  Simulating 7 proposal confirmations + deliberate overrides")
    print("  + 1 degraded merchant (25% override rate)\n")

    # Process normal transactions
    print("  ── Normal merchants ──────────────────────────────────────")
    print(f"  {'ID':<6} {'Merchant':<20} {'Proposed':<8} {'Confirmed':<10} {'Signal'}")
    for tx in DEMO_TRANSACTIONS:
        proposal = categorize(tx)
        feedback = simulate_user_decision(tx, proposal, rng, override_probability=0.05)
        store.record(feedback)
        icon = "✓" if feedback.signal == FeedbackSignal.CONFIRM else "≠"
        print(f"  {icon} {tx.id:<6} {tx.merchant:<20} {feedback.proposed_account:<8} "
              f"{feedback.confirmed_account:<10} {feedback.signal.value}")

    # Simulate degraded merchant (model has wrong mapping for this merchant)
    print(f"\n  ── Degraded merchant: Microsoft (25% override rate) ─────")
    simulate_degraded_merchant(store, "Microsoft", n=20, rng=rng)
    ms_stats = store.get_stats("microsoft")
    print(f"  After 20 transactions: overrides={ms_stats.overrides} confirms={ms_stats.confirms} "
          f"override_rate={ms_stats.override_rate:.0%}")

    # Manual categorizations from REJECTED queue
    print(f"\n  ── Manual categorizations (from REJECTED queue) ─────────")
    for merchant, account, evidence in MANUAL_CATEGORIZATIONS:
        feedback = FeedbackRecord(
            transaction_id=f"manual-{merchant[:8]}",
            merchant=merchant,
            proposed_account="4990",
            confirmed_account=account,
            signal=FeedbackSignal.MANUAL,
            override_reason=None,
        )
        store.record(feedback)
        print(f"  ✎ {merchant:<20} → {account}  (added to retrieval store)")

    # Summary and signals
    summary = store.summary()
    print(f"\n  ── Feedback store summary ───────────────────────────────")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Per-merchant breakdown
    print(f"\n  ── Per-merchant stats ────────────────────────────────────")
    print(f"  {'Merchant':<22} {'Total':<8} {'Override%':<12} {'Status'}")
    for merchant, stats in store._stats.items():
        if stats.demotion_signal():
            status = "⚠ DEMOTION NEEDED"
        elif stats.promotion_candidate():
            status = "↑ promotion candidate"
        else:
            status = "  ok"
        print(f"  {merchant:<22} {stats.total:<8} {stats.override_rate:.0%}         {status}")

    # Demotions
    demotions = store.demotions_needed()
    if demotions:
        print(f"\n  ── Required actions ─────────────────────────────────────")
        for merchant in demotions:
            s = store.get_stats(merchant)
            print(f"  ⚠ Demote '{merchant}' from AUTO_BOOK to PROPOSAL_SENT")
            print(f"    Reason: {s.overrides}/{s.total} overrides ({s.override_rate:.0%} > 5% threshold)")
            print(f"    Action: flag for pattern review + shadow mode for this merchant")

    # Custom patterns learned
    custom = store.custom_patterns_learned()
    if custom:
        print(f"\n  ── Custom patterns learned from manual categorizations ──")
        for merchant, (account, evidence) in custom.items():
            print(f"  '{merchant}' → {account}  ({evidence})")
            print(f"  Will appear as PROPOSAL_SENT (not REJECTED) on next occurrence")

    # RAG additions
    rag = store.rag_additions()
    if rag:
        print(f"\n  ── RAG retrieval store additions ────────────────────────")
        for entry in rag:
            print(f"  + {entry['merchant']:<20} → {entry['account_code']}  "
                  f"human_verified={entry['human_verified']} source={entry['source']}")

    print(f"\n  ── Learning loop principle ─────────────────────────────")
    print(f"  The pipeline gets more accurate for each specific business over time")
    print(f"  Override rate per merchant → demotion signal (narrow thresholds)")
    print(f"  Confirm rate per merchant  → promotion candidate (widen thresholds)")
    print(f"  Manual categorizations     → ground truth in retrieval store")
    print(f"  The model doesn't need to be retrained — retrieval learns faster")
