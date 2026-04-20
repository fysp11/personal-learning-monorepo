# Finom — Process Closure Note

**Date:** April 14, 2026
**Outcome:** No offer. Finom indicated a profile mismatch after the third interview.

## What Happened

1. **Interview 1** (Mar 31) — Dmitry Ivanov, CTO. Positive. Covered product direction, AI Accountant architecture, org model. Moved forward.
2. **Interview 2** (Apr 8) — Ivo Dimitrov, CAIO. Positive. Discussed central AI team structure, adoption stream, agent patterns. Moved to technical round.
3. **Interview 3** (Apr 14) — Viktar Adynets, Senior AI Engineer. 90-min round (30 min technical questions + 60 min live coding). Rejected with profile mismatch cited.

## Why It Ended

Finom is looking for a different profile than what this application targeted. The specific mismatch wasn't detailed, but the pattern suggests:
- The role may require deeper hands-on implementation at a specific layer (e.g., more infrastructure/platform, less product/architecture)
- Or the team composition they're building doesn't align with the positioning this prep assumed

This is a **calibration gap**, not a capability gap. The interviews went well at each stage — the issue surfaced at the final round where the team's actual needs became concrete.

## What Worked Well

- **Workspace structure** — dashboard, numbered interview folders, prep/insights split, interviewer profiles. All of it scaled well across 3 rounds.
- **Cross-company prep** — Delphyr and Finom shared themes (EU AI Act, production AI systems, evaluation). The cross-company insights files saved significant prep time.
- **Prep depth** — MAS architecture, confidence calibration, agent safety patterns, live-coding preparation. All high-signal and transferable.
- **Day-of-card format** — one-page quick references for pre-interview review. Keep this pattern.

## What To Improve Next Time

- **Earlier role calibration** — probe for the exact profile and seniority level during the first interview, not just the product and team direction
- **Ask for the rejection reason in writing** — if the company says "profile mismatch," ask what specific skills or experience they were looking for. This is fair game and helps future applications.

## Reusable Material

These files have high reuse value for similar AI engineering roles:

- `insights/interview-3-retrospective.md` — **post-interview analysis**: what likely happened, what "profile mismatch" means technically, what to fix for the next live coding round
- `insights/transferable-patterns-next-ai-role.md` — **synthesis**: vocabulary, live-round operating discipline, Python implementation reference, numbers to know
- `insights/mas-coordination-patterns.md` — multi-agent systems (orchestrator-worker, saga, circuit breaker)
- `insights/confidence-calibration-deep-dive.md` — ECE, Platt scaling, calibration drift
- `insights/agent-safety-transaction-semantics.md` — commit/rollback, autonomy ladder, HITL taxonomy
- `insights/design-patterns-correctness-sensitive-ai.md` — 7 patterns for correctness-critical AI
- `insights/observability-production-agents.md` — tracing, canary routing, alert taxonomy
- `code/python-pipeline/pipeline.py` — **canonical Python implementation**: runs out of the box, covers sync + async batch, multi-market (DE+FR), all terminal states
- `prep/multi-agent-system-architecture-for-fintech.md` — MAS architecture for fintech
- `prep/german-sme-accounting-domain-primer.md` — domain vocabulary (useful for any EU fintech)
- `../cross-company-insights.md` and `../cross-company-insights-deep-patterns.md` — transferable interview patterns
- `../eu-ai-act-regulatory-prep.md` — EU AI Act compliance (useful for any EU AI role)
- `../star-stories.md` — reusable STAR stories

## Lessons

1. **Three rounds without alignment on role specifics is a risk.** If the role description is ambiguous, push harder for clarification in rounds 1-2.
2. **Profile mismatch at round 3 usually means the company's internal calibration changed** — they may have refined what they need through the interview process itself.
3. **The best interview prep is transferable.** Everything built here applies to the next AI engineering role at an EU company with agentic products.
4. **Live coding rounds test fluency, not architecture.** The architectural vocabulary landed well. What a 60-minute live round tests is: can you write clean, idiomatic Python quickly under observation? Build this as the primary skill, not an afterthought.
5. **Build Python first.** The prep heavily used TypeScript (Zod, bun). EU AI companies run Python. The canonical Python pipeline is now in `code/python-pipeline/pipeline.py` — this should be the default for future live rounds.
6. **Scoping compression matters.** 5-minute detailed scoping is too long for a 60-minute round. The compressed version (< 90 seconds) needs to be the rehearsed default.

## Post-Mortem Analysis (Apr 16)

See `insights/interview-3-retrospective.md` for the full post-interview analysis, including:
- What "profile mismatch" likely means in implementation terms
- Four scenarios for what happened in the live round
- What was strong (preserve for future rounds)
- What to build before the next technical live round

See `insights/transferable-patterns-next-ai-role.md` for the synthesis of everything reusable, including the Python implementation reference and the live-round operating discipline.
