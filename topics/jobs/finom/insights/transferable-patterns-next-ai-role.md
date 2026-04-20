# Transferable Patterns for the Next AI Engineering Role

Saved: 2026-04-16

Built from the Finom interview cycle. Everything here applies to any EU-based AI engineering role with a live technical round, particularly in fintech, legaltech, or any correctness-sensitive domain.

---

## Part 1: The Interview Taxonomy for AI Engineering Roles

### What the different rounds actually test

| Round | Who interviews | What they evaluate | Optimal positioning |
|-------|---------------|-------------------|---------------------|
| CTO / Co-founder intro | C-suite | Strategic fit, product thinking, culture | "I build systems that change the operational reality, not just demos" |
| Central AI / CAIO | Head of AI | Architectural judgment, patterns, org fit | "AI for ambiguity. Software for policy. Earned autonomy." |
| Lead/Senior Engineer | Direct peer | Implementation fluency, code quality, judgment under pressure | "I code clean Python quickly and verify every output before moving on" |

**Critical lesson:** Each round has a different evaluator profile. Round 3 evaluators are not asking "can this person think well?" — they already know you can. They're asking "will I want to work next to this person every day, and can they match my implementation speed?"

---

## Part 2: The Core Technical Vocabulary

These concepts, combined with production specifics, separate strong AI engineering candidates from smart generalists. Use them with precision, not as buzzwords.

### The boundary framing (say this first, every time)

> "AI for ambiguity. Deterministic for policy. The boundary is: what failure mode does the wrong answer create?"

- Merchant categorization → AI (wrong answer = user correction, bounded cost)
- VAT calculation → deterministic (wrong answer = tax audit, unbounded cost)
- Confidence routing → deterministic (threshold from calibration data, not model judgment)
- Booking entry → deterministic (double-entry math has no ambiguity)

### Confidence calibration vocabulary

The ECE (Expected Calibration Error) number is a strong differentiator. Very few candidates know it.

| Term | Definition | Use in interview |
|------|-----------|-----------------|
| ECE | Average gap between predicted confidence and actual accuracy | "Our bar is ECE < 0.05. Above that, the thresholds are unreliable." |
| Platt scaling | Logistic regression on model outputs to produce calibrated probabilities | "I'd calibrate per market — France needs different parameters than Germany." |
| Per-market calibration | Different calibration curves per country/segment | "Germany after 10K transactions; France starts at Level 0 — no calibration data yet." |
| Confidence drift | ECE rises over time as data distribution shifts | "Leading indicator, not lagging. I monitor this before accuracy metrics degrade." |

### The maturity ladder

The 5-level earned autonomy ladder is a signature answer. Name it explicitly:

| Level | Behavior | Advancement criteria |
|-------|----------|---------------------|
| 0 — Shadow | Runs but discards output | >85% agreement with humans for 30 days |
| 1 — Suggest | AI suggests, human decides | >90% acceptance for 14 days |
| 2 — Draft | AI pre-fills, user confirms | <5% correction rate for 14 days |
| 3 — Auto with audit | AI executes, user reviews daily | <2% correction + ECE < 0.05 for 30 days |
| 4 — Full auto | AI executes, alerts on anomalies | 60 days continuous, no regressions |

> "I don't widen automation based on enthusiasm. I widen based on data. The ladder makes autonomy earnable, not claimable."

### The 7-step system design skeleton

1. **Scope** — input, output, worst kind of wrong
2. **AI boundary** — what's judgment vs policy
3. **Pipeline** — explicit stages with typed contracts
4. **Confidence routing** — thresholds from calibration
5. **Observability** — confidence distribution, terminal state, business KPIs
6. **Scale** — batching, async, caching, model cascading
7. **Failures** — FM list with severity and mitigation

### The invariants (name these when asked "what must always be true?")

- **Auto-book invariant**: Confidence ≥ threshold AND not reverse-charge AND valid VAT mechanism
- **Terminal state invariant**: Every ingested transaction reaches exactly one terminal state within SLA
- **Idempotency invariant**: Same transaction processed twice → same booking, no double-count
- **Auditability invariant**: Every routing decision logged with input, confidence, threshold, outcome — replayable

---

## Part 3: Live Coding Operating Discipline

### The 60-minute structure (canonical)

```
min 0-3:   Scope — input, output, failure cost, AI boundary. NO CODE.
min 3-8:   Type contracts — Pydantic models or Zod schemas
min 8-18:  AI stage — stub LLM call, keyword matching mock, confidence score
min 18-28: Deterministic stage — VAT calculation, market config
min 28-35: Confidence router — 3-way branch, all terminal states covered
min 35-45: Orchestrator — chain stages, trace object per transaction
min 45-55: Test cases — happy path, low confidence, edge case
min 55-60: Wrap-up — 2 next steps, one closing question
```

