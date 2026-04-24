# Interview 3 — Final Day Synthesis

Saved: 2026-04-23

This document synthesizes all deepened Q13-Q15 material, the FM inventory, and Viktar tactics into a single coherent mental model. Read this on the day of the interview. It assumes you have already read the technical answer bank and pre-call cheat sheet.

---

## The Master Mental Model (30-second version)

> I maintain three invariants: every transaction reaches a terminal state, VAT is always deterministic code, and confidence scores are calibrated before routing thresholds are trusted. Each invariant maps to a named failure mode — FM-15, FM-07/08/09, and FM-04/10. This is not defensive engineering; it's how I make the system predictable under adversarial conditions.

This mental model is CP-language. Name the invariants first, behaviors second.

---

## The One Diagram (memorize this)

```
TransactionInput
  → [AI] categorize()            ← only LLM call; outputs (category, confidence)
  → [DETERMINISTIC] calculate_vat()  ← compliance override fires FIRST
  → [DETERMINISTIC] route()         ← threshold gate; four terminal states
  → WorkflowOutcome

Terminal states: auto_booked | proposal_sent | rejected | requires_review
Invariant 1: every tx reaches exactly one of these (FM-15 prevention)
Invariant 2: VAT is always code, never model (FM-07/08/09 prevention)
Invariant 3: ECE < 0.05 before trusting thresholds (FM-04/10 prevention)
```

---

## Three Invariants → Failure Modes → Detection (know these cold)

### Invariant 1: Terminal State Enforcement

**What it prevents**: FM-15 Silent Reject — transaction ingested, never resolved.

**How it's enforced**: Transaction lifecycle registry + `findStrandedTransactions()` scheduled query. Any non-terminal state past the SLA window triggers a dead-letter alert.

**Interview trigger**: "What breaks silently in your system?" → FM-15. No tx disappears without an ops alert.

---

### Invariant 2: Deterministic VAT

**What it prevents**: FM-07 Reverse Charge Miss, FM-08 Exempt Misclassification, FM-09 Kleinunternehmer Error.

**How it's enforced**: VAT calculation is a pure function. No LLM. Policy is code, not prompts. The compliance override in the router fires BEFORE the confidence check — reverse charge vendor always routes to `requires_review` regardless of model confidence.

**The quote to say**: "Tax is policy. Policy is deterministic. Only the messy input parsing is AI."

**CP edge case**: "What if the vendor name is ambiguous — 'Microsoft' could be retail or B2B Ireland?" → That's FM-02. The VAT layer doesn't resolve vendor ambiguity — it applies a deterministic rule to whatever the extraction layer gives it. If the extraction is uncertain about B2B status, the router escalates to `requires_review` before VAT runs.

---

### Invariant 3: Calibrated Confidence Before Routing

**What it prevents**: FM-04 Overconfident Miscategorization, FM-10 Confidence Inflation.

**How it's enforced**: ECE < 0.05 is the gate condition before enabling any confidence-based routing. New markets start at 100% human review. ECE is monitored weekly per market.

**The math**: ECE = Σ (n_bin/N) × |acc_bin − conf_bin|. Below 0.05 means the model's stated confidence reliably predicts its actual accuracy.

**How to calibrate**: Platt scaling — fit logistic regression on a held-out set to remap raw scores. Does not require model retraining. Works even if raw scores are biased high (FM-10).

**What calibration does NOT fix**: Low accuracy (Q15 answer). A well-calibrated model at 70% accuracy is honest but needs better features/training, not calibration fixes.

---

## Confidence Routing Decision Tree

```
category_result.confidence:
  ├─ reverse_charge? → ALWAYS requires_review (compliance override, fires first)
  ├─ ≥ 0.85 → auto_booked
  │    ↑ ECE < 0.05 must be verified before this branch is trusted
  ├─ ≥ 0.55 → proposal_sent
  └─ < 0.55 → rejected (explicit terminal, not silent discard)
```

