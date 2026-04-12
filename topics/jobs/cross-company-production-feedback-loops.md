# Production Feedback Loops — Instrumentation Patterns for Correctness-Sensitive AI

Saved: 2026-04-11

## Context

Both Finom and Delphyr need AI systems that get better over time without manual retraining. The mechanism is **production feedback loops** — structured pathways from user corrections back to model/system improvement. This insight provides concrete implementation patterns.

---

## The Feedback Loop Architecture

```
User Action → Observation → Classification → Signal → Improvement
```

### Finom Example

```
Accountant corrects category: "Office supplies" → "Marketing materials"
  → Observation: correction logged with original confidence (0.87)
  → Classification: category error (not amount error, not VAT error)
  → Signal: merchant "PrintShop GmbH" miscategorized
  → Improvement options:
    a. Add to category override table (deterministic)
    b. Include in next fine-tuning batch (ML)
    c. Recalibrate confidence thresholds (statistical)
```

### Delphyr Example

```
Doctor edits SOAP note: changes "no history of diabetes" → "Type 2 diabetes since 2019"
  → Observation: negation error logged with source citation
  → Classification: factual error, negation subtype
  → Signal: extraction model mishandled negation in Dutch clinical text
  → Improvement options:
    a. Add negation test case to evaluation suite
    b. Strengthen negation detection in extraction prompt
    c. Flag similar patterns for human review until fixed
```

---

## Pattern 1: Correction Classification

Not all corrections are equal. Classify them to route improvement actions.

### Taxonomy for Financial AI (Finom)

| Correction Type | Example | Severity | Auto-Fixable? |
|----------------|---------|----------|---------------|
| **Category error** | Office → Marketing | Medium | Merchant override table |
| **Amount error** | €89.50 → €85.90 | High | Extraction model fix |
| **VAT error** | 19% → 7% (reduced rate) | Critical | Tax rule update |
| **Duplicate** | Transaction booked twice | High | Dedup logic fix |
| **Missing transaction** | Unprocessed invoice | Medium | Pipeline reliability fix |
| **Wrong market** | Booked as DE, should be FR | High | Market detection fix |

### Taxonomy for Clinical AI (Delphyr)

| Correction Type | Example | Severity | Auto-Fixable? |
|----------------|---------|----------|---------------|
| **Negation error** | "no pain" → "pain" | Critical | Prompt/model fix |
| **Attribution error** | Wrong patient visit | High | Retrieval scope fix |
| **Temporal error** | Wrong chronological order | Medium | Timeline logic fix |
| **Omission** | Missing medication | High | Completeness threshold |
| **Hallucination** | Fabricated finding | Critical | Guardrail tightening |
| **Formatting** | Wrong SOAP section | Low | Template fix |

---

## Pattern 2: Feedback Signal Routing

Different corrections trigger different improvement pathways.

```typescript
// Conceptual: correction router
interface Correction {
  originalValue: string;
  correctedValue: string;
  correctionType: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  context: Record<string, unknown>;
  timestamp: Date;
}

type ImprovementAction =
  | { type: 'override_table'; key: string; value: string }
  | { type: 'eval_case'; input: string; expectedOutput: string }
  | { type: 'threshold_adjust'; direction: 'tighten' | 'loosen'; amount: number }
  | { type: 'prompt_update'; section: string; change: string }
  | { type: 'human_review_flag'; pattern: string; until: Date };

function routeCorrection(correction: Correction): ImprovementAction[] {
  const actions: ImprovementAction[] = [];

  // Every correction becomes a test case
  actions.push({
    type: 'eval_case',
    input: correction.context.originalInput as string,
    expectedOutput: correction.correctedValue,
  });

  // Critical corrections trigger immediate safety response
  if (correction.severity === 'critical') {
    actions.push({
      type: 'human_review_flag',
      pattern: correction.correctionType,
      until: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    });
  }

  // Deterministic fixes when possible
  if (correction.correctionType === 'category_error' && correction.context.merchant) {
    actions.push({
      type: 'override_table',
      key: correction.context.merchant as string,
      value: correction.correctedValue,
    });
  }

  return actions;
}
```

---

