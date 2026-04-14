# Live Round Clock Guide — 60-Minute Timer

**Format**: 30 min technical questions → 60 min live problem-solving with Claude Code or Codex  
**This guide**: the 60-minute live coding block only

---

## Pre-Clock (before the timer starts)

**Listen for the problem statement. Extract these five things before touching the keyboard:**

1. Input — what comes in (raw doc, transaction list, vendor string)?
2. Output — what must come out (booking record, proposal, batch report)?
3. Failure cost — what's the worst kind of wrong answer (wrong VAT rate = critical, wrong description = low)?
4. Automation boundary — what should auto-complete vs surface for review?
5. Market — Germany, France, or abstract?

If unclear: "Before I start — can I confirm the failure cost hierarchy? I want to make sure I weight my routing decisions correctly."

---

## Minute 0–5 — Scope and Contracts

**Deliverable**: Zod types (TypeScript) or Pydantic models (Python) for input, output, and confidence envelope on screen.

**If Python**, key translations: `z.object` → `class Model(BaseModel)`, `z.enum` → `class Enum(str, Enum)`, `z.number()` → `float`, `z.string()` → `str`. Full reference: `prep/3-python-live-round-cheatsheet.md`.

```typescript
// What comes in
const TransactionInput = z.object({
  id: z.string(),
  vendor: z.string(),
  amount: z.number(),
  market: z.enum(["DE", "FR"]),
  description: z.string().optional(),
});

// What comes out of each stage
const CategoryResult = z.object({
  category: z.string(),
  confidence: z.number().min(0).max(1),
  reasoning: z.string(),
});

const BookingRecord = z.object({
  accountCode: z.string(),   // SKR03 or PCG
  vatRate: z.number(),
  mechanism: z.enum(["standard", "reverse_charge", "exempt"]),
  status: z.enum(["auto_booked", "proposal_sent", "rejected", "requires_review"]),
});
```

**Say while typing**: "I always define contracts first — these become the forcing function for every stage downstream, and they're what you test against."

**Recovery pivot if behind**: Skip optional fields, just get the core input/output shapes in.

---

## Minute 5–12 — Market Policy Config

**Deliverable**: At least one `MarketPolicy` object (DE) with VAT rates and account code prefix.

```typescript
const DE_POLICY = {
  market: "DE" as const,
  vatRates: { standard: 0.19, reduced: 0.07 },
  chartOfAccounts: "SKR03",
  accountCodes: {
    office_supplies: "4930",
    software: "4980",
    travel: "4660",
    meals: "4650",
  },
  reverseChargeApplies: (vendor: string) =>
    ["amazon web services", "google ireland", "microsoft ireland"].some(v =>
      vendor.toLowerCase().includes(v)
    ),
};
```

**Say**: "I put market configuration in data, not code — adding France means adding `FR_POLICY`, not changing the pipeline. VAT calculation stays deterministic; only categorization goes near the LLM."

**Recovery pivot if behind**: Inline the config directly in the function call, annotate with `// TODO: extract to policy object`.

---

## Minute 12–22 — Categorization Stage (AI Step)

**Deliverable**: `categorize()` function that returns `CategoryResult` with confidence.

```typescript
async function categorize(
  input: TransactionInput,
  policy: typeof DE_POLICY
): Promise<CategoryResult> {
  // Simulate LLM call — in production this calls the model
  // Key: return confidence, not just a label
  const result = await llmCategorize(input.vendor, input.description);

  return CategoryResult.parse({
    category: result.category,
    confidence: result.confidence,
    reasoning: result.reasoning,
  });
}
```

**Say**: "This is the only stage that touches the LLM. Everything downstream is deterministic. The confidence score here drives routing — that's the contract the rest of the pipeline depends on."

**Interviewer question likely here**: "What if confidence is 0.72?"  
**Answer**: "0.72 lands in the proposal zone — above the 0.55 floor but below 0.85 auto-book. We generate a structured proposal and wait for confirmation. We never auto-book that."

