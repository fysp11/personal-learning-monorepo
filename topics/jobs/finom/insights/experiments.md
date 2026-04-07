# Finom — Technical Experiments

Hands-on projects to build domain competence and demonstrate skills for the 2nd round. Each experiment is scoped to 2-4 hours.

---

## Experiment 1: MCP Skill Server for Accounting

**Goal**: Build a working MCP server that exposes accounting-related tools — demonstrates MCP fluency and maps directly to Finom's architecture.

### Setup
```bash
pip install mcp pydantic
```

### MCP Server: German Accounting Skills
```python
from mcp.server import Server
from mcp.types import Tool, TextContent
import json

app = Server("accounting-skills")

@app.tool()
async def categorize_transaction(
    merchant_name: str,
    amount: float,
    description: str,
    country: str = "DE"
) -> list[TextContent]:
    """Categorize a bank transaction to SKR03 account code.

    Args:
        merchant_name: Name of the merchant
        amount: Transaction amount in EUR
        description: Transaction description from bank
        country: ISO country code (DE, FR, IT, ES, NL)
    """
    # In production: call LLM with structured output
    # For demo: rule-based + LLM fallback
    categories = {
        "restaurant": {"skr03": "4650", "name": "Bewirtungskosten", "vat": 0.19},
        "office": {"skr03": "4930", "name": "Bürobedarf", "vat": 0.19},
        "software": {"skr03": "4964", "name": "EDV-Kosten", "vat": 0.19},
        "travel": {"skr03": "4660", "name": "Reisekosten", "vat": 0.19},
        "postage": {"skr03": "4910", "name": "Porto", "vat": 0.19},
    }
    # Simplified classification logic
    result = classify(merchant_name, description, categories)
    return [TextContent(type="text", text=json.dumps(result))]

@app.tool()
async def calculate_vat(
    amount: float,
    category_code: str,
    country: str = "DE",
    is_b2b_intra_eu: bool = False,
    counterparty_vat_id: str | None = None
) -> list[TextContent]:
    """Calculate VAT for a transaction. Deterministic rules engine.

    Args:
        amount: Gross transaction amount in EUR
        category_code: SKR03 account code
        country: ISO country code
        is_b2b_intra_eu: Whether this is an intra-EU B2B transaction
        counterparty_vat_id: EU VAT ID of counterparty (for reverse charge)
    """
    vat_rates = {
        "DE": {"standard": 0.19, "reduced": 0.07},
        "FR": {"standard": 0.20, "reduced": 0.055},
        "IT": {"standard": 0.22, "reduced": 0.10},
        "ES": {"standard": 0.21, "reduced": 0.10},
        "NL": {"standard": 0.21, "reduced": 0.09},
    }

    if is_b2b_intra_eu and counterparty_vat_id:
        # Reverse charge: 0% VAT, buyer accounts for it
        return [TextContent(type="text", text=json.dumps({
            "gross": amount,
            "net": amount,
            "vat_amount": 0,
            "vat_rate": 0,
            "mechanism": "reverse_charge",
            "note": f"Reverse charge applies. Counterparty VAT: {counterparty_vat_id}"
        }))]

    rate = vat_rates.get(country, {}).get("standard", 0.19)
    net = round(amount / (1 + rate), 2)
    vat_amount = round(amount - net, 2)

    return [TextContent(type="text", text=json.dumps({
        "gross": amount,
        "net": net,
        "vat_amount": vat_amount,
        "vat_rate": rate,
        "mechanism": "standard",
        "country": country
    }))]

@app.tool()
async def create_booking_entry(
    date: str,
    description: str,
    debit_account: str,
    credit_account: str,
    amount: float,
    vat_amount: float | None = None,
    vat_account: str = "1576"  # Vorsteuer in SKR03
) -> list[TextContent]:
    """Create a double-entry bookkeeping record (Buchungssatz).

    Args:
        date: Transaction date (YYYY-MM-DD)
        description: Booking description
        debit_account: SKR03 account to debit
        credit_account: SKR03 account to credit
        amount: Net transaction amount
        vat_amount: VAT amount (if applicable)
        vat_account: VAT account code (default: 1576 Vorsteuer)
    """
    entries = [
        {"account": debit_account, "debit": amount, "credit": 0},
        {"account": credit_account, "debit": 0, "credit": amount + (vat_amount or 0)},
    ]
    if vat_amount:
        entries.append({"account": vat_account, "debit": vat_amount, "credit": 0})

    return [TextContent(type="text", text=json.dumps({
        "date": date,
        "description": description,
        "entries": entries,
        "balanced": True
    }))]
```