## Pattern 3: Correction-Driven Evaluation Suite Growth

The most valuable feedback loop: every human correction becomes a test case.

### The Flywheel

```
Production corrections → New test cases → Evaluation suite grows
                                            ↓
                         Model/prompt changes → Run eval suite
                                            ↓
                         Regression detected? → Block deployment
                                            ↓
                         No regression → Deploy → More corrections → ...
```

### Implementation

```
Week 1:    50 eval cases (hand-written)
Week 4:   200 eval cases (50 hand-written + 150 from corrections)
Week 12:  800 eval cases (50 hand-written + 750 from corrections)
Month 6: 2000+ eval cases (organically grown, covers real failure modes)
```

**Why this matters:** Hand-written eval cases test what you *imagine* will go wrong. Correction-driven cases test what *actually* goes wrong. The latter is always more valuable.

### Quality Filter

Not every correction should become a test case. Filter:
- **Duplicate:** Same correction pattern already in suite → skip
- **Ambiguous:** Reasonable people would disagree → flag for review
- **User error:** The correction was wrong → discard
- **Edge case:** So rare it would overfit the eval → tag as low-weight

---

## Pattern 4: Calibration Drift Detection

Track whether confidence calibration is drifting over time.

### Monitoring Dashboard Metrics

| Metric | Healthy Range | Alert Threshold |
|--------|--------------|-----------------|
| **ECE (Expected Calibration Error)** | < 0.05 | > 0.10 |
| **Auto-book accuracy** | > 97% | < 95% |
| **Review queue rate** | 10-20% | > 30% or < 5% |
| **Correction rate** | < 3% | > 5% |
| **Critical error rate** | < 0.1% | > 0.5% |

### Drift Causes

- **New merchant types:** Business grows, encounters vendors not in training data
- **Regulatory changes:** VAT rates change, new tax categories added
- **Seasonal patterns:** Year-end transactions differ from mid-year
- **Market expansion:** New country with different accounting conventions
- **Model update:** New LLM version changes confidence distribution

---

## Pattern 5: The Earned Autonomy Ratchet

Connect feedback loop quality to automation level.

```
Level 0: All transactions require human review (launch)
  ↓ (achieve: ECE < 0.10, accuracy > 90%, 500+ reviewed transactions)
Level 1: High-confidence transactions auto-booked (first threshold)
  ↓ (achieve: ECE < 0.05, accuracy > 95%, 5000+ reviewed transactions)
Level 2: Medium-confidence transactions auto-booked (expanded threshold)
  ↓ (achieve: ECE < 0.03, accuracy > 98%, 20000+ reviewed transactions)
Level 3: Only low-confidence and novel patterns require human review
```

**Each level requires:**
1. Measured accuracy above threshold
2. Calibration quality (ECE) above threshold
3. Minimum volume of human-verified outcomes
4. No critical errors in trailing window

**Each level can be revoked:**
- Critical error detected → drop one level
- ECE drifts above threshold → drop one level
- New market or major model change → reset to Level 0 for that scope

---

## Cross-Company Application

| Pattern | Finom | Delphyr |
|---------|-------|---------|
| Correction classification | Category/amount/VAT errors | Negation/omission/hallucination |
| Signal routing | Override table + eval case | Eval case + prompt update |
| Eval suite growth | Transaction categorization accuracy | Clinical extraction accuracy |
| Calibration monitoring | Auto-book accuracy per market | Clinical note accuracy per specialty |
| Earned autonomy | Auto-book threshold expansion | Reduced human review requirements |

The framework is identical; only the error taxonomy and severity weights change.

---

## Interview Talking Points

### For Finom (Interview 3)

> "The system gets smarter from corrections, not just from model updates. Every time an accountant fixes a category, that becomes a test case. Over time, the evaluation suite becomes a mirror of real-world failure modes — which is always more valuable than synthetic benchmarks."

### For Delphyr (Follow-Up)

> "In clinical AI, the feedback loop is both the most valuable and the most sensitive component. Every doctor correction teaches the system, but you need consent and anonymization before using clinical corrections for improvement. The privacy architecture around the feedback loop is as important as the loop itself."
