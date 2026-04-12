# Interview 3 — Night-Before Review Sequence

Saved: 2026-04-11

## Purpose

A single reading sequence for the evening before the April 14 interview. Each item has a time estimate. Total: ~45 minutes. Don't cram — skim what you've already internalized, slow down on anything that feels fuzzy.

---

## Phase 1: Refresh the Thesis (5 min)

1. **`NEXT_STEP.md`** — Read the "Core Synthesis" section (lines 83-130). Internalize the one-sentence thesis:
   > Build proactive AI workflows that actually complete meaningful work, but earn autonomy stage by stage.

2. **`prep/3-lead-ai-engineer-day-of-card.md`** — Skim the "2-Minute Skim" section. Memorize the three things to prove.

---

## Phase 2: Fresh Intel (3 min)

3. **`prep/fresh-intel-april-2026.md`** — Read the "Key Updates" section. Know the headline numbers:
   - AI Accountant: GA for all German customers
   - 200K+ accounts
   - Upcoming: Lohnsteueranmeldung, Zusammenfassende Meldung
   - Late 2026: invoice financing, credit lines

---

## Phase 3: Technical Depth (15 min)

4. **`prep/3-lead-ai-hostile-followups.md`** — Read Categories 1-3 (confidence, AI boundaries, live coding). Practice the ECE explanation aloud:
   > "Of all predictions where the model said 0.85+, what percentage were correct? That's the calibration check."

5. **`insights/live-coding-with-ai-agents-advanced-patterns.md`** — Skim the "Three Modes" section and the "Things to Say Out Loud" table. These are your verbal anchors during the live round.

6. **`insights/confidence-calibration-deep-dive.md`** — Skim "Core Concepts" and the "Per-Market Calibration" section. Know why France needs conservative thresholds.

---

## Phase 4: Run the Code Once (10 min)

7. Open terminal, navigate to `code/`:
   ```bash
   cd topics/jobs/finom/code
   bun run rehearsal         # 20s — DE/FR pipeline, confidence routing
   bun run autonomous-batch  # 10s — month-end "go do, come back" pattern
   bun run resilience        # 15s — circuit breaker, idempotency, anomaly detection
   bun run calibration       # 10s — ECE, Platt scaling, per-market curves
   ```
   
   Don't analyze — just confirm everything runs and glance at the output patterns. The muscle memory of having *just seen* this output (especially the autonomous-batch summary line and the circuit breaker trip in resilience) helps during the interview.
   
   **Key outputs to recognize:**
   - `autonomous-batch`: "I processed 15 transactions... I'll wait for your signature."
   - `resilience`: "[circuit:categorization] → OPEN (failure rate 60% > threshold 40%)"
   - `calibration`: per-market ECE table showing IT worst-calibrated

---

## Phase 4b: Skim New Proposals (5 min)

8. **`prep/proposals/README.md`** — 2 minutes to scan the index. Know the two HIGH priority docs:
   - **Live-round clock**: minute-by-minute timer with recovery pivots
   - **Pre-call cheat sheet**: key numbers, deterministic/AI splits, maturity ladder, day-of checklist

---

## Phase 5: Self-Awareness (5 min)

9. **`prep/3-lead-ai-hostile-followups.md`** — Read Category 6 (Self-Awareness and Gaps) **and** the new Categories 7–11 pre-interview drill list at the bottom. Practice the "no fintech experience" answer aloud:
   > "I ran an SMB — I've done UStVA filing from the user side."

9. **`interviewers/V-Adynets.md`** — Skim the "Useful Interview Read" section. Expect someone who values precise decomposition and fast detection of hand-wavy logic.

---

## Phase 6: Questions to Ask (2 min)

10. **`prep/3-lead-ai-engineer-day-of-card.md`** — Read the "Questions to Ask Them" section. My top pick: "What's the hardest production bug you've had in the accounting pipeline?" — it signals you think about production reality, not just design elegance. Pick your top 3 (don't ask all 5 — it looks rehearsed). My recommendations:
    - "What does the team's day-to-day look like?"
    - "What's the hardest production bug you've had in the accounting pipeline?"
    - "If I joined, what would I own in the first 90 days?"

---

## Phase 7: System Design Template (5 min)

11. **`../cross-company-system-design-template.md`** — Skim the 7 steps. If they ask "design X", this is your skeleton:
    - Scope → AI boundary → Pipeline → Confidence routing → Observability → Scale → Failures
    - Know the Finom instantiation table by heart.

---

## Don't Do Tonight

- Don't read every insight document end-to-end
- Don't try to memorize SKR03 codes (you know the pattern; that's enough)
- Don't practice more than 2 hostile follow-ups aloud
- Don't write new code
- Don't stay up past your normal bedtime

---

## Morning Of

1. Coffee
2. Re-read the day-of card (2 min)
3. Open terminal, run `bun run rehearsal` once (20 sec)
4. Open Claude Code, verify authentication
5. Increase font size for screen share
6. Water on desk, this card on side screen

---

## The One Thing to Remember

If you forget everything else, remember this:

> **Scope before you code. Say "the most important boundary is: AI for ambiguity, rules for policy." Then draw the pipeline. Then implement one stage. Then add the confidence router. Narrate every decision.**

That sequence — scope, boundary, pipeline, implement, route, narrate — is the interview in 6 words.