**Recovery pivot if behind**: Stub with `return { category: "software", confidence: 0.9, reasoning: "mock" }` and move on — structure matters more than the LLM call simulation.

---

## Minute 22–32 — VAT and Booking Stages (Deterministic)

**Deliverable**: `calculateVat()` and `createBooking()` as pure functions.

```typescript
function calculateVat(
  category: string,
  vendor: string,
  policy: typeof DE_POLICY
): { vatRate: number; mechanism: "standard" | "reverse_charge" | "exempt" } {
  // Reverse charge always wins — deterministic, never LLM
  if (policy.reverseChargeApplies(vendor)) {
    return { vatRate: 0, mechanism: "reverse_charge" };
  }
  const rate = ["train", "book", "food"].some(k => category.includes(k))
    ? policy.vatRates.reduced
    : policy.vatRates.standard;
  return { vatRate: rate, mechanism: "standard" };
}

function createBooking(
  input: TransactionInput,
  category: string,
  vat: ReturnType<typeof calculateVat>,
  policy: typeof DE_POLICY
): BookingRecord {
  return {
    accountCode: policy.accountCodes[category as keyof typeof policy.accountCodes] ?? "4999",
    vatRate: vat.vatRate,
    mechanism: vat.mechanism,
    status: "auto_booked", // overridden by router
  };
}
```

**Say**: "VAT is deterministic — it must be. If I let the LLM calculate VAT rates I've mixed policy into the AI layer, and now I can't test it independently or audit it for GoBD compliance."

**Recovery pivot if behind**: Inline `vatRate = 0.19` as a constant, note "this would be driven by MarketPolicy in production".

---

## Minute 32–42 — Confidence Router

**Deliverable**: `route()` function with three thresholds, explicit terminal states.

```typescript
const THRESHOLDS = { AUTO_BOOK: 0.85, PROPOSAL: 0.55 };

function route(
  input: TransactionInput,
  category: CategoryResult,
  booking: BookingRecord,
  vat: ReturnType<typeof calculateVat>
): BookingRecord {
  // Reverse charge always surfaces — compliance override
  if (vat.mechanism === "reverse_charge") {
    return { ...booking, status: "requires_review" };
  }

  if (category.confidence >= THRESHOLDS.AUTO_BOOK) {
    return { ...booking, status: "auto_booked" };
  }
  if (category.confidence >= THRESHOLDS.PROPOSAL) {
    return { ...booking, status: "proposal_sent" };
  }
  return { ...booking, status: "rejected" }; // not "error" — explicit terminal state
}
```

**Say**: "Two thresholds: 0.85 for auto-book, 0.55 for proposal. Below 0.55 we reject rather than guess. Every transaction must reach one of four terminal states — that prevents silent rejects where a transaction was ingested but never resolved."

**Interviewer question likely here**: "Why 0.85 specifically?"  
**Answer**: "That's a calibration decision, not a hardcoded rule. We'd set it conservatively at launch — maybe 0.90 — then widen as we measure: if our override rate on auto-booked transactions stays under 2%, we can lower the threshold. The ECE has to be below 0.05 before I trust the confidence scores for routing at all."

**Recovery pivot if behind**: Hard-code two `if` branches and note "thresholds extracted to constants in production".

---

## Minute 42–50 — Pipeline Orchestrator

**Deliverable**: `processTransaction()` that chains all four stages with a trace.

```typescript
async function processTransaction(
  input: TransactionInput,
  policy: typeof DE_POLICY
): Promise<{ booking: BookingRecord; trace: StageTrace[] }> {
  const trace: StageTrace[] = [];
  const t = (stage: string, start: number) =>
    trace.push({ stage, durationMs: Date.now() - start });

  const t0 = Date.now();
  const category = await categorize(input, policy);
  t("categorize", t0);

  const t1 = Date.now();
  const vat = calculateVat(category.category, input.vendor, policy);
  t("vat", t1);

  const t2 = Date.now();
  const booking = createBooking(input, category.category, vat, policy);
  t("booking", t2);

  const t3 = Date.now();
  const routed = route(input, category, booking, vat);
  t("route", t3);

  return { booking: routed, trace };
}
```

