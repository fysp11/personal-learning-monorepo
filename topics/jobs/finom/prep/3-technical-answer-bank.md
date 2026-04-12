# Interview 3 — Technical Answer Bank

Saved: 2026-04-11

Full-depth answers for the hardest likely questions. These go beyond the drill targets in the prep plan — they include concrete architecture reasoning, failure mode analysis, and Finom-specific hooks.

---

## Q1: "How would you design expense categorization for German SMBs?"

### Full answer

I'd decompose this into five explicit stages with typed contracts between them.

**Stage 1 — Feature Extraction (AI-powered).** Take the raw bank transaction — merchant name, amount, description, maybe a linked receipt — and extract structured fields. This is where AI adds value because merchant names are messy, abbreviations vary, and receipt text is noisy. I'd use an LLM with structured output (JSON schema or Zod) to produce a normalized `ExtractedTransaction` object.

**Stage 2 — Category Proposal (AI-powered).** Given the extracted features, propose an SKR03 account code. This is the core classification step. I'd use either a fine-tuned classifier for common categories or an LLM with retrieval over the user's transaction history — because the same merchant might map to different accounts for different businesses. The key output is the proposed account code plus a confidence score.

**Stage 3 — VAT Calculation (Deterministic).** Once we have a category, VAT rules are policy — 19% standard, 7% reduced, reverse charge for B2B intra-EU. This must not be LLM-powered. A wrong VAT rate is a compliance violation, not a UX annoyance. I'd build this as a pure function that takes category + market + B2B flags and returns the exact VAT breakdown.

**Stage 4 — Confidence Routing (Deterministic).** Route based on the category confidence score. Above 0.85 → auto-book. Between 0.5 and 0.85 → create a structured proposal for the user showing what the system would do and why. Below 0.5 → reject and queue for manual categorization.

**Stage 5 — Booking Entry (Deterministic).** Create the double-entry accounting record: debit the expense account, credit the bank account, split out the Vorsteuer. This is mechanical once the inputs are confirmed.

**What I'd measure:** approval rate (what fraction auto-books), override rate (how often users correct a proposal), severe-error rate (wrong VAT or wrong account), and per-market accuracy breakdown.

**Why this design:** Each stage fails differently and can be improved independently. If extraction accuracy drops, we improve the extraction prompt — we don't need to retrain the categorizer. If VAT rules change for a new market, we add a config — we don't retrain anything.

---

## Q2: "What should be deterministic vs LLM-based?"

### Full answer

The rule is simple: **if the failure cost is compliance-related, it's deterministic. If the input is genuinely ambiguous, it's AI.**

