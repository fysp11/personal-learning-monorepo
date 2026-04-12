# Finom — Design Patterns for Correctness-Sensitive AI Systems

## Overview

This document captures the specific design patterns that make AI systems work in financial domains. These aren't generic software patterns — they're patterns that emerge from the intersection of AI capability and correctness requirements.

---

## Pattern 1: The Confidence Threshold Cascade

### Problem

A single confidence threshold doesn't work across different decision types. Categorizing a transaction at 85% confidence might be safe; approving a credit line at 85% is reckless.

### Solution: Domain-Specific Thresholds

```typescript
interface ConfidenceThresholds {
  // Per-decision-type thresholds
  categorize: {
    autoBook: 0.95,      // Very high bar for financial posting
    autoPropose: 0.80,   // Suggest but don't auto-commit
    requireReview: 0.60,  // Human must decide
    reject: 0.00,        // Don't even suggest
  },
  
  vat: {
    autoFile: 0.99,       // Tax filing requires near-certainty
    reviewRequired: 0.85, // Edge cases need human sign-off
    reject: 0.00,
  },
  
  credit: {
    autoApprove: 0.98,    // Credit risk is high-stakes
    manualReview: 0.85,  // Underwriter decision
    autoDecline: 0.70,   // Clear rejection threshold
    noAuto: 0.00,        // Never auto-decline, always human review
  },
}

function routeDecision(decision: AgentDecision, context: DecisionContext): RoutingResult {
  const thresholds = getThresholds(decision.type);
  
  if (decision.confidence >= thresholds.autoBook) {
    return { action: 'auto_book', requiresConfirmation: false };
  } else if (decision.confidence >= thresholds.autoPropose) {
    return { action: 'propose', requiresConfirmation: true };
  } else if (decision.confidence >= thresholds.requireReview) {
    return { action: 'queue_for_review', assignTo: context.reviewer };
  } else {
    return { action: 'reject', reason: 'confidence_below_threshold' };
  }
}
```

### Why This Matters for Finom

The AI Accountant spans categorization (routine), VAT calculation (compliance-critical), and credit decisions (high-stakes). A single threshold model would either be too conservative (slowing down routine work) or too aggressive (risking compliance failures). The cascade lets the system be appropriately careful at each layer.

---

## Pattern 2: The Human-in-the-Loop Selection

### Problem

Asking humans to review everything creates fatigue and slows everything down. Asking them to review nothing creates risk.

### Solution: Intelligent Selection for Review

```typescript
interface ReviewSelector {
  // Don't review: high confidence + known category + stable market
  shouldNotReview(decision: AgentDecision): boolean {
    return decision.confidence > 0.95
        && this.isKnownCategory(decision.category)
        && this.isStableMarket(decision.market);
  }
  
  // Must review: low confidence + new category + new market
  mustReview(decision: AgentDecision): boolean {
    return decision.confidence < 0.75
        || this.isNewCategory(decision.category)
        || this.isNewMarket(decision.market);
  }
  
  // Strategic review: sample from the middle
  // 10% of medium-confidence decisions, weighted by risk
  strategicSample(decision: AgentDecision): boolean {
    if (!this.mustReview(decision) && !this.shouldNotReview(decision)) {
      // Weight by risk score: new merchant, unusual amount, anomaly pattern
      const riskScore = this.computeRiskScore(decision);
      const sampleProbability = riskScore * 0.1;  // 10% base
      return Math.random() < sampleProbability;
    }
    return false;
  }
}
```

### The Review Queue Priority

| Priority | Condition | SLA | Example |
|----------|-----------|-----|---------|
| P0 | Must review + compliance impact | < 4 hours | VAT on new category |
| P1 | Must review + financial impact | < 24 hours | Credit decision |
| P2 | Strategic sample | < 1 week | Medium confidence, known merchant |
| P3 | User-initiated | < 48 hours | User asks about specific transaction |

---

## Pattern 3: The Market Configuration Schema

### Problem

Adding a new market (France, Italy, Spain) requires different tax rules, chart of accounts, and compliance requirements. This can't be hardcoded.

### Solution: Explicit Configuration with Validation

