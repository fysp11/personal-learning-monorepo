# Finom Interview 3 — 20-Hour Prep Schedule

**Interview:** April 14, 2026 (afternoon CET)
**Interviewer:** Viktar Adynets — Senior/Lead AI Engineer
**Format:** 90 min (30 min technical questions + 60 min live coding with Claude Code/Codex)

---

## Interview Thesis

> Production AI engineer who builds observable workflow systems, keeps policy deterministic, uses AI for ambiguity, and earns autonomy step by step.

**Short version:** AI for ambiguity. Software for policy. Measurable leverage over demo energy.

---

## What Viktar Is Likely Testing

- precise problem decomposition (CP/contest background)
- clean invariants and named failure modes
- fast detection of hand-wavy logic
- disciplined Codex/Claude use — force multiplier, not brain delegation
- production AI systems, not demos

---

## Cross-Cutting Threads (Weave Into Every Block)

- Every stage decomposition includes: how does this fail, how do we detect it, what's the severity?
- Q12 observability anchor: confidence distribution first, terminal state tracking second, business KPIs third
- The trace object is part of every live deliverable — not optional

---

## Block 1 — Technical Foundation (6h)

**Goal:** Sharpen the CP-minded lens. Viktar probes for invariants and named failure modes, not fuzzy AI vocabulary.

### Session 1A — v-adynets deep read + Q2/Q11 rewrite (2h)

- 30min: Re-read `v-adynets.md` fresh. Write 5 bullet points: how his CP/contest background changes what he values in an answer.
- 45min: Rewrite Q2 (deterministic vs AI) — frame each line around a named failure mode.
  > "VAT calc must be deterministic because a wrong rate triggers a Berichtigte Voranmeldung — that's a compliance event with a paper trail, not a UX correction."
- 45min: Rewrite Q11 (staged workflow vs single agent) — focus on heterogeneous failure modes and independent testability.
  > "If extraction and categorization are one stage, you can't regression-test categorization without hitting OCR."

### Session 1B — 7-step system design with Finom numbers (2h)

- 30min: Write out the 7-step framework applied to Germany: VAT 19%/7%, SKR03, UStVA monthly/quarterly, 200K accounts, ~99% auto-reconciliation.
- 45min: Practice Q3 (eval) and Q9 (production pain) using the sync→async numbers:
  > "On 20-item batch at 40ms/item, bounded async goes 864ms → 164ms — that's the Triple Dipper in practice."
- 45min: Practice Q12 (observability priority) — 3 layers: confidence distribution first, terminal state tracking second, business KPIs third. Know why that order.

### Session 1C — Failure mode inventory (2h)

- 1h: Write a failure mode inventory for the Finom accounting pipeline:
  - Extraction fails on bad OCR
  - Categorization fails on novel merchants
  - VAT fails on missing B2B flags
  - Router fails on uncalibrated thresholds
  - Booking fails on stale market config
  For each: detection method, response, severity.
- 30min: Practice Q7 (automate vs assist) and Q8 (AI team vs ML team) with failure mode language.
- 30min: Rehearse the 7-step framework out loud, cold, without notes. Time yourself — must be under 5 minutes.

---

## Block 2 — AI Design Patterns (6h)

**Goal:** Own confidence routing and staged workflow architecture cold. This is the structural core of Finom's AI system.

### Session 2A — Scenario A decomposition (2h)

- 30min: Read Scenario A in `3-live-round-scenarios.md` — then close the file and write the 5-stage pipeline from memory: extract → categorize → VAT → route → book.
- 30min: For each stage: typed input/output, failure mode, confidence threshold.
- 1h: On paper: draw the pipeline with all contracts, thresholds, and trace fields marked. Cold-scribblable in under 5 minutes.

### Session 2B — 3-stage implementation drill (2h)

- 2h: Implement from scratch (no reference): a 3-stage workflow (extract, categorize with mock AI, confidence route) with typed contracts (Pydantic/Zod), per-stage confidence, low-confidence escalation, and a trace array. Time-box to 90 minutes max.

### Session 2C — Automation ladder + multi-market (2h)

