# Deep Cross-Company Patterns: Finom x Delphyr

Saved: 2026-04-09

## Purpose

This document goes deeper than the surface-level shared themes identified in `cross-company-insights.md`. It captures **architectural patterns, engineering decisions, and mental models** that transfer between financial AI and clinical AI — and that form a reusable career thesis for correctness-sensitive AI systems.

---

## Pattern 1: The Confidence Routing Architecture

Both roles require systems where AI makes a judgment call, and the system decides whether to trust it. The architecture is structurally identical.

### The Universal Pattern

```
Input → Agent Judgment → Confidence Score → Router
                                              ├── High confidence  → Auto-execute
                                              ├── Medium confidence → Human review queue
                                              └── Low confidence   → Escalate / reject
```

### Finom Instantiation

| Component | Finom Implementation |
|-----------|---------------------|
| Input | Invoice, receipt, bank transaction |
| Agent judgment | Transaction categorization (SKR03 code assignment) |
| Confidence threshold (high) | >0.90 → auto-book into accounting ledger |
| Confidence threshold (medium) | 0.70–0.90 → flag for accountant review |
| Confidence threshold (low) | <0.70 → escalate to user with suggested options |
| Failure mode | Wrong tax filing (Berichtigte Voranmeldung needed) |

### Delphyr Instantiation

| Component | Delphyr Implementation |
|-----------|----------------------|
| Input | Clinical notes, lab results, imaging reports |
| Agent judgment | Information extraction + clinical summarization |
| Confidence threshold (high) | >0.95 → include in MDT briefing with citations |
| Confidence threshold (medium) | 0.70–0.95 → flag for clinician review |
| Confidence threshold (low) | <0.70 → abstain (omit from output, log reason) |
| Failure mode | Missed diagnosis, hallucinated clinical fact |

### Why This Matters For Interviews

This is the single most transferable pattern. Both companies need someone who can:
1. **Calibrate thresholds** — not just set them, but measure whether they're correct (calibration curves)
2. **Design the review UX** — the medium-confidence path is where most human effort goes
3. **Instrument the feedback loop** — human corrections should improve the model over time
4. **Handle threshold drift** — as data distribution changes, thresholds need recalibration

### Deeper Technical Dimension: Calibration vs. Discrimination

Most AI engineers focus on **discrimination** (can the model tell right from wrong?). Fewer focus on **calibration** (when the model says 0.85, is it right 85% of the time?). In both Finom and Delphyr, calibration matters more than raw accuracy because the routing decision depends on the confidence score being meaningful.

**Techniques to study:**
- Platt scaling for post-hoc calibration
- Temperature scaling for neural network outputs
- Expected Calibration Error (ECE) as a metric
- Reliability diagrams for visual calibration assessment

---

## Pattern 2: The Audit Trail Architecture

Both domains require complete traceability of every AI decision. This isn't just logging — it's a legal/regulatory requirement.

### Finom: Financial Audit Trail

Every automated booking must be traceable back to:
- Source document (invoice, receipt)
- Extracted data (amount, date, vendor, description)
- Classification decision (SKR03 code, VAT rate)
- Confidence score at decision time
- Whether human review was involved
- Timestamp and version of the model used

**Why:** German tax law requires businesses to maintain a complete audit trail (GoBD compliance). If the Finanzamt asks why a transaction was booked to a specific account, the system must be able to explain.

### Delphyr: Clinical Audit Trail

Every clinical AI output must be traceable back to:
- Source documents retrieved (clinical notes, lab results)
- Retrieval scores and ranking decisions
- Generated claims and their citation sources
- Confidence scores and routing decisions
- Whether clinician review/modification occurred
- Model version, timestamp, patient scope

**Why:** MDR (Medical Device Regulation) requires traceability. If a clinical decision was influenced by AI output, there must be a record of what the AI saw, what it produced, and how it was used.

### Shared Engineering Implications

1. **Structured decision logs** — not just text logs, but structured records that can be queried
2. **Immutable records** — append-only storage for audit trails (event sourcing pattern)
3. **Decision replay** — ability to replay a past decision with the same inputs to verify behavior
4. **Version tagging** — every output tagged with model version, prompt version, and retrieval configuration
5. **Retention policies** — financial records: 10 years (Germany); medical records: 15+ years (Netherlands)

---

## Pattern 3: The Domain-Deterministic Boundary

Both roles require a sharp boundary between what the AI decides and what deterministic logic handles.

### The Principle

> **Never let an LLM compute what a lookup table or formula can compute exactly.**

### Finom Application

| Deterministic (never LLM) | AI-powered (judgment calls) |
|---|---|
| VAT rate calculation (19%, 7%, 0%) | Transaction categorization |
| Double-entry booking rules | Vendor matching |
| UStVA filing format | Receipt extraction |
| Bank reconciliation matching | Cash flow prediction |
| Compliance thresholds | Anomaly detection |

### Delphyr Application

| Deterministic (never LLM) | AI-powered (judgment calls) |
|---|---|
| Drug interaction databases (DDI) | Clinical note summarization |
| Lab value reference ranges | Relevance ranking of documents |
| ICD-10 code validation | Information extraction from free text |
| Patient ID matching/scoping | Citation generation |
| FHIR resource structure | Clinical query interpretation |

### Why This Pattern Is Interview Gold

It shows you understand that **AI is a component, not the system**. Both Dmitry (Finom CTO) and Dejan (Delphyr Lead) are likely tired of candidates who think "just use GPT-4" is an architecture. The candidate who says "VAT rates come from a lookup table, not a model" or "drug interactions come from a database, not the LLM" demonstrates production maturity.

