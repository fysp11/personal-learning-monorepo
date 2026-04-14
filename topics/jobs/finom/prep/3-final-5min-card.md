# T-Minus 5 Minutes — Final Card

**Interview 3 — Lead AI Engineer — April 14, 2026 (afternoon CET)**
**Interviewer: Viktar Adynets**

---

## Your One Sentence

> "I build AI systems where the model handles judgment, rules handle policy, confidence routing controls risk, and every decision is traceable."

---

## Three Things to Prove

1. I think clearly about **production AI systems**
2. I can **decompose ambiguous workflows** into controllable pieces
3. I can use an **AI coding agent well** without losing rigor

---

## The Boundary Rule (Say This First, Every Time)

**"AI for ambiguity. Software for policy."**

- Categorization → AI (messy input, judgment required)
- VAT calculation → deterministic (it's law, not a prediction)
- Confidence routing → deterministic (thresholds from calibration data)
- Booking entry → deterministic (double-entry math)

---

## Numbers That Must Come Out Cleanly

| Thing | Number |
|-------|--------|
| Auto-book threshold | **0.85** |
| Proposal threshold | **0.55** |
| Calibration bar | **ECE < 0.05** |
| German VAT | **19% / 7%** |
| French VAT | **20% / 10% / 5.5% / 2.1%** |
| Finom accounts | **200K+** |
| GoBD retention | **10 years** |
| Reverse charge law | **§13b UStG** |

---

## Live Round: First 5 Minutes

**DO NOT TOUCH THE KEYBOARD FIRST.**

Say this:
> "Before I start — the input is [X], the output should be [Y], and the worst kind of wrong is [Z]. The most important boundary: categorization is AI, VAT is deterministic."

Then write types/contracts. Then AI stage. Then deterministic stages. Then router. Then wire. Then demo.

---

## If Your Mind Goes Blank

Say: "Let me step back to the invariants. Every transaction must reach exactly one terminal state. The router is the thing that makes that possible — let me build that first."

Then build the router:
```python
if vat.mechanism == "reverse_charge":
    return RoutingStatus.REQUIRES_REVIEW
if confidence >= 0.85:
    return RoutingStatus.AUTO_BOOKED
if confidence >= 0.55:
    return RoutingStatus.PROPOSAL_SENT
return RoutingStatus.REJECTED
```

This is always the most impressive 10 lines.

---

## If They Challenge a Decision

- **"Why 0.85?"** → "That comes from calibration. ECE under 0.05 means the scores are trustworthy. I start conservative and widen based on override rate data."
- **"Why not LLM for VAT?"** → "Wrong rate = tax audit + Berichtigte Voranmeldung. Policy is deterministic. Only messy inputs are AI."
- **"You have no fintech experience"** → "I ran an SMB. I've filed UStVA. I know the friction from the user side. The engineering patterns are domain-agnostic; the domain knowledge I already have."

---

## Close Strong

At minute 57, say one of:
- "Before I wrap — in production I'd add a WorkflowTrace with correlation ID so I can reconstruct any transaction's path from ingestion to terminal state."
- "The France extension is `FR_POLICY`: PCG codes, 20/10/5.5/2.1% rates, Chorus Pro integration. Orchestrator doesn't change."
- "The eval question: is ECE under 0.05? Override rate under 2%? If not, raise the threshold before widening automation."

---

## Your Best Question for Them

> "What's the hardest production bug you've had in the accounting pipeline?"

(Signals: you think about production reality, not just design elegance.)