### The scoping statement (< 90 seconds)

> "Input: bank transaction. Output: booked accounting entry or human review queue item. Worst kind of wrong: VAT rate error. AI handles categorization — merchant names are ambiguous. Rules handle VAT calculation — it's law, not prediction. Router decides the path based on calibrated confidence. Let's build."

That's it. Don't expand. Start coding.

### The three agent-assisted coding modes

**Mode 1 — Scaffold (first 5 min):** You define contracts; agent fills boilerplate. You review every type field.

**Mode 2 — Implementation (min 5-45):** One stage at a time. Give the agent a constrained prompt ("implement VAT calculation as a pure function, German market, standard rate 19%, reduced 7%, reverse charge detection for B2B intra-EU"). 10-second read after every generation.

**Mode 3 — Debug/extend (min 45-60):** Targeted edits only. If something breaks, read the error, form a hypothesis, fix the specific line. Don't regenerate the whole file.

### Recovery sentences (memorize these)

| Situation | Say |
|-----------|-----|
| Scoping running long | "I have what I need — let me start with the contracts" |
| Implementation blocked | "I'll stub this and move on — the contract matters more than the body right now" |
| Generated code is wrong | "This isn't quite right — I'm going to fix [specific line] before we proceed" |
| Running out of time | "I'll flag what's missing rather than rush — the router is the critical part and it's working" |
| Blank — mind going | "Let me step back to the invariants. Every transaction needs exactly one terminal state. The router makes that possible. Let me build that." |

---

## Part 4: Python Implementation Reference

The canonical live-round implementation pattern in Python. Use this when the exercise is Python (Finom, and most AI-heavy companies, prefer Python for AI work).

### Type contracts (Pydantic)

```python
from pydantic import BaseModel
from enum import Enum
from typing import Optional

class RoutingStatus(str, Enum):
    AUTO_BOOKED = "auto_booked"
    PROPOSAL_SENT = "proposal_sent"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"

class Transaction(BaseModel):
    id: str
    merchant: str
    amount: float
    description: str
    is_b2b: bool = False

class CategoryProposal(BaseModel):
    account_code: str
    confidence: float
    evidence: str

class VatCalculation(BaseModel):
    rate: float
    amount: float
    mechanism: str  # "standard", "reduced", "reverse_charge", "exempt"

class BookingEntry(BaseModel):
    debit_account: str
    credit_account: str
    net_amount: float
    vat_amount: float

class WorkflowOutcome(BaseModel):
    transaction_id: str
    status: RoutingStatus
    category: Optional[CategoryProposal] = None
    vat: Optional[VatCalculation] = None
    booking: Optional[BookingEntry] = None
    trace: list[dict] = []
```

### The categorizer (AI stage — mock version for live round)

```python
MERCHANT_CATEGORIES = {
    "aws": ("4940", 0.95, "cloud infrastructure → IT costs"),
    "uber": ("4670", 0.88, "transport → travel costs"),
    "lieferando": ("4650", 0.82, "food delivery → meal expense"),
    "notary": ("6825", 0.91, "legal service → professional fees"),
}

def categorize(tx: Transaction) -> CategoryProposal:
    key = tx.merchant.lower().split()[0]
    if key in MERCHANT_CATEGORIES:
        code, conf, evidence = MERCHANT_CATEGORIES[key]
        return CategoryProposal(account_code=code, confidence=conf, evidence=evidence)
    return CategoryProposal(account_code="4990", confidence=0.35, evidence="no pattern match — manual review needed")
```

### The VAT calculator (deterministic stage)

```python
DE_VAT_RATES = {"standard": 0.19, "reduced": 0.07}
REDUCED_RATE_ACCOUNTS = {"4650", "4670"}  # food, travel

def calculate_vat(category: CategoryProposal, tx: Transaction, market: str = "DE") -> VatCalculation:
    if tx.is_b2b:  # Reverse charge: §13b UStG
        return VatCalculation(rate=0.0, amount=0.0, mechanism="reverse_charge")
    
    rates = DE_VAT_RATES  # extend with FR_VAT_RATES, IT_VAT_RATES as needed
    if category.account_code in REDUCED_RATE_ACCOUNTS:
        rate = rates["reduced"]
        mechanism = "reduced"
    else:
        rate = rates["standard"]
        mechanism = "standard"
    
    vat_amount = round(tx.amount * rate / (1 + rate), 2)
    return VatCalculation(rate=rate, amount=vat_amount, mechanism=mechanism)
```

