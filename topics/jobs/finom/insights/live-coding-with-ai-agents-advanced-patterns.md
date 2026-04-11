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

## Live Round Strategy: What to Say Out Loud

The interviewer evaluates your thinking, not just your code. These are the **verbal checkpoints** that demonstrate product engineering judgment:

### At Problem Statement

> "Before I start coding — let me make sure I understand the boundary. The categorization is where AI adds value; VAT calculation must be deterministic because tax law isn't ambiguous. The interesting design question is what happens at the boundary — when the AI isn't sure."

### At Confidence Router

> "This is the most important 10 lines in the system. Everything upstream produces a confidence score; everything downstream depends on this routing decision. In production, I'd want this to be configurable per market because risk tolerance differs."

### At Observability

> "I'm adding a trace because in production, when a transaction is mis-categorized, the first question is always: what did each stage decide, and what was the confidence? Without the trace, debugging is archaeology."

### At Multi-Market Extension

> "Adding France means: different chart of accounts, different VAT rates, different reduced-rate categories. The key insight is that market config is data, not code — you shouldn't need a deploy to add Italy."

---

## Common Pitfalls in Agent-Assisted Live Rounds

| Pitfall | What It Looks Like | How to Avoid |
|---------|-------------------|--------------|
| **Volume trap** | Generating 300 lines in first 5 minutes | Scope small, verify often |
| **Delegation fallacy** | "Claude, design the architecture" | You design; agent implements |
| **Review skip** | Accepting agent output without reading | 10-second pause after each generation |
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
