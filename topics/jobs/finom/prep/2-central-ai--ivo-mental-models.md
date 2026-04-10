# Finom Ivo Interview - Mental Models

Saved: 2026-04-08

## Purpose

Compact note for two reusable ideas:
- the sharpened `zoom in / zoom out` model
- the best decomposition example grounded in Finom's AI accounting context

---

## 1. Sharpened Model

### Core idea

`Zoom in` to decompose AI work into smaller, evaluatable joints.

`Zoom out` to make sure the workflow creates real user and business value.

### The useful split

- Let AI handle `linguistic ambiguity`
- Let deterministic systems handle `policy, control, and execution`

### Practical rule

Ask:
- is this step mostly language understanding, messy interpretation, or semantic matching?
- or is this step applying explicit business logic, regulatory logic, thresholds, or write permissions?

If it is mostly ambiguity, AI may be the right tool.

If it is mostly policy or consequence, keep it deterministic.

### Interview-ready line

> I zoom in to decompose AI work into observable joints, and zoom out to make sure the workflow actually creates product value. AI should handle linguistic ambiguity; deterministic systems should handle policy and control.

### If challenged on over-decomposition

Use this answer:

> I do not decompose for elegance. I decompose where failure cost is meaningful or where the model's reasoning would otherwise stay opaque. If a step is cheap, low-risk, and easy to evaluate end-to-end, I keep it simple. If a step has accounting, tax, or compliance risk, I want smaller joints so I can measure, constrain, and improve them.

Short version:

> I decompose only where control buys safety or debuggability.

### Product bridge

`Zoom in` protects workflow quality.

`Zoom out` checks whether the workflow improves:
- activation
- trust
- retention
- expansion

Strongest quick link:

`safety -> trust -> activation`

If the first AI workflow feels opaque or risky, users will not adopt it enough to realize value.

### 3-layer model

`Star = control layer`
- rules
- thresholds
- approvals
- auditability
- deterministic logic

`Planets = workflow joints`
- extraction
- classification
- reconciliation
- proposal
- routing

`System = product/business layer`
- user trust
- activation
- retention
- cross-surface leverage
- org ownership

20-second version:

> I think in three layers: control, workflow, and product. The control layer defines what AI is allowed to do, the workflow layer defines the joints where AI helps, and the product layer checks whether that help creates actual user and business value.

---

## 2. Best Decomposition Example

### Use this, not "file my taxes"

Best example:

`invoice -> VAT treatment -> booking draft`

Why this works:
- close to Finom's AI accounting reality
- small enough to evaluate
- meaningful enough to show judgment
- naturally separates AI work from deterministic tax/accounting logic

### Bad monolith

Bad prompt shape:

> Here is an invoice. Categorize it, decide VAT treatment, and book it.

Why it is weak:
- one opaque output
- one vague confidence score
- no local failure detection
- hard to improve safely

### Mental ingest view

Think of the workflow as a small file tree, not as one prompt:

```text
invoice_workflow/
├── 00_document_quality_gate
│   └── "is this input usable at all?"
├── 10_extract_fields
│   └── vendor, amount, date, VAT ID, line items
├── 20_normalize_vendor
│   └── match against known vendors / history
├── 30_classify_expense_intent
│   └── "what was this purchase actually for?"
├── 40_retrieve_tax_rules
│   └── only rules valid for this date/country/transaction type
├── 50_apply_vat_policy
│   └── deterministic VAT / reverse-charge decision
├── 60_build_booking_draft
│   └── SKR03 booking entry
├── 70_route_case
│   └── auto-complete / propose / human review
└── 80_request_missing_variable
    └── ask one targeted question if blocked
```

Another useful mental split:

```text
AI handles:
├── messy extraction
├── semantic classification
└── ambiguous vendor / intent interpretation

Deterministic code handles:
├── policy rules
├── thresholds
├── write permissions
├── accounting math
└── audit / routing logic
```