**Key numbers**:
- 0.85 = auto-book threshold (set by calibration, not gut; widen only when override rate < 2%)
- 0.55 = proposal floor (below this, the model doesn't know enough to even propose)
- ECE 0.05 = calibration gate (must pass per-market before routing is trusted)
- 2% = max auto-book override rate before tightening threshold
- 30 days = minimum window for maturity ladder advancement

---

## Maturity Ladder (condensed)

| Level | Name | Gate |
|-------|------|------|
| 0 — Shadow | Run, discard, measure | 85% agreement w/ human, 30 days |
| 1 — Suggest | Show, human decides | 90% acceptance, 14 days |
| 2 — Draft | Pre-fill, user confirms | <5% correction, 14 days |
| 3 — Auto+audit | Execute, daily review | <2% correction, 30d + ECE<0.05 |
| 4 — Full auto | Execute, alert on anomaly | 60d no regression |

**New market rule**: Always starts at Level 0 regardless of Germany's maturity. Confidence scores are not portable across market distributions.

---

## Germany → France Extension (one paragraph)

The orchestrator doesn't change. Add `FR_POLICY`: PCG account codes (6xx expense prefix vs SKR03 4xxx), 4-rate VAT (20%/10%/5.5%/2.1%), CA3 filing to DGFiP instead of UStVA to ELSTER, Chorus Pro e-invoicing integration by September 2026. Cold-start France at Level 0 — ECE will be worse than Germany at launch because calibration corpus is empty. Build 500-1000 reviewed French transactions before setting any threshold.

**The one-liner**: "Market policy is data. Adding France means writing `FR_POLICY`, not changing the pipeline."

---

## Named Failure Modes by Layer (quick-reference)

**Extraction**: FM-01 OCR Drift, FM-02 Vendor Ambiguity, FM-03 Missing Context
**Categorization**: FM-04 Overconfident Misc., FM-05 Category-Tax Mismatch, FM-06 Amount Parse
**VAT/Policy**: FM-07 Reverse Charge Miss, FM-08 Exempt Mis., FM-09 Kleinunternehmer
**Calibration**: FM-10 Confidence Inflation, FM-11 Category Drift
**Orchestration**: FM-12 Multi-Rate Split, FM-13 Credit Note Reversal, FM-14 Escalation Storm, FM-15 Silent Reject, FM-16 Stage Leak
**Filing**: FM-17 Stale Market Config, FM-18 ELSTER Double-Submit

**Say in the interview**: "My pipeline maintains three invariants mapped to these layers — FM-15 is the orchestration invariant, FM-07/08/09 are the policy invariant, FM-04/10 are the calibration invariant."

---

## GoBD — Why the Audit Trail is Law

- German tax law for electronic accounting records
- Requirements: immutable, machine-readable, 10-year retention, decision replay
- What it means for AI: every routing decision must log input + confidence + threshold → replayable years later
- Pattern: event-sourcing (append-only, never mutate historical records)
- **Answer to "why not just a database log?"**: "GoBD requires immutability. A mutable database allows historical correction — that's a liability, not a feature. Event-sourcing gives you an append-only log you can replay any historical decision from."

---

## Python vs TypeScript for the Live Round

If the interviewer expects Python (Finom's AI stack is Python + C#):
- Reference: `topics/ai-engineering/code/python-categorization-pipeline.py`
- All four stages implemented, runnable, calibration check included
- Same invariants, same terminal states, same confidence routing as TypeScript version
- `asyncio.Semaphore` for bounded batch concurrency (same pattern as TypeScript version)

If TypeScript:
- Reference: `topics/ai-engineering/code/accounting-mas-pipeline.ts`
- Live round clock in `proposals/3-live-round-clock.md`

**Opening line for live round**: "Do you have a language preference for the implementation, or should I ask Viktar what stack he'd want to review against?"

---

## Viktar Adynets — CP-Specific Tactics (condensed)

What he values (inferred from CP background — Grodno State 2019-2020 ICPC):
1. **Name failure modes, not just describe them** — "FM-07" not "might miss reverse charge"
2. **State invariants before behavior** — invariants are first-class properties
3. **Name edge cases proactively** — don't wait to be asked about mixed-rate invoices
4. **Prefer exact numbers** — "ECE < 0.05", "P50 drops 2σ below baseline"
5. **Draw the deterministic/probabilistic boundary precisely** — not "roughly here"

Signals during interview:
- He asks "what else?" → add the tail case you didn't mention yet
- He probes "why 0.85?" → justify from calibration data, not gut
- He asks "why not just...?" → he's testing whether you'll put policy in the model; don't
- He stays silent → add one more edge case

---

## Observability Priority Order

1. **Confidence distribution** (add day one) — rolling P10/P50/P90 per market. Leading indicator of accuracy degradation. Alert when P50 drops >2σ below 30-day baseline.

2. **Terminal state tracking** (add second) — every tx must reach a terminal state within SLA window. Silent rejects (FM-15) are invisible without this.

3. **Business KPIs** (by week one) — auto-book rate, override rate, proposal acceptance rate, review queue depth, severe error rate. These are Ivo's metrics.

**What NOT to add first**: raw request/response logs (creates PII surface before health metrics), token counts (cost, not health), model latency percentiles (visible before SLA impact, confidence drift is not).

---

## Closing Lines for the Live Round

Choose two of these based on what came up:

1. "In production I'd add a batch health summary: confidence P10/P50/P90 vs 30-day baseline, stranded count, auto-book rate. That's what the ops team looks at."
2. "Before this goes to production I'd run the eval harness: is ECE under 0.05? Is override rate under 2%? If not, I raise the threshold."
3. "Adding France is one `FR_POLICY` object — PCG codes, 4-rate VAT, CA3 filing. The orchestrator doesn't change. September 2026 is the Chorus Pro deadline, that's the hard dependency."
4. "The trace satisfies GoBD: every routing decision is logged with the input and confidence score, immutable and replayable for 10 years."

**Final sentence**: "If I had another 20 minutes I'd add the autonomous batch processor — takes the full transaction list, runs the pipeline, returns auto-processed/proposals/requires-attention in one structured report. That's the 'go do the task, come back' pattern Ivo described."

---

## Questions to Ask Viktar (choose 2)

1. "In the live exercise — do you weight more toward a complete implementation slice or the verification and reasoning path?"
2. "Where does the current accounting pipeline fail most often: extraction, categorization, orchestration, or the integration layer with the ledger?"
3. "What separates engineers who get faster with Claude Code from those who generate review burden?"
4. "If I joined, what would I own in the first 90 days — and what's the thing that needs the most attention right now?"
