# Live Coding with AI Agents — Advanced Patterns for Interview 3

Saved: 2026-04-11

## Context

Interview 3 is a 60-minute live coding round with Claude Code / Codex. Ivo explicitly cares whether these tools make engineers faster or slower. This insight goes beyond the rehearsal code to document **meta-patterns** — how to operate during the live round itself.

---

## The Three Modes of Agent-Assisted Coding

### Mode 1: Scaffold Mode (First 5 Minutes)

**When:** Starting a new problem, defining architecture.

**Pattern:** You drive; the agent fills boilerplate.

```
You: "Create the type contracts for a 3-stage pipeline: categorize → calculate → book"
Agent: generates Zod schemas, interfaces, type aliases
You: review contracts, adjust naming, add domain constraints
```

**Why this works for interviews:** The interviewer sees you making architectural decisions while the agent handles mechanical typing. You're demonstrating judgment, not delegation.

**Anti-pattern:** Asking the agent to "design the system" — this is the one thing you must do yourself.

### Mode 2: Implementation Mode (Minutes 5-45)

**When:** Contracts exist, filling in stage logic.

**Pattern:** One stage at a time, verify before proceeding.

```
You: "Implement the categorize function — keyword matching with confidence scoring"
Agent: generates implementation
You: read the output, check edge cases, fix any issues
You: "Now implement VAT calculation — pure deterministic, no AI"
```

**Critical discipline:** After each agent output, pause for 10-15 seconds to actually read it. The interviewer watches whether you verify or blindly accept.

**Anti-pattern:** Generating all stages at once and hoping they compose correctly.

### Mode 3: Debug/Extend Mode (Minutes 45-60)

**When:** Core works, adding observability or handling edge cases.

**Pattern:** Targeted edits, not rewrites.

```
You: "Add a trace array that captures stage name, duration, and decision for each stage"
Agent: adds observability
You: "Add a test case for an unknown merchant — should route to review"
```

**Why this matters:** The last 15 minutes reveal whether you use AI tools to polish or to panic.

---

## Confidence Router as Interview Centerpiece

The confidence router is the single most demonstrable pattern for Finom's domain. It connects three things the interviewer cares about:

1. **AI/deterministic boundary** — categorization is AI, VAT is rules
2. **Operational safety** — bad categories don't reach the ledger
3. **Measurable leverage** — auto-book rate is a direct metric for FTE reduction

### The Three-Tier Threshold Pattern

```typescript
// This is the talking point, not just code
const THRESHOLDS = {
  autoBook: 0.85,  // "We trust this enough to commit without human eyes"
  review: 0.50,    // "Plausible but not safe — queue for human"
  reject: 0.50,    // Below this: don't even propose, ask for manual input
};
```

**Interview talking point:** "These thresholds aren't magic numbers — they come from calibration. In production, you'd measure: of all transactions where the model said 0.85+ confidence, what fraction were actually correct? That's your calibration curve, and it tells you whether your threshold is too aggressive or too conservative."

### How the Router Evolves

| Stage | Behavior | When |
|-------|----------|------|
| Launch | Conservative (autoBook: 0.95) | Day 1 in new market |
| Tuned | Balanced (autoBook: 0.85) | After 10K+ calibrated transactions |
| Mature | Aggressive (autoBook: 0.75) | Market-specific model with correction feedback |

This is the "earned autonomy" pattern Ivo described — start conservative, widen as trust is measured.

---

## Evidence Gate as the Second Control Point

Confidence alone is not enough for finance-sensitive workflows. The second control point is evidence completeness.

### The pattern

```typescript
const canAutoBook =
  result.confidence >= thresholds.autoBook &&
  result.evidence.isComplete &&
  !result.evidence.hasPolicyConflict;
```

### Why this matters in the interview

- It shows you understand that unsupported certainty is not real trust.
- It upgrades observability from "we logged the answer" to "we know why the answer was allowed to act."
- It gives you a cleaner deterministic boundary: the model can propose, but code decides whether the proposal is sufficiently supported.

### Good live-round phrasing

> "I don't want to auto-book off confidence alone. I want confidence plus evidence completeness, otherwise the system is confident and un-auditable."

> "This keeps proposal mode useful: the model can still move work forward, but unsupported claims stay reviewable instead of silently becoming ledger entries."

---

## Execution-Model Refactor Pattern

One especially strong live-round move is to improve throughput **without** changing the public interface. This shows mature engineering judgment because you protect downstream integrations while still fixing the bottleneck.

### Contract parity rule

Say this explicitly:

> "I want shared request and response contracts first. Then I can change execution underneath them without making every caller pay for my refactor."

### The concrete pattern

```
Frozen API contract
  → shared models
  → same endpoint paths
  → same response ordering and error shape

Changed execution layer
  → sequential sync loop
  → bounded async fan-out
  → semaphore-capped concurrency
```

### Why this scores well

- It proves you understand that interfaces are product surface area.
- It shows you can make `Codex` / `Claude` faster by giving them a narrow, local refactor target.
- It demonstrates measurable leverage: lower batch latency without hand-wavy redesign.
- It maps cleanly to Finom's environment, where internal improvement is useful only if domain teams can adopt it without integration churn.

### Good live-round phrasing

> "I'm not going to redesign the world here. I'll keep the contract fixed, isolate the slow execution path, and swap sequential waiting for bounded concurrency so the gain is measurable and low-risk."

> "The control point is the semaphore. Unbounded async looks clever in a demo and unstable in production."

> "Before I optimize, I want a baseline by stage. If model time is only 15% of the path and retrieval or queueing is the bottleneck, async fan-out is the wrong fix."

---

## Python Async Discipline — Named Pitfalls for Live Round

