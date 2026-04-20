# Next AI Engineering Role — Action Plan

Saved: 2026-04-17

Built from the full Finom interview cycle (rounds 1–3). This is the distilled action plan for the next EU AI engineering role with a live technical round. It assumes the skills are in place and focuses on what to practice and change.

---

## The Single Sentence That Must Change

**Before Finom:**
> "I'm an architect who can implement when needed."

**After Finom:**
> "I'm a strong Python engineer who thinks architecturally while coding."

This is not just positioning. It must be true in practice. The live round revealed the gap between the architectural narrative (strong) and the implementation fluency under pressure (to be improved). Close the gap before the next round.

---

## What to Practice Before the Next Technical Round

### 1. Python under time pressure (biggest priority)

**The gap:** The live round was 60 minutes, Python, under observation. Preparation was TypeScript-heavy.

**The drill:**
- Set a 45-minute timer
- Open a blank file: `touch pipeline.py`
- Implement the full categorization pipeline (Pydantic models → categorizer → VAT → router → orchestrator) from memory
- Target: type contracts complete in < 8 min, first working test case in < 20 min, full pipeline with trace in < 40 min
- Run 3 times before the next round. No re-reading the reference between attempts.

**What passing looks like:** You can produce clean, running Python with Pydantic in 45 minutes with no lookup, no hesitation, and visible verification steps.

### 2. Scoping under 90 seconds

**The gap:** Scoping ran long and compressed coding time.

**The drill:**
- Set a 90-second timer
- Say out loud: input, output, worst failure cost, AI boundary, first implementation slice
- Stop when the timer hits 90 seconds — if you're still scoping, the statement is too long

**The canonical sentence (memorize this):**
> "Input: bank transaction. Output: booked entry or review queue. Worst wrong: VAT rate error. AI handles categorization; rules handle VAT and booking. I'll freeze the contracts and build the router first."

That's it. 4 sentences. Practice until it takes < 60 seconds.

### 3. Verification ritual (make it visible)

**The gap:** Verification behavior under observation — may have been rushed.

**The practice:**
After every Claude Code / Codex edit:
1. Pause 10 seconds
2. Read the diff
3. Say one specific thing you verified aloud: "I'm checking the router still returns a terminal state for all confidence levels."

This is a habit, not a decision. Practice it in solo drills until the pause is automatic.

### 4. Recovery pivots (memorize 3 sentences)

When the implementation stalls, say one of these immediately:
- "I'll stub this as a pure function returning the contract type and move on — the contract matters more than the body right now."
- "I'm going to flag this as the gap and keep moving — the router is the critical component and it's working."
- "Let me step back to the invariants. Every transaction needs exactly one terminal state. The router makes that possible. Let me build from there."

These prevent visible freezing. Practice saying them before the round so they come out naturally.

---

## What to Change in Positioning

### Round 3 positioning shift (implementation-forward)

| Before | After |
|--------|-------|
| "Let me think about the architecture before coding" | "Here's the contract — coding now, architecture commentary while it moves" |
| Design discussion, then implementation | Contracts → immediate first working slice → architecture commentary in narration |
| "The important insight here is..." | "I'm choosing Pydantic models first because..." |

The signal the interviewer reads:
- **Old signal:** "This person thinks carefully but starts slowly."
- **New signal:** "This person thinks carefully AND ships quickly."

### The 30-second implementation frame (use this in round 3 style interviews)

> "I'll scope this quickly, freeze the contract, and build the thinnest correct Python slice. Architecture commentary comes while the code is moving. The first thing I want working is the deterministic control point — that tells us where the risk budget is."

---

## What to Preserve (These Worked)

### Answer skeleton — keep using it, always

Frame → Design Choice → Tradeoff → Failure Mode → Control/Metric

Every technical question answer must hit all 5. This worked in rounds 1-2 and is a differentiator.

### AI/deterministic boundary — say it first

"AI for ambiguity. Software for policy." This framing lands every time. Lead with it.

### Maturity ladder (5 levels) — signature answer

Shadow → Suggest → Draft → Auto with audit → Full auto, with explicit advancement criteria. Very few candidates name this with concrete thresholds. Keep it.

### The Confident AI eval story — anchor for eval conversations

10-day → 3-hour improvement cycles, 60+ hrs/week reclaimed. This is a specific, credible production outcome. Keep using it when evals come up.

### The invariants (name these when asked "what must always be true?")

- Auto-book invariant: confidence ≥ threshold AND not reverse-charge AND valid VAT
- Terminal state invariant: every transaction reaches exactly one terminal state within SLA
- Idempotency invariant: same transaction twice → same result, no double-count
- Auditability invariant: every routing decision logged with input, confidence, threshold, outcome

---

## Pre-Round Checklist (Next Technical Interview)

### 48 hours before

- [ ] Run the 45-minute Python pipeline drill from scratch (no reference)
- [ ] Run the 90-second scoping drill 5 times
- [ ] Run the full 60-minute mock simulation in `3-mock-interview-simulation.md` with a timer

### Night before

- [ ] Re-read `transferable-patterns-next-ai-role.md` Part 3 and Part 4
- [ ] Confirm Python environment: `python3 pipeline.py` and `python3 eval_harness.py` both pass
- [ ] Run the scoping drill one more time
- [ ] Confirm Claude Code or Codex is authenticated and accessible

### Morning of

- [ ] Read `3-final-5min-card.md` (5 minutes only)
- [ ] Run `python3 pipeline.py` to confirm environment
- [ ] Do not re-read extensive prep materials — trust the practice

---

## How to Read a New Role Quickly

When a new AI engineering role comes up, answer these questions in order:

1. **What does their live round look like?** (language, duration, format, tool usage)
2. **Who is round 3?** (senior engineer peer, or manager/architect?) → adjusts positioning
3. **What AI products are in production?** (scale, domain, correctness requirements)
4. **What is their tech stack?** (Python? C#? TypeScript?) → determines demo language
5. **What is their expansion roadmap?** (what domains are next?) → shows you're ahead

For any fintech AI role, the Finom prep materials are directly reusable:
- `insights/technical-deep-dive.md` → production AI system design
- `insights/confidence-calibration-deep-dive.md` → calibration vocabulary
- `prep/3-technical-answer-bank.md` → Q1–Q16 with full answers
- `code/python-pipeline/pipeline.py` → live round reference
- `code/python-pipeline/eval_harness.py` → eval infrastructure demo

---

## Red Flags to Watch For (Interview Process Signals)

| Signal | What it means | How to adjust |
|--------|---------------|---------------|
| Round 3 is a "Senior Engineer" not an "Architect" | Direct peer evaluation — coding speed matters | Lead with implementation, narrate architecture |
| "Creative, not stock" | Evaluator wants judgment, not patterns | Frame in your own words first, then anchor to patterns |
| 60-minute live with AI tools | Tests implementation speed + judgment simultaneously | Practice the 45-min drill, verify visibly |
| Round 1-2 strong, Round 3 "profile mismatch" | Gap at implementation layer | Ensure fluency matches architectural narrative |
| "Profile mismatch" (not "technical gap") | Role scope more specific than JD implied | Ask about role specifics in round 2 directly |

---

## The One Metric That Matters for the Next Round

**How fast can you produce a working, clean Python pipeline from a blank file?**

Target: 45 minutes for the full categorization pipeline with trace, working test output, and zero lookup.

That is the gap to close before the next technical round.
