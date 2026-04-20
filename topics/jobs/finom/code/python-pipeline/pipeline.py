"""
Transaction Categorization Pipeline — Python Reference Implementation
Built for: AI Engineering live coding rounds
Purpose: Canonical Python version of the multi-stage fintech AI pipeline

Architecture:
    1. Feature extraction / categorization (AI stage — mock with keyword matching)
    2. VAT calculation (deterministic — policy as code)
    3. Confidence routing (deterministic — threshold from calibration)
    4. Booking entry (deterministic — double-entry math)
    5. Orchestrator with per-stage trace

Run:
    python pipeline.py          # runs 6 test cases
    python pipeline.py --async  # runs async batch version
"""

import time
import asyncio
import argparse
from enum import Enum
from typing import Optional
from dataclasses import dataclass, field


# ─────────────────────────────────────────
# Type contracts
# ─────────────────────────────────────────

class RoutingStatus(str, Enum):
    AUTO_BOOKED = "auto_booked"
    PROPOSAL_SENT = "proposal_sent"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"


@dataclass
class Transaction:
    id: str
    merchant: str
    amount: float  # gross amount including VAT
    description: str
    is_b2b: bool = False
    market: str = "DE"


@dataclass
class CategoryProposal:
    account_code: str  # SKR03 for DE, PCG for FR
    confidence: float   # [0, 1] — must be calibrated (ECE < 0.05)
    evidence: str       # what justified this categorization


@dataclass
class VatCalculation:
    rate: float         # e.g. 0.19 for standard DE VAT
    amount: float       # VAT portion in euros
    net_amount: float   # gross - VAT
    mechanism: str      # "standard" | "reduced" | "reverse_charge" | "exempt"


@dataclass
class BookingEntry:
    debit_account: str   # expense account (e.g. "4940")
    credit_account: str  # bank account (e.g. "1200")
    net_amount: float
    vat_amount: float
    vat_account: str     # "1576" for Vorsteuer in DE


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
# Market configuration (policy as data)
# ─────────────────────────────────────────

MARKET_CONFIG = {
    "DE": {
        "standard_vat": 0.19,
        "reduced_vat": 0.07,
        "chart": "SKR03",
        "bank_account": "1200",
        "vat_account": "1576",   # Vorsteuer
        "reduced_accounts": {"4650", "4670"},  # food, travel
    },
    "FR": {
        "standard_vat": 0.20,
        "reduced_vat": 0.10,     # main reduced; also 5.5% and 2.1% exist
        "chart": "PCG",
        "bank_account": "512",
        "vat_account": "44566",  # TVA déductible
        "reduced_accounts": {"6251", "6252"},  # travel, subsistence
    },
}


# ─────────────────────────────────────────
# Stage 1: Categorization (AI stage — mock)
# ─────────────────────────────────────────

# In production: replace with LLM call + structured output + retrieval-augmented history
# Mock preserves the contract: returns CategoryProposal with a calibrated confidence score
MERCHANT_PATTERNS: dict[str, tuple[str, str, float, str]] = {
    # keyword: (skr03_code, pcg_code, confidence, evidence_template)
    "aws":        ("4940", "6156", 0.95, "cloud infrastructure → IT operating costs"),
    "amazon":     ("4940", "6156", 0.88, "amazon.de → likely IT or office supplies"),
    "uber":       ("4670", "6251", 0.90, "ride service → travel costs"),
    "lufthansa":  ("4670", "6251", 0.93, "airline → business travel"),
    "lieferando": ("4650", "6256", 0.82, "food delivery → meal expense (reduced VAT)"),
    "notary":     ("6825", "6226", 0.91, "legal service → professional fees"),
    "rechtsanw":  ("6825", "6226", 0.89, "attorney/lawyer → professional fees"),
    "consult":    ("6825", "6226", 0.85, "consulting service → professional fees"),
    "softwar":    ("4940", "6156", 0.87, "software license → IT costs"),
    "office":     ("4930", "6064", 0.79, "office supplies or microsoft → office costs"),
}


def categorize(tx: Transaction) -> CategoryProposal:
    """
    AI stage: merchant → account code + calibrated confidence.
    Keyword matching is the mock. In production: LLM with structured output.
    """
    merchant_lower = tx.merchant.lower()
    description_lower = tx.description.lower()

    for keyword, (de_code, fr_code, conf, evidence) in MERCHANT_PATTERNS.items():
        if keyword in merchant_lower or keyword in description_lower:
            code = de_code if tx.market == "DE" else fr_code
            return CategoryProposal(
                account_code=code,
                confidence=conf,
                evidence=evidence,
            )

    # No match — return low confidence, send to human review
    fallback_code = "4990" if tx.market == "DE" else "6288"
    return CategoryProposal(
        account_code=fallback_code,
        confidence=0.30,
        evidence="no pattern match — requires manual categorization",
    )


# ─────────────────────────────────────────
# Stage 2: VAT calculation (deterministic)
# ─────────────────────────────────────────

