"""
Invoice Financing — Credit Risk Signal Pipeline

Finom's late-2026 roadmap: invoice financing and credit lines for freelancers.
This pipeline demonstrates how the same AI/deterministic boundary principle
applies to a new domain: credit risk assessment.

Domain differences from transaction categorization:
  - Input: invoice + business health data (not a single transaction)
  - AI value: fraud signal detection and cash-flow health scoring from messy doc data
  - Deterministic layer: credit policy rules (hard limits, concentration checks, blacklist)
  - Output: finance/reject decision with explicit approval gates — not a booking entry
  - Failure cost: much higher — bad credit decision ≠ wrong account code, it's capital at risk

Run:
    python3 risk_pipeline.py
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ─────────────────────────────────────────
# Domain types
# ─────────────────────────────────────────

class RiskDecision(str, Enum):
    APPROVED = "approved"           # within policy, high signal quality
    MANUAL_REVIEW = "manual_review" # signal is ambiguous or policy edge case
    DECLINED = "declined"           # hard policy violation or critical signal
    INSUFFICIENT_DATA = "insufficient_data"  # can't score without more info


@dataclass
class Invoice:
    id: str
    issuer_id: str              # Finom business account
    counterparty_name: str
    counterparty_vat_id: str
    gross_amount: float
    currency: str = "EUR"
    issue_date: str = ""
    due_date: str = ""
    description: str = ""
    is_recurring_counterparty: bool = False


@dataclass
class BusinessProfile:
    account_id: str
    months_active: int              # account age
    avg_monthly_revenue: float      # rolling 3-month
    monthly_transaction_count: int
    prior_financing_defaults: int
    outstanding_financing_amount: float
    industry_code: str              # e.g. "IT", "RETAIL", "CONSTRUCTION"


@dataclass
class FraudSignals:
    """
    AI-derived signals from document and pattern analysis.
    Each signal has its own confidence — not a single model output.
    """
    counterparty_vat_verified: bool         # VIES check
    invoice_template_anomaly_score: float   # [0,1] — 0=normal, 1=suspicious
    counterparty_age_days: Optional[int]    # freshly registered = risk signal
    self_dealing_score: float               # [0,1] — issuer and counterparty linked?
    duplicate_invoice_probability: float   # [0,1] — seen this invoice pattern before?
    evidence: list[str] = field(default_factory=list)


@dataclass
class CreditPolicyCheck:
    """
    Deterministic policy rules — these are always code, never model judgment.
    """
    passes_min_account_age: bool       # ≥ 3 months
    passes_revenue_multiple: bool      # invoice ≤ 3× avg monthly revenue
    passes_concentration_limit: bool   # counterparty ≤ 60% of revenue
    passes_outstanding_cap: bool       # total outstanding ≤ 5× avg monthly
    passes_default_history: bool       # 0 prior defaults
    hardcoded_limit_eur: float = 25_000.0  # max single invoice financing


@dataclass
class StageTrace:
    stage: str
    duration_ms: int
    decision: str


@dataclass
class RiskAssessment:
    invoice_id: str
    decision: RiskDecision
    fraud_signals: Optional[FraudSignals] = None
    policy_check: Optional[CreditPolicyCheck] = None
    risk_score: Optional[float] = None   # [0, 1] — AI-derived composite
    approved_amount: Optional[float] = None
    decline_reasons: list[str] = field(default_factory=list)
    trace: list[StageTrace] = field(default_factory=list)


# ─────────────────────────────────────────
# Stage 1: Fraud signal extraction (AI stage)
# ─────────────────────────────────────────

def extract_fraud_signals(invoice: Invoice, profile: BusinessProfile) -> FraudSignals:
    """
    AI stage: extract fraud risk signals from invoice + business data.
    In production: LLM + structured output over invoice document + business graph.
    Mock here: rule-based proxies that return calibrated scores.
    """
    evidence = []
    signals = FraudSignals(
        counterparty_vat_verified=bool(invoice.counterparty_vat_id),
        invoice_template_anomaly_score=0.0,
        counterparty_age_days=None,
        self_dealing_score=0.0,
        duplicate_invoice_probability=0.0,
    )

    # Mock: freshly registered counterparty
    if not invoice.is_recurring_counterparty:
        signals.invoice_template_anomaly_score = 0.15
        evidence.append("new counterparty — no prior payment history")

    # Mock: high invoice relative to revenue (concentration risk signal)
    if invoice.gross_amount > profile.avg_monthly_revenue * 2:
        signals.invoice_template_anomaly_score += 0.20
        evidence.append(f"invoice €{invoice.gross_amount:.0f} is {invoice.gross_amount/profile.avg_monthly_revenue:.1f}× avg monthly revenue")

    # Mock: no VAT ID on counterparty for large invoice
    if not invoice.counterparty_vat_id and invoice.gross_amount > 5000:
        signals.invoice_template_anomaly_score += 0.30
        evidence.append("counterparty VAT ID missing on invoice > €5000")

    # Mock: low activity business applying for high advance
    if profile.monthly_transaction_count < 10 and invoice.gross_amount > 10_000:
        signals.self_dealing_score = 0.40
        evidence.append("low-activity account requesting high advance")

    signals.evidence = evidence
    return signals


# ─────────────────────────────────────────
# Stage 2: Credit policy check (deterministic)
# Hard rules — these must be code, not model judgment.
# ─────────────────────────────────────────

MAX_REVENUE_MULTIPLE = 3.0      # invoice ≤ 3× avg monthly revenue
MAX_CONCENTRATION = 0.60        # counterparty ≤ 60% of last 3 months revenue
MAX_OUTSTANDING_MULTIPLE = 5.0  # total outstanding ≤ 5× avg monthly
MAX_FINANCING_AMOUNT = 25_000.0
MIN_ACCOUNT_AGE_MONTHS = 3


def check_credit_policy(invoice: Invoice, profile: BusinessProfile) -> CreditPolicyCheck:
    """
    Deterministic policy checks — a policy violation means DECLINED regardless of
    fraud signal scores or model confidence.
    """
    revenue_multiple = invoice.gross_amount / max(profile.avg_monthly_revenue, 1)
    outstanding_after = profile.outstanding_financing_amount + invoice.gross_amount
    outstanding_multiple = outstanding_after / max(profile.avg_monthly_revenue, 1)

    return CreditPolicyCheck(
        passes_min_account_age=(profile.months_active >= MIN_ACCOUNT_AGE_MONTHS),
        passes_revenue_multiple=(revenue_multiple <= MAX_REVENUE_MULTIPLE),
        passes_concentration_limit=True,   # simplified: would need counterparty revenue breakdown
        passes_outstanding_cap=(outstanding_multiple <= MAX_OUTSTANDING_MULTIPLE),
        passes_default_history=(profile.prior_financing_defaults == 0),
        hardcoded_limit_eur=MAX_FINANCING_AMOUNT,
    )


# ─────────────────────────────────────────
# Stage 3: Risk scoring (AI stage — composite)
# Weighted combination of fraud signals → single risk score [0, 1]
# ─────────────────────────────────────────

FRAUD_SIGNAL_WEIGHTS = {
    "template_anomaly": 0.35,
    "self_dealing": 0.40,
    "duplicate": 0.20,
    "vat_missing": 0.05,
}


def compute_risk_score(signals: FraudSignals) -> float:
    """
    AI-derived composite risk score. Low = safe, high = risky.
    In production: this would be a calibrated ML model or LLM scorer.
    """
    score = (
        FRAUD_SIGNAL_WEIGHTS["template_anomaly"] * signals.invoice_template_anomaly_score +
        FRAUD_SIGNAL_WEIGHTS["self_dealing"] * signals.self_dealing_score +
        FRAUD_SIGNAL_WEIGHTS["duplicate"] * signals.duplicate_invoice_probability +
        FRAUD_SIGNAL_WEIGHTS["vat_missing"] * (0 if signals.counterparty_vat_verified else 1)
    )
    return round(min(score, 1.0), 3)


# ─────────────────────────────────────────
# Stage 4: Decision router (deterministic)
# Policy violations → DECLINED (regardless of risk score)
# Risk score thresholds → APPROVED / MANUAL_REVIEW / DECLINED
# ─────────────────────────────────────────

RISK_APPROVE_THRESHOLD = 0.10    # score ≤ 0.10 → approve (calibrated against DE baseline)
RISK_REVIEW_THRESHOLD = 0.45     # score 0.10–0.45 → manual review


def make_decision(
    invoice: Invoice,
    policy: CreditPolicyCheck,
    risk_score: float,
) -> tuple[RiskDecision, list[str], Optional[float]]:
    """
    Returns (decision, decline_reasons, approved_amount).
    Policy violations always override risk scores — deterministic rules first.
    """
    decline_reasons = []

    # Deterministic policy gates — checked before any model score
    if not policy.passes_min_account_age:
        decline_reasons.append("account age < 3 months")
    if not policy.passes_revenue_multiple:
        decline_reasons.append(f"invoice exceeds {MAX_REVENUE_MULTIPLE}× avg monthly revenue")
    if not policy.passes_outstanding_cap:
        decline_reasons.append(f"total outstanding would exceed {MAX_OUTSTANDING_MULTIPLE}× avg monthly")
    if not policy.passes_default_history:
        decline_reasons.append("prior financing default on record")
    if invoice.gross_amount > policy.hardcoded_limit_eur:
        decline_reasons.append(f"invoice exceeds hard limit of €{policy.hardcoded_limit_eur:,.0f}")

    if decline_reasons:
        return RiskDecision.DECLINED, decline_reasons, None

    # Risk score routing
    if risk_score <= RISK_APPROVE_THRESHOLD:
        return RiskDecision.APPROVED, [], min(invoice.gross_amount, policy.hardcoded_limit_eur)
    if risk_score <= RISK_REVIEW_THRESHOLD:
        return RiskDecision.MANUAL_REVIEW, [f"elevated fraud risk score: {risk_score:.2f}"], None

    decline_reasons.append(f"fraud risk score too high: {risk_score:.2f}")
    return RiskDecision.DECLINED, decline_reasons, None


# ─────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────

def assess_invoice(invoice: Invoice, profile: BusinessProfile) -> RiskAssessment:
    trace: list[StageTrace] = []

    t0 = time.monotonic()
    signals = extract_fraud_signals(invoice, profile)
    trace.append(StageTrace(
        stage="fraud_signals",
        duration_ms=round((time.monotonic() - t0) * 1000),
        decision=f"anomaly={signals.invoice_template_anomaly_score:.2f} self_dealing={signals.self_dealing_score:.2f}",
    ))

    t1 = time.monotonic()
    policy = check_credit_policy(invoice, profile)
    policy_flags = [k for k, v in {
        "min_age": policy.passes_min_account_age,
        "revenue_multiple": policy.passes_revenue_multiple,
        "outstanding_cap": policy.passes_outstanding_cap,
        "default_history": policy.passes_default_history,
    }.items() if not v]
    trace.append(StageTrace(
        stage="policy_check",
        duration_ms=round((time.monotonic() - t1) * 1000),
        decision=f"violations={policy_flags or 'none'}",
    ))

    t2 = time.monotonic()
    risk_score = compute_risk_score(signals)
    trace.append(StageTrace(
        stage="risk_score",
        duration_ms=round((time.monotonic() - t2) * 1000),
        decision=f"score={risk_score:.3f}",
    ))

    decision, decline_reasons, approved_amount = make_decision(invoice, policy, risk_score)
    trace.append(StageTrace(
        stage="decision",
        duration_ms=0,
        decision=f"decision={decision} approved=€{approved_amount or 0:.0f}",
    ))

    return RiskAssessment(
        invoice_id=invoice.id,
        decision=decision,
        fraud_signals=signals,
        policy_check=policy,
        risk_score=risk_score,
        approved_amount=approved_amount,
        decline_reasons=decline_reasons,
        trace=trace,
    )


# ─────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────

if __name__ == "__main__":
    # Stable freelance developer: recurring client, established account
    strong_profile = BusinessProfile(
        account_id="biz-001",
        months_active=18,
        avg_monthly_revenue=8_000,
        monthly_transaction_count=45,
        prior_financing_defaults=0,
        outstanding_financing_amount=0,
        industry_code="IT",
    )

    # New account: low activity, no history
    weak_profile = BusinessProfile(
        account_id="biz-002",
        months_active=2,
        avg_monthly_revenue=2_000,
        monthly_transaction_count=4,
        prior_financing_defaults=0,
        outstanding_financing_amount=0,
        industry_code="RETAIL",
    )

    test_cases = [
        (
            Invoice(
                id="inv-001", issuer_id="biz-001",
                counterparty_name="Acme GmbH", counterparty_vat_id="DE123456789",
                gross_amount=6_000, is_recurring_counterparty=True,
                description="Monthly software development retainer",
            ),
            strong_profile,
            "Happy path — established business, known counterparty"
        ),
        (
            Invoice(
                id="inv-002", issuer_id="biz-001",
                counterparty_name="New Client AG", counterparty_vat_id="DE987654321",
                gross_amount=18_000, is_recurring_counterparty=False,
                description="One-time consulting project",
            ),
            strong_profile,
            "Large new client — elevated risk, manual review expected"
        ),
        (
            Invoice(
                id="inv-003", issuer_id="biz-002",
                counterparty_name="Mystery Corp", counterparty_vat_id="",
                gross_amount=15_000, is_recurring_counterparty=False,
                description="Consulting services",
            ),
            weak_profile,
            "New account + no VAT ID + large invoice — should decline"
        ),
        (
            Invoice(
                id="inv-004", issuer_id="biz-001",
                counterparty_name="BigCo International", counterparty_vat_id="DE555000111",
                gross_amount=30_000, is_recurring_counterparty=True,
                description="Large recurring contract",
            ),
            strong_profile,
            "Exceeds hard limit of €25,000 — policy decline"
        ),
    ]

    icons = {
        RiskDecision.APPROVED: "✓",
        RiskDecision.MANUAL_REVIEW: "→",
        RiskDecision.DECLINED: "✗",
        RiskDecision.INSUFFICIENT_DATA: "?",
    }

    print("\n══ Invoice Financing — Credit Risk Pipeline ══\n")
    for invoice, profile, scenario in test_cases:
        result = assess_invoice(invoice, profile)
        icon = icons[result.decision]
        print(f"  {icon} [{result.invoice_id}] {scenario}")
        print(f"     decision: {result.decision}  |  risk_score: {result.risk_score:.3f}")
        if result.approved_amount:
            print(f"     approved: €{result.approved_amount:,.0f}")
        if result.decline_reasons:
            print(f"     reasons: {'; '.join(result.decline_reasons)}")
        if result.fraud_signals and result.fraud_signals.evidence:
            print(f"     signals: {' | '.join(result.fraud_signals.evidence)}")
        trace_str = " → ".join(f"{t.stage}({t.duration_ms}ms)" for t in result.trace)
        print(f"     trace: {trace_str}\n")
