# Finom — Observability Architecture for Production AI Agents

## The Observability Imperative

Finom's use of Confident AI reduced iteration cycles from 10 days to 3 hours. But that's **development** observability. **Production** observability is harder — you can't replay a live financial transaction through the agent to see what happened.

This document covers the architectural patterns for observing agent behavior in production, where every decision matters and the cost of failure is real money.

## The Three Pillars

```
┌─────────────────────────────────────────────────────────────┐
│                   OBSERVABILITY ARCHITECTURE                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   TRACES    │  │   METRICS   │  │   LOGS      │        │
│  │             │  │             │  │             │        │
│  │ What        │  │ How well    │  │ What        │        │
│  │ happened    │  │ is it       │  │ actually    │        │
│  │ in order    │  │ performing  │  │ happened    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│       ↓                 ↓                ↓                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              CORRELATION ID                         │   │
│  │  Links traces, metrics, and logs for a single       │   │
│  │  agent execution or user session                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Pattern 1: The Agent Trace Structure

### What to Capture

```typescript
interface AgentTrace {
  // Identity
  traceId: string;           // Unique per execution
  parentTraceId?: string;    // For sub-agent calls
  agentId: string;
  agentVersion: string;
  
  // Timing
  startedAt: Date;
  finishedAt?: Date;
  duration?: number;         // milliseconds
  
  // Input (the context the agent saw)
  context: {
    userQuery: string;
    retrievedDocuments: DocumentRef[];
    systemPrompt: string;
    toolDefinitions: Tool[];
  };
  
  // Output (the decision made)
  decision: {
    chosenAction: string;
    reasoning: string;       // The model's output
    confidence: number;
    toolCalls: ToolCall[];
  };
  
  // Quality (post-hoc evaluation)
  evaluation?: {
    correct: boolean;
    errorType?: 'wrong_category' | 'wrong_vat' | 'missed_audit' | 'hallucination';
    severity?: 'low' | 'medium' | 'high' | 'critical';
    correctedBy?: 'user' | 'audit' | 'system';
  };
}
```

### Finom-Specific Trace Points

| Trace Point | What to Capture | Why It Matters |
|-------------|-----------------|-----------------|
| Transaction received | Amount, merchant, timestamp | Baseline for all downstream decisions |
| Category chosen | SKR03 code, confidence, reasoning | Primary output, primary failure mode |
| VAT calculated | Rate, amount, mechanism (reverse charge, exempt) | Compliance-critical |
| Booking created | Debit/credit accounts, amounts | Ledger integrity |
| Human review requested | What was shown, what user chose | Calibration signal |

## Pattern 2: The Confidence Histogram

### Real-Time Monitoring

```typescript
interface ConfidenceHistogram {
  // Buckets: <0.5, 0.5-0.7, 0.7-0.85, 0.85-0.95, >0.95
  buckets: number[];
  
  // Per-bucket accuracy (computed from corrections)
  bucketAccuracy: Map<number, number>;
  
  // Drift detection
  previousAccuracy?: number;
  currentAccuracy: number;
  driftThreshold = 0.05;  // 5% drop triggers alert
  
  // Per-market breakdown
  marketBreakdown: Map<string, MarketMetrics>;
}

interface MarketMetrics {
  sampleCount: number;
  accuracy: number;
  avgConfidence: number;
  calibrationError: number;
  errorBreakdown: Map<string, number>;  // error type → count
}
```

### The Calibration Dashboard

```
Confidence Distribution (Last 7 Days)
═══════════════════════════════════════════════════════
  <50%   │████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  127
  50-70% │████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░  234
  70-85% │████████████████░░░░░░░░░░░░░░░░░░░░░  456
  85-95% │████████████████████████░░░░░░░░░░░░  823
  >95%   │████████████████████████████████████  1,892