def calculate_vat(category: CategoryProposal, tx: Transaction) -> VatCalculation:
    """
    Deterministic stage: tax law is not a prediction.
    Wrong VAT rate = Berichtigte Voranmeldung (amended filing) + potential penalty.
    """
    config = MARKET_CONFIG.get(tx.market, MARKET_CONFIG["DE"])

    # Reverse charge: §13b UStG (DE) — B2B intra-EU services
    # The buyer self-assesses VAT; no deductible input tax here
    if tx.is_b2b:
        return VatCalculation(
            rate=0.0,
            amount=0.0,
            net_amount=tx.amount,
            mechanism="reverse_charge",
        )

    # Reduced rate applies to food and travel in most EU markets
    if category.account_code in config["reduced_accounts"]:
        rate = config["reduced_vat"]
        mechanism = "reduced"
    else:
        rate = config["standard_vat"]
        mechanism = "standard"

    vat_amount = round(tx.amount * rate / (1 + rate), 2)
    net_amount = round(tx.amount - vat_amount, 2)

    return VatCalculation(
        rate=rate,
        amount=vat_amount,
        net_amount=net_amount,
        mechanism=mechanism,
    )


# ─────────────────────────────────────────
# Stage 3: Confidence routing (deterministic)
# ─────────────────────────────────────────
# Thresholds come from calibration data, not intuition.
# Rule: widen only when ECE < 0.05 and override rate < 2%.

AUTO_BOOK_THRESHOLD = 0.85   # calibrated against DE production data
PROPOSAL_THRESHOLD = 0.55    # below this: low signal, human review required


def route(category: CategoryProposal, vat: VatCalculation) -> RoutingStatus:
    """
    The most important 10 lines in the system.
    Every transaction must reach exactly one terminal state.
    """
    # Reverse charge always goes to review — compliance decision
    if vat.mechanism == "reverse_charge":
        return RoutingStatus.REQUIRES_REVIEW

    if category.confidence >= AUTO_BOOK_THRESHOLD:
        return RoutingStatus.AUTO_BOOKED

    if category.confidence >= PROPOSAL_THRESHOLD:
        return RoutingStatus.PROPOSAL_SENT

    return RoutingStatus.REJECTED


# ─────────────────────────────────────────
# Stage 4: Booking entry (deterministic)
# ─────────────────────────────────────────

def create_booking(
    category: CategoryProposal,
    vat: VatCalculation,
    tx: Transaction,
) -> BookingEntry:
    """
    Double-entry accounting: debit expense, credit bank, split VAT.
    Mechanical — no AI involved.
    """
    config = MARKET_CONFIG.get(tx.market, MARKET_CONFIG["DE"])
    return BookingEntry(
        debit_account=category.account_code,
        credit_account=config["bank_account"],
        net_amount=vat.net_amount,
        vat_amount=vat.amount,
        vat_account=config["vat_account"],
    )


# ─────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────

def process_transaction(tx: Transaction) -> WorkflowOutcome:
    """
    Chains the 4 stages with a per-stage trace.
    Observability: trace captures timing, confidence, and routing decision.
    """
    trace: list[StageTrace] = []

    # Stage 1: Categorization (AI)
    t0 = time.monotonic()
    category = categorize(tx)
    trace.append(StageTrace(
        stage="categorize",
        duration_ms=round((time.monotonic() - t0) * 1000),
        decision=f"code={category.account_code} confidence={category.confidence:.2f}",
    ))

    # Stage 2: VAT (deterministic)
    t1 = time.monotonic()
    vat = calculate_vat(category, tx)
    trace.append(StageTrace(
        stage="vat",
        duration_ms=round((time.monotonic() - t1) * 1000),
        decision=f"mechanism={vat.mechanism} rate={vat.rate:.0%} amount={vat.amount}",
    ))

    # Stage 3: Routing (deterministic)
    status = route(category, vat)
    trace.append(StageTrace(
        stage="route",
        duration_ms=0,
        decision=f"status={status}",
    ))

    # Stage 4: Booking (deterministic, only if auto-booked)
    booking = None
    if status == RoutingStatus.AUTO_BOOKED:
        booking = create_booking(category, vat, tx)

    return WorkflowOutcome(
        transaction_id=tx.id,
        status=status,
        category=category,
        vat=vat,
        booking=booking,
        trace=trace,
    )


# ─────────────────────────────────────────
# Async batch version (production pattern)
# ─────────────────────────────────────────

async def categorize_async(tx: Transaction) -> CategoryProposal:
    """Async wrapper — in production this would be an async LLM call."""
    await asyncio.sleep(0)  # yield to event loop
    return categorize(tx)


async def process_transaction_async(tx: Transaction) -> WorkflowOutcome:
    category = await categorize_async(tx)
    vat = calculate_vat(category, tx)
    status = route(category, vat)
    booking = create_booking(category, vat, tx) if status == RoutingStatus.AUTO_BOOKED else None
    return WorkflowOutcome(
        transaction_id=tx.id,
        status=status,
        category=category,
        vat=vat,
        booking=booking,
    )


