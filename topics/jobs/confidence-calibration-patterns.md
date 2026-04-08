# Confidence Calibration Patterns for Production AI

## Purpose

Deep technical pattern that applies to both Finom and Delphyr roles. Confidence calibration — the alignment between a system's stated confidence and its actual accuracy — is the engineering discipline that makes staged autonomy work.

---

## Why Confidence Calibration Is the Core Skill

Both companies need systems that know when they're wrong:

| Domain | What "wrong" means | Consequence of overconfidence |
|--------|-------------------|-------------------------------|
| Finom (accounting) | Wrong categorization at high confidence | Auto-filed tax record with errors |
| Finom (lending) | Wrong credit score at high confidence | Bad loan approved automatically |
| Delphyr (clinical) | Wrong extraction at high confidence | Incorrect patient summary presented as fact |
| Delphyr (MDT prep) | Missing information not flagged | Clinician assumes completeness, misses critical data |

**The pattern:** Overconfidence is more dangerous than low accuracy. A system that says "I'm 95% sure" when it's actually 60% correct will cause more harm than a system that says "I'm 60% sure" and routes to human review.

---

## Calibration vs. Accuracy

These are different properties:

- **Accuracy:** How often the system is correct
- **Calibration:** How well the stated confidence matches actual accuracy
- **Discrimination:** How well the system separates correct from incorrect predictions

A perfectly calibrated system with 70% accuracy is safer than a poorly calibrated system with 85% accuracy — because the calibrated system knows which 30% to escalate.

### Expected Calibration Error (ECE)

The standard metric. Bins predictions by confidence, measures the gap between average confidence and average accuracy in each bin:

```
ECE = Σ (|bin_size| / total) × |avg_confidence_in_bin - avg_accuracy_in_bin|
```

Lower is better. ECE = 0 means perfectly calibrated.

### Reliability Diagram

Visual diagnostic: plot average accuracy (y) against average confidence (x) per bin. Perfect calibration = diagonal line. Above the diagonal = underconfident (safe). Below = overconfident (dangerous).

---

## Calibration Patterns in Multi-Agent Systems

### Pattern 1: Per-Agent Confidence Emission

Each agent in a pipeline emits a confidence score with its output:

```typescript
interface AgentOutput<T> {
  result: T;
  confidence: 'high' | 'medium' | 'low';
  confidenceScore: number; // 0.0 - 1.0
  calibrationMethod: string; // how this score was derived
}
```

**Why this matters:** Different agents have different accuracy profiles. The extraction agent might be well-calibrated but the categorization agent overconfident. Per-agent confidence lets the orchestrator make routing decisions.

### Pattern 2: Confidence Propagation

Downstream confidence is bounded by upstream confidence:

```
Pipeline confidence ≤ min(agent_1_confidence, agent_2_confidence, ...)
```

**Alternative: multiplicative propagation:**
```
Pipeline confidence = agent_1_confidence × agent_2_confidence × ...
```

Multiplicative is more conservative (better for safety-critical domains) but can produce very low end-to-end confidence even when individual agents are good.

**Recommended: weakest-link with override:**
- Default: pipeline confidence = minimum agent confidence
- Exception: if a downstream agent has independent verification (e.g., cross-references with a known database), it can raise confidence above the upstream minimum
- The override must be logged and auditable

### Pattern 3: Confidence-Based Routing

The orchestrator uses confidence to decide the processing path:

```
High confidence (>0.9)  → Auto-complete (no human review)
Medium confidence (0.6-0.9) → Draft + human review
Low confidence (<0.6)   → Escalate to specialist / reject

Thresholds are domain-specific and tuned per workflow.
```

**Finom example:**
- High: Auto-categorize and file the tax record
- Medium: Draft the categorization, present for approval
- Low: Flag as "needs manual review" with the raw document

**Delphyr example:**
- High: Include in MDT brief as confirmed fact
- Medium: Include with "verify" flag
- Low: Include in "information gaps" section

### Pattern 4: Calibration Monitoring in Production

Confidence calibration drifts over time. Monitor it:

1. **Periodic golden set evaluation** — run production model against labeled data monthly
2. **Downstream feedback loops** — when humans override high-confidence decisions, that's a calibration signal
3. **ECE trending** — track ECE over time; rising ECE = degrading calibration
4. **Per-category breakdown** — calibration may be good overall but terrible for specific categories (e.g., perfectly calibrated for standard transactions, overconfident for edge-case tax scenarios)