Accuracy by Bucket:
  <50%:   42%  ⚠️ EXPECTED: ~45%      CALIBRATED
  50-70%: 61%  ⚠️ EXPECTED: ~60%      OK
  70-85%: 78%  ✓ EXPECTED: ~77%      OK
  85-95%: 91%  ✓ EXPECTED: ~90%      OK
  >95%:   98%  ✓ EXPECTED: ~97%      OK

⚠️ ALERT: Germany market accuracy dropped 6% since yesterday
```

### Alert Triggers

| Condition | Action |
|-----------|--------|
| Calibration error > 10% at any threshold | Downgrade autonomy to next level |
| Accuracy drops > 5% week-over-week | Freeze auto-routing, investigate |
| Error rate by market > baseline + 2σ | Alert on-call, prepare rollback |
| Latency p99 > 5s for categorization | Page infrastructure |

## Pattern 3: The Correction Feedback Loop

### The Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  CORRECTION FEEDBACK LOOP                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   User corrects: "This was Office Supplies, not Travel"    │
│         │                                                    │
│         ▼                                                    │
│   ┌─────────────┐                                           │
│   │ Correction  │  Store: original, correction,            │
│   │ Captured    │  timestamp, user_id, transaction_id       │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────┐                                           │
│   │ Similarity  │  Find: same merchant, similar amount,     │
│   │ Search      │  similar timeframe                        │
│   └──────┬──────┘                                           │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────┐     ┌─────────────┐                       │
│   │ Batch       │     │ Retrain or  │                       │
│   │ Update      │ ──► │ Flag for     │                       │
│   │             │     │ human review │                       │
│   └─────────────┘     └─────────────┘                       │
│          │                                                   │
│          ▼                                                   │
│   ┌─────────────┐                                           │
│   │ Metrics     │  Update calibration, accuracy,            │
│   │ Updated     │  market-specific baselines                │
│   └─────────────┘                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Implementation

```typescript
class CorrectionFeedbackLoop {
  async onCorrection(correction: Correction): Promise<void> {
    // 1. Store the correction
    await this.store.correction(correction);
    
    // 2. Find similar transactions
    const similar = await this.findSimilar(correction);
    
    // 3. If enough similar cases, batch update
    if (similar.length >= this.batchThreshold) {
      await this.batchUpdate(similar, correction);
      await this.metrics.record({
        type: 'batch_correction',
        count: similar.length,
        correctionType: correction.type,
      });
    } else {
      // 4. Otherwise, flag for human review of similar cases
      await this.flagForReview(similar);
    }
    
    // 5. Update calibration metrics
    await this.calibration.update(correction);
  }
  
  async findSimilar(correction: Correction): Promise<Transaction[]> {
    // Same merchant (normalized)
    // Similar amount (±10%)
    // Within 30 days
    // Same market
    return this.store.query({
      merchant: normalize(correction.original.merchant),
      amountWithin: [correction.original.amount * 0.9, correction.original.amount * 1.1],
      dateWithin: [correction.original.date - 30 days, correction.original.date],
      market: correction.original.market,
    });
  }
}
```

## Pattern 4: A/B Testing Agents

### The Challenge

You can't easily A/B test a financial agent because:
- The ground truth takes months to verify (tax filing accepted)
- Each transaction is different; comparing "accuracy" across different transactions is meaningless
- You can't show two different categorizations to the same user

### The Solution: Canary Routing

```typescript
interface CanaryConfig {
  // Percentage of traffic to new version
  trafficPercent: number;
  
  // Which decisions to test
  decisionTypes: ('categorize' | 'vat' | 'booking')[];
  
  // Which markets to test
  markets: string[];
  
  // Success metrics
  metrics: {
    accuracyDrop: number;        // Allow up to 2% drop
    latencyIncrease: number;     // Allow up to 500ms
    userCorrectionRate: number;  // Allow up to 5%
  };
  
  // Rollback trigger
  rollbackIf: {
    errorRateAbove: number;       // If > 1% errors, rollback
    accuracyBelow: number;       // If accuracy drops > 3%, rollback
  };
}