```typescript
const MarketConfigSchema = z.object({
  marketCode: z.enum(['DE', 'FR', 'IT', 'ES', 'NL']),
  
  // Tax configuration
  taxRates: z.object({
    standard: z.number(),      // e.g., 19 (France) vs 21 (Hungary)
    reduced: z.number(),       // e.g., 10 (France) vs 5 (Germany)
    zero: z.array(z.string()), // exempt categories
  }),
  
  // Chart of accounts
  chartOfAccounts: z.object({
    code: z.string(),          // e.g., '4650' (SKR03)
    name: z.string(),          // e.g., 'Bewirtungskosten'
    vatEligible: z.boolean(),
    deductibility: z.number(), // 1.0 = 100%, 0.7 = 70%
  }).array(),
  
  // Tax form requirements
  taxForms: z.object({
    formCode: z.string(),      // e.g., 'UStVA' (Germany)
    frequency: z.enum(['monthly', 'quarterly', 'annually']),
    deadlineDays: z.number(),
    fields: z.array(z.object({
      fieldCode: z.string(),
      source: z.enum(['computed', 'manual', 'imported']),
    })),
  }).array(),
  
  // Validation rules specific to market
  validationRules: z.object({
    maxTransactionAmount: z.number(),
    requireVatIdForB2B: z.boolean(),
    reverseChargeMechanism: z.boolean(),
  }),
});

// Adding a new market = adding a config file, not code
const franceConfig: MarketConfig = {
  marketCode: 'FR',
  taxRates: { standard: 20, reduced: 10, zero: ['export', 'health', 'education'] },
  chartOfAccounts: frenchPCG,  // Plan Comptable Général
  taxForms: [{ formCode: 'CA3', frequency: 'monthly', deadlineDays: 24, ... }],
  validationRules: { maxTransactionAmount: 10000, requireVatIdForB2B: true, reverseChargeMechanism: true },
};
```

### The Validation Contract

```typescript
function validateMarketConfig(config: MarketConfig): ValidationResult {
  const errors: ValidationError[] = [];
  
  // Schema validation
  const parseResult = MarketConfigSchema.safeParse(config);
  if (!parseResult.success) {
    errors.push(...parseResult.errors);
  }
  
  // Cross-field validation
  if (config.taxRates.reduced >= config.taxRates.standard) {
    errors.push('Reduced rate must be less than standard rate');
  }
  
  // Overlap detection
  const exemptCategories = config.taxRates.zero;
  for (const category of config.chartOfAccounts) {
    if (exemptCategories.includes(category.code) && category.vatEligible) {
      errors.push(`Category ${category.code} marked VAT-eligible but also in zero-rate list`);
    }
  }
  
  return { valid: errors.length === 0, errors };
}
```

---

## Pattern 4: The Error Taxonomy with Severity Weights

### Problem

A wrong category description is annoying; a wrong VAT rate is a compliance violation. Raw accuracy hides this difference.

### Solution: Severity-Weighted Scoring

```typescript
const ErrorWeights = {
  // Low severity: wrong description, but numbers are correct
  wrong_description: {
    weight: 1,
    autoBookable: true,
    userCorrectionExpected: true,
  },
  
  // Medium severity: wrong category affecting reporting
  wrong_category: {
    weight: 3,
    autoBookable: false,
    requiresAuditReview: false,
  },
  
  // High severity: wrong VAT calculation or mechanism
  wrong_vat: {
    weight: 5,
    autoBookable: false,
    requiresAuditReview: true,
    couldTriggerTaxAuthorityIssue: true,
  },
  
  // Critical: wrong booking breaking ledger integrity
  wrong_booking: {
    weight: 10,
    autoBookable: false,
    requiresImmediateReview: true,
    causesLedgerInconsistency: true,
  },
};

function computeScore(results: EvaluationResult[]): WeightedScore {
  let totalWeight = 0;
  let errorCount = 0;
  
  for (const result of results) {
    const weight = ErrorWeights[result.errorType]?.weight ?? 1;
    totalWeight += weight;
    if (!result.correct) errorCount++;
  }
  
  return {
    rawAccuracy: (results.length - errorCount) / results.length,
    weightedErrorRate: totalWeight / results.length,
    // If weighted error rate > 0.1, fail the evaluation
    passing: (totalWeight / results.length) < 0.1,
  };
}
```

### Per-Error-Type Breakdown

| Error Type | Example | Weight | Auto-Book? | Review Required |
|------------|---------|--------|------------|-----------------|
| Wrong description | "Office supplies" vs "Supplies" | 1 | ✓ | No |
| Wrong category | "Travel" vs "Office" | 3 | ✗ | Yes |
| Wrong VAT rate | 19% vs 7% | 5 | ✗ | Audit |
| Wrong VAT mechanism | Standard vs reverse charge | 5 | ✗ | Audit |
| Wrong booking | Debit/Credit swapped | 10 | ✗ | Immediate |

---

## Pattern 5: The Staging/Commit Architecture

### Problem

AI decisions in production need to be reviewable before becoming effective. But the system also needs to know what was decided so it can be observed.

