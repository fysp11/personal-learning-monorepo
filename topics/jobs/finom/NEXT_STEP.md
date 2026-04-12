# Finom — Next Step

## Interview Thesis

- **Dmitry** tested engineering rigor and production readiness.
- **Interview 3** is a technical round with a `Senior AI Engineer`: `30 min` technical questions, `60 min` live problem-solving with `Claude Code` or `Codex`.
- The `2026-04-09` capture watchlog for the Ivo round remained stable through `2026-04-09T21:49:07Z` and still shows `no-whisper-processes-detected`, so the Ivo-derived signals below are safe to use as prep input.
- The recruiter follow-up confirms the format, but the engineer name is still noisy / unconfirmed in the source record, so optimize for role shape rather than a guessed person.
- Best positioning: **product-minded AI engineer** who can decompose ambiguous workflows, keep controls explicit, and use coding agents without losing rigor.

---

## Dmitry — What To Carry Forward

### Role

- CTO at Finom

### What he seems to care about

- Production AI, not demos
- Evaluation, observability, latency, and failure modes
- Product-grounded engineering decisions
- Agent orchestration in real workflows
- AI embedded into product engineering, not treated as a novelty silo

### Strongest signals from the first interview

- Finom is serious about **agentic accounting workflows**
- The role is closer to **product engineering with strong AI depth** than to pure research
- Reliability, operational ownership, and shipping quality matter as much as model capability
- Finom appears to want AI capabilities spread through product engineering, even if some central capability exists

### What to prove if his lens comes back up

- You can productionize AI systems cleanly
- You think in terms of evaluation and observability, not just prompts and models
- You understand approval flows, failure isolation, fallback behavior, and rollout discipline

---

## Interview 3 — What To Optimize For

### Safest profile

- Senior or lead AI engineer working close to real implementation
- Likely the `leading engineer` Ivo explicitly said would evaluate your technical side because he is `a little bit technical` but `not super technical`
- Likely cares more about technical judgment, workflow design, and execution quality than company-level narrative
- Safest framing: **hands-on evaluator of how you think, scope, work creatively, and turn AI tooling into real speed**
- Likely operating inside the org shape Ivo described: `AI team` distinct from `ML team`, with some shared patterns and some domain embedding
- Likely expects a `product engineer` profile: technical depth plus operational leverage plus enough influence to help adoption
- Likely expects someone comfortable in a `small`, direct, low-ceremony engineering environment
- Likely sits near a team that treats AI-tool usage as an operating capability, not just a personal preference

### What they likely care about

- Deterministic vs LLM boundaries
- Workflow decomposition and failure handling
- Confidence routing and human review
- Observability, evals, and rollback paths
- How well you use `Codex` / `Claude` under time pressure
- Whether those tools make you faster instead of noisier
- Whether you can design something `creative`, not just answer textbook system-design prompts
- Engineering judgment over raw coding speed
- Whether you can work inside a `small`, high-caliber, direct-feedback team without needing a lot of process scaffolding
- Whether you connect design choices to business outcomes like less manual work, fewer support steps, or lower review burden
- Whether your design actually completes work and returns a result, instead of stopping at a recommendation
- Whether you can help adoption happen in practice through usable patterns instead of mandates
- Whether you can reason about workflow compression with metrics like reduced manual touch or lower `FTE per active customer`

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

> Ivo pointed to tax workflow automation in `Germany` with movement toward `France`, so expect questions that start from a real shipped finance workflow and then expand to multi-market scaling.

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

---

## Prep Materials Index (Updated Apr 12 — Iteration 8)

### Day-Of (read in this order)
1. `prep/3-lead-ai-engineer-day-of-card.md` — 2-min skim: thesis, checklist, key numbers, gap responses
2. `prep/fresh-intel-april-2026.md` — latest signals: GA, 200K+, payroll roadmap
3. `prep/proposals/README.md` — 2-min scan: what each proposal doc adds

