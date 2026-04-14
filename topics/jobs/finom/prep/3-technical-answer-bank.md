# Interview 3 — Technical Answer Bank

Saved: 2026-04-11

Full-depth answers for the hardest likely questions. These go beyond the drill targets in the prep plan — they include concrete architecture reasoning, failure mode analysis, and Finom-specific hooks.

---

## Viktar-specific answer posture

### What to say
- "I’d define the workflow boundary first, then separate ambiguity from policy."
- "Central AI should own reusable core patterns; integration should bridge them; embedded domain teams should turn them into trusted product behavior."
- "I’m optimizing for adoption and operational leverage, not just a clever architecture."
- "The goal is to make the workflow complete meaningful work and come back with a traceable result."
- "I’d keep the deterministic policy in code and use AI only where the input is genuinely ambiguous."

### What not to say
- "Let’s just centralize everything."
- "The model can decide the policy."
- "I’d throw Codex at the whole problem and see what comes back."
- "If the system is good enough, adoption will happen automatically."
- "We can make the rules prompt-based for faster iteration."

### Default 20-second frame
> I decompose the workflow into typed stages, keep policy deterministic, use AI for ambiguity, attach confidence and severity to every step, and verify with offline evals plus production monitoring. For Finom specifically, I'd treat adoption as part of the system: central patterns, integration as the bridge, embedded teams as the place where the behavior becomes real, and operator metrics like review rate and FTE per active customer as the proof that the workflow is actually compressing work.

### Key invariants to name if probed
If the interviewer asks "what must always be true?" — this is invariant thinking. Name these explicitly:
- **Auto-book invariant**: Every auto-booked transaction has calibrated confidence ≥ threshold, is not a reverse-charge case, and has a valid VAT mechanism.
- **Terminal state invariant**: Every ingested transaction reaches exactly one terminal state within SLA — no silent drops.
- **Idempotency invariant**: Processing the same transaction twice produces the same booking — no double-counting.
- **Auditability invariant**: Every routing decision is logged with input, confidence, threshold, and outcome — replayable for GoBD.

---

## Q1: "How would you design expense categorization for German SMBs?"

### Full answer

I'd decompose this into five explicit stages with typed contracts between them.

**Stage 1 — Feature Extraction (AI-powered).** Take the raw bank transaction — merchant name, amount, description, maybe a linked receipt — and extract structured fields. This is where AI adds value because merchant names are messy, abbreviations vary, and receipt text is noisy. I'd use an LLM with structured output (JSON schema or Zod) to produce a normalized `ExtractedTransaction` object.

**Stage 2 — Category Proposal (AI-powered).** Given the extracted features, propose an SKR03 account code. This is the core classification step. I'd use either a fine-tuned classifier for common categories or an LLM with retrieval over the user's transaction history — because the same merchant might map to different accounts for different businesses. The key output is the proposed account code plus a confidence score and the evidence used to justify it, like matching receipt fields, prior similar bookings, or policy references.

**Stage 3 — VAT Calculation (Deterministic).** Once we have a category, VAT rules are policy — 19% standard, 7% reduced, reverse charge for B2B intra-EU. This must not be LLM-powered. A wrong VAT rate is a compliance violation, not a UX annoyance. I'd build this as a pure function that takes category + market + B2B flags and returns the exact VAT breakdown.

**Stage 4 — Confidence Routing (Deterministic).** Route based on the category confidence score and evidence completeness. Above 0.85 with valid VAT evidence and no policy contradictions → auto-book. Between 0.5 and 0.85 or with partial evidence → create a structured proposal for the user showing what the system would do, why, and what evidence is still missing. Below 0.5 → reject and queue for manual categorization.

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

**Layer 4 — Evidence support quality.** Measure whether each material claim is backed by the expected evidence. Did the categorizer cite the receipt, merchant history, or market rule it relied on? Missing evidence should block auto-book even if raw confidence is high, because unsupported certainty is exactly how finance workflows become un-auditable.

**Layer 5 — Regression detection.** Compare every eval run against a baseline. If a prompt or model change makes reverse-charge detection worse, catch it before it ships. Store historical results and flag any case that changed from pass to fail.

I'd run this in CI against every model, prompt, or pipeline change. Production monitoring adds: override rate tracking, confidence distribution shifts, evidence-missing rate, and per-market accuracy over time.

