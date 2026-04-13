# Interview 3 — Day-Of Quick Reference Card

Date: Tuesday, April 14, 2026 (afternoon CET)
Duration: 90 minutes (30 questions + 60 live coding)
Interviewer: Viktar Adynets — Senior/Lead AI Engineer
Format: Claude Code or Codex live exercise

---

## 2-Minute Skim

### My thesis

**Production AI engineer who builds observable workflow systems, keeps policy deterministic, uses AI for ambiguity, and earns autonomy step by step.**

### My technical thesis

**AI for ambiguity. Software for policy. Measurable leverage over demo energy.**

### Org thesis

**Core > layers > product; central > integration > embed(domain).**

### Three things to prove

1. I think clearly about production AI systems
2. I can decompose ambiguous workflows into controllable pieces
3. I can use an AI coding agent well without losing rigor

### One-sentence positioning

> "I build AI systems where the model handles judgment, rules handle policy, confidence routing controls risk, and every decision is traceable."

---

### Fresh intel (April 11)

- AI Accountant is now **GA for all German customers** (not beta)
- **200K+ accounts** across Europe (up from 125K in earlier prep)
- Roadmap: **Lohnsteueranmeldung** (payroll) and **Zusammenfassende Meldung** (intra-EU) coming soon
- GmbH/UG support expanding (beyond freelancers)
- **Invoice financing and credit lines** expected late 2026
- Target: **€225B** SMB financial services market

---

## Before the Call (15 min)

- [ ] Terminal open, font size large for screen share
- [ ] `bun run rehearsal` verified working (Finom code folder)
- [ ] Claude Code authenticated and responsive
- [ ] Zod available (`import { z } from "zod"` works)
- [ ] Second monitor or split screen ready
- [ ] Water, notes, this card visible on side screen

---

## First 30 Minutes: Technical Questions

### If asked about system design

Use the 7-step framework: scope → AI boundary → pipeline → confidence routing → observability → scale → failures

**Start with:** "Before I design — the input is [X], the output is [Y], and a wrong output costs [Z]. The most important boundary is: categorization is AI, tax calculation is deterministic rules."

### If asked about confidence routing

> "The threshold comes from calibration data. ECE under 0.05 means the scores are trustworthy. In a new market, start at 100% human review, calibrate on the first 1000 transactions, then widen."

### If asked about multi-market

> "Market config is data, not code. Adding Italy means one config object, zero code changes. The exception is country-specific pipeline hooks — Italy needs SDI e-invoicing, which is an async post-processing step."

### If asked about AI coding tools

> "Three modes: scaffold mode for contracts (you drive, agent fills boilerplate), implementation mode one stage at a time (verify before proceeding), debug mode for targeted fixes. The discipline: 10-second pause after every agent generation to actually read it."

### If asked about adoption

> "Trust is earned, not declared. Start with proposal mode, track confirmation rate, and only move to auto-mode when the data supports it. The metric is confirmation rate, not enthusiasm. The relationship layer matters too: central AI sets reusable patterns, integration makes them usable, and embedded teams turn them into habits."

---

## Live Coding Round: 60 Minutes

### First 5 minutes: SCOPE before coding

> "Let me make sure I understand the problem before I start. The input is... the output should be... the correctness bar is..."

Do NOT start coding immediately. The interviewer watches whether you think first.

### Architecture first, implementation second

1. Define type contracts (Zod schemas) — 3 min
2. Implement categorization (AI-powered stage) — 8 min
3. Implement tax calculation (deterministic) — 5 min
4. Add confidence router — 3 min
5. Wire orchestrator with trace — 5 min
6. Test cases (happy path + edge case) — 5 min
7. Add market extensibility if time — 10 min

### Things to say out loud

| When | Say |
|------|-----|
| At start | "I'll define contracts first so we agree on the shape" |
| At AI stage | "This is where the LLM adds value — categorization is judgment" |
| At tax stage | "This is deterministic — tax law isn't a prediction" |
| At router | "This is the most important 10 lines in the system" |
| At trace | "Without this, debugging is archaeology" |
| If stuck | "Let me step back and think about what we need next" |
| At verification | "I'm the project owner here — I set the rules, the agent fills in, and I verify every output" |

### Red flags to avoid

- Generating 300 lines without reading them
- Asking the agent to "design the architecture"
- Coding in silence for more than 60 seconds
- Over-engineering with factories, DI, abstract base classes
- Adding things they didn't ask for instead of polishing what they did

---

## Key Numbers

| Metric | Germany | France | Italy |
|--------|---------|--------|-------|
| Standard VAT | 19% | 20% | 22% |
| Reduced VAT | 7% | 5.5% / 10% | 4% / 5% / 10% |
| Chart standard | SKR03 | PCG | Piano dei Conti |
| E-invoicing | No | Interview-derived target / unconfirmed | Yes (SDI) |

*France values here are interview-derived planning assumptions, not public-canonical intel.*

---

## Gap Responses (if challenged)

**"No fintech experience"** → "Domain arbitrage — industry knowledge is the #1 differentiator in AI engineering right now, and I have it from the user side. I ran an SMB, I've done UStVA filing, I know what the accounting workflows feel like when they're broken. The engineering patterns — confidence routing, evals, observability — are domain-agnostic. The domain knowledge I already have; the German tax specifics are learnable and deterministic."

**"No C#/.NET"** → "AI work is Python. I'd interact with C# through APIs. Learning to read C# is weeks, not months."

**"Biggest risk hiring you?"** → "Domain ramp time. Mitigation: real SMB context + fast learner + engineering patterns already there."

---

## Questions to Ask Them

1. "What does the team's day-to-day look like — how do you balance central AI patterns with domain delivery?"
2. "What's the hardest production bug you've had in the accounting pipeline?"
3. "Where do you see AI coding tools creating the most leverage in your workflow?"
4. "If I joined, what would I own in the first 90 days?"
5. "How do you think about the boundary between what's centralized in the AI team vs embedded in product squads, and how do you keep the relationship layer healthy?"
