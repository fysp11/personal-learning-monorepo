"""
Scenario B — Clean Refactored Pipeline

The refactored version of bad_agent.py.
Every architectural sin identified in REFACTOR_NOTES.md is fixed here.

Key changes:
  - Typed contracts (dataclasses) instead of plain dicts
  - AI stage isolated behind a clean interface with real confidence
  - VAT calculation extracted as a pure deterministic function
  - Compliance check (reverse charge) made explicit and logged
  - Three-way confidence router — no "warn and continue"
  - All terminal states represented in RoutingStatus
  - Per-stage trace for auditability

Run:
    python3 good_pipeline.py
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ─────────────────────────────────────────
# Typed contracts
# ─────────────────────────────────────────

class RoutingStatus(str, Enum):
    AUTO_BOOKED = "auto_booked"
    PROPOSAL_SENT = "proposal_sent"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"


@dataclass
class CategoryProposal:
    account_code: str
    confidence: float   # [0.0, 1.0] — from model output, not random
    evidence: str


@dataclass
class VatCalculation:
    rate: float
    amount: float
    net_amount: float
    mechanism: str   # "standard" | "reduced" | "reverse_charge" | "exempt"


@dataclass
class BookingEntry:
    debit_account: str
    credit_account: str
    net_amount: float
    vat_amount: float
    vat_account: str


@dataclass
class StageTrace:
    stage: str
    duration_ms: int
    decision: str


@dataclass
class WorkflowOutcome:
    transaction_id: str
    status: RoutingStatus
    category: Optional[CategoryProposal] = None
    vat: Optional[VatCalculation] = None
    booking: Optional[BookingEntry] = None
    trace: list[StageTrace] = field(default_factory=list)


# ─────────────────────────────────────────
# Market config — policy as data, not code branches
# ─────────────────────────────────────────

MARKET_CONFIG = {
    "DE": {
        "standard_vat": 0.19,
        "reduced_vat": 0.07,
        "bank_account": "1200",
        "vat_account": "1576",
        "reduced_accounts": {"4650", "4670"},
    },
}


# ─────────────────────────────────────────
# Stage 1: Categorization — AI stage
# (mock — in production: async LLM call with structured output)
# ─────────────────────────────────────────

MERCHANT_PATTERNS = {
    "aws":        ("4940", 0.95, "cloud infrastructure → IT costs"),
    "amazon":     ("4940", 0.88, "amazon.de → IT or office supplies"),
    "uber":       ("4670", 0.90, "ride service → travel costs"),
    "lieferando": ("4650", 0.82, "food delivery → meal expense"),
    "consult":    ("6825", 0.85, "consulting service → professional fees"),
    "notary":     ("6825", 0.91, "legal/notary → professional fees"),
}


def categorize(tx_id: str, merchant: str, description: str) -> CategoryProposal:
    """
    AI stage: returns a category proposal WITH calibrated confidence.
    The confidence comes from the model (here: keyword-matching proxy).
    It does NOT compute VAT — that is a separate deterministic stage.
    """
    for keyword, (code, conf, evidence) in MERCHANT_PATTERNS.items():
        if keyword in merchant.lower() or keyword in description.lower():
            return CategoryProposal(account_code=code, confidence=conf, evidence=evidence)

    return CategoryProposal(
        account_code="4990",
        confidence=0.28,
        evidence="no pattern match — manual categorization required",
    )


# ─────────────────────────────────────────
# Stage 2: Compliance gate — before any routing
# Reverse charge is a compliance decision, not a confidence decision.
# Always force REQUIRES_REVIEW for B2B intra-EU — log the override explicitly.
# ─────────────────────────────────────────

def apply_compliance_override(
    category: CategoryProposal,
    is_b2b: bool,
    trace: list[StageTrace],
) -> Optional[RoutingStatus]:
    """
    Returns a forced terminal state if a compliance rule applies,
    or None if normal confidence routing should proceed.
    """
    if is_b2b:
        trace.append(StageTrace(
            stage="compliance",
            duration_ms=0,
            decision="reverse_charge_override: is_b2b=True → REQUIRES_REVIEW (§13b UStG)",
        ))
        return RoutingStatus.REQUIRES_REVIEW
    return None


# ─────────────────────────────────────────
# Stage 3: VAT calculation — pure deterministic function
# Tax law is not ambiguous. This is never AI.
# ─────────────────────────────────────────

def calculate_vat(
    category: CategoryProposal,
    amount: float,
    is_b2b: bool,
    market: str = "DE",
) -> VatCalculation:
    if is_b2b:
        return VatCalculation(rate=0.0, amount=0.0, net_amount=amount, mechanism="reverse_charge")

    config = MARKET_CONFIG.get(market, MARKET_CONFIG["DE"])
    if category.account_code in config["reduced_accounts"]:
        rate, mechanism = config["reduced_vat"], "reduced"
    else:
        rate, mechanism = config["standard_vat"], "standard"

    vat = round(amount * rate / (1 + rate), 2)
    return VatCalculation(rate=rate, amount=vat, net_amount=round(amount - vat, 2), mechanism=mechanism)


# ─────────────────────────────────────────
# Stage 4: Confidence router — three terminal states, no "warn and continue"
# Thresholds from calibration data. Widen only when ECE < 0.05.
# ─────────────────────────────────────────

AUTO_BOOK_THRESHOLD = 0.85
PROPOSAL_THRESHOLD = 0.55


def route(category: CategoryProposal) -> RoutingStatus:
    """
    Every transaction reaches exactly one of four terminal states.
    No path exists that warns and continues — that is not a terminal state.
    """
    if category.confidence >= AUTO_BOOK_THRESHOLD:
        return RoutingStatus.AUTO_BOOKED
    if category.confidence >= PROPOSAL_THRESHOLD:
        return RoutingStatus.PROPOSAL_SENT
    return RoutingStatus.REJECTED


# ─────────────────────────────────────────
# Stage 5: Booking — only executes on AUTO_BOOKED
# ─────────────────────────────────────────

def create_booking(
    category: CategoryProposal,
    vat: VatCalculation,
    market: str = "DE",
) -> BookingEntry:
    config = MARKET_CONFIG.get(market, MARKET_CONFIG["DE"])
    return BookingEntry(
        debit_account=category.account_code,
        credit_account=config["bank_account"],
        net_amount=vat.net_amount,
        vat_amount=vat.amount,
        vat_account=config["vat_account"],
    )


# ─────────────────────────────────────────
# Orchestrator — chains stages, builds trace
# ─────────────────────────────────────────

def process_transaction(
    tx_id: str,
    merchant: str,
    amount: float,
    description: str,
    is_b2b: bool = False,
    market: str = "DE",
) -> WorkflowOutcome:
    trace: list[StageTrace] = []

    # Stage 1: Categorization (AI)
    t0 = time.monotonic()
    category = categorize(tx_id, merchant, description)
    trace.append(StageTrace(
        stage="categorize",
        duration_ms=round((time.monotonic() - t0) * 1000),
        decision=f"code={category.account_code} conf={category.confidence:.2f}",
    ))

    # Stage 2: Compliance override (before confidence routing)
    forced_status = apply_compliance_override(category, is_b2b, trace)

    # Stage 3: VAT (deterministic)
    t1 = time.monotonic()
    vat = calculate_vat(category, amount, is_b2b, market)
    trace.append(StageTrace(
        stage="vat",
        duration_ms=round((time.monotonic() - t1) * 1000),
        decision=f"mechanism={vat.mechanism} rate={vat.rate:.0%} vat=€{vat.amount}",
    ))

    # Stage 4: Routing (deterministic — compliance override takes priority)
    status = forced_status if forced_status else route(category)
    trace.append(StageTrace(
        stage="route",
        duration_ms=0,
        decision=f"status={status} (forced={forced_status is not None})",
    ))

    # Stage 5: Booking (only for auto-booked)
    booking = None
    if status == RoutingStatus.AUTO_BOOKED:
        booking = create_booking(category, vat, market)

    return WorkflowOutcome(
        transaction_id=tx_id,
        status=status,
        category=category,
        vat=vat,
        booking=booking,
        trace=trace,
    )


# ─────────────────────────────────────────
# Test cases — run to verify
# ─────────────────────────────────────────

if __name__ == "__main__":
    test_cases = [
        dict(tx_id="t1", merchant="AWS", amount=119.0, description="EC2 instance"),
        dict(tx_id="t2", merchant="Lieferando", amount=35.70, description="team lunch"),
        dict(tx_id="t3", merchant="Acme Consulting", amount=5000.0, description="advisory", is_b2b=True),
        dict(tx_id="t4", merchant="Unknown Corp", amount=299.0, description="mystery charge"),
    ]

    icons = {
        RoutingStatus.AUTO_BOOKED: "✓",
        RoutingStatus.PROPOSAL_SENT: "→",
        RoutingStatus.REQUIRES_REVIEW: "⚠",
        RoutingStatus.REJECTED: "✗",
    }

    print("\n══ Scenario B — Clean Pipeline (compare to bad_agent.py) ══\n")
    for tc in test_cases:
        outcome = process_transaction(**tc)
        icon = icons[outcome.status]
        print(f"  {icon} [{outcome.transaction_id}] {tc['merchant']} → {outcome.status}")
        if outcome.category:
            print(f"     category: {outcome.category.account_code} | conf: {outcome.category.confidence:.0%}")
        if outcome.vat:
            print(f"     VAT: {outcome.vat.mechanism} {outcome.vat.rate:.0%} = €{outcome.vat.amount:.2f}")
        if outcome.booking:
            print(f"     booking: DR {outcome.booking.debit_account} / CR {outcome.booking.credit_account}")
        trace_summary = " → ".join(f"{t.stage}({t.duration_ms}ms)" for t in outcome.trace)
        print(f"     trace: {trace_summary}\n")