**Finom-specific hook:** I saw you use Confident AI for eval infrastructure — going from 10-day improvement cycles to 3-hour iterations is exactly the velocity gain that makes eval-first development practical. That kind of eval velocity is what lets you move from shadow mode to auto-book with confidence in the data, not just confidence in the model. The evaluation framework I described is the thing you'd run inside those faster iteration cycles. And the key insight from your own setup: the bottleneck wasn't engineer time — it was that product managers were locked out of the eval loop. Unblocking them is what turned 10 days into 3 hours.

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

**Finom-specific color:** Three markets are already live for tax filing — Germany (UStVA), Italy (F24 Ordinario on mobile), and France is the expansion target. The ZM report (EC Sales List) just shipped for Germany. Each new market adds a policy module and one test suite; the orchestrator stays the same.

**The trap to avoid:** Encoding market-specific rules in prompts. If VAT rates live in the LLM's system prompt, you can't test them deterministically, you can't version them, and you can't guarantee they're correct. Market policy must be code, not prompts.

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

**Finom-specific frame:** Ivo's question about whether Codex/Claude make engineers faster or slower is the same question Finom already answered for evals with Confident AI — 10-day cycles became 3-hour cycles. The velocity gain comes from faster feedback, not faster output. Coding agents work the same way: they're a net win when they accelerate verification cycles (e.g., "generate the test, I verify correctness"), and a net loss when they accelerate code volume without accelerating verification. The metric should be convergence speed to correct, not lines produced per hour.

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
- Package the pattern at the integration seam teams already touch: shared contracts, one orchestration template, trace hooks, and a minimal eval harness. If adoption requires a rewrite, it is not a reusable pattern.

**Finom-specific color:** Finom is running 5-10 active AI products right now — not just the AI Accountant. Each product has sub-agents connected to dedicated MCP servers and backend microservices. The central AI team's leverage comes from shared eval infrastructure (they went from 10-day improvement cycles to 3-hour cycles by unblocking product managers), shared tool interfaces, and shared observability patterns. The question is always: does the next product team start from scratch, or do they inherit a tested spine?

**How to avoid becoming a bottleneck:**
- Domain teams own their outcomes. The central team provides leverage, not approval gates.
- If a team wants to deviate from the pattern, ask why — it might reveal a real limitation. Don't block them.
- Rotate people between central and domain work so knowledge flows both ways.

**What I'd measure:** time-to-first-shipped workflow on the shared pattern, percent of AI workflows using the common trace format, review-rate reduction after adoption, and whether teams keep the pattern six weeks later instead of forking around it.

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

## Q9: "What production pain points do you expect in a system like this?"

### Full answer

I think about this as the "Triple Dipper" — every production AI system fights three tensions simultaneously: **latency, cost, and accuracy.** Optimizing one directly stresses the others. In a financial AI workflow, there's a fourth: **trust.** Getting that wrong doesn't just degrade UX; it creates compliance risk.

**Latency:** Multi-step workflows get slow when every transaction calls the model synchronously. I'd use batching, async processing where possible, and cache common merchants or repeated patterns. Concretely, I preserve the same `GET /health`, `POST /categorize`, and `POST /categorize/batch` API contract, but change the batch path from sequential sync calls to bounded async concurrency with a semaphore. On a 20-item mock batch with 40ms/item latency, that cuts elapsed time from ~864ms to ~164ms — measurable execution leverage, not just "async sounds better." The control point is the semaphore; unbounded `asyncio.gather` looks clever and destabilizes the provider.

**Cost:** The long tail is expensive if the model runs on every item. Three levers: (1) semantic caching — cache embeddings of common merchant patterns, so repeated queries hit cache, not the model; (2) model cascading — route straightforward, high-pattern transactions through a smaller, cheaper model, and only escalate ambiguous or novel inputs to the larger model; (3) re-ranker before LLM — if categorization uses retrieval over prior transaction history, a lightweight re-ranker can filter irrelevant context before it reaches the model, cutting token cost without touching accuracy. This also reduces latency.

**Trust:** Confidence scores drift over time. I'd monitor calibration per market, override rate, and severe-error rate. If calibration worsens (ECE climbs above 0.05), I tighten the routing threshold before accuracy metrics degrade — because accuracy is a lagging indicator, calibration is leading.

The next layer is **debuggability**. Every decision needs a trace: raw input, extracted fields, model output, confidence, routing decision, and final booking. Without that, production support becomes archaeology.

