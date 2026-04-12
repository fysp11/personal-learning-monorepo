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
- Whether you connect design choices to business outcomes like less manual work or lower review burden

### What they are likely testing

- Can you structure an ambiguous problem quickly?
- Can you choose the right abstraction level?
- Can you verify and correct AI-generated code instead of trusting it blindly?
- Can you combine technical rigor with product judgment?
- Can you produce forward motion in a small-team, high-autonomy environment without waiting for perfect instructions?
- Can you translate a central AI pattern into something a domain team would actually adopt?
- Can you explain why some teams get slower with AI tools and what habits reverse that?

---

## Core Synthesis — Reconcile Dmitry And Interview 3

This is the most important prep point:

> Build AI where ambiguity is real, keep policy deterministic, and make the workflow observable enough that humans can trust and debug it.

More precise after the Ivo source record:

> Build proactive AI workflows that actually complete meaningful work, but earn autonomy stage by stage with deterministic controls, visible failure points, and approval gates where compliance risk is real.

And more concretely from Ivo's framing:

> The target UX is closer to `go do the task, then come back` than `here is the next thing you should click`.

Finom-specific business read:

> The company is not optimizing for "AI features" in the abstract. It is optimizing for operational compression, AI-native product behavior, and selective replacement of low-leverage human work.

Concrete source record anchor:

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

Use this frame:

- I build **production-grade AI systems**
- I know how to turn ambiguous workflow steps into **observable staged systems**
- I use coding agents as force multipliers, not as substitutes for engineering judgment
- I care about correctness-sensitive workflows and trust
- I can work across both `central AI` and `domain` contexts by translating reusable patterns into domain-specific delivery
- I can help good patterns get adopted, not just implemented once
- I can make AI-tool usage operationally useful for a small team, not just personally impressive

### One-line version

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
10. How do you make AI tooling increase engineering throughput instead of slowing people down?

---

## Good Questions To Ask The Interviewer

1. What kinds of AI systems is the team actually shipping today?
2. Where do current workflows break down most often: extraction, reasoning, orchestration, or integration?
3. How do you evaluate correctness for finance-sensitive automations?
4. What does strong performance in this role look like after 3 to 6 months?
5. How does the team divide responsibilities between shared AI infrastructure and product delivery?
6. What do you wish candidates understood better about your stack or workflow design?
7. In the live round, do you care more about completeness or reasoning quality?
8. Where is the current friction: central AI discovering good patterns, or domain teams turning those patterns into durable product behavior?
9. What have you seen separate engineers who get faster with `Codex` / `Claude` from those who get slower?

---

## Answers To Have Ready

### Why Finom

- AI applied to operational workflows where correctness matters
- Strong match for production AI rather than demo-driven AI
- Interesting and important tension between embedded product work and shared AI leverage

### Why you

- You can build real systems, not just prototypes
- You care about evaluation, observability, and reliability
- You can think at both workflow level and platform/org level
- You centralize selectively rather than ideologically

### Central AI philosophy

- Keep deterministic control where failure cost is high
- Use AI where the input is ambiguous or unstructured
- Measure success by override rate, severe-error rate, review burden, and shipped workflow value
- Add an operational lens: time saved, manual steps removed, and review load reduced
- Treat `AI team` and `ML team` as different functions: LLM workflow design is closer to product/software architecture than classic predictive ML
- Use central teams to create reusable patterns and adoption leverage, not to pull every domain decision away from product teams
- Measure progress in real workflow terms: approvals avoided, review load reduced, cycle time shortened, and manual work actually removed

---

## Prep Materials Index (Updated Apr 11)

### Day-Of
- `prep/3-lead-ai-engineer-day-of-card.md` — **2-minute skim** with thesis, checklist, verbal checkpoints, key numbers, gap responses
- `prep/fresh-intel-april-2026.md` — **canonical public signals**: AI Accountant GA, 200K+ accounts, payroll/ZM roadmap

### Technical Depth
- `prep/3-lead-ai-engineer-prep-plan.md` — main 17-question prep plan
- `prep/3-lead-ai-hostile-followups.md` — 18 hostile follow-up questions with target answers
- `insights/live-coding-with-ai-agents-advanced-patterns.md` — scaffold/implement/debug modes for the 60-min live round
- `insights/confidence-calibration-deep-dive.md` — ECE, Platt scaling, earned autonomy math

### Code (All Verified Running)
- `code/live-round-rehearsal.ts` — `bun run rehearsal` — the core 20-min drill
- `code/confidence-calibration.ts` — `bun run calibration` — per-market calibration analysis
- `code/multi-market-expansion-drill.ts` — `bun run multi-market` — DE/FR/IT/NL zero-code extension

### Cross-Company
- `../cross-company-system-design-template.md` — reusable 7-step system design framework
- `../cross-company-production-feedback-loops.md` — correction routing and eval suite growth
- `../cross-company-error-taxonomy-worked-examples.md` — Finom-specific error trees

---

## Final Reminder

- For **Interview 3**, prove: **I can reason clearly, scope fast, and use AI tools without losing control of the system.**