### Solution: Explicit State Machine

```typescript
enum DecisionState {
  PENDING = 'pending',           // Agent decided, not shown to user
  PROPOSED = 'proposed',         // Shown to user, awaiting confirmation
  CONFIRMED = 'confirmed',       // User confirmed, ready to execute
  COMMITTED = 'committed',       // Actually executed in ledger
  REJECTED = 'rejected',         // User rejected the decision
  ROLLED_BACK = 'rolled_back',   // Was committed, now undone
}

interface AgentDecision {
  id: string;
  state: DecisionState;
  
  // What the agent decided
  decision: {
    category: string;
    confidence: number;
    reasoning: string;
  };
  
  // State transitions
  stateHistory: Array<{
    from: DecisionState;
    to: DecisionState;
    at: Date;
    by: 'agent' | 'user' | 'system';
    reason?: string;
  }>;
  
  // For committed decisions: the actual ledger entry
  ledgerEntry?: LedgerEntry;
  
  // For rolled-back: compensation record
  compensationRecord?: CompensationRecord;
}

// State transitions
function transition(
  decision: AgentDecision,
  newState: DecisionState,
  triggeredBy: 'agent' | 'user' | 'system',
  reason?: string
): AgentDecision {
  // Validate transition is legal
  const legalTransitions: Record<DecisionState, DecisionState[]> = {
    [DecisionState.PENDING]: [DecisionState.PROPOSED, DecisionState.REJECTED],
    [DecisionState.PROPOSED]: [DecisionState.CONFIRMED, DecisionState.REJECTED],
    [DecisionState.CONFIRMED]: [DecisionState.COMMITTED, DecisionState.REJECTED],
    [DecisionState.COMMITTED]: [DecisionState.ROLLED_BACK],  // Only via compensation
    [DecisionState.REJECTED]: [],  // Terminal
    [DecisionState.ROLLED_BACK]: [],  // Terminal
  };
  
  if (!legalTransitions[decision.state].includes(newState)) {
    throw new Error(`Illegal transition from ${decision.state} to ${newState}`);
  }
  
  return {
    ...decision,
    state: newState,
    stateHistory: [
      ...decision.stateHistory,
      { from: decision.state, to: newState, at: new Date(), triggeredBy, reason }
    ],
  };
}
```

---

## Pattern 6: The MCP Tool Boundary

### Problem

Agents need to call external services (banking, tax engines, document services). Each service might have different APIs, auth requirements, and failure modes.

### Solution: MCP as the Integration Layer

```typescript
// MCP tool definition for categorization
const categorizeTool = {
  name: 'categorize_transaction',
  description: 'Categorize a transaction to the appropriate chart of accounts code',
  
  inputSchema: {
    type: 'object',
    properties: {
      transactionId: { type: 'string' },
      market: { type: 'string', enum: ['DE', 'FR', 'IT', 'ES', 'NL'] },
      amount: { type: 'number' },
      currency: { type: 'string' },
      merchantName: { type: 'string' },
      merchantCategory: { type: 'string' },  // From bank
      description: { type: 'string' },
    },
    required: ['transactionId', 'market', 'amount', 'merchantName'],
  },
  
  outputSchema: {
    type: 'object',
    properties: {
      categoryCode: { type: 'string' },
      categoryName: { type: 'string' },
      confidence: { type: 'number', minimum: 0, maximum: 1 },
      reasoning: { type: 'string' },
      alternatives: {
        type: 'array',
        items: {
          categoryCode: { type: 'string' },
          confidence: { type: 'number' },
        },
      },
    },
  },
};

// MCP tool definition for VAT calculation (deterministic)
const calculateVatTool = {
  name: 'calculate_vat',
  description: 'Calculate VAT for a transaction given category and market',
  
  inputSchema: {
    type: 'object',
    properties: {
      market: { type: 'string', enum: ['DE', 'FR', 'IT', 'ES', 'NL'] },
      categoryCode: { type: 'string' },
      amount: { type: 'number' },
      isB2B: { type: 'boolean' },
      counterpartyVatId: { type: 'string' },
    },
    required: ['market', 'categoryCode', 'amount'],
  },
  
  outputSchema: {
    type: 'object',
    properties: {
      vatRate: { type: 'number' },
      vatAmount: { type: 'number' },
      netAmount: { type: 'number' },
      mechanism: { 
        type: 'string', 
        enum: ['standard', 'reduced', 'exempt', 'reverse_charge', 'no_vat'] 
      },
    },
  },
};

// The agent workflow
async function processTransaction(tx: Transaction): Promise<AgentWorkflowResult> {
  // 1. AI decides category (not deterministic, can be wrong)
  const categoryResult = await mcpClient.callTool('categorize_transaction', {
    transactionId: tx.id,
    market: tx.market,
    amount: tx.amount,
    merchantName: tx.merchant,
    // ... etc
  });
  
  // 2. System calculates VAT (deterministic, correctness required)
  const vatResult = await mcpClient.callTool('calculate_vat', {
    market: tx.market,
    categoryCode: categoryResult.categoryCode,
    amount: tx.amount,
    isB2B: tx.isB2B,
  });
  
  // 3. System creates booking (deterministic)
  const bookingResult = await mcpClient.callTool('create_booking', {
    transactionId: tx.id,
    category: categoryResult.categoryCode,
    vat: vatResult,
  });
  
  // Route based on confidence
  if (categoryResult.confidence >= 0.95) {
    return { action: 'auto_book', ... };
  } else if (categoryResult.confidence >= 0.80) {
    return { action: 'propose', ... };
  } else {
    return { action: 'require_review', ... };
  }
}
```

