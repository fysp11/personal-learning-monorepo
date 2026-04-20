# Credit Risk and Invoice Financing — AI Engineering Patterns

Saved: 2026-04-17

Context: Finom's public roadmap (April 2026) targets invoice financing and credit lines for freelancers by late 2026. This extends AI engineering scope from accounting automation into financial risk — a domain with higher capital risk and stricter policy requirements.

---

## How This Differs From Transaction Categorization

| Dimension | Transaction Categorization | Invoice Financing / Credit |
|-----------|--------------------------|---------------------------|
| Unit | Single bank transaction | Invoice + business health profile |
| AI value-add | Ambiguous merchant text → account code | Fraud signals from document + behavior patterns |
| Deterministic layer | VAT law, booking rules | Credit policy (hard limits, concentration, history) |
| Failure cost | User correction or tax amendment | Capital loss (bad loan) or fraud exposure |
| Reversibility | Override and rebook | Partially reversible (collections) or not at all |
| Approval gate | Confidence routing | Always explicit human approval for new clients |
| Feedback loop | User overrides train categorizer | Repayment outcomes train risk model |

**The key insight:** The AI/deterministic boundary moves. In accounting, AI does the core judgment (categorization) and deterministic logic enforces compliance. In credit risk, AI extracts fraud signals from unstructured data, but the *actual credit decision* is governed by hard policy rules — and the policy rules come first.

---

## The AI/Deterministic Split for Invoice Financing

### What AI does well here

1. **Invoice template anomaly detection** — AI can analyze the visual/structural features of uploaded invoice PDFs. Fraudulent invoices often reuse templates, have font inconsistencies, or contain formatting anomalies that pattern-match against known fraud templates. This is genuine AI work: the signal is in unstructured visual/semantic space.

2. **Self-dealing detection** — AI can analyze the business graph: does the invoice issuer have a known relationship with the counterparty (same address, related company, shared director)? This requires entity resolution across noisy free-text fields — a genuine AI task.

3. **Cash flow pattern analysis** — Given transaction history, AI can score business health: revenue trend, payment consistency, seasonal patterns. This is closer to ML (time-series classification) but the feature engineering is LLM-assisted for noisy data.

4. **Counterparty classification** — Is this a legitimate business? A new entity vs. established? Does the invoice amount match typical invoices in this industry? AI can score these from messy external data.

### What must be deterministic

1. **Hard credit limits** — Maximum single invoice advance (e.g., €25,000) must be code. The AI should never override this.

2. **Policy rules** — Minimum account age (3 months), maximum revenue multiple (3×), maximum outstanding balance (5× monthly). These are business risk decisions that have been explicitly approved by the risk committee. They must be code.

3. **Default history check** — If a business has ever defaulted on a Finom financing product, the decision is deterministic: declined. Not model judgment.

4. **VAT ID validation** — Counter-party VAT ID checked against VIES. Ground truth, not model opinion.

5. **Concentration limits** — If one counterparty represents >60% of a business's revenue, that's a concentration risk. The check is deterministic.

### Why policy-before-score matters

```
Wrong order: AI score → policy check → decision
Right order: policy check → AI score → decision
```

If a hard policy rule (e.g., account age < 3 months) would decline the application anyway, you don't need to run AI scoring. Running the AI first wastes compute and creates a dangerous situation where a strong AI score might be used to rationalize overriding the policy. Policy gates come first.

---

## Pipeline Design

