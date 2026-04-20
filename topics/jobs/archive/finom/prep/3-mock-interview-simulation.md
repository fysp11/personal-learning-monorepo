# Interview 3 — Mock Interview Simulation

Saved: 2026-04-11

A timed self-test simulating the full 90-minute round. Use a timer. Answer out loud (not just in your head). Score yourself honestly after each section.

---

## Setup (2 minutes)

- Open a terminal with Claude Code ready
- Have `topics/ai-engineering/code/` accessible
- Set a 90-minute timer
- Record yourself if possible (audio only is fine)

---

## Part 1 — Technical Questions (30 minutes)

Answer each question out loud in 2-3 minutes. Use the answer skeleton: **Frame → Design Choice → Tradeoff → Failure Mode → Control/Metric**

### Question 1 (3 min)
**"How would you design expense categorization for German SMBs?"**

Self-score:
- [ ] Named all 5 stages (extraction, categorization, VAT, routing, booking)
- [ ] Explicitly said VAT is deterministic
- [ ] Named confidence thresholds
- [ ] Mentioned a specific metric (approval rate, override rate, severe-error rate)

### Question 2 (3 min)
**"What should be deterministic vs LLM-based in a financial workflow?"**

Self-score:
- [ ] Gave a clear principle (failure cost = deterministic; genuine ambiguity = AI)
- [ ] Named at least 3 deterministic items (VAT, booking, filing, routing)
- [ ] Named at least 3 AI items (extraction, categorization, anomaly detection)
- [ ] Connected to compliance risk, not just difficulty

### Question 3 (3 min)
**"How would you evaluate a financial AI workflow?"**

Self-score:
- [ ] Named severity-weighted accuracy (not just raw accuracy)
- [ ] Mentioned calibration / ECE
- [ ] Said "run in CI"
- [ ] Named regression detection

### Question 4 (3 min)
**"How would you generalize Germany-first workflows toward France?"**

Self-score:
- [ ] Described MarketPolicy / MarketConfig pattern
- [ ] Said "workflow shape stays the same, policy modules change"
- [ ] Named specific differences (SKR03 vs PCG, 19% vs 20%, UStVA vs CA3)
- [ ] Said "market rules must be code, not prompts"

### Question 5 (3 min)
**"Why do AI coding tools sometimes make teams slower?"**

Self-score:
- [ ] Named at least 2 failure modes (volume without judgment, architecture delegation, verification gap)
- [ ] Gave a concrete prevention strategy
- [ ] Connected to Finom's context (small team, high standards)
- [ ] Didn't sound anti-tool — showed you use them well

### Question 6 (3 min)
**"How should a central AI team help without becoming a bottleneck?"**

Self-score:
- [ ] Named what to centralize (eval, orchestration, safety, tooling)
- [ ] Named what to leave with domains (product decisions, UX, prioritization)
- [ ] Said "adoption is a product, not a memo"
- [ ] Mentioned measuring adoption, not just creation

### Question 7 (3 min)
**"When should you automate the work vs just assist the user?"**

Self-score:
- [ ] Named 4 conditions (clear boundary, bounded failure, deterministic policy, obvious rollback)
- [ ] Said "earned autonomy" or "proposal mode first"
- [ ] Connected to Ivo's "go do the task, then come back" frame
- [ ] Gave a concrete example of graduating from proposal to auto-action

### Question 8 (3 min)
**"What is the difference between an AI team and an ML team?"**

Self-score:
- [ ] Named core difference (prediction/optimization vs workflow execution/orchestration)
- [ ] Named different failure modes (statistical vs compositional)
- [ ] Connected to Finom specifically (ML = credit/risk, AI = accounting/agents)
- [ ] Didn't dismiss either — showed respect for both

### Reflection (6 min)
- Which questions felt weakest?
- Where did you ramble or lose structure?
- Did you follow the answer skeleton consistently?
- Re-read the weak answers from `3-technical-answer-bank.md`

---

## Part 2 — Live Coding (60 minutes)

### The Prompt

Read this, then close the document and work from memory:

> **"Design and implement a transaction categorization pipeline for a German SMB fintech. The system should take bank transactions, categorize them to the appropriate accounting code, calculate VAT, and create booking entries. It should handle confidence-based routing so low-confidence results go to human review instead of auto-booking. Use Claude Code to build it."**

### Timer Checkpoints

**0:00-5:00 — Scoping (DO NOT CODE)**
- State the workflow boundary out loud
- Define input/output/failure modes
- Decide what's AI vs deterministic
- Ask clarifying questions (even to yourself)

Self-score:
- [ ] Did NOT start coding in the first 5 minutes
- [ ] Defined input and output types
- [ ] Named what's deterministic (VAT, booking)
- [ ] Named what's AI (categorization)
- [ ] Stated a success metric

**5:00-15:00 — Type Definitions**
- Define all interfaces: TransactionInput, CategoryProposal, VatCalculation, BookingEntry, WorkflowOutcome

Self-score:
- [ ] All types defined with explicit fields
- [ ] Confidence is a number, not just high/medium/low
- [ ] WorkflowOutcome has status discrimination (auto_booked / needs_review / rejected)
- [ ] Used Zod or explicit interfaces

**15:00-30:00 — Deterministic Stages**
- Implement VAT calculation (pure function, no AI)
- Implement booking entry creation (mechanical double-entry)
- Implement market config for DE

Self-score:
- [ ] VAT handles standard rate (19%)
- [ ] VAT handles at least one edge case (reverse charge or reduced rate)
- [ ] Booking is balanced (debit = credit)
- [ ] Market config is parameterized, not hardcoded

**30:00-45:00 — AI Stage + Routing**
- Implement categorization (mock AI with keyword matching)
- Implement confidence-based routing
- Wire the orchestrator

Self-score:
- [ ] Categorization returns confidence score
- [ ] Routing has explicit thresholds
- [ ] High confidence → auto-book, medium → propose, low → reject
- [ ] Orchestrator is a simple function, not a framework

**45:00-55:00 — Observability + Testing**
- Add trace/log for each stage
- Run at least 3 test cases (happy path, low confidence, edge case)

Self-score:
- [ ] Trace captures stage name, duration, decision
- [ ] At least one test case auto-books
- [ ] At least one test case routes to review
- [ ] Output is readable and shows the full flow

**55:00-60:00 — Wrap-up**
- State what you'd do next (add France, add eval, add persistence)
- Ask your closing question

Self-score:
- [ ] Named 2-3 concrete next steps
- [ ] Didn't apologize for what's missing
- [ ] Showed awareness of production gaps without overcomplicating
- [ ] Asked a good question

---

## Overall Self-Assessment

Score each dimension 1-5:

| Dimension | Score | Notes |
|-----------|-------|-------|
| Clarity of scoping | /5 | |
| Answer structure (skeleton) | /5 | |
| Deterministic vs AI separation | /5 | |
| Confidence routing design | /5 | |
| Claude Code usage (precise, scoped) | /5 | |
| Verification before claiming done | /5 | |
| Time management | /5 | |
| Connecting to business outcomes | /5 | |

### Target: 30+ out of 40

If below 30, re-read:
1. `3-lead-ai-engineer-day-of-card.md`
2. `3-technical-answer-bank.md`
3. `3-live-round-scenarios.md`

Then run the simulation again.