Finally, I expect **workflow-specific failures**, not just model failures: bad OCR from scanned documents, stale market config, missing VAT evidence, unawaited coroutines that silently drop transactions, and support queues that grow because the proposal UX is unclear. I'd design the system to fail visibly and conservatively, then measure where humans are still getting pulled in.

---

## Q10: "How do you decide when to widen automation from proposal mode to auto-book?"

### Full answer

There's a specific maturity ladder with measurable criteria at each level. You don't widen based on enthusiasm — you widen based on data.

**The five levels:**

| Level | Behavior | Advancement criteria |
|-------|----------|---------------------|
| 0 — Shadow | AI runs internally, output discarded, only metrics collected | >85% agreement with human decisions for 30 days |
| 1 — Suggest | AI suggests, human decides | >90% acceptance rate for 14 days |
| 2 — Draft | AI pre-fills, user confirms before execution | <5% correction rate for 14 days |
| 3 — Auto with audit | AI executes, user reviews daily summary | <2% correction rate for 30 days; ECE < 0.05 |
| 4 — Full auto | AI executes, user alerted on anomalies only | Continuous monitoring with no regressions for 60 days |

**For a new market (e.g., France launch):** Start at Level 0 regardless of Germany's track record. Zero calibration data means the confidence scores are unvalidated. Collect the first 1000 reviewed transactions in France, measure agreement rate and ECE, then advance through the ladder.

**For an existing market when model changes:** Regression test + shadow mode for 7 days. If agreement rate with the previous model's confirmed decisions is >95%, advance. If it drops, investigate before widening.

**What not to do:** Don't advance based on aggregate accuracy. A model that's 95% accurate on easy cases but fails systematically on reverse charge won't show up in the aggregate number. Advance based on per-category agreement rate, not total accuracy.

**Specific metric thresholds for Finom:**
- Shadow → Suggest: 85% agreement with human-confirmed bookings, measured over 30 days
- Suggest → Draft: 90% acceptance rate (user changes their mind <10% of the time)
- Draft → Auto: <5% correction rate (users change the pre-filled result less than 5% of the time)
- Auto → Full auto: <2% correction rate sustained for 30 days + ECE < 0.05 + no critical error in last 100 transactions

## Q11: "How do you prove the system reduced work instead of just moving it around?"

### Full answer

I'd separate **workflow completion metrics** from **operator-load metrics**, because a lot of AI systems look good on the first and fail on the second.

**Workflow completion metrics:**
- percent of transactions reaching a terminal state without manual intervention
- cycle time from ingestion to booked entry
- percent of tax filings assembled as draft-complete without operator repair

**Operator-load metrics:**
- review rate per 100 transactions
- average review minutes per escalated case
- correction rate after auto-book
- support tickets created per 1000 automated decisions
- FTE per active customer

The key question is whether the human work went away or just moved later in the process. If auto-book rate improves but support tickets spike, we didn't compress work; we relocated it from accounting ops to support and reconciliation.

So the production dashboard I care about is:
- automation rate
- review rate
- correction severity
- support burden
- net cycle time
- FTE per active customer

If Ivo asks for business language, I'd say: "I only count this as success if the workflow reduces review load and exception handling enough to improve FTE per active customer. Faster model calls without lower operator load are not business leverage."

## Q12: "How would you integrate AI into an existing C# / Python system?"

### One-line answer

> "The AI work is Python and TypeScript. For the C# boundary, I'd start by reading the OpenAPI contracts and existing integration tests — that's enough to design and implement clean API clients. I've worked across language boundaries before and the integration patterns (REST, gRPC, shared schemas) are language-agnostic. The domain ramp would take weeks; the language ramp is days."

---

---

## Q13: "When would you use a staged workflow versus a single agent?"

### One-line answer

> A single agent is right when the problem fits in one context window and tolerates graceful degradation. A staged workflow is right when failure modes are heterogeneous, steps have different trust levels, or you need independent testability per stage.

### Full answer

The decision comes down to three questions:

**1. Are the failure modes the same across the task?**

If a task can fail in only one way (e.g., "classify this text into one of ten categories"), a single agent is fine. If different sub-tasks can fail differently — OCR degrades, VAT rules change, confidence calibration drifts per market — then a staged workflow is required. You need to fail, alert, and fix each stage independently, not debug a combined blob.

