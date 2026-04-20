# Python Live Round Quick Reference

Saved: 2026-04-13

If the exercise is in Python (likely given Finom's Python + C# stack), use these patterns. TypeScript Zod → Python Pydantic. The logic is identical; only the types change.

---

## Stage Contracts (Pydantic)

```python
from pydantic import BaseModel
from typing import Literal
from enum import Enum

class Market(str, Enum):
    DE = "DE"
    FR = "FR"

class TransactionInput(BaseModel):
    id: str
    vendor: str
    amount: float
    market: Market
    description: str = ""
    is_b2b: bool = False
    counterparty_vat_id: str | None = None

class CategoryResult(BaseModel):
    account_code: str
    account_name: str
    confidence: float  # 0.0 to 1.0
    reasoning: str

class VatResult(BaseModel):
    vat_rate: float
    net_amount: float
    vat_amount: float
    mechanism: Literal["standard", "reduced", "reverse_charge", "exempt"]

class RoutingStatus(str, Enum):
    AUTO_BOOKED = "auto_booked"
    PROPOSAL_SENT = "proposal_sent"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"

class WorkflowResult(BaseModel):
    transaction_id: str
    status: RoutingStatus
    category: CategoryResult | None = None
    vat: VatResult | None = None
    trace: list[dict] = []
```

---

## Market Policy (Deterministic)

```python
from dataclasses import dataclass

@dataclass
class MarketPolicy:
    market: str
    standard_vat_rate: float
    reduced_vat_rate: float
    chart_of_accounts: dict[str, tuple[str, str]]  # category -> (code, name)
    reverse_charge_vendors: list[str]

    def get_account(self, category: str) -> tuple[str, str]:
        return self.chart_of_accounts.get(category, ("4999", "Miscellaneous"))

    def is_reverse_charge(self, vendor: str) -> bool:
        v = vendor.lower()
        return any(rc in v for rc in self.reverse_charge_vendors)

DE_POLICY = MarketPolicy(
    market="DE",
    standard_vat_rate=0.19,
    reduced_vat_rate=0.07,
    chart_of_accounts={
        "software": ("4980", "Software Licenses"),
        "office_supplies": ("4930", "Office Supplies"),
        "travel": ("4660", "Business Travel"),
        "meals": ("4650", "Business Meals"),
        "cloud_services": ("4980", "Cloud Services"),
    },
    reverse_charge_vendors=["amazon web services", "google ireland", "microsoft ireland", "github"],
)

FR_POLICY = MarketPolicy(
    market="FR",
    standard_vat_rate=0.20,
    reduced_vat_rate=0.10,  # Note: FR has 4 rates — simplify to 2 for v1
    chart_of_accounts={
        "software": ("628", "Software and IT Services"),
        "office_supplies": ("606", "Office Supplies"),
        "travel": ("625", "Business Travel"),
        "meals": ("625", "Restaurant / Meals"),
    },
    reverse_charge_vendors=["amazon web services", "google ireland", "microsoft ireland"],
)
```

---

## Categorization Stage (AI Stub)

```python
import asyncio

CATEGORY_KEYWORDS = {
    "software": ["github", "aws", "azure", "google cloud", "stripe", "heroku"],
    "office_supplies": ["bürobedarf", "staples", "office depot", "paper"],
    "travel": ["bahn", "lufthansa", "uber", "taxi", "hotel"],
    "meals": ["restaurant", "cafe", "münchen", "essen", "lunch"],
    "cloud_services": ["amazon web services", "azure", "google cloud"],
}

async def categorize(tx: TransactionInput, policy: MarketPolicy) -> CategoryResult:
    """AI step — keyword stub; production uses LLM with structured output."""
    vendor_lower = tx.vendor.lower()
    desc_lower = tx.description.lower()
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in vendor_lower or kw in desc_lower for kw in keywords):
            # High confidence for known vendors
            confidence = 0.92 if any(kw in vendor_lower for kw in keywords) else 0.71
            code, name = policy.get_account(category)
            return CategoryResult(
                account_code=code,
                account_name=name,
                confidence=confidence,
                reasoning=f"Matched keyword pattern for {category}",
            )
    
    # Unknown merchant — low confidence
    code, name = policy.get_account("unknown")
    return CategoryResult(
        account_code="4999",
        account_name="Miscellaneous",
        confidence=0.35,
        reasoning="No keyword match — requires human review",
    )
```

---

## VAT and Routing (Deterministic)

```python
def calculate_vat(tx: TransactionInput, category: CategoryResult, policy: MarketPolicy) -> VatResult:
    """Deterministic — tax law is not a prediction."""
    # Reverse charge overrides everything
    if policy.is_reverse_charge(tx.vendor) and tx.is_b2b:
        return VatResult(
            vat_rate=0.0,
            net_amount=tx.amount,
            vat_amount=0.0,
            mechanism="reverse_charge",
        )
    
    # Reduced rate items
    reduced_categories = {"meals", "books", "public_transport"}
    rate = (
        policy.reduced_vat_rate
        if any(k in category.account_name.lower() for k in ["food", "book", "train"])
        else policy.standard_vat_rate
    )
    
    net = tx.amount / (1 + rate)
    vat = tx.amount - net
    return VatResult(
        vat_rate=rate,
        net_amount=round(net, 2),
        vat_amount=round(vat, 2),
        mechanism="standard",
    )

AUTO_BOOK_THRESHOLD = 0.85
PROPOSAL_THRESHOLD = 0.55

def route(tx: TransactionInput, category: CategoryResult, vat: VatResult) -> RoutingStatus:
    """Deterministic routing — confidence thresholds + compliance overrides."""
    # Reverse charge is a hard compliance override
    if vat.mechanism == "reverse_charge":
        return RoutingStatus.REQUIRES_REVIEW
    
    if category.confidence >= AUTO_BOOK_THRESHOLD:
        return RoutingStatus.AUTO_BOOKED
    if category.confidence >= PROPOSAL_THRESHOLD:
        return RoutingStatus.PROPOSAL_SENT
    return RoutingStatus.REJECTED
```

---

## Orchestrator with Trace

```python
import time

async def process_transaction(tx: TransactionInput, policy: MarketPolicy) -> WorkflowResult:
    trace = []
    
    # Stage 1: Categorize (AI)
    t0 = time.monotonic()
    category = await categorize(tx, policy)
    trace.append({"stage": "categorize", "ms": round((time.monotonic() - t0) * 1000), 
                  "confidence": category.confidence})
    
    # Stage 2: VAT calculation (deterministic)
    t1 = time.monotonic()
    vat = calculate_vat(tx, category, policy)
    trace.append({"stage": "vat", "ms": round((time.monotonic() - t1) * 1000),
                  "mechanism": vat.mechanism})
    
    # Stage 3: Route (deterministic)
    t2 = time.monotonic()
    status = route(tx, category, vat)
    trace.append({"stage": "route", "ms": round((time.monotonic() - t2) * 1000),
                  "decision": status.value})
    
    return WorkflowResult(
        transaction_id=tx.id,
        status=status,
        category=category,
        vat=vat,
        trace=trace,
    )
```

---

## Async Batch (Bounded Concurrency)

```python
import asyncio
from asyncio import Semaphore

async def process_batch(
    transactions: list[TransactionInput],
    policy: MarketPolicy,
    max_concurrent: int = 5,
) -> list[WorkflowResult]:
    """Bounded async fan-out — not unbounded asyncio.gather."""
    sem = Semaphore(max_concurrent)
    
    async def bounded(tx: TransactionInput) -> WorkflowResult:
        async with sem:
            return await process_transaction(tx, policy)
    
    return await asyncio.gather(*[bounded(tx) for tx in transactions])
```

**Say**: "The semaphore is the control point. Unbounded `asyncio.gather` looks clean but destabilizes the provider under load. I keep concurrency bounded and measurable."

---

## Test Cases (Run These Live)

```python
async def run_demo():
    # Happy path — auto-book
    t1 = TransactionInput(id="t1", vendor="GitHub Inc", amount=10.0, market=Market.DE, 
                          description="Pro subscription")
    r1 = await process_transaction(t1, DE_POLICY)
    assert r1.status == RoutingStatus.AUTO_BOOKED
    print(f"✓ t1: {r1.status.value} ({r1.category.confidence:.2f} confidence)")
    
    # Unknown merchant — proposal
    t2 = TransactionInput(id="t2", vendor="Müller GmbH", amount=89.0, market=Market.DE,
                          description="Unknown service")
    r2 = await process_transaction(t2, DE_POLICY)
    assert r2.status == RoutingStatus.REJECTED  # confidence < 0.55
    print(f"✓ t2: {r2.status.value} (unknown merchant, low confidence)")
    
    # Reverse charge — always surfaces
    t3 = TransactionInput(id="t3", vendor="Amazon Web Services Ireland", amount=320.0, 
                          market=Market.DE, is_b2b=True)
    r3 = await process_transaction(t3, DE_POLICY)
    assert r3.status == RoutingStatus.REQUIRES_REVIEW
    assert r3.vat.mechanism == "reverse_charge"
    print(f"✓ t3: {r3.status.value} (§13b reverse charge override)")
    
    print("\nAll assertions passed. System routes correctly.")

if __name__ == "__main__":
    asyncio.run(run_demo())
```

---

## One-Line Python Equivalences (TypeScript → Python)

| TypeScript | Python |
|-----------|--------|
| `z.object({...})` | `class Model(BaseModel)` |
| `z.enum([...])` | `class Enum(str, Enum)` |
| `type Foo = z.infer<...>` | `model: Foo` type annotation |
| `interface Foo { ... }` | `class Foo(BaseModel)` |
| `async function f()` | `async def f()` |
| `await Promise.all(...)` | `await asyncio.gather(...)` |
| `z.number().min(0).max(1)` | `confidence: float  # 0-1, validate separately` |