**Say**: "The trace is what makes this debuggable. Every stage logs its duration and decision — when a transaction routes wrong, I can replay the trace and see exactly where confidence dropped or which rule fired."

**Recovery pivot if behind**: Remove the trace entirely, just chain the function calls and return the booking.

---

## Minute 50–57 — Demo Run + Edge Cases

**Deliverable**: 3 test cases exercising the three routing paths.

```typescript
// Happy path — auto-book
await processTransaction({ id: "t1", vendor: "Bürobedarf GmbH", amount: 45.99,
  market: "DE", description: "Office supplies" }, DE_POLICY);
// Expected: auto_booked, 19% VAT, account 4930

// Proposal zone — confirm required
await processTransaction({ id: "t2", vendor: "Restaurant München", amount: 89.00,
  market: "DE", description: "Business dinner" }, DE_POLICY);
// Expected: proposal_sent, 19% VAT (meals at standard in DE)

// Reverse charge — always surfaces
await processTransaction({ id: "t3", vendor: "Amazon Web Services Ireland",
  amount: 320.00, market: "DE", description: "Cloud compute" }, DE_POLICY);
// Expected: requires_review, reverse_charge, 0% VAT
```

**Say for edge case**: "Reverse charge always surfaces regardless of confidence — that's a compliance override. I shouldn't let a high confidence score auto-book a cross-border B2B service without a human seeing it."

**Recovery pivot if behind**: Describe the test cases verbally and run one. Three cases > zero cases.

---

## Minute 57–60 — Close and Extension Points

**Say (choose 2 of these based on what came up):**

1. **Observability**: "In production I'd add a WorkflowTrace with correlation ID wrapping the whole batch — so I can reconstruct any transaction's full path from ingestion to terminal state."

2. **Evaluation**: "Before this goes to production I'd run the eval harness against a labeled set. Specifically: is the ECE under 0.05? Is the override rate on auto-booked transactions under 2%? If not, I raise the auto-book threshold."

3. **France expansion**: "Adding France is adding `FR_POLICY` — 20/10/5.5/2.1% rates, PCG account codes, Chorus Pro filing. The orchestrator doesn't change. September 2026 is the French B2B e-invoicing mandate deadline, so that integration needs to be in production before then."

4. **GoBD**: "For German customers, the audit trail isn't optional — GoBD requires immutable, machine-readable records with 10-year retention. The trace I built satisfies that if we persist it; the event-sourcing pattern lets us replay any historical decision."

**Final sentence**: "If I had another 20 minutes I'd add the batch processor layer — takes the whole transaction list, runs this pipeline, returns auto-processed / proposals / requires-attention in one structured report. That's the 'go do the task, come back' UX."

---

## Clock Recovery Matrix

| You realize at minute... | You are behind on... | Minimum pivot |
|--------------------------|----------------------|---------------|
| 15 | Types not done | Define inline, no Zod |
| 25 | Categorize not done | Return hardcoded mock |
| 35 | VAT not done | Inline `vatRate = 0.19`, note it |
| 45 | Router not done | Two `if` statements only |
| 52 | Orchestrator not done | Chain calls, no trace |
| 57 | No demo | Describe what would print, skip running |

**Never recover by skipping the router.** The routing logic — thresholds, terminal states, reverse-charge override — is what signals production thinking. Everything else can be sketched.

---

## Phrases to Avoid

- "I'll come back to that" (without actually coming back)
- "You'd normally use a framework for this" (name the abstraction yourself or skip it)
- "The LLM would handle that" (say which stage, which confidence level, which threshold)
- "This is just a demo" (say "in production I'd also add X" instead)

---

## One-Line Self-Check at Minute 30

> "I have typed contracts, a categorization stub, and a deterministic VAT function. The router is next."

If you cannot say that at minute 30, you're behind. Use the recovery matrix above.