When narrating the batch refactor (Scenario F), use specific Python vocabulary. These are the pitfalls senior engineers name; naming them signals depth that "async is faster" does not.

### The three failure modes to name out loud

**1. Blocking the event loop**
> "If I put a CPU-heavy operation inside the async handler — say, synchronous PDF parsing or heavy JSON schema validation — it freezes the entire event loop. Everything queued behind it waits. The fix is `loop.run_in_executor` for CPU work, keeping the async path clean for I/O."

**2. Synchronous library inside async context**
> "Using `requests` or `time.sleep` inside an async function defeats the concurrency entirely. The thread blocks, and Python can't switch to pending coroutines. I'd use `httpx` or `aiohttp` for outbound calls and `asyncio.sleep` for delays."

**3. Unawaited coroutines — silent failures**
> "If you schedule a coroutine with `asyncio.create_task` but don't handle the result or await it, exceptions disappear silently. The task fails, nothing surfaces, and the transaction is in a non-terminal state with no alert. I always attach `.add_done_callback` or gather results explicitly so failures are never silent."

### GIL — one sentence when relevant
> "Python's GIL means true CPU parallelism requires multiprocessing, not threading. But for this batch problem, the bottleneck is I/O-bound — waiting for LLM responses — so async with bounded concurrency is exactly right. No need for multiprocessing here."

### The semaphore as a production control
```python
# This is the one control point for provider stability
sem = asyncio.Semaphore(MAX_CONCURRENT)

async def bounded_categorize(item):
    async with sem:
        return await categorization_service.categorize(item)

results = await asyncio.gather(
    *[bounded_categorize(item) for item in batch],
    return_exceptions=True  # don't let one failure kill the batch
)
```

> "The semaphore isn't just about latency. It's about not hammering the LLM provider into rate-limiting. Unbounded `gather` on a 1000-item batch looks like a DDoS from the provider's perspective."

### Measurable claim for the live round
The latency gain is concrete: a 20-item batch with 40ms/item LLM latency runs in ~864ms sequentially. Bounded async (concurrency=5) runs in ~164ms. The claim is measurable; state the numbers, not just "faster."

---

## Live Round Strategy: What to Say Out Loud

The interviewer evaluates your thinking, not just your code. These are the **verbal checkpoints** that demonstrate product engineering judgment:

### At Problem Statement

> "Before I start coding — let me make sure I understand the boundary. The categorization is where AI adds value; VAT calculation must be deterministic because tax law isn't ambiguous. The interesting design question is what happens at the boundary — when the AI isn't sure."

> "I also want a baseline metric early — review rate, p95 stage latency, or time to first token — so we can tell whether the change actually improved the workflow."

### At Confidence Router

> "This is the most important 10 lines in the system. Everything upstream produces a confidence score; everything downstream depends on this routing decision. In production, I'd want this to be configurable per market because risk tolerance differs."

> "I also want to tie this to operator economics immediately: if this lowers automation errors but raises review minutes per 100 transactions, we didn't really improve the workflow."

### At Observability

> "I'm adding a trace because in production, when a transaction is mis-categorized, the first question is always: what did each stage decide, and what was the confidence? Without the trace, debugging is archaeology."

> "I also want the trace to record the evidence bundle or missing-evidence reason, because 'the model felt good about it' is not an audit trail."

> "If retrieval is part of the design, I want the final output to cite which receipt field, prior booking, or market rule justified the action. Otherwise the answer is structured but still not grounded."

### At Adoption Surface

> "I'm keeping the public contract small and obvious so a product team could adopt this without rewriting their service boundary. If the reusable path is heavier than the local workaround, teams will bypass it."

> "I want the agent to generate one bounded slice at a time because that keeps review burden low and makes the pattern easier for other engineers to trust."

### At Multi-Market Extension

> "Adding France means: different chart of accounts, different VAT rates, different reduced-rate categories. The key insight is that market config is data, not code — you shouldn't need a deploy to add Italy."

---

## Common Pitfalls in Agent-Assisted Live Rounds

| Pitfall | What It Looks Like | How to Avoid |
|---------|-------------------|--------------|
| **Volume trap** | Generating 300 lines in first 5 minutes | Scope small, verify often |
| **Delegation fallacy** | "Claude, design the architecture" | You design; agent implements |
| **Review skip** | Accepting agent output without reading | 10-second pause after each generation |
| **Speed theater** | More generated code, same or worse operator/review load | Name the metric you are improving, not just the code you are writing |
| **Optimization without baseline** | Refactoring for speed with no stage timing data | Capture a quick before-state first: stage timings, TTFT, or p95 latency |
| **Over-engineering** | Adding DI, factories, abstract base classes | Keep it concrete and flat |
| **Under-explaining** | Coding in silence | Narrate decisions, especially trade-offs |
| **Tool wrestling** | Spending 5 minutes on agent config | Know your setup cold before the interview |

---

## Pre-Interview Environment Checklist

- [ ] Claude Code / Codex installed and authenticated
- [ ] TypeScript + Bun running (test with `bun run rehearsal`)
- [ ] Zod available (`bun add zod` already done)
- [ ] Terminal font size increased for screen sharing
- [ ] `live-round-rehearsal.ts` run once to verify everything works
- [ ] Second monitor or split screen for reviewing agent output

---

## Connection to Prep Materials

- **Rehearsal code:** `code/live-round-rehearsal.ts` — the 20-minute drill that exercises all patterns above
- **MAS demo:** `code/accounting-mas-pipeline.ts` — the full architectural reference
- **Interview questions:** `prep/3-lead-ai-engineer-prep-plan.md` — likely questions and answer skeletons
- **MCP study:** `insights/mcp-architecture-study.md` — if they ask about tool/service integration