```
Invoice upload + business account data
  → Stage 1: Input validation (deterministic)
      - counterparty VAT ID → VIES check
      - required fields present (invoice date, amount, issuer)
      - duplicate invoice detection (hash or embedding match)
  → Stage 2: Policy gate (deterministic — must pass all to continue)
      - account age ≥ 3 months
      - invoice ≤ 3× avg monthly revenue
      - total outstanding ≤ 5× avg monthly
      - 0 prior defaults
      - invoice ≤ €25,000 hard limit
  → Stage 3: Fraud signal extraction (AI)
      - invoice template anomaly score
      - self-dealing score (business graph analysis)
      - counterparty classification (new vs established)
      - cash flow health score
  → Stage 4: Risk scoring (AI — composite)
      - weighted combination of fraud signals
      - calibrated confidence on the composite score
  → Stage 5: Decision router (deterministic)
      - risk score ≤ 0.10 + no policy flags → APPROVED
      - risk score 0.10–0.45 → MANUAL_REVIEW
      - risk score > 0.45 → DECLINED
  → Stage 6: Approval event (always explicit)
      - no auto-financing without human approval for first 3 invoices per business
      - after track record established, high-confidence low-risk can auto-advance
```

---

## Key Invariants

Unlike accounting, there is no "proposal mode" for credit decisions — the stakes are too high.

1. **Policy invariant:** A hard policy violation results in DECLINED regardless of AI score. No exception.
2. **New business invariant:** First 3 financing applications always require manual review regardless of score. Trust is earned.
3. **Amount invariant:** Approved financing amount ≤ min(invoice amount, hard limit). Never round up.
4. **Auditability invariant:** Every decision — approve, review, decline — is logged with the exact policy checks run, the AI signals extracted, and the score computed. Required for regulatory review.
5. **Idempotency invariant:** Processing the same invoice twice produces the same decision. (If policy inputs haven't changed.)

---

## Evaluation Patterns for Credit Risk

The eval framework differs from accounting because the cost function is asymmetric:

| Error type | Cost |
|------------|------|
| False positive (approve bad invoice) | Capital loss — potentially catastrophic |
| False negative (decline good invoice) | Lost revenue — recoverable |

This means the eval harness should weight false positives 10–50× higher than false negatives, depending on the fraud category:

```python
FRAUD_SEVERITY = {
    "self_dealing": "critical",        # highest capital risk
    "duplicate_invoice": "critical",   # direct fraud
    "vat_id_missing_large": "high",   # likely irregular
    "new_counterparty_large": "medium", # elevated but recoverable
    "template_anomaly": "medium",
    "low_activity_high_amount": "high",
}
```

### What to measure in production

- **Approval rate** vs **default rate** (primary business metric)
- **Fraud detection rate** (true positive on known fraud in holdout)
- **False negative on critical fraud** (should be near-zero)
- **Time to decision** (business cares about this: sub-minute target)
- **Override rate** (how often human reviewers overturn the score)
- **Calibration per segment** (new accounts vs established, IT vs construction)

---

## Connection to the Interview

If asked about Finom's credit expansion in an interview:

> "Invoice financing is architecturally different from accounting because the failure cost is asymmetric — a wrong booking is a user correction, a bad credit decision is capital loss. That changes the AI/deterministic boundary: policy rules come first and are never overridable by a model score. AI adds value at the fraud signal extraction layer — template anomaly detection, self-dealing pattern recognition, business health scoring. But the credit decision itself is deterministic: hard limits, concentration checks, default history. The same pipeline pattern applies: input validation → policy gate → AI signals → composite score → router. The difference is that 'proposal mode' doesn't exist here — every decision is either approved with explicit authorization or declined."

Sharper version:

> "The accounting pipeline earned autonomy through calibration data. Invoice financing starts with explicit human approval for every new client and earns automation as repayment history builds. Same maturity ladder principle, different starting point — and the stakes mean the bar is higher before you widen."

---

## What This Signals to an Interviewer

Building this domain extension demonstrates:

1. **Domain depth beyond the JD** — you've thought about where Finom is going, not just where they are
2. **Consistent architecture vocabulary** — same AI/deterministic boundary, same pipeline pattern, same confidence routing
3. **Adjusted failure cost reasoning** — you know the cost function shifts and can explain why the design changes
4. **Production mindset** — policy gates before AI scoring is a production engineering choice, not a theoretical one

This is the kind of forward preparation that distinguishes "I know your current product" from "I'm thinking about your next 18 months."
