# Fraud and Risk Architecture for Fintech AI

## Purpose

The Senior AI Engineer job posting explicitly mentions "fraud and risk workflows" as part of the role scope. This document provides the reference knowledge and architectural thinking needed to discuss fraud and risk in a Finom interview context.

---

## Why Fraud Matters for Finom's AI Strategy

Finom's AI capabilities create new fraud surfaces:

| AI Capability | Fraud Surface It Creates |
|--------------|--------------------------|
| Auto-categorization | Adversarial miscategorization to hide fraud |
| Auto-reconciliation | Manipulated invoice/payment matching |
| Tax preparation | Fraudulent tax claims via fabricated expenses |
| AI-powered lending | Synthetic identities, inflated revenue, loan fraud |
| Invoice financing | Ghost invoices, duplicate financing |
| Multi-agent automation | Adversarial inputs that exploit agent trust chains |

The central AI team must think about fraud not as a separate system but as a **cross-cutting concern** embedded in every agent.

---

## Fraud Detection Architecture Patterns

### Pattern 1: Anomaly-First Detection

Most SME fraud is detectable as anomalies against established behavioral baselines:

```
Transaction Stream
       │
       ▼
┌──────────────────────┐
│ Baseline Builder      │ ← Builds per-customer behavioral profile
│ - Spending patterns   │    (updated continuously)
│ - Timing patterns     │
│ - Counterparty graph  │
│ - Category ratios     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Anomaly Scorer        │ ← Scores each transaction against baseline
│ - Statistical (z-score│
│   on amount, timing)  │
│ - Graph-based (new    │
│   counterparty,       │
│   unusual network)    │
│ - Behavioral (pattern │
│   break, velocity     │
│   change)             │
└──────────┬───────────┘
           │
           ▼
   Anomaly Score + Explanation
```

**Key insight for interviews:** Anomaly detection is not binary fraud/not-fraud. It produces a risk score that feeds into the same confidence-based routing pattern used throughout Finom's MAS:

- Low anomaly score → process normally
- Medium anomaly score → flag for review, continue processing
- High anomaly score → hold transaction, alert fraud team

### Pattern 2: Rule-Based + ML Hybrid

Pure ML misses known fraud patterns; pure rules miss novel patterns. The production approach is hybrid:

**Rules layer (fast, interpretable, regulatory):**
- Velocity checks: >N transactions in M minutes
- Amount thresholds: transaction > X% of historical average
- Known blacklists: sanctioned entities, known fraud patterns
- Compliance rules: AML limits, PEP screening

**ML layer (adaptive, pattern-discovering):**
- Transaction classification: normal / suspicious / confirmed-fraud
- Customer segmentation: risk tier assignment based on behavioral features
- Network analysis: graph-based detection of fraud rings, shell companies
- Time-series: detect gradual behavioral drift (boiling frog patterns)

**Combination:**
```
Transaction → Rules Engine → ML Scorer → Combined Risk Score → Routing
                   │              │
                   ▼              ▼
             Rule triggers    ML confidence
             (hard blocks)   (soft scoring)
```

### Pattern 3: Adversarial Robustness for AI Systems

When AI auto-processes transactions, adversaries will probe the AI:

**Attack vectors against Finom-type systems:**

1. **Categorization manipulation** — craft transaction descriptions that trick the classifier into wrong categories (e.g., personal expense classified as business, luxury goods classified as office supplies)
2. **Reconciliation gaming** — create invoices that match payment amounts but are fabricated
3. **Gradual drift** — slowly shift spending patterns to avoid anomaly detection thresholds
4. **Split transactions** — break large amounts into small ones below detection thresholds (structuring)
5. **Invoice fraud** — submit altered invoices with inflated amounts for tax deduction or financing

**Defenses:**

