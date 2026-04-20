"""
Live Round Drill — 45-Minute Practice Scenario

Scenario: You join a fintech company. They give you a skeleton file and ask you to:
  1. Diagnose what's wrong (5 minutes)
  2. Add multi-currency support (20 minutes)
  3. Add an audit log (10 minutes)
  4. Write one eval test (5 minutes)
  5. Explain what you'd add in production (5 minutes)

This file is the SKELETON — contains intentional bugs and missing features.
Run it first to see what breaks. Then fix it following the time-box below.

The SOLUTION section at the bottom shows the expected output — don't look until done.

--- TIME BOX ---
  0:00 – 1:30   Scope: read skeleton, name 3 things wrong, sketch terminal states
  1:30 – 21:30  Build: multi-currency VAT (EUR, USD, GBP with exchange rates)
  21:30 – 31:30 Build: per-transaction audit log with stage decisions
  31:30 – 36:30 Build: one eval test proving reverse-charge routes correctly
  36:30 – 41:30 Narrate: what you'd add in production (calibration, idempotency, circuit breaker)
  41:30 – 45:00 Buffer / cleanup / questions

Run:
    python3 live_round_drill.py           # see the broken output
    python3 live_round_drill.py --fixed   # see the fixed output (cheat mode)
"""

import sys
import time
from dataclasses import dataclass
from typing import Optional


# ─────────────────────────────────────────
# SKELETON (intentionally broken)
# Diagnose: what's wrong here?
# ─────────────────────────────────────────

@dataclass
class SkeletonTransaction:
    id: str
    merchant: str
    amount: float
    currency: str    # "EUR", "USD", "GBP"
    is_b2b: bool = False


def skeleton_categorize(tx: SkeletonTransaction) -> dict:
    """Bug 1: merges AI judgment with routing threshold."""
    if "aws" in tx.merchant.lower():
        code = "4940"
        confidence = 0.95
    elif "lieferando" in tx.merchant.lower():
        code = "4650"
        confidence = 0.82
    else:
        code = "4990"
        confidence = 0.3
    # Bug 2: routes here — mixing AI with business rule
    if confidence > 0.85:
        return {"account_code": code, "status": "AUTO_BOOKED", "amount": tx.amount}
    return {"account_code": code, "status": "PROPOSAL", "amount": tx.amount}


def skeleton_vat(result: dict, tx: SkeletonTransaction) -> dict:
    """Bug 3: VAT is always 19% regardless of category or B2B status."""
    vat = result["amount"] * 0.19
    result["vat"] = vat
    result["net"] = result["amount"] - vat
    # Bug 4: no currency handling — USD and GBP silently treated as EUR
    return result


def skeleton_process(tx: SkeletonTransaction) -> dict:
    result = skeleton_categorize(tx)
    return skeleton_vat(result, tx)


# ─────────────────────────────────────────
# FIXED VERSION
# Run with --fixed to see this
# ─────────────────────────────────────────

EXCHANGE_RATES_TO_EUR = {
    "EUR": 1.00,
    "USD": 0.92,    # mock: 1 USD = 0.92 EUR
    "GBP": 1.17,    # mock: 1 GBP = 1.17 EUR
    "CHF": 1.04,
}

VAT_RATES = {
    "standard": 0.19,   # DE §12 UStG Abs.1
    "reduced":  0.07,   # meals, public transport
    "exempt":   0.00,   # B2B reverse charge
}

REDUCED_ACCOUNTS = {"4650", "4670"}   # meals, travel → reduced VAT


@dataclass
class FixedCategoryProposal:
    account_code: str
    confidence: float
    evidence: str


@dataclass
class FixedVatResult:
    rate: float
    mechanism: str
    gross_eur: float
    vat_eur: float
    net_eur: float
    original_currency: str
    original_amount: float
    exchange_rate: float


@dataclass
class AuditEntry:
    stage: str
    decision: str
    duration_ms: float


@dataclass
class FixedResult:
    transaction_id: str
    status: str   # AUTO_BOOKED | PROPOSAL_SENT | REQUIRES_REVIEW | REJECTED
    category: Optional[FixedCategoryProposal]
    vat: Optional[FixedVatResult]
    audit: list[AuditEntry]