// Traffic flow
┌──────────────┐
│   Incoming   │
│ Transaction  │
└──────┬───────┘
       │
       ▼
┌─────────────────────────────────────┐
│         Canary Router               │
│                                     │
│  if (within(canaryConfig.markets)   │
│     && random() < canaryConfig %)   │
│    → Route to agent-v2               │
│  else                               │
│    → Route to agent-v1 (control)     │
└─────────────────────────────────────┘
```

### Shadow Mode (Alternative)

If you can't risk any user impact:

```typescript
// Run v2 in shadow mode, never commit its decisions
// Compare v1 vs v2 decisions on same transactions
// Measure: agreement rate, latency, and (if ground truth available) accuracy

const shadowResult = await agentV2.decide(transaction);
const productionResult = agentV1.decide(transaction);

// Log comparison
await this.observability.log({
  traceId: transaction.id,
  v1Decision: productionResult,
  v2Decision: shadowResult,
  agreement: productionResult.category === shadowResult.category,
  latencyDiff: shadowResult.latency - productionResult.latency,
});
```

## Pattern 5: The Alert Taxonomy

Not all alerts are equal. This is the severity matrix:

| Severity | Definition | Example | Response Time | Who |
|----------|------------|---------|---------------|-----|
| **P0 - Critical** | Direct financial loss or compliance failure | Agent filed wrong tax return | < 15 min | On-call + CTO |
| **P1 - High** | High-probability financial impact | 10% of transactions miscategorized today | < 1 hour | On-call |
| **P2 - Medium** | Potential future impact, requires investigation | Calibration drift detected | < 24 hours | Team lead |
| **P3 - Low** | Informational, no immediate action | New merchant pattern detected | < 1 week | Backlog |

### Alert Fatigue Prevention

```typescript
// Don't alert on every deviation — alert on trends
interface AlertCondition {
  // Not: "accuracy < 90%"
  // But: "accuracy < 90% for 3 consecutive hours"
  
  type: 'threshold' | 'trend' | 'anomaly';
  metric: string;
  threshold?: number;
  window: Duration;       // 3 hours
  consecutive: number;   // 3 consecutive violations
  
  // For anomaly detection
  baseline?: MetricBaseline;
  sigma?: number;        // 2σ from baseline
}
```

## Connection to Confident AI

The Finom/Confident AI integration handles:
- **Fast iteration**: Test hypotheses in 3 hours, not 10 days
- **Evaluation runs**: Automated accuracy measurement
- **Regression detection**: Compare against baseline

The patterns here handle:
- **Production monitoring**: What happens in live system
- **Calibration tracking**: Are confidence scores trustworthy
- **Correction feedback**: How user fixes improve the system

Together: Eval tells you when to promote → Safety patterns handle promotion → Observability confirms promotion worked

## Interview Talking Points

1. **"The hardest part of production agent observability isn't the tracing — it's the ground truth. A categorization looks right for months until the tax filing is rejected. That's why correction feedback loops and calibration tracking matter more than raw accuracy."**

2. **"I don't trust a confidence score without calibration data. In a new market, the model might say 90% but only be right 70%. That's over-confidence. You need to measure calibration error, not just accuracy."**

3. **"Canary routing for agents is different from traditional canary deploys. You can't A/B test financial decisions on the same transaction. Instead, you route 5% to the new version in a specific market, measure accuracy drop, and rollback if it exceeds threshold."**

4. **"The correction feedback loop is where most teams fail. They capture the fix but never ask: were there similar transactions that should also be fixed? That's the difference between a one-off bug fix and a systemic improvement."**

## Related Files

- `code/eval-harness.ts` — Production evaluation framework
- `code/confidence-calibration.ts` — ECE and threshold analysis
- `insights/mcp-architecture-study.md` — MCP observability patterns
- `prep/fresh-intel-april-2026-updated.md` — Confident AI integration (March 2026)