### Technical Depth
- `prep/3-lead-ai-engineer-prep-plan.md` — 17-question prep plan, drills 1–9
- `prep/3-lead-ai-hostile-followups.md` — **11 categories**, including iterations 4–7 topics
- `prep/3-live-round-scenarios.md` — 5 scenario playbooks (A–E) for live coding
- `prep/3-lead-ai-engineer-night-before.md` — night-before reading sequence + warm-up scripts
- `prep/3-technical-answer-bank.md` — 9 full-depth answers (Q1–Q9 including C#/.NET)
- `insights/live-coding-with-ai-agents-advanced-patterns.md` — verbal anchors for live round
- `insights/confidence-calibration-deep-dive.md` — ECE, Platt scaling, earned autonomy math

### Domain Knowledge
- `prep/german-sme-accounting-domain-primer.md` — vocabulary reference
- `prep/proposals/3-ustava-walkthrough.md` — procedural month-end close narrative
- `prep/proposals/3-france-expansion-technical.md` — PCG, CA3, Sept 2026 Chorus Pro mandate

### Business Impact
- `prep/proposals/3-fte-metric-analysis.md` — FTE/customer decomposition + interview answers
- `prep/proposals/3-90-day-plan.md` — first-90-days answer mapped to Ivo's three workstreams
- `prep/proposals/3-adoption-mechanics.md` — what makes AI adoption actually work

### Failure Modes
- `prep/proposals/3-financial-ai-failure-modes.md` — 20 named failure modes across 7 categories

### Behavioral
- `prep/proposals/3-interview3-story-bank.md` — 6 stories with story→question mapping table
- `prep/gap-mitigation.md` — fintech gap, C#/.NET gap, other objections

### Code (9 demos — all verified running)

| Script | What it proves |
|--------|---------------|
| `bun run rehearsal` | Core pipeline: extract → categorize → VAT → route → book, DE+FR |
| `bun run demo` | Multi-agent orchestration, circuit breaking, end-to-end trace |
| `bun run eval` | Severity-weighted evaluation, calibration, regression detection |
| `bun run calibration` | ECE, Platt scaling, per-market calibration curves |
| `bun run multi-market` | Zero-code market addition, Zod-validated config, Italy SDI |
| `bun run mcp-server` | MCP skill server, 5 markets, composable tools |
| `bun run resilience` | Circuit breaker, idempotency, lifecycle audit, anomaly detection |
| `bun run autonomous-batch` | Month-end "go do the task, come back" — structured completion report |
| `bun run refactoring-exercise` | Scenario B: messy blob → clean stages, all anti-patterns labeled |

**Night-before warm-up** (5 scripts, ~60 seconds):
```bash
cd topics/jobs/finom/code
bun run rehearsal && bun run autonomous-batch && bun run resilience && bun run refactoring-exercise && bun run calibration
```

### Cross-Company
- `../cross-company-system-design-template.md` — 7-step system design skeleton
- `../cross-company-production-feedback-loops.md` — correction routing, eval suite growth
- `../cross-company-error-taxonomy-worked-examples.md` — Finom-specific error trees

---

## Final Reminder

- For **Dmitry**, prove: **I can build this well.**
- For **Interview 3**, prove: **I can reason clearly, scope fast, and use AI tools without losing control of the system.**

### Key numbers to know cold

| Number | What it is |
|--------|-----------|
| 19% / 7% | German VAT rates (standard / reduced) |
| 20% / 10% / 5.5% / 2.1% | French VAT rates |
| 0.85 / 0.5 | Auto-book / proposal confidence thresholds |
| ECE < 0.05 | Calibration bar before trusting confidence for routing |
| Sept 1, 2026 | French B2B e-invoicing mandate (Chorus Pro) |
| 200K+ | Finom active accounts (Apr 2026) |
| FTE/customer | Ivo's business metric for AI impact |
| SKR03 / PCG | German / French chart of accounts standard |