### Better decomposition

1. `Document quality gate`
Check whether the image / OCR quality is usable.
Deterministic checks.

2. `Field extraction`
Extract vendor, amount, date, VAT ID, line items.
AI / OCR joint.

3. `Vendor normalization`
Match to known vendor records or historical patterns.
Retrieval + deterministic matching.

4. `Workflow class`
Is this low-risk recurring domestic spend or a high-risk complex exception?
Deterministic routing policy.

5. `Expense intent classification`
What was the purchase actually for?
This is a strong AI joint because it is linguistic and contextual.

6. `Tax rule retrieval`
Retrieve only the tax rules valid for that date, geography, and transaction type.
Deterministic metadata filtering first, semantic retrieval second.

7. `VAT decision`
Apply deductible / reverse-charge / domestic treatment.
Deterministic rule engine.

8. `Booking draft`
Map the result into SKR03 / bookkeeping structure.
Deterministic accounting logic.

9. `Routing`
Auto-complete, propose, or force review.
Workflow policy, not one global model score.

10. `Human micro-review`
If something critical is missing, ask for one targeted input instead of dumping failure details.

### Joint-by-joint breakdown

#### Joint 0: document quality gate

Question:

> Is this input good enough for downstream automation?

Use deterministic checks for:
- OCR completeness
- missing totals
- missing date
- unreadable image quality
- unsupported document type

Why this matters:

Do not let low-quality input poison the rest of the workflow.

#### Joint 1: field extraction

Question:

> What facts can I reliably extract from the document?

Typical outputs:
- vendor
- gross amount
- currency
- date
- VAT ID
- line items

This is a good AI / OCR joint because the task is messy and document-shaped.

Metric:
- field-level extraction accuracy

Failure mode:
- extraction looks plausible but misses one critical field

#### Joint 2: vendor normalization

Question:

> Is this vendor already known in the system?

Typical methods:
- deterministic exact match
- fuzzy match
- retrieval over vendor history

Why this matters:

Vendor normalization is one of the best ways to reduce ambiguity before asking the AI to reason.

Metric:
- vendor-match rate
- false-match rate

Failure mode:
- wrong vendor history pollutes downstream categorization

#### Joint 3: workflow class

Question:

> What risk class is this case?

Examples:
- low-risk recurring domestic telecom invoice
- medium-risk unusual merchant but standard VAT path
- high-risk cross-border hardware purchase with reverse-charge implications

This should stay deterministic because the purpose is control, not cleverness.

Metric:
- routing precision by workflow class

Failure mode:
- system gives high autonomy to the wrong case class

#### Joint 4: expense intent classification

Question:

> What is this purchase actually for in business terms?

Examples:
- office supplies
- software subscription
- travel
- meals / entertainment

This is one of the best AI joints because:
- merchant strings are messy
- descriptions are linguistic
- user history and context help

Metric:
- classification agreement rate vs reviewer outcome

Failure mode:
- plausible but wrong category with high confidence

#### Joint 5: tax rule retrieval

Question:

> Which rules are relevant for this exact transaction?

Important principle:

Do deterministic filtering first:
- country
- effective date
- transaction type
- B2B vs B2C

Only then do semantic retrieval.

Why this matters:

It prevents "technically retrieved but legally irrelevant" context from entering the model.

Metric:
- retrieval precision for relevant rules

Failure mode:
- correct text from the wrong period or wrong jurisdiction

#### Joint 6: VAT decision

Question:

> Given the classified intent and retrieved context, what VAT mechanism applies?

This should be deterministic because:
- the branch logic is explicit
- the cost of error is high
- it must be testable and auditable

Examples:
- standard VAT
- reduced VAT
- exempt
- reverse charge

Metric:
- VAT rule correctness

Failure mode:
- legal/compliance error, even when extraction was otherwise fine

#### Joint 7: booking draft

Question:

