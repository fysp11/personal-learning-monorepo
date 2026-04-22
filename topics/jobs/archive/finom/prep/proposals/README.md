# Interview 3 Prep — Proposal Documents

Deep-dive documents created during iteration cycles. Organized by relevance to the April 14 technical round.

## HIGH PRIORITY — Read These First

| Document | What it adds | When to use |
|----------|-------------|-------------|
| `3-scheduled-signal-refinement-prompt.md` | High-rigor scheduled prompt for mining any relevant new signal and selectively upgrading Interview 3 prep docs toward hard skills, product judgment, and execution quality | Use in automations / recurring prep refresh runs |
| `3-live-round-clock.md` | Minute-by-minute 60-min live coding timer: deliverables per gate, recovery pivots, clock recovery matrix | Read night before; use recovery matrix if you fall behind |
| `3-pre-call-cheat-sheet.md` | 2-page synthesis: key numbers table, deterministic vs AI splits, named failure modes, maturity ladder, GoBD one-liner, France delta, day-of checklist | Read 15 minutes before the interview — final recall document |
| `3-failure-mode-inventory.md` | **Full FM-01 to FM-18 inventory** with detection signals, responses, severity, and prevention patterns for all 18 named failure modes. Organized by pipeline layer. Includes interview anchor phrase using invariant language. | Read for any production pain, failure mode, or observability question — especially if Viktar probes invariants |
| `../../../../ai-engineering/code/python-sync-async-refactor/INTERVIEW_PACK.md` | Python technical drill: bad sync AI REST API refactored to async with same contract, plus interview talk-track anchors | Read before live coding rehearsal focused on latency/cost/trust questions |

## Related files

- `../3-technical-answer-bank.md` — Q1–Q12 full-depth answers
- `../3-live-round-scenarios.md` — Scenario playbooks (A–E) for the 60-min exercise
- `../../code/autonomous-batch-processor.ts` — Month-end "go do the task, come back" batch pattern
- `../../code/production-resilience-patterns.ts` — Circuit breaker, idempotency, lifecycle audit
- `../../code/refactoring-exercise.ts` — Scenario B: messy blob → clean staged pipeline
- `../../code/observability-patterns.ts` — Confidence drift, terminal state tracking, business KPI dashboard
