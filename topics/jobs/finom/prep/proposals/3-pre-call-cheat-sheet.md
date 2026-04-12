# Pre-Call Cheat Sheet — Read 15 Minutes Before Interview

**Interview 3 — Lead AI Engineer — April 14, 2026**  
**Format**: 30 min technical questions + 60 min live coding with Claude Code or Codex

---

## The One Thesis

> Build proactive AI workflows that complete meaningful work, but earn autonomy stage by stage — deterministic controls where failure cost is high, LLM only where input is genuinely ambiguous.

---

## Numbers to Know Cold

| Number | What it is | Why it matters |
|--------|-----------|----------------|
| **0.85** | Auto-book threshold | Below this → proposal, not booking |
| **0.55** | Proposal threshold | Below this → reject (explicit terminal state) |
| **ECE < 0.05** | Calibration bar | Must pass before using confidence for routing |
| **19% / 7%** | German VAT (standard / reduced) | Deterministic — never LLM |
| **20% / 10% / 5.5% / 2.1%** | French VAT rates | PCG chart of accounts |
| **Sept 1, 2026** | French B2B e-invoicing mandate | Chorus Pro / Factur-X format |
| **200K+** | Finom active accounts (Apr 2026) | Scale of the problem |
| **FTE / active customer** | Ivo's business metric | How AI impact is measured |
| **10 years** | GoBD retention requirement | Makes audit trail legally required |
| **§13b UStG** | Reverse charge law | Always surfaces for review, never auto-books |

---

## Five Deterministic vs AI Splits (Know These Cold)

| Stage | Deterministic | AI |
|-------|--------------|-----|
| VAT calculation | ✓ Always | Never — rules are laws |
| Reverse charge detection | ✓ Vendor list / VAT ID check | Never — compliance |
| Account code lookup | ✓ Category → code mapping | Never — chart of accounts is fixed |
| Categorization | — | ✓ Ambiguous text input |
| Extraction from messy docs | — | ✓ Unstructured input |

**One-liner**: "Tax is policy. Policy is deterministic. Only the messy input parsing is AI."

---

## Named Failure Modes (Say These, Not Generic Descriptions)

- **FM-01 OCR drift** — scanned doc quality degrades over time, confidence inflates
- **FM-04 Overconfident miscategorization** — model says 0.92, actually wrong; needs calibration
- **FM-07 Reverse charge miss** — cross-border B2B auto-booked without surfacing; §13b violation
- **FM-10 Confidence inflation** — raw scores systematically too high; Platt scaling fixes
- **FM-14 Escalation storm** — bad batch floods human review queue; circuit breaker prevents
- **FM-15 Silent reject** — transaction ingested, never reaches terminal state; lifecycle registry prevents
- **FM-16 Stage leak** — transaction double-processed on retry; idempotency key prevents
- **FM-18 ELSTER double-submit** — tax filing submitted twice; idempotency on filing ID prevents

---

## Staged Rollout Maturity Ladder (Level Numbers + Criteria)

| Level | Name | Advancement criteria |
|-------|------|---------------------|
| **0** | Shadow | >85% agreement with human baseline, 30 days |
| **1** | Suggest | >90% acceptance rate, 14 days |
| **2** | Draft | <5% correction rate, 14 days |
| **3** | Auto + audit | <2% correction rate, 30 days + ECE < 0.05 |
| **4** | Full auto | 60 days no regression at Level 3 criteria |

**One-liner**: "I don't open the autonomy ratchet based on feel — I have specific criteria for each level, and I track ECE separately because a well-calibrated model needs different advancement gates than an accurate but overconfident one."

---

## GoBD — Why the Audit Trail Is Law, Not Engineering Preference

- **GoBD** = German tax law for electronic accounting records
- **Requirements**: immutable records, machine-readable, 10-year retention, decision replay
- **What it means for AI**: every routing decision must be logged with the input, confidence score, and threshold that triggered it — so it can be replayed and audited years later
- **Pattern**: event-sourcing; append-only log of decisions, never mutate historical records