For Finom: extraction fails when document quality degrades (FM-01), categorization fails when the model is overconfident (FM-04), VAT fails when B2B flags are missing (FM-07). These require independent monitoring and independent improvement loops — that alone mandates staged architecture.

**2. Do steps have different trust levels or authorization requirements?**

A single agent cannot have one part that auto-executes and one part that requires human approval. In a staged workflow, you can insert an approval gate between the proposal stage and the booking stage. The agent that generates proposals has no access to the booking ledger. The booking step only runs after explicit confirmation.

This is why financial workflows can't be a single agent: the LLM that categorizes should not have write access to the accounting ledger. Separation is a security control, not just a style preference.

**3. Can you test the steps independently?**

With a single agent, you can only test the end-to-end output. With staged workflows, you can run the VAT calculation against 1000 labeled transactions without touching the LLM. You can regression-test the router against a saved confidence distribution. You can calibrate the categorizer on new market data without changing the booking step.

This is the operational argument: independent testability means you can improve one component without revalidating the whole system.

### When a single agent is actually right

- Exploration or prototype: you don't know the right stage boundaries yet
- Advisory output only: the agent recommends, a human acts — no approval gate needed
- The entire task is unstructured input → structured summary (no compliance-sensitive action)
- Short-lived script: one-off data cleaning, not a production workflow

### The key phrase

> "I use a single agent to explore and a staged workflow to ship. Once I know what can go wrong, I formalize the stages — because each named failure mode deserves its own circuit breaker."

---

---

## Q14: "What observability would you add first to a financial AI workflow?"

### One-line answer

> Three layers in priority order: confidence distribution (is the model drifting?), terminal state tracking (is every transaction resolving?), and business KPI deltas (is the automation actually helping?).

### Full answer

Most engineers start with request logs. That's the wrong first layer for financial AI — it tells you what happened, not whether the system is healthy.

**Layer 1: Confidence distribution (add first, day one)**

Track the rolling P10/P50/P90 of confidence scores per stage, per market. If the P50 for categorization in Germany drops from 0.82 to 0.71 over a week, you have a signal before any transaction is misbooked. Compare each batch's distribution against the 30-day historical baseline. Alert if P50 drops more than 2σ below historical.

Why first: confidence drift is the leading indicator for accuracy degradation. Accuracy metrics are lagging — you need corrections to accumulate before you see them. Confidence distribution is real-time.

**Layer 2: Terminal state tracking (add second)**

Every transaction must reach one of: `auto_booked`, `proposal_sent`, `rejected`, `requires_review`, `error_logged`. Track the time-in-state for every transaction. Alert if any transaction has been in a non-terminal state for more than the SLA window (e.g., 2 hours for batch jobs).

Why second: silent rejects (FM-15) are invisible without this. A transaction that was ingested and then dropped due to an unhandled exception has no representation in accuracy metrics — it just disappears.

**Layer 3: Business KPI deltas (add by end of week one)**

Track per-week:
- Auto-book rate (target: >70% at steady state, <30% at new market launch)
- Override rate on auto-booked transactions (target: <2%, alert at >5%)
- Proposal acceptance rate (target: >85%, drop signals the model is proposing wrong accounts)
- Review queue depth (alert if growing week-over-week — indicates escalation storm FM-14)
- Severe error rate (wrong VAT or wrong account code — target: zero, any occurrence is a P1)

Why: these are the metrics Ivo will look at. Connecting technical health to business impact is how the AI team demonstrates that their work reduces FTE per customer.

**What NOT to add first**

- Raw request/response logs: useful for debugging but creates a privacy/compliance surface for customer financial data. Add with field-level PII scrubbing after the health metrics.
- Model latency percentiles: important eventually, but latency degradation is visible before it affects SLA. Confidence drift and silent rejects are not.
- Token counts: developer-facing cost metric, not operational health.

### Instrumentation pattern

```
SpanTrace (per transaction):
  → correlation_id, market, transaction_id
  → per_stage: { name, duration_ms, confidence, decision }
  → terminal_state, total_duration_ms
  → batch_id (for anomaly detection)

BatchHealthSummary (per batch run):
  → confidence P10/P50/P90 vs 30d baseline
  → stranded_count (non-terminal past SLA)
  → auto_book_rate, override_rate, severe_error_count
  → alert_fired: boolean, alert_reason
```

### The key phrase

