# Interview 3 Prep — Iteration Proposals

This directory holds deeper prep artifacts created during the Ralph loop iterations. Each document represents a focused deepening of a specific knowledge area beyond the core prep plan.

## Contents

| Document | What it adds | When to use |
|----------|-------------|-------------|
| `3-ustava-walkthrough.md` | Step-by-step procedural walkthrough of a German SME's month-end accounting close, from transaction ingestion to ELSTER filing | Answer "walk me through what the AI actually does" or "describe a user's month-end experience" |
| `3-financial-ai-failure-modes.md` | Named catalog of 20 failure modes across extraction, categorization, VAT, confidence routing, orchestration, and market expansion | Answer any question about reliability, production incidents, what keeps you up at night, or how you'd test this system |

## Related files

- `../3-technical-answer-bank.md` — Q9 added: polyglot C#/.NET integration talking points
- `../german-sme-accounting-domain-primer.md` — vocabulary reference (prerequisite to the UStVA walkthrough)
- `../../code/mcp-accounting-server.ts` — live code demonstrating MarketPolicy interface and confidence routing
- `../../code/eval-harness.ts` — severity-weighted evaluation framework referenced in FM-04, FM-10
