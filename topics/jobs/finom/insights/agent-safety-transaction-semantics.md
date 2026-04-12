# Finom — Agent Safety & Transaction Semantics

## The Financial Agent Constraint

In consumer AI, a wrong answer is annoying. In financial AI, a wrong categorization is a compliance violation, a wrong VAT calculation is a tax filing error, and a wrong booking entry is a ledger integrity failure.

This document captures the architectural patterns for building agents that operate with **transactional semantics** — where every AI action can be committed or rolled back, and where the system explicitly tracks what happened vs what was supposed to happen.

## Core Principle: Earned Autonomy

```
┌─────────────────────────────────────────────────────────────┐
│                  AUTONOMY LADDER                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Level 5: Auto-filing                                     │
│        ↑                                                    │
│   Level 4: Auto-booking with audit                          │
│        ↑                                                    │
│   Level 3: Auto-propose, auto-execute on explicit confirm   │
│        ↑                                                    │
│   Level 2: Propose only, human executes                     │
│        ↑                                                    │
│   Level 1: Full human review before any action             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

The ladder tracks **measured trust**:
- New agent → Level 1
- Pass N evaluation runs at Level 1 → Level 2
- Pass calibration checks at Level 2 → Level 3
- Pass production monitoring at Level 3 → Level 4
- Pass external audit at Level 4 → Level 5

**Key insight**: The autonomy ratchet only moves forward when calibration data proves it should. Moving from auto-categorize to auto-book isn't a product decision — it's a measurement decision.

## Pattern 1: The Commit/Rollback Architecture

### Concept

Every agent action is staged in a **pending** state before becoming effective. The system maintains:

1. **Intention**: What the agent wants to do
2. **Effect**: What would happen if committed
3. **Compensation**: How to undo it if needed

### Implementation Structure

```typescript
interface AgentAction<T> {
  id: string;
  agentId: string;
  actionType: 'categorize' | 'book' | 'file' | 'classify';
  intention: T;           // What the agent proposes
  confidence: number;     // 0-1, must be above threshold
  compensation?: string;  // ID of action that undoes this
  
  // State machine
  status: 'pending' | 'committed' | 'rejected' | 'rolled_back';
  committedAt?: Date;
  committedBy?: string;   // human or auto
}

interface Transaction<T> {
  id: string;
  actions: AgentAction[];
  
  // All-or-nothing: either all commit or all roll back
  commit(): Promise<void>;
  rollback(): Promise<void>;
}
```

### Why This Matters for Finom

The credit line expansion is a perfect example. The categorization agent says "this transaction is office supplies, 90% confidence." The credit agent says "this business is creditworthy, 85% confidence."

If the credit decision is wrong and a loan is approved based on miscategorized cash flow, you need:
- The original decision recorded
- The audit trail of what changed
- The ability to recalculate without manual intervention
- The regulatory requirement to show the decision was based on correct data

This is impossible without transactional semantics.

## Pattern 2: Confidence-Aware Routing

### The Routing Matrix

```
                    │ Low (<0.6)    │ Medium (0.6-0.85) │ High (>0.85)
────────────────────┼───────────────┼──────────────────┼──────────────
Categorization      │ Reject        │ Propose          │ Auto-book
                    │ → Queue       │ → User confirms  │ → Execute
────────────────────┼───────────────┼──────────────────┼──────────────
VAT Calculation     │ Reject        │ Propose          │ Auto-file
(deterministic)     │ → Audit       │ → Review         │ → Submit
                    │               │                  │
────────────────────┼───────────────┼──────────────────┼──────────────
Credit Decision     │ Reject        │ Manual review    │ Conditional
                    │ → Decline     │ → Underwriter    │ → Approve
```

**Critical**: The thresholds are different per domain. Categorization at 85% might be safe; credit at 85% is reckless.

### The Calibration Contract

```typescript
interface CalibrationMetrics {
  // For a given confidence threshold
  threshold: number;
  
  // Actual accuracy at or above this threshold
  actualAccuracy: number;
  
  // Expected accuracy (what the model claimed)
  expectedAccuracy: number;
  
  // Calibration error
  calibrationError: number;
  
  // Sample size at this threshold
  sampleSize: number;
}

// If calibrationError > 0.1 at a threshold, don't auto-route
// If sampleSize < 100, don't trust the metrics
// If calibrationError degrades > 0.02 over 30 days, downgrade autonomy
```

## Pattern 3: The Audit Trail Requirement

### Financial AI Audit Requirements

1. **Decision provenance**: What data did the agent see?
2. **Reasoning capture**: Why did it choose this?
3. **Human review record**: Who approved/rejected?
4. **Modification history**: What changed between staging and commit?
5. **Compensation record**: If rolled back, what was the impact?

### Implementation

```typescript
interface AuditEvent {
  timestamp: Date;
  eventType: 'agent_decision' | 'user_review' | 'commit' | 'rollback' | 'modify';
  
