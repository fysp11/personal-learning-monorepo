# Finom — Multi-Agent System Coordination Patterns

## Why This Matters

Finom explicitly describes their AI Accountant as a **distributed multi-agent system (MAS)** — multiple autonomous AI agents collaborating within a shared environment. This is not a single-model pipeline. Understanding how agents coordinate, fail independently, and avoid race conditions is critical for this role.

This document covers the coordination patterns that make a MAS reliable in a financial domain.

---

## The Coordination Problem

In a single-agent pipeline, failure is simple: one thing fails, one rollback path. In a MAS:

```
Single Agent:              MAS:
─────────────              ──────────────────────────────────
Input → Agent → Output     Input → Agent-A ──→ Agent-B
                                       ↘            ↓
                                    Agent-C → Agent-D → Output
                                                     ↓
                               What if Agent-B fails after Agent-A commits?
```

The coordination problem is: **how do you maintain consistency when multiple agents can succeed or fail independently?**

---

## Pattern 1: The Orchestrator-Worker Architecture

### Design

One agent (the orchestrator) coordinates all others. Workers execute specific tasks and report back.

```typescript
interface OrchestratorState {
  workflowId: string;
  phase: 'extraction' | 'categorization' | 'vat' | 'routing' | 'booking';
  agents: {
    [agentId: string]: {
      status: 'idle' | 'running' | 'completed' | 'failed';
      result?: AgentResult;
      error?: string;
    };
  };
  decisions: Decision[];
  trace: TraceEvent[];
}

class WorkflowOrchestrator {
  async process(transaction: Transaction): Promise<WorkflowOutcome> {
    const state: OrchestratorState = this.initState(transaction);
    
    // Sequential stages — each result feeds the next
    const extracted = await this.runAgent('extractor', state, transaction);
    const category = await this.runAgent('categorizer', state, extracted);
    const vat = await this.runVatCalculation(state, category); // deterministic, no agent
    const routed = await this.routeByConfidence(state, category);
    
    if (routed.action === 'auto_book') {
      return await this.runAgent('booker', state, { category, vat, transaction });
    } else {
      return { action: 'propose', proposal: { category, vat } };
    }
  }
  
  private async runAgent(agentId: string, state: OrchestratorState, input: any): Promise<AgentResult> {
    state.agents[agentId] = { status: 'running' };
    
    try {
      const result = await this.agents[agentId].execute(input);
      state.agents[agentId] = { status: 'completed', result };
      this.trace(state, { agentId, result, timestamp: Date.now() });
      return result;
    } catch (error) {
      state.agents[agentId] = { status: 'failed', error: error.message };
      throw new AgentFailure(agentId, error);
    }
  }
}
```

### Why This Works for Finom

- The orchestrator owns the workflow state — if any agent fails, the orchestrator controls rollback
- Each agent is independently replaceable — swap the categorizer without changing the orchestrator
- The trace captures which agent made which decision — critical for the audit trail

---

## Pattern 2: Parallel Agent Execution with Fan-Out/Fan-In

### When to Use It

Some stages can run in parallel. For a transaction with both a receipt image and a bank description:

```
Transaction
  ├── OCR Agent (extracts from receipt image)  ─────────┐
  └── NLP Agent (extracts from bank description) ───────┤
                                                          ↓
                                              Merger Agent (reconciles both)
                                                          ↓
                                              Categorization Agent
```

### Implementation

```typescript
async function parallelExtraction(transaction: Transaction): Promise<ExtractedFeatures> {
  const [ocrResult, nlpResult] = await Promise.allSettled([
    ocrAgent.extract(transaction.receiptImage),
    nlpAgent.extract(transaction.bankDescription),
  ]);
  
  // Both succeeded: merge results, highest confidence wins per field
  if (ocrResult.status === 'fulfilled' && nlpResult.status === 'fulfilled') {
    return mergeWithConfidence(ocrResult.value, nlpResult.value);
  }
  
  // One failed: use the other with reduced confidence
  if (ocrResult.status === 'fulfilled') {
    return { ...ocrResult.value, sourceConfidence: ocrResult.value.confidence * 0.9 };
  }
  if (nlpResult.status === 'fulfilled') {
    return { ...nlpResult.value, sourceConfidence: nlpResult.value.confidence * 0.9 };
  }
  
  // Both failed: route to human review
  throw new ExtractionFailure('Both OCR and NLP extraction failed');
}

function mergeWithConfidence(
  ocr: ExtractionResult,
  nlp: ExtractionResult
): ExtractedFeatures {
  // Each field: use the result with higher confidence
  return {
    merchantName: ocr.merchantNameConf > nlp.merchantNameConf
      ? { value: ocr.merchantName, confidence: ocr.merchantNameConf }
      : { value: nlp.merchantName, confidence: nlp.merchantNameConf },
    amount: nlp.amountConf > ocr.amountConf  // NLP is better at amounts
      ? { value: nlp.amount, confidence: nlp.amountConf }
      : { value: ocr.amount, confidence: ocr.amountConf },
    // ... etc
  };
}
```