async def process_batch_async(transactions: list[Transaction], max_concurrent: int = 5) -> list[WorkflowOutcome]:
    """
    Bounded concurrency: semaphore prevents overloading the LLM provider.
    Unbounded asyncio.gather looks clever but destabilizes in production.
    """
    sem = asyncio.Semaphore(max_concurrent)

    async def bounded(tx: Transaction) -> WorkflowOutcome:
        async with sem:
            return await process_transaction_async(tx)

    return await asyncio.gather(*[bounded(tx) for tx in transactions])


# ─────────────────────────────────────────
# Output / display
# ─────────────────────────────────────────

def print_outcome(outcome: WorkflowOutcome, tx: Transaction) -> None:
    status_icons = {
        RoutingStatus.AUTO_BOOKED:    "✓",
        RoutingStatus.PROPOSAL_SENT:  "→",
        RoutingStatus.REQUIRES_REVIEW: "⚠",
        RoutingStatus.REJECTED:       "✗",
    }
    icon = status_icons[outcome.status]
    print(f"\n  {icon} [{outcome.transaction_id}] {tx.merchant} (€{tx.amount:.2f}) → {outcome.status}")

    if outcome.category:
        print(f"    category: {outcome.category.account_code} | conf: {outcome.category.confidence:.0%}")
        print(f"    evidence: {outcome.category.evidence}")
    if outcome.vat:
        print(f"    VAT: {outcome.vat.mechanism} {outcome.vat.rate:.0%} = €{outcome.vat.amount:.2f} (net: €{outcome.vat.net_amount:.2f})")
    if outcome.booking:
        print(f"    booking: DR {outcome.booking.debit_account} / CR {outcome.booking.credit_account} | Vorsteuer: €{outcome.booking.vat_amount:.2f}")
    if outcome.trace:
        stage_summary = " → ".join(f"{t.stage}({t.duration_ms}ms)" for t in outcome.trace)
        print(f"    trace: {stage_summary}")


def print_batch_summary(outcomes: list[WorkflowOutcome]) -> None:
    total = len(outcomes)
    auto = sum(1 for o in outcomes if o.status == RoutingStatus.AUTO_BOOKED)
    proposal = sum(1 for o in outcomes if o.status == RoutingStatus.PROPOSAL_SENT)
    review = sum(1 for o in outcomes if o.status == RoutingStatus.REQUIRES_REVIEW)
    rejected = sum(1 for o in outcomes if o.status == RoutingStatus.REJECTED)

    print(f"\n  ── Batch summary ─────────────────────────────────────")
    print(f"  Total:        {total}")
    print(f"  Auto-booked:  {auto}  ({auto/total:.0%})")
    print(f"  Proposed:     {proposal}  ({proposal/total:.0%})")
    print(f"  Review:       {review}  ({review/total:.0%})")
    print(f"  Rejected:     {rejected}  ({rejected/total:.0%})")
    print(f"  ──────────────────────────────────────────────────────")


# ─────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────

TEST_TRANSACTIONS = [
    # Happy path — high confidence, standard VAT
    Transaction(id="t1", merchant="AWS", amount=119.0, description="EC2 instance charges", market="DE"),
    # Reduced VAT — food delivery
    Transaction(id="t2", merchant="Lieferando", amount=35.70, description="team lunch", market="DE"),
    # Reverse charge — B2B intra-EU service
    Transaction(id="t3", merchant="Acme Consulting Ltd", amount=5000.0, description="advisory services", is_b2b=True, market="DE"),
    # Low confidence — unknown merchant
    Transaction(id="t4", merchant="Unknown Corp GmbH", amount=299.0, description="mystery charge", market="DE"),
    # French market — PCG codes, different VAT rates
    Transaction(id="t5", merchant="Uber", amount=48.0, description="business travel Paris", market="FR"),
    # Medium confidence — borderline for proposal
    Transaction(id="t6", merchant="Office World", amount=85.50, description="stationery and printer paper", market="DE"),
]


def run_sync() -> None:
    print("\n══ Transaction Categorization Pipeline — Sync Mode ══")
    print(f"  Processing {len(TEST_TRANSACTIONS)} transactions...")

    outcomes = [process_transaction(tx) for tx in TEST_TRANSACTIONS]

    for tx, outcome in zip(TEST_TRANSACTIONS, outcomes):
        print_outcome(outcome, tx)

    print_batch_summary(outcomes)


async def run_async() -> None:
    print("\n══ Transaction Categorization Pipeline — Async Batch Mode ══")
    print(f"  Processing {len(TEST_TRANSACTIONS)} transactions (max_concurrent=3)...")

    t_start = time.monotonic()
    outcomes = await process_batch_async(TEST_TRANSACTIONS, max_concurrent=3)
    elapsed = round((time.monotonic() - t_start) * 1000)

    for tx, outcome in zip(TEST_TRANSACTIONS, outcomes):
        print_outcome(outcome, tx)

    print_batch_summary(outcomes)
    print(f"\n  Total batch elapsed: {elapsed}ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--async", dest="run_async", action="store_true", help="Run async batch version")
    args = parser.parse_args()

    if args.run_async:
        asyncio.run(run_async())
    else:
        run_sync()