### The router (most important 10 lines)

```python
AUTO_BOOK_THRESHOLD = 0.85
PROPOSAL_THRESHOLD = 0.55

def route(category: CategoryProposal, vat: VatCalculation) -> RoutingStatus:
    if vat.mechanism == "reverse_charge":
        return RoutingStatus.REQUIRES_REVIEW  # always review reverse charge
    if category.confidence >= AUTO_BOOK_THRESHOLD:
        return RoutingStatus.AUTO_BOOKED
    if category.confidence >= PROPOSAL_THRESHOLD:
        return RoutingStatus.PROPOSAL_SENT
    return RoutingStatus.REJECTED
```

### The orchestrator with trace

```python
import time

def process_transaction(tx: Transaction) -> WorkflowOutcome:
    trace = []
    
    t0 = time.monotonic()
    category = categorize(tx)
    trace.append({"stage": "categorize", "duration_ms": round((time.monotonic() - t0) * 1000), "confidence": category.confidence})
    
    t1 = time.monotonic()
    vat = calculate_vat(category, tx)
    trace.append({"stage": "vat", "duration_ms": round((time.monotonic() - t1) * 1000), "mechanism": vat.mechanism})
    
    status = route(category, vat)
    trace.append({"stage": "route", "status": status})
    
    booking = None
    if status == RoutingStatus.AUTO_BOOKED:
        booking = BookingEntry(
            debit_account=category.account_code,
            credit_account="1200",  # bank account
            net_amount=round(tx.amount - vat.amount, 2),
            vat_amount=vat.amount,
        )
    
    return WorkflowOutcome(
        transaction_id=tx.id,
        status=status,
        category=category,
        vat=vat,
        booking=booking,
        trace=trace,
    )
```

### Test cases (run these in the live round)

```python
if __name__ == "__main__":
    cases = [
        Transaction(id="t1", merchant="AWS", amount=119.0, description="EC2 instance"),
        Transaction(id="t2", merchant="Lieferando", amount=45.0, description="team lunch"),
        Transaction(id="t3", merchant="Unicorn Consulting", amount=5000.0, description="advisory", is_b2b=True),
        Transaction(id="t4", merchant="Unknown Corp", amount=300.0, description="mystery charge"),
    ]
    
    for tx in cases:
        outcome = process_transaction(tx)
        print(f"\n[{outcome.transaction_id}] {tx.merchant} → {outcome.status}")
        if outcome.booking:
            print(f"  booked: {outcome.booking.debit_account} / {outcome.booking.credit_account}")
        print(f"  confidence: {outcome.category.confidence:.2f} | VAT: {outcome.vat.mechanism} ({outcome.vat.rate:.0%})")
```

---

## Part 5: Numbers to Know Cold

| Metric | Value |
|--------|-------|
| Auto-book threshold | 0.85 |
| Proposal threshold | 0.55 |
| Calibration bar | ECE < 0.05 |
| German standard VAT | 19% |
| German reduced VAT | 7% |
| French VAT rates | 20% / 10% / 5.5% / 2.1% |
| Italian standard VAT | 22% |
| Reverse charge law | §13b UStG (Germany) |
| Shadow mode duration | 30 days |
| Auto→Full auto criteria | <2% correction + 60 days |
| GoBD retention | 10 years |

---

## Part 6: Questions That Signal Production Maturity

These questions show you think about systems surviving production, not just solving the interview problem:

1. "Where do you currently see calibration drift showing up first — in which market or transaction category?"
2. "What's your SLA for a transaction to reach a terminal state, and how do you detect silent rejects?"
3. "When you added France as a second market, what in the pipeline actually changed vs what was reused?"
4. "How do you manage the relationship between the central AI team and embedded product engineers — do they come to you or do you go to them?"
5. "What's the hardest production bug you've had in the accounting pipeline?" ← best single question

---

## Part 7: The Right Positioning for Each Role Type

| Role type | Lead with | Signal phrase |
|-----------|-----------|---------------|
| Central AI team | Reusable patterns, eval infrastructure, adoption mechanics | "I centralize the hard parts — eval, orchestration, safety — and leave product decisions with domain teams" |
| Product AI engineer | Full-stack ownership, end-to-end delivery | "I own the workflow from ingestion to terminal state — I build it, monitor it, and improve it" |
| ML platform / infra | Evaluation infra, model serving, observability tooling | "I build the spine that every AI product runs on" |
| Lead / hands-on senior | Implementation fluency + judgment | "I code quickly, verify carefully, and narrate every decision" |