> "I add confidence distribution monitoring on day one because it's the leading indicator — by the time accuracy metrics degrade, you've already misboked real transactions. Terminal state tracking catches the silent failures metrics don't see. Business KPIs connect it to what the team actually cares about."

---

## Q15: "If you joined, what would you own in the first 90 days?"

### One-line answer

> "In the first 30 days I'd ship something small and correct — not design something large. By day 60 I'd own one production component with measurable impact. By day 90 I'd have a reusable pattern two other engineers have actually used."

### Full answer

I'd structure it around three concrete deliverables, not a learning plan.

**Days 1–30: Read the production system, then ship one thing.**

I'd spend the first week reading live code, tracing one transaction from ingestion to booking entry, and understanding the actual failure modes — not the documented ones, the production ones. Then I'd pick one small, well-scoped improvement: either a missing failure mode handler, a calibration gap in one market, or a non-terminal transaction in the dead-letter queue. Ship it with tests and a trace. The goal is to prove I can operate on the real system, not just describe patterns.

**Days 31–60: Own one production component with a measurable metric.**

The accounting pipeline has clear seams: extraction, categorization, VAT, routing, observability. I'd take ownership of one component — most likely the confidence routing layer or the eval harness — and attach a metric I'm responsible for. If it's routing: override rate and auto-book rate, tracked weekly. If it's eval: regression detection coverage, measured in "percent of failure modes with a CI-blocking test case." The goal is that when the number moves, I know why.

**Days 61–90: Produce one reusable pattern two other engineers have used.**

By day 90 I want to have built one thing that two engineers who weren't involved have adopted. That's the central AI team's success condition: not "we documented a pattern" but "two teams used it and kept using it six weeks later." It could be an orchestration template, a confidence calibration helper, or a trace format. The measure is adoption, not creation.

**What I would not do in the first 90 days:** redesign the architecture, propose a new evaluation framework before understanding the current one, or declare what the team should be doing differently. The learning curve in a fintech domain is real — I'd earn the right to influence direction by first demonstrating I can ship and operate within it.

**If Viktar asks "but what if we don't have a clear project for you?":**

> "Then I'd create one. The accounting pipeline has observable metrics — override rate, escalation rate, per-market ECE. I'd find the worst-performing metric and own improving it. The work is always there; the question is whether I can find it."

---

## Q16: "How would you handle a live round problem you haven't prepared for?"

### One-line answer

> "The problem framing is always the same: scope the input and output first, identify the failure cost hierarchy, draw the pipeline, then implement one stage at a time with typed contracts between them."

### Full answer

The categorization workflow is the example I've prepared, but the pattern transfers to any AI workflow problem.

**The universal approach:**

1. **Scope before touching the keyboard** (2 min): "The input is [X], the output must be [Y], and the worst kind of wrong is [Z]."

2. **Draw the AI/deterministic boundary** (1 min): "What in this problem is judgment? What is policy? Judgment → AI stage. Policy → deterministic stage."

3. **Define typed contracts** (3 min): Pydantic models or Zod schemas for input, output, and confidence envelope for the AI stage.

4. **Implement the AI stage as a stub first** (5 min): Return a typed result with a confidence score. The exact LLM call is secondary — the contract matters.

5. **Implement the deterministic stage** (5 min): Pure function, no side effects, testable independently.

6. **Add the confidence router** (5 min): Always. This is the most important 10 lines regardless of problem domain.

7. **Wire an orchestrator with a trace** (5 min): Chain the stages, capture per-stage timing and decisions.

**What this looks like for common alternative problems:**

- **Invoice processing**: extraction stage (AI, unstructured → structured), field validation (deterministic, required fields present), approval routing (deterministic, amount threshold or vendor rule).
- **Support ticket triage**: intent classification (AI, freetext → category + confidence), SLA calculation (deterministic, category → response time), escalation routing (deterministic, confidence + severity).
- **Fraud signal scoring**: feature extraction (deterministic, rule-based signals), model scoring (AI, probability), action routing (deterministic, threshold + compliance override for high-value transactions).

**The invariants that apply everywhere:**

Every AI workflow, regardless of domain, needs: (1) confidence scores on AI outputs, (2) deterministic policy enforcement, (3) explicit terminal states, (4) a trace per request. These are not categorization-specific — they are the architecture of any production AI workflow. Implement these and you've demonstrated production thinking regardless of the specific problem.