- 45min: Study Q10 (automation maturity ladder). Write the 5 levels with Finom numbers: Germany at Level 3, France starts at Level 0 with specific calibration criteria to advance.
- 45min: Study Q4 (Germany → France generalization). Write the `MarketConfig` interface — then explain why VAT rates must be code, not prompts, in 30 seconds.
- 30min: Practice the ladder + multi-market out loud. Must sound natural, not rehearsed.

---

## Block 3 — AI Harnessing Execution (8h)

**Goal:** The 60-minute live coding exercise. Viktar explicitly cares whether Codex/Claude Code makes you faster or just generates cleanup work.

### Session 3A — Environment verification (2h)

- 30min: Verify `uv sync` works in the sync→async pack directory.
- 30min: Run `bad_sync_api.py --self-check` and `good_async_api.py --self-check`. Confirm both pass.
- 30min: Run demo mode side by side: `bad_sync_api.py --demo` and `good_async_api.py --demo`. Note the exact elapsed_ms numbers.
- 30min: Verify Claude Code / Codex is authenticated and responsive. Test with a simple prompt.

### Session 3B — Scenario F timed simulation (3h)

- 15min: Read Scenario F (sync→async refactor) in `3-live-round-scenarios.md` — then close it.
- 5min: Start the clock.
- 50min: Execute Scenario F under full time pressure:
  1. Scope before coding
  2. Freeze request/response contracts
  3. Extract AI dependency behind shared port
  4. Replace sequential loop with `asyncio.gather` + semaphore
  5. Preserve ordering and error shape
  6. Add one contract-parity test
- 5min: Stop. Assess: where did you rush? Over-engineer? Scope first?
- 45min: Run it again (second attempt). Scope aggressively, reject unnecessary abstractions, keep the trace simple.

### Session 3C — Codex discipline + Finom anchor (2h)

- 30min: List the 5 Codex discipline rules: precise instructions, small steps, read every output, correct fast, reject unnecessary abstractions. For each: what does bad look like vs good.
- 30min: Practice giving Codex a small, scoped task — one function, not a module. Time the loop: prompt → read → correct → verify. Be surgical, not expansive.
- 30min: Write and rehearse the 20-second Finom anchor:
  > "I'm changing execution strategy, not API shape. Bounded concurrency cuts latency without changing client integration. The semaphore is the circuit breaker — unbounded fan-out destabilizes the provider under load."
- 30min: Practice out loud — must sound like you, not a script.

### Session 3D — Day-of card + final review (1h)

- 30min: Read `3-lead-ai-engineer-day-of-card.md` fresh. Identify the 3 things most likely to trip you under pressure.
- 30min: Re-read the 10 red flags. Pick the 2 you're most likely to fall into and write a one-sentence recovery line for each.

---

## Schedule at a Glance

| Block | Session | Hours |
|-------|---------|-------|
| **Technical Foundation** | 1A: v-adynets + Q2/Q11 | 2h |
| | 1B: 7-step with Finom numbers | 2h |
| | 1C: Failure mode inventory | 2h |
| **AI Design Patterns** | 2A: Scenario A decomposition | 2h |
| | 2B: 3-stage implementation drill | 2h |
| | 2C: Automation ladder + multi-market | 2h |
| **AI Harnessing Execution** | 3A: Environment verification | 2h |
| | 3B: Scenario F timed sim (×2) | 3h |
| | 3C: Codex discipline + anchor | 2h |
| | 3D: Day-of card + red flags | 1h |
| **Total** | | **20h** |

---

## Red Flags to Avoid

- sounding framework-first
- overusing the word `agentic`
- letting the coding tool lead the design
- overclaiming fintech expertise
- proposing LLMs for policy-bound tax logic
- skipping verification because "the code looks fine"
- sounding excited about AI without connecting it to operational leverage

---

## Last-Minute Card

If you blank during the round, return to this:

> First define the workflow boundary. Then separate ambiguity from policy. Keep AI on messy judgment, keep deterministic systems on control and compliance, add confidence-aware routing, and verify with observable outputs before calling it done.