MERCHANT_PATTERNS = {
    "aws":        ("4940", 0.95, "cloud infra → IT costs"),
    "lieferando": ("4650", 0.82, "food delivery → meals"),
    "uber":       ("4670", 0.90, "ride service → travel"),
    "telekom":    ("4920", 0.78, "telecom → phone costs"),
    "consult":    ("6825", 0.85, "consulting → professional fees"),
}

AUTO_BOOK_THRESHOLD  = 0.85
PROPOSAL_THRESHOLD   = 0.55


def fixed_categorize(tx: SkeletonTransaction) -> tuple[FixedCategoryProposal, float]:
    t0 = time.monotonic()
    merchant_lower = tx.merchant.lower()
    for keyword, (code, conf, evidence) in MERCHANT_PATTERNS.items():
        if keyword in merchant_lower:
            return FixedCategoryProposal(code, conf, evidence), (time.monotonic() - t0) * 1000
    return FixedCategoryProposal("4990", 0.30, "no pattern match"), (time.monotonic() - t0) * 1000


def fixed_vat(category: FixedCategoryProposal, tx: SkeletonTransaction) -> tuple[FixedVatResult, float]:
    t0 = time.monotonic()
    rate_eur = EXCHANGE_RATES_TO_EUR.get(tx.currency, 1.0)
    gross_eur = round(tx.amount * rate_eur, 2)

    if tx.is_b2b:
        mechanism, rate = "reverse_charge", 0.0
    elif category.account_code in REDUCED_ACCOUNTS:
        mechanism, rate = "reduced", VAT_RATES["reduced"]
    else:
        mechanism, rate = "standard", VAT_RATES["standard"]

    vat_eur = round(gross_eur * rate / (1 + rate), 2)
    net_eur = round(gross_eur - vat_eur, 2)
    return FixedVatResult(
        rate=rate, mechanism=mechanism,
        gross_eur=gross_eur, vat_eur=vat_eur, net_eur=net_eur,
        original_currency=tx.currency, original_amount=tx.amount, exchange_rate=rate_eur,
    ), (time.monotonic() - t0) * 1000


def fixed_route(category: FixedCategoryProposal, vat: FixedVatResult, tx: SkeletonTransaction) -> tuple[str, float]:
    t0 = time.monotonic()
    if tx.is_b2b:
        return "REQUIRES_REVIEW", (time.monotonic() - t0) * 1000
    if category.confidence >= AUTO_BOOK_THRESHOLD:
        return "AUTO_BOOKED", (time.monotonic() - t0) * 1000
    if category.confidence >= PROPOSAL_THRESHOLD:
        return "PROPOSAL_SENT", (time.monotonic() - t0) * 1000
    return "REJECTED", (time.monotonic() - t0) * 1000


def fixed_process(tx: SkeletonTransaction) -> FixedResult:
    audit: list[AuditEntry] = []

    category, cat_ms = fixed_categorize(tx)
    audit.append(AuditEntry(
        stage="categorize",
        decision=f"code={category.account_code} conf={category.confidence:.2f}",
        duration_ms=cat_ms,
    ))

    vat, vat_ms = fixed_vat(category, tx)
    audit.append(AuditEntry(
        stage="vat",
        decision=f"mechanism={vat.mechanism} rate={vat.rate:.0%} gross_eur=€{vat.gross_eur:.2f}",
        duration_ms=vat_ms,
    ))

    status, route_ms = fixed_route(category, vat, tx)
    audit.append(AuditEntry(
        stage="route",
        decision=f"status={status}",
        duration_ms=route_ms,
    ))

    return FixedResult(
        transaction_id=tx.id,
        status=status,
        category=category,
        vat=vat,
        audit=audit,
    )


# ─────────────────────────────────────────
# Eval test
# ─────────────────────────────────────────

def test_reverse_charge_routes_to_review():
    """B2B transaction must ALWAYS route to REQUIRES_REVIEW regardless of confidence."""
    tx = SkeletonTransaction(id="test-b2b", merchant="AWS", amount=5000.0, currency="EUR", is_b2b=True)
    result = fixed_process(tx)
    assert result.status == "REQUIRES_REVIEW", (
        f"B2B transaction routed to {result.status} — compliance invariant violated"
    )
    assert result.vat is not None and result.vat.mechanism == "reverse_charge", (
        f"B2B transaction should have reverse_charge mechanism, got {result.vat.mechanism}"
    )
    return True


