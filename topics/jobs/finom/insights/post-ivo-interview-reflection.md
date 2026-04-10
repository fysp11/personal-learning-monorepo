# Finom — Post-Ivo Interview Reflection & Next Steps

Saved: 2026-04-09

## Interview Context

- **Date:** April 8, 2026
- **Interviewer:** Ivo Dimitrov (co-founder, Chief AI Officer)
- **Duration:** 45 minutes
- **Format:** Second round, following Dmitry (CTO) first-round on March 31

## Status

**Outcome not yet recorded.** This document provides a structured framework for capturing the interview outcome and planning next steps regardless of result.

---

## Capture Framework

When captured material the outcome, answer these questions:

### 1. What Was Asked?
- Did Ivo focus on org design (central vs embedded)?
- Did he test build-vs-buy judgment?
- Were there system design questions?
- Did he explore specific workflow scenarios (accounting, invoicing, tax)?
- How much was cultural fit vs technical depth?

### 2. What Landed Well?
- Which stories or framings got visible engagement?
- Did the "centralize selectively" framing resonate?
- Was the MCP architecture discussion relevant?
- Did domain knowledge (SKR03, UStVA, EU tax regimes) come up?

### 3. What Didn't Land?
- Were there questions that caught you off guard?
- Were there areas where you felt underprepared?
- Did any of the prepared narratives feel forced or irrelevant?

### 4. Signals About Next Steps
- Did Ivo signal additional rounds?
- Was there mention of team meetings, take-home assignments, or offer timelines?
- Did he share anything about the team's current priorities or challenges?

---

## Deepening Technical Preparation: Agentic Evaluation Framework

Regardless of outcome, this is the highest-value technical artifact to build next. It directly demonstrates the "evaluation as core capability" thesis that both Dmitry and Ivo value.

### Experiment: Financial Agent Evaluation Framework

**Goal:** Build a reusable evaluation framework that tests agent accuracy across multiple EU tax regimes.

**Architecture:**

```
Test Suite Generator
    ├── Synthetic transaction generator (DE, FR, IT, ES, NL)
    ├── Ground truth labels (correct SKR03 code, VAT rate, booking entries)
    └── Edge case library (reverse charges, exempt services, split invoices)

Agent Under Test
    ├── Transaction categorization agent
    ├── VAT calculation agent
    └── Booking suggestion agent

Evaluation Engine
    ├── Per-field accuracy (category, VAT rate, amount, date)
    ├── Severity-weighted scoring (VAT errors >> description errors)
    ├── Calibration assessment (confidence vs actual accuracy)
    ├── Cross-market consistency (same vendor type across countries)
    └── Regression detection (compare against baseline)

Report Generator
    ├── Per-market accuracy breakdown
    ├── Error taxonomy (commission, omission, severity)
    ├── Confidence calibration curves
    └── Regression alerts
```

### Test Case Categories

| Category | Examples | Severity |
|----------|----------|----------|
| Standard domestic | German freelancer invoicing for consulting | Low (high volume, well-understood) |
| Cross-border EU | Dutch company invoicing German client (reverse charge) | High (reverse charge rules complex) |
| Mixed VAT | Invoice with 19% and 7% items | Medium (common but error-prone) |
| Exempt services | Medical services, educational services | High (wrong VAT = compliance violation) |
| Small business | Kleinunternehmer §19 UStG (no VAT charged) | Medium (must not add VAT) |
| Credit notes | Partial refund on previous invoice | Medium (must correctly reverse original) |
| Digital services | SaaS sold to EU consumer (MOSS/OSS rules) | High (destination-based VAT since 2021) |

### Implementation Sketch (TypeScript)

```typescript
interface TransactionTestCase {
  id: string;
  market: "DE" | "FR" | "IT" | "ES" | "NL";
  category: string;
  description: string;
  input: {
    vendor: string;
    amount: number;
    currency: string;
    description: string;
    documentType: "invoice" | "receipt" | "credit_note";
  };
  expectedOutput: {
    skr03Code: string;
    vatRate: number;
    vatAmount: number;
    netAmount: number;
    bookingEntries: Array<{
      account: string;
      debit: number;
      credit: number;
    }>;
  };
  severity: "critical" | "high" | "medium" | "low";
  edgeCaseType?: string;
}

interface EvaluationResult {
  testCaseId: string;
  passed: boolean;
  fieldResults: {
    skr03Code: { expected: string; actual: string; correct: boolean };
    vatRate: { expected: number; actual: number; correct: boolean };
    vatAmount: { expected: number; actual: number; correct: boolean; delta: number };
    bookingEntries: { expected: number; actual: number; structurallyCorrect: boolean };
  };
  confidence: number;
  severity: "critical" | "high" | "medium" | "low";
  severityWeightedScore: number;
}

interface EvaluationReport {
  totalCases: number;
  overallAccuracy: number;
  severityWeightedAccuracy: number;
  perMarket: Record<string, { accuracy: number; count: number; criticalErrors: number }>;
  perCategory: Record<string, { accuracy: number; count: number }>;
  calibration: {
    expectedCalibrationError: number;
    bins: Array<{ confidenceRange: [number, number]; accuracy: number; count: number }>;
  };
  regressions: Array<{ testCaseId: string; previousResult: string; currentResult: string }>;
}
```

### Why This Is High Signal

1. **Shows evaluation discipline** — the thing Dmitry explicitly valued
2. **Demonstrates domain understanding** — EU tax edge cases prove you've done the homework
3. **Reusable architecture** — the pattern works for any classification agent, not just accounting
4. **Calibration awareness** — goes beyond accuracy to confidence quality
5. **Severity-weighted thinking** — shows production maturity

---

## Next Actions

### If Advancing to Next Round
1. Build the evaluation framework experiment (4-5 hours)
2. Prepare a system design walkthrough: "Design transaction categorization for 5 EU markets"
3. Have concrete questions about Central AI team's current mandate and org boundaries
4. Study Finom's recent product changes (lending, invoicing updates)

### If Waiting
1. Build the evaluation framework anyway — it's a portfolio piece
2. Continue deepening EU tax regime knowledge
3. Explore Finom's product as a user (free tier signup)

### If Not Advancing
1. Capture what was learned about fintech AI challenges
2. Apply the evaluation framework pattern to other opportunities
3. The MCP architecture study and MAS knowledge are broadly applicable
4. EU accounting domain knowledge could be relevant to other European fintech roles

---

## Broader Career Signal

The Finom interview process has validated that "production AI systems in correctness-sensitive domains" is a genuine market need. Whether or not this specific role works out, the preparation has built depth in:

- Multi-agent system architecture
- MCP as an integration pattern
- EU regulatory awareness for AI in finance
- Financial workflow automation patterns
- Evaluation framework design for business-critical AI