  // For agent decisions: what the model actually said
  agentReasoning?: {
    prompt: string;
    response: string;
    tokensUsed: number;
    model: string;
  };
  
  // For human reviews: what the human saw and chose
  humanReview?: {
    userId: string;
    presentedWith: AgentAction[];
    decisions: ('approve' | 'reject' | 'modify')[];
    modifiedValues?: Record<string, any>;
  };
  
  // For modifications: what was different
  diff?: {
    before: Record<string, any>;
    after: Record<string, any>;
    reason: string;
  };
}
```

**GDPR note**: Agent reasoning capture must comply with EU requirements. The prompt may contain personal data, so this is part of the data subject record.

## Pattern 4: The Compensation Chain

### Scenario: Correction Cascade

```
User corrects: "This was not Office Supplies, it was Travel"

1. Transaction correction
   └─ Reverse the original booking
   └─ Create new booking with correct category
   
2. VAT cascade (if category change affects VAT)
   └─ Original: 19% on €100 = €19
   └─ Corrected: 0% (travel is exempt in Germany)
   └─ Refund: €19 to Vorsteuer
   
3. Report cascade
   └─ Recalculate UStVA
   └─ Potentially trigger amended filing
   
4. Credit cascade (if categorization affects cash flow analysis)
   └─ Recalculate business health score
   └─ If credit decision would change → flag for review
```

### Implementation Pattern

```typescript
class CompensationChain {
  async compensate(actionId: string, correction: Correction): Promise<CompensationResult> {
    const original = await this.store.get(actionId);
    
    // 1. Create compensating action (not a simple "undo")
    const compensation = {
      type: 'reverse_and_rebook',
      originalAction: original,
      newAction: correction.target,
      cascades: this.detectCascades(original, correction),
    };
    
    // 2. Validate compensation is possible
    await this.validate(compensation);
    
    // 3. Execute in order (reverse then rebook)
    await this.execute(compensation);
    
    // 4. Record for audit
    await this.audit.record({ original, compensation, correction });
  }
  
  detectCascades(original: AgentAction, correction: Correction): Cascade[] {
    // VAT changes if category changes
    // Report changes if any posting changes
    // Credit decision changes if cash flow projection changes
    return cascades;
  }
}
```

## Pattern 5: The Human-in-the-Loop Taxonomy

Not all HITL is equal. Different decisions need different human involvement:

| Decision Type | Time Sensitivity | Human Role | Latency Target |
|--------------|------------------|------------|----------------|
| Credit approval | High | Underwriter review | < 1 hour |
| Tax filing | Fixed deadline | Sign-off | < 24 hours |
| Category correction | Low | User confirm | < 1 week |
| Anomaly flag | Medium | Operations review | < 48 hours |
| New category creation | Low | Taxonomy owner | < 1 month |

**Key insight**: The system should not ask for human input at the same urgency for all cases. Tax filing deadline = immediate. Category correction = batch.

## Connection to Finom's Confident AI Usage

From the Confident AI case study: Finom reduced iteration cycles from 10 days to 3 hours using eval infrastructure. This is the **observability side** of safety.

The safety patterns here (commit/rollback, compensation chain, audit trail) are the **operational side**. They work together:

- **Eval** tells you when the agent is reliable enough to promote
- **Safety patterns** tell you what to do when reliability breaks

In production, both are required.

## Interview Talking Points

1. **"I think about agent safety as transactional semantics — every AI action is staged before it becomes real, and the system can undo it."**

2. **"The autonomy ladder isn't a product decision, it's a measurement decision. You don't promote an agent to auto-file because it's good — you promote it because calibration data proves it's trustworthy at that level."**

3. **"Compensation chains are the hardest part of financial agents. Undoing one categorization might affect VAT, reporting, and credit decisions. You need to think in cascades, not single actions."**

4. **"The Confident AI infrastructure Finom uses handles evaluation velocity. The patterns here handle what happens when evaluation fails in production. Both are required."**

## Related Files

- `experiments/agent-safety-harness/` — POC implementation of commit/rollback
- `code/eval-harness.ts` — Severity-weighted evaluation framework
- `code/confidence-calibration.ts` — ECE and threshold analysis
- `insights/post-ivo-interview-reflection.md` — Ivo's feedback on safety patterns