---

## Pattern 4: The Staged Rollout Model

Both companies need AI that earns trust over time, not AI that launches fully autonomous.

### The Universal Maturity Ladder

```
Level 0: Shadow mode     — AI runs, outputs discarded, only metrics collected
Level 1: Suggest mode    — AI suggests, human decides and executes
Level 2: Draft mode      — AI drafts, human reviews before execution
Level 3: Auto-with-audit — AI executes, human can review/undo
Level 4: Full automation — AI executes, human alerted only on anomalies
```

### Finom Progression Example (Transaction Categorization)

| Level | Behavior | Criteria to advance |
|-------|----------|-------------------|
| Shadow | Categorize all transactions internally, compare to manual | >85% agreement for 30 days |
| Suggest | Show suggested category to accountant | >90% acceptance rate for 14 days |
| Draft | Pre-fill category, user confirms | <5% correction rate for 14 days |
| Auto-audit | Auto-book, user reviews daily summary | <2% correction rate for 30 days |
| Full auto | Auto-book, alert on anomalies only | Continuous monitoring, no regressions |

### Delphyr Progression Example (MDT Briefing)

| Level | Behavior | Criteria to advance |
|-------|----------|-------------------|
| Shadow | Generate briefing internally, compare to manual prep | Clinician blind review scores >4/5 |
| Suggest | Show AI briefing alongside manual prep | >80% information overlap confirmed |
| Draft | Generate briefing, clinician reviews before meeting | <10% substantive correction rate |
| Primary | AI briefing is default, clinician reviews highlights | Sustained quality over 3 months |
| *Full auto* | *Not applicable — clinical AI should always have human oversight* | *Regulatory constraint* |

### Key Difference: Clinical AI Has a Hard Ceiling

Full automation is **not the goal** in healthcare. The maturity model tops out at "primary source with human oversight." This is a regulatory and ethical constraint, not a technical one. In finance, full automation is achievable for low-risk, high-volume operations.

---

## Pattern 5: The Error Taxonomy

Both domains need error classification that goes beyond "right/wrong" to capture the severity and type of error.

### Shared Error Dimensions

| Dimension | Finom Example | Delphyr Example |
|-----------|---------------|-----------------|
| **False positive** | Flagged a correct categorization for review (waste of time) | Flagged a safe output for review (clinician fatigue) |
| **False negative** | Missed a wrong categorization (financial error propagated) | Missed a hallucination (incorrect clinical information used) |
| **Commission error** | Booked to wrong SKR03 account | Included unsupported clinical claim |
| **Omission error** | Failed to extract a line item from invoice | Missed a relevant lab result in summary |
| **Severity-weighted** | Wrong VAT rate (compliance risk) vs. wrong description (cosmetic) | Wrong medication info (patient safety) vs. wrong date format (cosmetic) |

### Why Severity-Weighted Error Metrics Matter

Standard accuracy treats all errors equally. In both domains, a **wrong VAT rate** and a **misspelled vendor name** have vastly different consequences. Similarly, a **hallucinated drug interaction** and a **slightly imprecise date** are not equivalent errors.

**Interview-ready framing:**
> "I would design the evaluation framework around severity-weighted metrics, not just accuracy. A 95% accuracy that includes 5% high-severity errors is worse than 90% accuracy with only low-severity errors."

---

## Pattern 6: The Feedback Loop Architecture

Both roles need systems that improve from human corrections, not just from retraining.

### The Feedback Cycle

```
AI Output → Human Review → Correction (if needed) → Structured Feedback Record
     ↑                                                         │
     └─────────────── Model/Prompt/Threshold Update ←──────────┘
```

### Finom: Accountant Corrections

When an accountant corrects a categorization:
1. Record: original prediction, correct label, confidence score, context
2. Analyze: was this a known edge case or a new pattern?
3. Act: update prompt examples, adjust threshold, or flag for retraining batch

### Delphyr: Clinician Corrections

When a clinician corrects a summary:
1. Record: original output, clinician edit, retrieval context, confidence
2. Analyze: was relevant information missing from retrieval, or was generation unfaithful?
3. Act: improve retrieval (if missing), improve generation (if unfaithful), or expand golden set

### The Meta-Insight

The feedback loop reveals whether the problem is **retrieval** (wrong inputs to the model) or **generation** (wrong outputs from the model). This diagnostic distinction is critical in both domains and shapes the improvement strategy.

---

## Synthesis: The Correctness-Sensitive AI Engineer Profile

These patterns converge on a specific engineering profile that both companies need:

1. **Systems thinker** — sees the AI model as one component in a larger workflow
2. **Calibration-aware** — understands that confidence scores must be meaningful, not just numbers
3. **Audit-conscious** — designs for traceability from day one
4. **Boundary-setter** — knows where deterministic logic belongs and where AI adds value
5. **Staged deployer** — earns trust through measured rollout, not big-bang launches
6. **Error-taxonomist** — classifies errors by severity, not just frequency
7. **Feedback-architect** — designs systems that learn from human corrections

This profile is the career thesis. Both Finom and Delphyr are different instantiations of the same need.

---

## Practical Application: Interview Bridges

When asked about healthcare experience in a Finom interview, or about fintech experience in a Delphyr interview, the response pattern is:

> "The domain is different, but the engineering challenges are structurally identical. In both cases, you need [pick relevant pattern above]. Here's how I'd apply it to [their domain]..."

This document provides the specific patterns to make that bridge concrete rather than hand-wavy.