### Test with Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "accounting": {
      "command": "python",
      "args": ["-m", "accounting_skills"]
    }
  }
}
```

### Interview Talking Point
"I built an MCP server exposing German accounting skills — categorization, VAT calculation, and double-entry booking. The key design decision was making VAT calculation deterministic (rule engine, not LLM) while keeping categorization LLM-powered. For financial operations, you need to separate 'judgment calls' from 'compliance math'."

---

## Experiment 2: Multi-Agent Transaction Pipeline

**Goal**: Build an end-to-end multi-agent pipeline that processes a bank transaction from receipt to booking entry.

### Architecture
```python
from langgraph.graph import StateGraph
from pydantic import BaseModel

class TransactionState(BaseModel):
    # Input
    transaction_id: str
    merchant: str
    amount: float
    date: str
    country: str = "DE"
    receipt_text: str | None = None

    # Progressive enrichment
    category: dict | None = None
    category_confidence: float = 0.0
    vat_calculation: dict | None = None
    booking_entry: dict | None = None
    needs_review: bool = False
    review_reason: str | None = None

# Build the graph
graph = StateGraph(TransactionState)

graph.add_node("extract_receipt", extract_receipt_info)
graph.add_node("categorize", categorize_transaction)
graph.add_node("calculate_vat", calculate_vat)
graph.add_node("create_booking", create_booking_entry)
graph.add_node("validate", validate_booking)
graph.add_node("route_review", route_for_review)

graph.add_edge("extract_receipt", "categorize")
graph.add_edge("categorize", "route_review")
graph.add_conditional_edges(
    "route_review",
    lambda state: "calculate_vat" if not state.needs_review else "human_review",
    {"calculate_vat": "calculate_vat", "human_review": END}
)
graph.add_edge("calculate_vat", "create_booking")
graph.add_edge("create_booking", "validate")

graph.set_entry_point("extract_receipt")
pipeline = graph.compile()
```

### Test Scenarios
| Scenario | Expected Behavior |
|----------|-------------------|
| German restaurant receipt, €45.80 | Categorize → Bewirtungskosten, 19% VAT, auto-book |
| Unknown merchant, €2,500 | Low confidence → route to review |
| UK vendor, B2B, no VAT ID | Flag: might need reverse charge, needs review |
| Amazon receipt, mixed items | Split categorization, multiple booking entries |
| Duplicate transaction | Detect and flag, do not double-book |

### Interview Talking Point
"I built a LangGraph-based multi-agent pipeline for German transaction processing. The most interesting challenge was confidence-based routing — the categorization agent outputs a confidence score, and anything below 0.85 gets queued for human review rather than auto-booked. This prevents the 'wrong tax filing' failure mode while still automating the 90% of transactions that are straightforward."

---

## Experiment 3: Polyglot C#/.NET + Python Service

**Goal**: Build a minimal integration between a C# service and Python AI service — demonstrates ability to work in Finom's polyglot stack.

### Architecture
```
C# Service (Transaction API)           Python Service (AI Categorizer)
  ├─ POST /transactions                  ├─ POST /categorize
  ├─ GET /transactions/{id}              ├─ POST /extract-receipt
  └─ POST /transactions/{id}/book        └─ GET /health
         │                                       │
         └──── gRPC or HTTP ────────────────────┘
```

### C# Service (minimal)
```csharp
// TransactionService.cs
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/transactions")]
public class TransactionController : ControllerBase
{
    private readonly HttpClient _aiClient;

    public TransactionController(IHttpClientFactory factory)
    {
        _aiClient = factory.CreateClient("AICategorizer");
    }