Deterministic:
- VAT rate calculation (wrong rate = tax penalty)
- Reverse charge detection (given structured B2B flags and VAT ID)
- Booking entry creation (mechanical double-entry math)
- Filing deadlines and submission rules
- Threshold routing (confidence → action mapping)
- Market-specific policy modules (each market's chart of accounts, tax rates)

AI-powered:
- Merchant name normalization (messy abbreviations, typos)
- Receipt OCR and field extraction (unstructured images → structured data)
- Transaction categorization (which SKR03 account? depends on context)
- Anomaly detection (is this pattern unusual?)
- Natural-language explanations for users

The boundary is not "hard vs easy" — it's "failure mode." Getting a category wrong means the user corrects it. Getting a VAT rate wrong means a formal tax amendment and potential penalties. The cost function tells you where the boundary should be.

---

## Q3: "How would you evaluate a financial AI workflow?"

### Full answer

I'd build a **severity-weighted evaluation framework** with four layers.

**Layer 1 — Field-level accuracy.** Compare each output field against ground truth: account code, VAT rate, amounts, mechanism. Report per-field accuracy, not just overall pass/fail. A wrong description is different from a wrong VAT rate.

**Layer 2 — Severity weighting.** Assign severity to each test case: critical (wrong VAT, missed reverse charge), high (wrong account code in a way that changes tax treatment), medium (wrong account code, same tax treatment), low (cosmetic). Weight the accuracy by severity. Raw accuracy of 90% means nothing if all the failures are critical.

**Layer 3 — Confidence calibration.** Measure Expected Calibration Error (ECE). When the model says 0.9 confidence, is it actually correct 90% of the time? Poor calibration means the routing thresholds are meaningless — you'll auto-book things you shouldn't, or escalate things that are fine.

**Layer 4 — Regression detection.** Compare every eval run against a baseline. If a prompt or model change makes reverse-charge detection worse, catch it before it ships. Store historical results and flag any case that changed from pass to fail.

I'd run this in CI against every model, prompt, or pipeline change. Production monitoring adds: override rate tracking, confidence distribution shifts, and per-market accuracy over time.

---

## Q4: "How would you generalize Germany-first workflows toward France?"

### Full answer

The key insight is that the **workflow shape** is the same across markets — the **policy modules** are different.

I'd parameterize market-specific rules into a `MarketConfig` object:

```
MarketConfig {
  standardVatRate: number
  reducedVatRate: number
  chartOfAccounts: Record<category, { code, name }>
  vatAccount: string
  filingRequirements: { type, frequency, deadline }
  specialRules: { reverseCharge, exemptions, ... }
}
```

Germany uses SKR03/SKR04, 19%/7% VAT, UStVA monthly/quarterly filing. France uses PCG, 20%/10%/5.5%/2.1% VAT, CA3 filing. But the categorize → calculate VAT → route → book flow is identical.

**What must NOT change per market:** the orchestrator, the confidence routing, the trace/observability layer, the eval framework shape.

**What must change per market:** the chart of accounts mapping, VAT rate tables, specific tax rules (French TVA has four rates, not two), filing format and submission APIs.

**How I'd implement it:** Each market gets a policy module that implements a `MarketPolicy` interface. The orchestrator doesn't know about SKR03 or PCG — it calls `policy.getAccountCode(category)` and `policy.calculateVat(amount, category)`. Adding Spain means writing one new policy module and test suite, not changing the core pipeline.

**The trap to avoid:** encoding market-specific rules in prompts. If VAT rates live in the LLM's system prompt, you can't test them deterministically, you can't version them, and you can't guarantee they're correct. Market policy must be code, not prompts.

---

## Q5: "Why do AI coding tools sometimes make teams slower?"

### Full answer

Three failure modes I've seen:

**Volume without judgment.** The tool generates code fast, so the engineer generates more code than the problem needs. More code means more surface area to review, more bugs to find, more tests to write. The output goes up, but the signal-to-noise ratio goes down.

**Architecture delegation.** The engineer dumps a vague problem into the tool and accepts whatever architecture comes back. The tool optimizes for plausible-looking code, not for the team's patterns, constraints, or production requirements. You end up with code that works in isolation but creates integration debt.

**Verification gap.** Generated code looks right — the formatting is clean, the variable names are reasonable, the structure is familiar. So people review it less carefully than hand-written code, even though it may contain subtle errors. The tool creates a false sense of confidence.

**How I'd prevent this at Finom:**

1. Define interfaces and contracts first, then use the tool for implementation. The human owns the architecture; the tool fills in typed functions.
2. Keep prompts scoped and small. Ask for one function, not a whole module. Inspect each output before moving on.
3. Insist on a verification step — run it, test it, check the edge cases. If the tool makes it easier to write code, spend the saved time on better verification.
4. Measure net effect, not gross output. The question isn't "how much code did we write?" — it's "how fast did we converge to a correct, maintainable solution?"

---

## Q6: "How should a central AI team help without becoming a bottleneck?"

### Full answer

Centralize the **hard reusable parts** — not every product decision.

**What to centralize:**
- Evaluation patterns and frameworks (so every team doesn't reinvent accuracy measurement)
- Orchestration conventions (standard stage contracts, trace format, confidence propagation)
- Safety controls (confidence routing, human review flows, compliance guards)
- Shared tooling (MCP skill servers, prompt management, model gateway)
- A few proven workflow templates that solve real problems

**What to leave with domain teams:**
- Specific product decisions (what to automate, what UX to build)
- Domain-specific prompt tuning and test cases
- Feature prioritization and user research
- Integration with their own backend services

**How to avoid becoming decorative:**
- Ship working templates, not white papers. If the accounting team can use your orchestration template and be productive in a day, they will. If they need a three-week onboarding, they'll work around you.
- Make the reusable path faster than the local workaround. Good defaults, observability out of the box, clear interfaces.
- Measure adoption, not just creation. A pattern that three teams use is worth more than ten patterns nobody uses.

**How to avoid becoming a bottleneck:**
- Domain teams own their outcomes. The central team provides leverage, not approval gates.
- If a team wants to deviate from the pattern, ask why — it might reveal a real limitation. Don't block them.
- Rotate people between central and domain work so knowledge flows both ways.

---

## Q7: "When should you automate the work vs just assist the user?"

### Full answer

Automate when four conditions are met:

1. **Task boundary is clear.** The input, output, and success condition can be explicitly defined. "Categorize this transaction to SKR03" is clear. "Help the user with their finances" is not.

2. **Failure cost is bounded.** A wrong categorization can be corrected by the user with one click. A wrong tax filing requires a formal amendment. For bounded failures, automate with confidence routing. For unbounded failures, keep it as a proposal.

3. **Policy-heavy parts are deterministic.** If the automation depends on compliance rules, those rules must be code, not prompts. You can automate the workflow around them, but the rules themselves must be verifiable and testable.

4. **Approval or rollback path is obvious.** The user must be able to see what the system did, understand why, and undo it if needed. If the action is irreversible (like filing a tax return), it should always require explicit approval.

When these conditions aren't all met, start with **proposal mode** — the system does the analysis and presents a structured recommendation, but the user takes the action. Then measure overrides. If the override rate drops below some threshold (say 5%), you've earned the right to automate that step. **Earned autonomy, not claimed autonomy.**

Ivo's frame is useful here: the goal is "go do the task, then come back" — but the system should earn that trust stage by stage, not claim it day one.

---

## Q8: "What makes an AI team different from an ML team?"

### Full answer

Different core problems, different engineering patterns, different risk profiles.

**ML team:** Builds prediction and optimization systems. Credit scoring, fraud detection, recommendation engines. The core artifact is a trained model with a well-defined input/output. The engineering challenge is data pipelines, feature engineering, model training, and serving infrastructure. Failures are statistical — the model is wrong some percentage of the time, and you manage that through thresholds and monitoring.

**AI team:** Builds LLM-driven workflow execution systems. Accounting automation, document processing, conversational agents, tool-using workflows. The core artifact is an orchestrated pipeline of LLM calls, tools, and deterministic logic. The engineering challenge is prompt engineering, tool integration, confidence routing, and multi-step workflow reliability. Failures are compositional — a workflow can fail at any stage, and errors compound through the pipeline.

**Where they overlap:** Both need evaluation frameworks, monitoring, and data quality. Both care about latency and cost. Both serve the same product.

**Where they differ:**
- ML models are trained once and served many times. LLM workflows are designed once and executed with different inputs each time.
- ML failure modes are well-understood (bias, drift, distribution shift). LLM failure modes include hallucination, instruction following failures, tool misuse, and reasoning errors.
- ML teams optimize metrics like AUC, precision/recall. AI teams optimize workflow completion rates, override rates, and severity-weighted accuracy.

At Finom, this probably means: the ML team handles credit scoring and risk models, while the AI team handles the accounting workflow automation, document understanding, and agentic product experiences.

---

## Q9: "Our core platform is in C#/.NET — how do you work in a polyglot stack?"

### Full answer

I'd design the boundary deliberately, not apologetically.

**The boundary is the asset, not the problem.** If the core banking ledger, double-entry engine, and ELSTER filing are in C#, that's exactly right — those need deterministic behavior, type safety, and high test coverage. The AI orchestration layer on top (categorization, extraction, confidence routing) can be TypeScript or Python without any tension, because the two layers communicate through a well-defined API boundary.

**How I'd structure the integration:**

The C# core exposes a thin API surface for what the AI layer needs:
- `POST /bookings` — create a double-entry booking entry (input: confirmed category, amount, VAT breakdown)
- `GET /chart-of-accounts?market=DE` — retrieve valid account codes for routing validation
- `POST /ustava/draft` — submit a VAT return draft for review

The AI orchestration layer calls these APIs after the AI work is done. It never directly writes to the accounting ledger — it only submits confirmed, validated results through the C# service boundary.

**Why this is cleaner than a monolith:**

If the categorization model changes (new LLM, new prompt), I redeploy the AI layer. The C# core doesn't change. If a tax rule changes (new VAT rate in France), the C# core is updated deterministically and the AI layer picks it up via the config API. No shared state, no coordinated deploys.

**What I'd own vs what I'd consume:**

I own: the TypeScript/Python orchestration pipeline, MCP skill servers, prompt management, eval harness, confidence routing, observability. I consume: the C# booking API, market config API, filing API.

I'd read the C# service contracts (OpenAPI spec or proto) rather than the implementation. I don't need to write C# to design a clean integration — I need to understand the contract. On a practical level: reading C# service code is feasible for someone with TypeScript experience in a few days. The syntax patterns are similar enough that I can review, understand, and even propose changes to C# interfaces.

**What I'd want to establish early:**

A clear definition of which layer owns which concern. Specifically: does the AI layer validate the category against the chart of accounts before calling the C# API, or does the C# API validate on receipt? I'd push for validation on both sides — the AI layer runs a local check (market config downloaded via API) and the C# API enforces it as a contract. Defense in depth for a compliance-critical operation.

### Gap response variant (if pressed on C# specifically):

> "The AI work is Python and TypeScript. For the C# boundary, I'd start by reading the OpenAPI contracts and existing integration tests — that's enough to design and implement clean API clients. I've worked across language boundaries before and the integration patterns (REST, gRPC, shared schemas) are language-agnostic. The domain ramp would take weeks; the language ramp is days."