> How should this become a balanced accounting entry?

This is deterministic accounting logic:
- debit expense account
- debit input VAT account when applicable
- credit bank

Metric:
- balanced-entry rate
- correct account mapping

Failure mode:
- technically valid extraction but invalid accounting entry

#### Joint 8: routing

Question:

> Should this auto-complete, draft, or stop for review?

This is a workflow policy, not a model output.

Inputs to routing:
- workflow class
- extraction quality
- classification confidence
- tax rule certainty
- downstream consequence

Metric:
- severe error rate
- reviewability / intervention rate
- unnecessary escalation rate

Failure mode:
- one global confidence score masks local risk

#### Joint 9: human micro-review

Question:

> What is the smallest useful question to ask the human?

Good review shape:
- preserve successful work
- isolate the missing variable
- ask for one targeted confirmation or input

Bad review shape:
- dump raw payloads
- ask user to debug the pipeline

Metric:
- approval-without-edit rate
- correction capture quality
- time-to-resolution

Failure mode:
- fake safety through exhausting human review

### Joint ownership cheat sheet

```text
00_document_quality_gate      -> deterministic
10_extract_fields             -> AI / OCR
20_normalize_vendor           -> retrieval + deterministic matching
30_classify_expense_intent    -> AI
40_retrieve_tax_rules         -> deterministic filter + semantic retrieval
50_apply_vat_policy           -> deterministic
60_build_booking_draft        -> deterministic
70_route_case                 -> deterministic workflow policy
80_request_missing_variable   -> AI-assisted UX payload, deterministic trigger
```

### Why this is strong

This example lets you say:

- AI handles ambiguity
- software handles policy
- each joint has its own metric
- failures become local instead of global
- autonomy is earned by workflow class

### Example of targeted intervention

Good example:

The system extracts vendor name, amount, and date, but cannot verify the VAT ID needed for reverse-charge treatment.

Bad UX:
- dump JSON into a review queue
- ask the user to debug the whole workflow

Good UX:
- preserve the successful extraction
- halt autonomous execution
- ask one clean question:

> I matched this invoice to the Dublin vendor, but I cannot verify the vendor VAT ID needed for reverse-charge treatment. Can you provide the VAT ID or confirm this should be handled as a domestic expense?

That turns failure into a collaborative workflow instead of a trust-breaking workflow.

### Code-backed mental model

#### 1. The orchestrator should enforce explicit stage boundaries

From the MAS demo:

```ts
const classResult = await this.classificationAgent.execute(doc, trace);
results.classification = classResult.data;

const extractResult = await this.extractionAgent.execute(doc, trace);
results.extraction = extractResult.data;

if (!extractResult.success || extractResult.confidence === 'low') {
  trace.log({ agentId: 'orchestrator', event: 'circuit_break', details: 'Extraction too low confidence' });
  return { status: 'escalated', reason: 'Extraction confidence too low for automated processing', trace: trace.summary(), results };
}
```

Why this matters:
- extraction is evaluated separately
- failure is local and visible
- low-confidence upstream output stops unsafe downstream automation

#### 2. Categorization is a good AI joint because it has layered signals

From the categorizer:

```python
# Priority:
# 1. User history
# 2. Merchant keyword rules
# 3. Description analysis
# 4. Default fallback

if user_history and merchant_lower in user_history:
    ...

for keyword, (code, reason) in MERCHANT_RULES.items():
    if keyword in merchant_lower:
        ...
```

Why this matters:
- AI is not the first move
- known patterns should collapse ambiguity before the model reasons
- the fallback can stay AI-assisted but bounded

#### 3. VAT logic should not be left to model intuition

From the VAT engine:

```python
if is_b2b_intra_eu and counterparty_vat_id:
    return VATResult(
        gross=amount,
        net=amount,
        vat_amount=0.0,
        vat_rate=0.0,
        mechanism=VATMechanism.REVERSE_CHARGE,
        ...
    )
```