    [HttpPost("{id}/categorize")]
    public async Task<IActionResult> Categorize(string id)
    {
        var transaction = await GetTransaction(id);
        var response = await _aiClient.PostAsJsonAsync("/categorize", new
        {
            merchant = transaction.Merchant,
            amount = transaction.Amount,
            description = transaction.Description
        });
        var category = await response.Content.ReadFromJsonAsync<CategoryResult>();
        return Ok(category);
    }
}
```

### Python Service (FastAPI)
```python
from fastapi import FastAPI
from pydantic import BaseModel
import openai

app = FastAPI()

class CategorizeRequest(BaseModel):
    merchant: str
    amount: float
    description: str

class CategoryResult(BaseModel):
    skr03_code: str
    category_name: str
    confidence: float
    vat_rate: float

@app.post("/categorize", response_model=CategoryResult)
async def categorize(req: CategorizeRequest) -> CategoryResult:
    # LLM-based categorization with structured output
    response = await openai.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_schema", "json_schema": CategoryResult.model_json_schema()},
        messages=[{
            "role": "system",
            "content": "Categorize this German business transaction to SKR03 account code."
        }, {
            "role": "user",
            "content": f"Merchant: {req.merchant}, Amount: {req.amount}€, Description: {req.description}"
        }]
    )
    return CategoryResult.model_validate_json(response.choices[0].message.content)
```

### Interview Talking Point
"I prototyped a C#/.NET + Python polyglot integration to get comfortable with Finom's stack. The C# service handles transaction domain logic while Python handles LLM-based categorization. The key learning was that the service boundary should align with the 'judgment vs. compliance' split — deterministic financial logic in C#, probabilistic AI in Python."

---

## Experiment 4: Agent Evaluation Framework for Financial Accuracy

**Goal**: Build an evaluation pipeline that measures categorization accuracy across EU markets.

### Dataset
Create a synthetic evaluation dataset:
```python
eval_cases = [
    {
        "merchant": "Büro Discount GmbH",
        "amount": 89.50,
        "country": "DE",
        "expected_skr03": "4930",
        "expected_category": "Bürobedarf",
        "expected_vat_rate": 0.19
    },
    {
        "merchant": "SNCF",
        "amount": 120.00,
        "country": "FR",
        "expected_pcg": "625",
        "expected_category": "Déplacements",
        "expected_vat_rate": 0.10
    },
    # ... 100+ cases across DE, FR, IT, ES, NL
]
```

### Metrics
- **Category accuracy**: Exact match on chart-of-accounts code
- **VAT accuracy**: Correct rate selection (critical — wrong VAT = compliance issue)
- **Confidence calibration**: Is 0.9 confidence actually 90% accurate?
- **Cross-market consistency**: Same merchant categorized consistently across markets
- **Edge case handling**: Reverse charge, exempt, split-rate detection

### Evaluation Report Output
```
Market  | Category Acc. | VAT Acc. | Avg Confidence | Calibration Error
--------|--------------|----------|----------------|------------------
DE      | 92.3%        | 97.1%    | 0.87           | 0.04
FR      | 88.1%        | 95.6%    | 0.82           | 0.07
IT      | 85.7%        | 94.2%    | 0.79           | 0.06
ES      | 87.4%        | 96.0%    | 0.81           | 0.05
NL      | 91.0%        | 97.5%    | 0.85           | 0.03
```

### Interview Talking Point
"I built an eval framework testing categorization accuracy across 5 EU markets. The key finding was that VAT accuracy must be near-perfect (>95%) because errors compound into compliance risk, while category accuracy can tolerate more flexibility since users can correct it. This informed the confidence threshold design — VAT routing is stricter than category routing."

---

## Priority Order
1. **Experiment 1** (MCP Skill Server) — highest signal, maps to Finom's architecture directly
2. **Experiment 2** (Multi-Agent Pipeline) — demonstrates LangGraph + production agent design
3. **Experiment 4** (Eval Framework) — shows measurement mindset Dmitry values
4. **Experiment 3** (Polyglot Service) — nice to have, shows willingness to work in C#