---

## Pattern 7: The Evasion Detection Pattern

### Problem

Agents might "hallucinate" non-existent merchants, accounts, or categories, especially in edge cases where the training data is thin.

### Solution: Strict Validation Against Known Entities

```typescript
interface EvasionDetector {
  // Check if category actually exists in this market's chart of accounts
  validateCategory(categoryCode: string, market: string): ValidationResult {
    const chart = getChartOfAccounts(market);
    const exists = chart.some(c => c.code === categoryCode);
    return {
      valid: exists,
      error: exists ? null : `Category ${categoryCode} does not exist in ${market} chart of accounts`,
    };
  }
  
  // Check if merchant is a known entity in the database
  validateMerchant(merchantName: string): ValidationResult {
    const merchant = this.merchantDb.find(m => normalize(m.name) === normalize(merchantName));
    return {
      valid: true,  // Unknown merchants are OK, just flag them
      flags: merchant ? [] : ['unknown_merchant'],
    };
  }
  
  // Check if amount is within reasonable range for category
  validateAmount(categoryCode: string, amount: number, market: string): ValidationResult {
    const category = getCategory(categoryCode, market);
    if (!category) return { valid: false, error: 'unknown_category' };
    
    const typicalMax = category.typicalMaxAmount ?? amount * 10;
    if (amount > typicalMax) {
      return {
        valid: true,
        flags: ['unusual_amount_for_category'],
        warnings: [`${amount} exceeds typical max ${typicalMax} for ${categoryCode}`],
      };
    }
    return { valid: true };
  }
}

// Before accepting agent decision, run through detector
function validateDecision(decision: AgentDecision, tx: Transaction): ValidationResult {
  const checks = [
    detector.validateCategory(decision.categoryCode, tx.market),
    detector.validateMerchant(tx.merchantName),
    detector.validateAmount(decision.categoryCode, tx.amount, tx.market),
  ];
  
  const failures = checks.filter(c => !c.valid);
  const warnings = checks.flatMap(c => c.warnings ?? []);
  const flags = checks.flatMap(c => c.flags ?? []);
  
  if (failures.length > 0) {
    return { valid: false, errors: failures.map(f => f.error), warnings, flags };
  }
  
  // Even if valid, flag for review if warnings or flags
  if (warnings.length > 0 || flags.length > 0) {
    return { valid: true, requiresReview: true, warnings, flags };
  }
  
  return { valid: true };
}
```

---

## Summary: Pattern to Architecture Mapping

| Pattern | Solves | Finom Application |
|---------|--------|-------------------|
| Confidence Threshold Cascade | Different risk levels per decision type | Categorization vs VAT vs Credit |
| Human-in-the-Loop Selection | Review fatigue vs risk | Strategic sampling for review |
| Market Configuration Schema | Scaling across EU markets | Adding France, Italy, Spain |
| Error Taxonomy with Severity Weights | Raw accuracy hides critical errors | Weighted evaluation framework |
| Staging/Commit Architecture | Production safety for AI decisions | PENDING → PROPOSED → COMMITTED |
| MCP Tool Boundary | Language-agnostic service integration | C# core + Python AI |
| Evasion Detection | Hallucination in edge cases | Category/merchant validation |

---

## Related Files

- `code/accounting-mas-pipeline.ts` — Multi-agent orchestration
- `code/mcp-accounting-server.ts` — MCP implementation
- `code/eval-harness.ts` — Severity-weighted evaluation
- `insights/mcp-architecture-study.md` — Architecture deep dive
- `insights/agent-safety-transaction-semantics.md` — Safety patterns