Why this matters:
- explicit branch
- testable rule
- no "LLM felt confident" logic

#### 4. Booking is accounting math, not language reasoning

From the booking engine:

```python
lines.append(JournalLine(
    account=expense_account,
    account_name=expense_account_name,
    debit=net_amount,
    credit=0.0,
))

lines.append(JournalLine(
    account=BANK_ACCOUNT,
    account_name=ACCOUNT_NAMES[BANK_ACCOUNT],
    debit=0.0,
    credit=gross_amount,
))
```

Why this matters:
- once classification and VAT are settled, booking becomes structured accounting logic
- this joint should be deterministic, balanced, and easy to test

### Repo-shaped visual

This is a useful way to remember the decomposition against your repo:

```text
topics/jobs/finom/
├── code/
│   ├── accounting-mas-pipeline.ts
│   │   ├── classification agent
│   │   ├── extraction agent
│   │   ├── reconciliation agent
│   │   └── categorization agent
│   └── README.md
├── experiments/
│   └── mcp-accounting-skills/
│       └── accounting_skills/
│           ├── categorizer.py   -> "AI / heuristic intent joint"
│           ├── vat.py           -> "deterministic tax policy joint"
│           └── booking.py       -> "deterministic accounting execution joint"
└── prep/
    └── 2-central-ai--ivo-mental-models.md
```

Or in pure workflow form:

```text
raw invoice
  -> extract facts
  -> normalize vendor
  -> classify intent
  -> retrieve tax context
  -> apply VAT rules
  -> build booking draft
  -> route by risk
  -> ask one targeted question if blocked
```

### Rollout logic

1. `Shadow mode`
Run in parallel, compare against human ground truth, do not commit.

2. `Proposal mode`
Draft categorization / VAT / booking suggestions for approval.

3. `Selective autonomy`
Only automate narrow workflow classes that have earned trust.

Key line:

> Autonomy should be earned by workflow class, not declared globally.

### Metrics to mention

Per-joint metrics:
- extraction accuracy
- vendor-match rate
- classification agreement rate
- VAT-rule correctness

Workflow metrics:
- approval rate
- override rate
- severe error rate
- reviewability / intervention rate
- time saved

### Interview-ready answer

> I would not use "file the taxes" as my decomposition example because it is too broad and hides the control points. I would use "draft VAT treatment and booking for a single invoice." That is the right unit: small enough to evaluate, important enough to matter, and close to Finom's actual accounting AI. The AI should classify ambiguous intent; deterministic systems should own tax policy, booking logic, and routing.

### 60-second walkthrough version

> A good decomposition example at Finom is not "do the taxes," it is "draft VAT treatment and booking for one invoice." I would break that into document quality, extraction, vendor normalization, workflow class, expense-intent classification, tax-rule retrieval, deterministic VAT application, booking draft, and routing. The AI should own the ambiguous joints like extraction and intent classification. Deterministic systems should own tax policy, accounting math, and write permissions. That way each joint has its own metric, failures become local, and autonomy can be earned by workflow class rather than declared globally.

---

## 3. Central AI Link

This example also supports the central AI thesis.

`Central AI should own`
- reusable control patterns
- evaluation standards
- observability
- shared routing / approval rails
- retrieval and workflow primitives

`Product teams should own`
- workflow UX
- domain outcomes
- prioritization
- customer context

One-liner:

> Central AI should own the reusable hard parts: control, evals, observability, and shared workflow primitives. Product teams should own workflow outcomes.

---

## Related Notes

- `2-central-ai--ivo-simulation-2-ai-accounting-risk.md`
- `2-central-ai--ivo-day-of-card.md`
- `2-central-ai--ivo-question-drafting-strategy.md`
- `multi-agent-system-architecture-for-fintech.md`
- `../code/README.md`
- `../experiments/mcp-accounting-skills/README.md`