| Attack | Defense | Implementation |
|--------|---------|----------------|
| Categorization manipulation | Cross-validation with merchant data, receipt verification | Multi-signal classification (don't trust description alone) |
| Reconciliation gaming | Three-way matching (invoice + payment + delivery) | Reconciliation agent requires multiple evidence sources |
| Gradual drift | Rolling baseline with long-term trend analysis | Anomaly detection over multiple time horizons |
| Split transactions | Aggregate analysis over time windows | Rule: sum of small transactions to same counterparty |
| Invoice fraud | Document authenticity scoring, duplicate detection | OCR + hash comparison + metadata validation |

---

## Fraud-Specific Agent Design

### Within Finom's MAS Architecture

Fraud detection isn't a separate agent — it's a **cross-cutting capability** that touches multiple agents:

```
┌─────────────────────────────────────────────────┐
│                 Fraud Overlay                     │
│  (cross-cutting risk scoring on every agent)     │
├─────────────────────────────────────────────────┤
│                                                   │
│  Intake → Classification → Extraction → Recon    │
│    ↓           ↓              ↓          ↓       │
│  [risk]     [risk]         [risk]     [risk]     │
│                                                   │
│  Categorization → Tax Prep → Review → Filing     │
│       ↓              ↓         ↓        ↓        │
│     [risk]        [risk]    [risk]   [risk]      │
│                                                   │
└─────────────────────────────────────────────────┘
```

**Per-agent risk signals:**

| Agent | Risk Signal |
|-------|-------------|
| Intake | Document authenticity, metadata anomalies |
| Classification | Unusual document type for this customer |
| Extraction | Extracted amounts vs. historical patterns |
| Reconciliation | Unmatched items, forced matches, timing anomalies |
| Categorization | Category inconsistent with merchant/counterparty |
| Tax Prep | Deduction patterns anomalous for business type |
| Review | Human reviewer override patterns (are they rubber-stamping?) |
| Filing | Filing frequency anomalies, unusual correction patterns |

### Dedicated Fraud Agent (for Complex Cases)

For high-risk signals, a dedicated fraud investigation agent can:

1. **Aggregate signals** from multiple agents across the pipeline
2. **Pull historical context** for the customer (past flags, resolved incidents)
3. **Graph analysis** to detect relationship patterns (shared addresses, phone numbers, counterparties)
4. **Generate explanation** for the fraud team (why this was flagged, what evidence supports it)
5. **Recommend action** (hold, flag, alert, block) with confidence

---

## Lending-Specific Fraud Considerations

Finom's lending expansion introduces new fraud types:

### Invoice Financing Fraud
- **Ghost invoices:** Fake invoices for services never rendered, submitted for financing
- **Duplicate financing:** Same invoice submitted to multiple lenders
- **Inflated invoices:** Real invoices with inflated amounts

**Detection approach:**
- Cross-reference invoice with transaction history (does this counterparty relationship exist?)
- Duplicate detection across financing requests (hash matching on invoice features)
- Amount anomaly detection against historical invoice patterns

### Credit Application Fraud
- **Synthetic identities:** Fabricated business profiles with manufactured history
- **Revenue inflation:** Manipulated bank statements or transaction data
- **Business misrepresentation:** Claiming different business type than reality

**Detection approach:**
- Multi-source verification (don't trust self-reported data alone)
- Finom's advantage: they already have the real transaction data — compare application claims against observed behavior
- Behavioral consistency scoring: do application claims match actual account patterns?

---

## Evaluation Framework for Fraud Systems

### Metrics That Matter

| Metric | What It Measures | Why It Matters |
|--------|------------------|----------------|
| True Positive Rate (recall) | % of actual fraud caught | Missing fraud = financial loss |
| False Positive Rate | % of legitimate transactions flagged | Too many false positives = customer friction |
| Detection latency | Time from fraud to detection | Faster detection = less damage |
| Investigation efficiency | Fraud team hours per case | Scalability of the fraud operation |
| Customer impact | False positives leading to blocked accounts | Brand and trust damage |

### The False Positive Problem

In SME banking, false positives are expensive:
- A legitimate business owner blocked from their account is a churned customer
- European SMEs already distrust banking institutions — friction accelerates churn
- Finom's target of 1M customers means even a 0.1% false positive rate = 1,000 wrongly flagged customers

**Design principle:** Fraud detection must be confidence-calibrated (see confidence-calibration-patterns.md). The routing thresholds should minimize customer-facing friction for medium-risk cases:

- **High risk:** Block and alert fraud team
- **Medium risk:** Allow transaction, flag for async review
- **Low risk:** Process normally, log for pattern building

---

## Regulatory Context

### EU Anti-Money Laundering

- 6th Anti-Money Laundering Directive (6AMLD) — expanded criminal liability
- AML Authority (AMLA) established in Frankfurt — direct supervision of highest-risk entities
- Customer Due Diligence (CDD) and Enhanced Due Diligence (EDD) requirements
- Suspicious Activity Reports (SARs) — obligatory reporting

### PSD2 / Payment Services

- Strong Customer Authentication (SCA) requirements
- Transaction monitoring obligations
- Fraud reporting to national competent authorities

### Finom's Position

As an EMI (Electronic Money Institution), Finom has regulatory obligations for:
- Transaction monitoring (AML/CFT)
- Fraud detection and reporting
- Customer identity verification
- Suspicious transaction reporting

AI can help meet these obligations more efficiently — but the AI itself must be auditable and explainable.

---

## Interview Talking Points

### If Asked "How would you approach fraud detection for our platform?"

> "I'd embed fraud detection as a cross-cutting concern in the existing MAS, not as a separate system. Each agent already emits confidence signals — fraud risk is another signal in that same framework. The key is a hybrid approach: rules for known patterns and regulatory requirements, ML for adaptive detection of novel patterns, and confidence-based routing that minimizes false positives for legitimate customers. For lending specifically, Finom has a massive advantage — you already observe real transaction behavior, so you can cross-validate credit applications against actual data."

### If Asked "What's your experience with fraud detection?"

> "I haven't built fraud-specific systems, but the underlying patterns are the same ones I've applied in production AI: anomaly detection, confidence-based routing, human-in-the-loop for edge cases, and multi-signal classification. The fraud-specific domain knowledge — AML requirements, structuring patterns, invoice fraud types — is learnable. The engineering discipline of building reliable detection with calibrated confidence is what I bring."

### If Asked "How do you balance fraud detection with customer experience?"

> "False positives are the enemy. A blocked legitimate customer is a churned customer. The answer is confidence calibration and tiered routing: high-risk cases get blocked, medium-risk gets async review without blocking, low-risk processes normally. And you measure the customer impact explicitly — false positive rate is a first-class metric alongside detection rate."

---

## References

- EU 6AMLD regulatory framework
- PSD2 transaction monitoring requirements
- Finom EMI license obligations
- Cross-reference: `confidence-calibration-patterns.md` for calibration framework
- Cross-reference: `finom-ai-lending-expansion-analysis.md` for lending context