### Pattern 5: Temperature Scaling (Post-Hoc Calibration)

The simplest recalibration technique. Learn a single parameter T that rescales logits:

```
calibrated_confidence = softmax(logits / T)
```

T > 1 makes the model less confident (softens the distribution).
T < 1 makes the model more confident.

Fit T on a held-out validation set to minimize ECE. This is a post-hoc fix — it doesn't improve accuracy, just aligns confidence with accuracy.

### Pattern 6: Conformal Prediction Sets

Instead of a single answer with confidence, return a set of possible answers with a coverage guarantee:

```
"With 95% probability, the correct categorization is one of:
  - Betriebsausgabe (operating expense)
  - Reisekosten (travel expense)"
```

The set size is the uncertainty signal:
- Set size 1 = high confidence
- Set size 3+ = low confidence, needs human disambiguation

**Advantage:** Provides a formal statistical guarantee (coverage), not just a calibration estimate.
**Disadvantage:** Requires exchangeability assumption, harder to integrate into automated pipelines.

---

## Domain-Specific Calibration Challenges

### Finom: Financial Data

- **Class imbalance:** Most transactions are standard; rare categories (e.g., Anlagevermögen / fixed assets) may be poorly calibrated because the model has few examples
- **Threshold sensitivity:** In tax, "close to the line" matters — a transaction near the VAT threshold needs different handling than one clearly above or below
- **Temporal drift:** Tax rules change; a model calibrated on 2025 data may be overconfident on 2026 edge cases
- **Multi-currency:** Confidence for EUR transactions may differ from USD or GBP

### Delphyr: Clinical Data

- **Safety asymmetry:** Missing an allergy (false negative) is much worse than flagging a non-allergy (false positive) — calibration must be tuned for high recall in safety-critical categories
- **Rare conditions:** Long-tail diagnoses are inherently harder to calibrate — the model has fewer examples
- **Structured vs. free text:** Confidence on structured lab values should be near-deterministic; confidence on free-text extraction is inherently lower
- **Multilingual variation:** Dutch clinical abbreviations may have different calibration profiles than English

---

## Building a Calibration Practice

### For Both Roles: What to Build

1. **Calibration test suite** — golden set labeled by domain experts, used for periodic ECE measurement
2. **Reliability diagram dashboard** — visual monitoring of calibration over time
3. **Threshold tuning framework** — systematic approach to setting confidence thresholds per workflow
4. **Human feedback integration** — pipeline that captures human overrides and uses them to retrain/recalibrate
5. **Category-level calibration tracking** — not just aggregate ECE, but per-category calibration

### For Interviews: What to Say

> "Accuracy isn't enough — a system that's 85% accurate but can't tell you which 15% it's wrong about is dangerous in production. I focus on calibration: does the system's stated confidence match reality? If it says 95% confident, is it right 95% of the time? I measure this with reliability diagrams and ECE, monitor drift in production, and use confidence-based routing to decide what auto-completes vs. what gets human review. The routing thresholds are domain-specific — you'd set them differently for tax categorization vs. lending decisions vs. clinical extractions."

---

## Cross-Company Synthesis

The confidence calibration pattern is the technical implementation of "earned autonomy":

| Stage | Finom | Delphyr | Calibration Role |
|-------|-------|---------|-----------------|
| Shadow mode | AI categorizes, human does the work | AI summarizes, clinician does the work | Baseline calibration measurement |
| Draft mode | AI drafts, human approves | AI prepares brief, clinician reviews | Calibration-based routing decides what needs review |
| Selective automation | High-confidence auto-files | High-confidence facts shown without flags | Ongoing calibration monitoring prevents drift |
| Full autonomy | Standard transactions auto-processed | Routine summaries auto-generated | Continuous calibration guarantees the autonomy threshold |

**The career thesis:** Someone who understands confidence calibration can design systems that earn trust. That's the engineering skill behind "staged autonomy" — not a philosophy, but a measurable property with dashboards and thresholds.

---

## References

- Naeini et al., "Obtaining Well Calibrated Probabilities Using Bayesian Binning" (calibration theory)
- Guo et al., "On Calibration of Modern Neural Networks" (temperature scaling)
- Angelopoulos & Bates, "Conformal Prediction" (distribution-free uncertainty)
- Getmaxim.ai, "Multi-Agent System Reliability" (2026, production patterns)
- Cogentinfo, "Multi-Agent Orchestration Failure Playbook" (2026)