---

## Pattern 3: The Saga Pattern for Distributed Consistency

### Problem

In a MAS, if agent-D fails after agents A, B, and C have committed work, how do you maintain consistency?

```
Transaction Processing Saga:
  Step 1: Extraction (Agent-A) → succeeds, produces extracted features
  Step 2: Categorization (Agent-B) → succeeds, produces category proposal
  Step 3: VAT Calculation → succeeds, produces VAT breakdown
  Step 4: Booking Creation (Agent-D) → FAILS
  
  Question: What's the state of the system?
```

### The Saga Solution

Each step defines a compensation action — what to do if a later step fails:

```typescript
interface SagaStep<TInput, TOutput> {
  name: string;
  execute: (input: TInput) => Promise<TOutput>;
  compensate: (input: TInput, output: TOutput) => Promise<void>;
}

class TransactionSaga {
  private steps: SagaStep<any, any>[] = [
    {
      name: 'extract_features',
      execute: (tx) => extractionAgent.extract(tx),
      compensate: (tx, result) => auditLog.markExtractionAborted(result.id),
    },
    {
      name: 'categorize',
      execute: (features) => categorizationAgent.categorize(features),
      compensate: (features, result) => auditLog.markCategorizationAborted(result.id),
    },
    {
      name: 'create_booking',
      execute: (data) => bookingAgent.createBooking(data),
      compensate: (data, result) => bookingService.reverseBooking(result.bookingId),
    },
  ];
  
  async execute(transaction: Transaction): Promise<void> {
    const executed: Array<{ step: SagaStep<any, any>, input: any, output: any }> = [];
    
    try {
      let data: any = transaction;
      for (const step of this.steps) {
        const output = await step.execute(data);
        executed.push({ step, input: data, output });
        data = output;
      }
    } catch (error) {
      // Compensate in reverse order
      for (const { step, input, output } of [...executed].reverse()) {
        try {
          await step.compensate(input, output);
        } catch (compensationError) {
          // Log and escalate — this is a critical state inconsistency
          await this.escalate(step.name, compensationError);
        }
      }
      throw error;
    }
  }
}
```

### Why Financial AI Needs Sagas (Not Just Transactions)

Classic database transactions (ACID) don't work across agent boundaries:
- Agents may call external services (LLM API, banking core, tax engine)
- LLM calls can't be "rolled back" — the decision happened
- Cross-service consistency must be achieved through compensation

---

## Pattern 4: Agent Isolation and Failure Boundaries

### The Circuit Breaker Pattern

If the categorization agent degrades (slow, high error rate), don't let it cascade:

```typescript
class AgentCircuitBreaker {
  private failures = 0;
  private lastFailure?: Date;
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  
  async call<T>(agentFn: () => Promise<T>): Promise<T | FallbackResult> {
    if (this.state === 'open') {
      if (Date.now() - this.lastFailure!.getTime() > 60_000) {
        this.state = 'half-open';
      } else {
        return this.fallback();  // Fast-fail: route to human review
      }
    }
    
    try {
      const result = await agentFn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  private fallback(): FallbackResult {
    // Don't fail the workflow — route to human review instead
    return { 
      action: 'route_to_review', 
      reason: 'categorization_agent_circuit_open',
      confidence: 0,
    };
  }
}
```

**Key principle for Finom**: When the AI agent fails, the system should degrade gracefully to human review — not crash the whole accounting workflow.

---

## Pattern 5: Shared State and Message Passing

### Event-Driven vs Direct Call

**Direct call**: Orchestrator calls each agent synchronously. Simple, but coupling is tight.

**Event-driven**: Agents emit events, others subscribe. Loose coupling, but harder to trace.

For Finom's accounting pipeline, direct calls work best because:
1. The workflow is sequential — each stage depends on the previous
2. Traceability is critical — you need to know which agent made which decision
3. Latency matters — event queues add latency without benefit in this case

