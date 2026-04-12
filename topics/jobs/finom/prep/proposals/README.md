# Interview 3 Prep — Iteration Proposals

This directory holds deeper prep artifacts created during the Ralph loop iterations. Each document represents a focused deepening of a specific knowledge area beyond the core prep plan.

## Contents

| Document | What it adds | When to use |
|----------|-------------|-------------|
| `3-ustava-walkthrough.md` | Step-by-step procedural walkthrough of a German SME's month-end accounting close, from transaction ingestion to ELSTER filing | Answer "walk me through what the AI actually does" or "describe a user's month-end experience" |
| `3-financial-ai-failure-modes.md` | Named catalog of 20 failure modes across extraction, categorization, VAT, confidence routing, orchestration, and market expansion | Answer any question about reliability, production incidents, what keeps you up at night, or how you'd test this system |

## Iteration 6 additions

| Document | What it adds | When to use |
|----------|-------------|-------------|
| `3-france-expansion-technical.md` | PCG vs SKR03, 4-rate VAT structure, CA3 vs UStVA, September 2026 e-invoicing mandate (Chorus Pro/Factur-X), cold-start calibration problem, what transfers vs what's new | Any multi-market question; "how would you add France?"; what surprises the France launch |
| `3-fte-metric-analysis.md` | Deep analysis of Ivo's "FTE per active customer" metric — how to decompose it, which AI pipeline stages move it, how to measure it, how to answer "how would you know the AI is working?" | Metrics/impact questions; closing the round with business thinking |

## Iteration 6 code additions

| File | What it shows |
|------|--------------|
| `../../code/autonomous-batch-processor.ts` | The "go do the task, come back" pattern: 15-transaction month-end batch → 8 auto-booked, 3 proposals, 4 requires-attention, draft UStVA with natural-language summary. Shows earned autonomy (reverse charge always surfaced, filing requires signature). |

Run: `bun run autonomous-batch` in the `code/` directory.

## Iteration 5 additions

| Document | What it adds | When to use |
|----------|-------------|-------------|
| `3-90-day-plan.md` | Concrete 90-day plan mapped to Ivo's three workstreams: operational grounding → first contribution → adoption leverage | Answer "what would you do in your first 90 days?" — closes the round strong |
| `3-adoption-mechanics.md` | How AI adoption actually works: diagnostic first, fast path faster than workaround, live demo > workshop, right metrics (override rate, velocity delta) | Answer any question about the adoption workstream or making a central AI team useful |

## Iteration 5 code additions

| File | What it shows |
|------|--------------|
| `../../code/production-resilience-patterns.ts` | Circuit breaker (FM-14), idempotency registry (FM-16/FM-18), retry with backoff, transaction lifecycle audit (FM-15), batch anomaly detection (FM-01/FM-10) — all 5 patterns working together, mapped to failure mode catalog |

Run: `bun run resilience` in the `code/` directory.

## Related files

- `../3-technical-answer-bank.md` — Q9 added: polyglot C#/.NET integration talking points
- `../german-sme-accounting-domain-primer.md` — vocabulary reference (prerequisite to the UStVA walkthrough)
- `../../code/mcp-accounting-server.ts` — live code demonstrating MarketPolicy interface and confidence routing
- `../../code/eval-harness.ts` — severity-weighted evaluation framework referenced in FM-04, FM-10