def test_usd_converted_to_eur():
    """USD transaction should have gross_eur ≠ original amount."""
    tx = SkeletonTransaction(id="test-usd", merchant="AWS", amount=100.0, currency="USD", is_b2b=False)
    result = fixed_process(tx)
    assert result.vat.original_currency == "USD"
    assert result.vat.gross_eur == round(100.0 * EXCHANGE_RATES_TO_EUR["USD"], 2), (
        f"Expected gross_eur={100.0 * EXCHANGE_RATES_TO_EUR['USD']}, got {result.vat.gross_eur}"
    )
    return True


# ─────────────────────────────────────────
# Main
# ─────────────────────────────────────────

DEMO_TRANSACTIONS = [
    SkeletonTransaction("d01", "AWS EMEA",     119.0,  "EUR"),
    SkeletonTransaction("d02", "Lieferando",    47.80, "EUR"),
    SkeletonTransaction("d03", "AWS",         5000.0,  "USD", is_b2b=True),
    SkeletonTransaction("d04", "Uber UK",       45.0,  "GBP"),
    SkeletonTransaction("d05", "Unknown GmbH",  40.0,  "EUR"),
]

if __name__ == "__main__":
    fixed_mode = "--fixed" in sys.argv

    if not fixed_mode:
        print("\n══ SKELETON — Diagnose Bugs Before Running --fixed ══\n")
        print("  Bugs to find (don't scroll to solution):\n")
        print("  [1] ____________________________________________")
        print("  [2] ____________________________________________")
        print("  [3] ____________________________________________")
        print("  [4] ____________________________________________\n")
        print("  Skeleton output (should look wrong):\n")
        for tx in DEMO_TRANSACTIONS:
            result = skeleton_process(tx)
            print(f"  {tx.id} [{tx.currency}] {tx.merchant:<20} → {result}")
        print(f"\n  Bug 1: AI and routing merged (confidence threshold in categorize)")
        print(f"  Bug 2: Currency ignored (USD/GBP treated as EUR — silent wrong amount)")
        print(f"  Bug 3: VAT always 19% (meals should be 7%, B2B should be 0%)")
        print(f"  Bug 4: No audit trail (can't answer 'why was this booked this way?')")
        print(f"\n  Run with --fixed to see the corrected output.")
    else:
        print("\n══ FIXED — Multi-Currency + Audit Log ══\n")

        # Eval tests first
        print("  ── Eval tests ─────────────────────────────────────────")
        tests = [
            ("reverse_charge → REQUIRES_REVIEW", test_reverse_charge_routes_to_review),
            ("USD → EUR conversion",             test_usd_converted_to_eur),
        ]
        for name, fn in tests:
            passed = fn()
            print(f"  {'✓' if passed else '✗'} {name}")

        # Process transactions
        print(f"\n  ── Results ────────────────────────────────────────────")
        icons = {"AUTO_BOOKED": "✓", "PROPOSAL_SENT": "→", "REQUIRES_REVIEW": "⚠", "REJECTED": "✗"}
        for tx in DEMO_TRANSACTIONS:
            r = fixed_process(tx)
            icon = icons.get(r.status, "?")
            fx = f" (fx {r.vat.exchange_rate:.2f})" if r.vat and r.vat.original_currency != "EUR" else ""
            vat_info = f"  {r.vat.mechanism} {r.vat.rate:.0%} net=€{r.vat.net_eur:.2f}{fx}" if r.vat else ""
            print(f"  {icon} {tx.id} [{tx.currency}] {tx.merchant:<20} → {r.status}{vat_info}")

        # Show audit for one transaction
        sample = fixed_process(DEMO_TRANSACTIONS[2])   # B2B reverse charge
        print(f"\n  ── Audit trail: {sample.transaction_id} ─────────────────────────────")
        for entry in sample.audit:
            print(f"  [{entry.duration_ms:.3f}ms] {entry.stage:<12} {entry.decision}")

        print(f"\n  ── What I'd add in production ─────────────────────────")
        print(f"  1. Calibration gate: ECE < 0.05 before AUTO_BOOK_THRESHOLD = 0.85 is trusted")
        print(f"  2. Idempotency: sha256(tx_id + stage + input) → cache key → no double-booking")
        print(f"  3. Circuit breaker: trip if avg confidence < 0.70 over last 100 calls")
        print(f"  4. Exchange rate freshness: reject stale rates > 1h old (FX moves)")
        print(f"  5. Eval harness: severity weights — wrong VAT on B2B = critical (4×)")