**Exception**: Async background tasks like report generation, tax filing submission, and credit score recalculation. These should be event-driven:

```typescript
// Direct call: synchronous workflow
const categorized = await categorizationAgent.categorize(extracted);

// Event-driven: async downstream processes
await eventBus.publish('transaction.categorized', {
  transactionId: tx.id,
  category: categorized.category,
  vatImpact: categorized.vatImpact,
});

// Subscribers (async, don't block main workflow):
// - ReportAggregator: updates monthly summaries
// - TaxFiling: recalculates UStVA amounts
// - CreditScoring: updates cash flow projections
// - AuditLog: records the categorization event
```

---

## Pattern 6: Testing a MAS

### The Testing Pyramid for Multi-Agent Systems

```
          ╔═════════════════════════╗
          ║  E2E workflow tests     ║  (few, slow)
          ║  Full saga, real agents ║
          ╚═════════════════════════╝
        ╔═══════════════════════════════╗
        ║  Integration tests             ║
        ║  Orchestrator + mock agents   ║
        ╚═══════════════════════════════╝
      ╔═════════════════════════════════════╗
      ║  Unit tests                          ║
      ║  Each agent independently, mock LLM ║
      ╚═════════════════════════════════════╝
```

### Key Test Scenarios

```typescript
describe('Accounting MAS', () => {
  // Unit: agent produces correct output for known input
  it('categorizer maps "GitHub" to "Software" with high confidence', async () => {
    const result = await categorizationAgent.categorize({ merchantName: 'GitHub Inc' });
    expect(result.category).toBe('4655');  // SKR03: Software subscriptions
    expect(result.confidence).toBeGreaterThan(0.9);
  });
  
  // Integration: orchestrator routes correctly on low confidence
  it('routes low-confidence categorization to human review', async () => {
    const mockCategorizer = { categorize: () => ({ category: '4655', confidence: 0.3 }) };
    const orchestrator = new WorkflowOrchestrator({ categorizer: mockCategorizer });
    const result = await orchestrator.process(testTransaction);
    expect(result.action).toBe('route_to_review');
  });
  
  // Compensation: saga rolls back on late failure
  it('compensates completed steps when booking fails', async () => {
    const mockBooker = { createBooking: () => { throw new Error('DB connection lost'); } };
    const saga = new TransactionSaga({ booker: mockBooker });
    await expect(saga.execute(testTransaction)).rejects.toThrow();
    expect(auditLog.getAbortedExtractions()).toHaveLength(1);
  });
  
  // Chaos: circuit breaker opens on repeated failures
  it('circuit breaker opens after 5 consecutive failures', async () => {
    // ... trigger 5 failures, expect fast-fail on 6th
  });
});
```

---

## Connection to Finom's Public MAS Design

From Finom's public documentation, their AI Accountant is a "distributed multi-agent system where multiple autonomous AI agents collaborate within a shared environment."

This maps to:
- **Shared environment** = the workflow state, the transaction record, and the audit trail
- **Multiple autonomous agents** = extraction, categorization, VAT, routing, booking agents
- **Collaboration** = output of each agent is input to the next, with orchestrated confidence routing

The saga pattern explains how corrections work: when a user corrects a booking, the system runs compensation for everything downstream of the categorization decision — VAT, booking, report summaries.

---

## Interview Talking Points

1. **"A MAS needs coordination, not just composition. Putting multiple agents in sequence is easy — making them consistent when one fails is the engineering challenge."**

2. **"For Finom's accounting MAS, I'd use the saga pattern for the main transaction processing flow. Direct calls are better than events there because traceability matters, but async events work for downstream side effects like report updates and credit scoring."**

3. **"The circuit breaker pattern is how you make a financial MAS production-safe. If categorization degrades, you don't want it taking down the whole accounting workflow — you want graceful degradation to human review."**

4. **"Testing a MAS requires three levels: unit tests for each agent in isolation, integration tests for the orchestrator with mock agents, and E2E tests for the full saga. The important cases are compensation behavior — does the system roll back correctly when a step fails?"**

---

## Related Files

- `code/accounting-mas-pipeline.ts` — Multi-agent orchestration implementation
- `insights/agent-safety-transaction-semantics.md` — Safety patterns (commit/rollback)
- `insights/observability-production-agents.md` — Distributed tracing across agents
- `prep/multi-agent-system-architecture-for-fintech.md` — Architecture reference
