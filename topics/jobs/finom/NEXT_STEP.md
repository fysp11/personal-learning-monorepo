# Finom — Next Step

## Interview Thesis

- **Interview 3** is the live technical round: `30 min` technical questions, `60 min` Claude Code / Codex problem-solving.
- Best positioning: **product-minded AI engineer** who can decompose ambiguous workflows, keep controls explicit, and use coding agents without losing rigor.
- Canonical sources: `README.md`, `interviews/3-lead-ai-engineer/README.md`, `prep/fresh-intel-april-2026.md`.

---

## Carry-Forward Signals

- Production AI, not demos
- Evaluation, observability, latency, and failure modes
- Product-grounded engineering decisions
- Agent orchestration in real workflows
- AI embedded into product engineering, not treated as a novelty silo

---

## Interview 3 — What To Optimize For

### Safest profile

- Senior or lead AI engineer close to implementation
- Evaluates technical judgment, workflow design, and execution quality
- Expects a `product engineer` profile: technical depth plus operational leverage plus enough influence to help adoption
- Comfortable with a `small`, direct, low-ceremony engineering environment
- Treats AI-tool usage as an operating capability, not a novelty

### What they likely care about

- Deterministic vs LLM boundaries
- Workflow decomposition and failure handling
- Confidence routing and human review
- Observability, evals, and rollback paths
- Whether your design actually completes work and returns a result
- Whether you can help adoption happen in practice through usable patterns
- Whether you connect design choices to business outcomes like less manual work, lower review burden

### What they are likely testing

- Can you structure an ambiguous problem quickly?
- Can you choose the right abstraction level?
- Can you verify and correct AI-generated code instead of trusting it blindly?
- Can you combine technical rigor with product judgment?
- Can you produce forward motion in a small-team, high-autonomy environment without waiting for perfect instructions?
- Can you translate a central AI pattern into something a domain team would actually adopt?
- Can you explain why some teams get slower with AI tools and what habits reverse that?

---

## Core Synthesis

> Build proactive AI workflows that actually complete meaningful work, but earn autonomy stage by stage with deterministic controls, visible failure points, and approval gates where compliance risk is real.

And from Ivo's framing:

> The target UX is closer to `go do the task, then come back` than `here is the next thing you should click`.

Finom-specific business read:

> Ivo pointed to tax workflow automation in `Germany` with movement toward `France`; treat the France part as interview-derived, not public intel.

### Good framing

**Keep explicit:**
- stage boundaries
- typed inputs and outputs
- confidence signals
- fallback and review paths
- success metrics
- why a step is `proposal-only` versus allowed to act

**Use AI selectively for:**
- extraction from messy inputs
- proposal generation
- ambiguity resolution
- classification where heuristics are brittle

### Avoid

- Sounding like an agent maximalist
- Talking mostly in framework names
- Treating the model as policy engine
- Jumping into code without scoping the workflow first

---

## Best Positioning

> I build production-grade AI systems by keeping policy deterministic, isolating AI to the ambiguous parts, and shipping with evals, routing, and clear failure controls.

---

## Questions Interview 3 Is Likely To Ask

1. What should be deterministic vs LLM-driven in this workflow?
2. How would you decompose this problem into stages?
3. How would you evaluate a financial AI workflow?
4. How do you handle low-confidence outputs?
5. What observability would you add first?
6. When do you use a staged workflow versus a single agent?
7. How would you integrate this into an existing Python and C# stack?
8. What would you implement first if given 60 minutes?
9. How would you make an AI workflow genuinely proactive without making it unsafe?
10. How do you decide when to widen automation from proposal mode to auto-book?

---

## Good Questions To Ask The Interviewer

1. What kinds of AI systems is the team actually shipping today?
2. Where do current workflows break down most often: extraction, reasoning, orchestration, or integration?
3. How do you evaluate correctness for finance-sensitive automations?
4. What separates engineers who get faster with `Codex` / `Claude` from those who get slower?
5. Where is the current friction: central AI discovering good patterns, or domain teams turning those patterns into durable product behavior?

---

## Answers To Have Ready

### Why Finom

- AI applied to operational workflows where correctness matters
- Strong match for production AI rather than demo-driven AI
- Interesting tension between embedded product work and shared AI leverage

### Why you

- You can build real systems, not just prototypes
- You care about evaluation, observability, and reliability
- You can think at both workflow level and platform/org level

### Central AI philosophy

- Keep deterministic control where failure cost is high
- Use AI where the input is ambiguous or unstructured
- Measure success by override rate, severe-error rate, review burden, and shipped workflow value
- Treat `AI team` and `ML team` as different functions: LLM workflow design is closer to product/software architecture than classic predictive ML
- Use central teams to create reusable patterns and adoption leverage, not to pull every domain decision away from product teams
- Measure progress in real workflow terms: approvals avoided, review load reduced, cycle time shortened

---

## Prep Materials Index (Updated Apr 12 — Iteration 9)

### Day-Of (read in this order)
1. `prep/proposals/3-pre-call-cheat-sheet.md` — **15 min before call**: key numbers, deterministic/AI splits, maturity ladder, GoBD one-liner, France delta, day-of checklist
2. `prep/3-lead-ai-engineer-day-of-card.md` — 2-min skim: thesis, checklist, key numbers, gap responses
3. `prep/fresh-intel-april-2026.md` — canonical public signals: AI Accountant GA, 200K+ accounts

### Technical Depth
- `prep/3-lead-ai-engineer-prep-plan.md` — main 17-question prep plan
- `prep/3-technical-answer-bank.md` — **12 full-depth answers** including maturity ladder, staged workflow, observability
- `prep/3-lead-ai-hostile-followups.md` — hostile follow-up questions with target answers
- `prep/live-round-scenarios.md` — scenario playbooks (A–E) for the 60-min live coding exercise
- `prep/proposals/3-live-round-clock.md` — **minute-by-minute 60-min timer**: deliverables per gate, recovery pivots, clock recovery matrix
- `prep/3-lead-ai-engineer-night-before.md` — night-before reading sequence + warm-up scripts
- `insights/live-coding-with-ai-agents-advanced-patterns.md` — verbal anchors for live round
- `insights/confidence-calibration-deep-dive.md` — ECE, Platt scaling, earned autonomy math



### Code (verified running)
| Script | What it proves |
|--------|---------------|
| `bun run rehearsal` | Core pipeline: extract → categorize → VAT → route → book, DE+FR |
| `bun run demo` | Multi-agent orchestration, circuit breaking, end-to-end trace |
| `bun run eval` | Severity-weighted evaluation, calibration, regression detection |
| `bun run calibration` | ECE, Platt scaling, per-market calibration curves |
| `bun run autonomous-batch` | Month-end "go do the task, come back" — structured completion report |
| `bun run resilience` | Circuit breaker, idempotency, lifecycle audit, anomaly detection |
| `bun run refactoring-exercise` | Scenario B: messy blob → clean staged pipeline |
| `bun run observability` | Confidence drift, terminal state tracking, business KPI dashboard |

---

## Final Reminder

- For **Interview 3**, prove: **I can reason clearly, scope fast, and use AI tools without losing control of the system.**