**Answer if asked "why not just log to a database?"**: "GoBD requires the records to be immutable and auditable. A mutable database lets you correct historical entries — that's a liability. Event-sourcing gives you an append-only log; you can replay any historical state without trusting that nothing was altered."

---

## Calibration (One Paragraph to Say Out Loud)

"Confidence is just a number until you calibrate it. A model trained in Germany may say 90% confidence on a French transaction but only be right 70% of the time — that's over-confidence. I measure ECE per market, and if it's above 0.05 I apply Platt scaling: a logistic regression layer that maps raw scores to calibrated probabilities without retraining the model. New markets always start conservative — high threshold, low autonomy — and I measure ECE before widening. The earned autonomy ratchet only advances when the calibration evidence is there."

---

## France — What Actually Has to Change (Not What Stays the Same)

**New work**:
- PCG account code mapping (different from SKR03 — 6xx expense accounts, not 4xxx)
- 4-rate VAT rules: 20% standard, 10% food service, 5.5% essential food, 2.1% press
- CA3 VAT return → DGFiP (not ELSTER)
- Chorus Pro integration for e-invoicing (Sept 2026 mandate)
- Factur-X XML parser for structured invoice ingestion
- Cold-start calibration on FR corpus — ECE will be worse than DE at launch

**Unchanged**: pipeline shape, confidence routing, terminal state logic, circuit breaker, idempotency

**One-liner**: "The orchestrator doesn't change. I add `FR_POLICY` with PCG codes and 4-rate VAT. The hard work is DGFiP filing integration and building calibration data from scratch in a new market."

---

## FTE / Active Customer — The Business Decomposition

FTE cost per active customer decomposes into ~5 components:

1. **Transaction ingestion** — how many arrive per customer per month
2. **Categorization review rate** — what % need human review (target: <15%)
3. **VAT correction rate** — how often categorization leads to wrong VAT (target: <2%)
4. **Query / exception rate** — customer support tickets per automated decision
5. **Filing preparation time** — UStVA / CA3 assembly vs auto-draft

AI impact shows up when you can say: "We reduced review rate from 40% to 12%, which drove a 0.3x improvement in FTE per active customer." That's Ivo's language.

---

## Live Round Orientation (First 5 Minutes)

Before touching the keyboard:
1. What is the input? (raw doc / transaction record / batch)
2. What must come out? (booking record / proposal / batch report)
3. What is the worst kind of wrong? (wrong VAT = critical; wrong description = low)
4. Auto-complete boundary? (what is always human vs what can auto-book)
5. Which market? (Germany = SKR03, France = PCG)

**Say**: "Before I start — can I confirm the failure cost hierarchy? I want to make sure my routing decisions reflect the right severity weighting."

**At minute 30 check**: "I have typed contracts, a categorization stub, and deterministic VAT. The router is next." If you can't say this, use the recovery matrix in the clock guide.

---

## The Questions to Ask Them (Pick 2)

1. "Where does current workflow break down most often — extraction, categorization, orchestration, or integration with the ledger?"
2. "What separates engineers who get faster with Claude Code from those who get slower — what habits did you see make the difference?"
3. "How do you evaluate correctness for finance-sensitive automations where the ground truth is a tax rule, not a label?"
4. "Where is the current friction — central AI discovering good patterns, or domain teams turning those into durable product behavior?"

---

## One-Line Positioning

> "I build production-grade AI systems by keeping policy deterministic, isolating AI to the ambiguous parts, and shipping with evals, routing, and clear failure controls."

---

## Day-Of Checklist

- [ ] Run warm-up scripts: `bun run rehearsal && bun run autonomous-batch && bun run resilience`
- [ ] Key numbers reviewed (table above)
- [ ] Story bank skimmed — Story 1 (calibration failure), Story 6 (scoping under pressure)
- [ ] One failure mode per category ready to name
- [ ] France delta answer ready
- [ ] GoBD one-paragraph answer ready
- [ ] Questions for them chosen
