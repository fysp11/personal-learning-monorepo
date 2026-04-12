# Finom — Mental Models for AI Engineering Discussions

## The Meta-Principle

Technical architecture is easier to explain than **why** that architecture. Interviewers at this level don't just want to know "what" — they want to understand your decision-making framework.

This document provides the mental models for explaining Finom-relevant architectural choices in a way that demonstrates engineering judgment, not just implementation knowledge.

---

## Mental Model 1: "Earned Trust, Not Feature Flags"

### The Framework

```
FEATURE FLAG           vs           EARNED TRUST
─────────────────────────────────────────────────────────────
Product decision                  Measurement decision
Toggle on/off                     Gradual ramp based on data
One-dimensional                   Multi-dimensional (accuracy, 
                                   calibration, latency, safety)
```

### How to Explain It

> "When I think about promoting an agent from 'propose' to 'auto-book,' I don't think of it as a feature toggle. I think of it as a measurement exercise. The agent has earned trust when three conditions are met: its accuracy exceeds the threshold, its confidence scores are calibrated (it says 90% and is right 90%), and its failure modes are documented. That's not a product decision — it's a data decision."

### Why This Matters for Finom

Finom runs production AI in a compliance-critical domain. The difference between a feature flag and earned trust is the difference between:
- "We're comfortable enough to turn this on"
- "The data proves we should turn this on"

---

## Mental Model 2: "The Separation of Concerns Is the Architecture"

### The Framework

```
WHAT IS AI           │  WHAT IS DETERMINISTIC
─────────────────────────────────────────────────────────────
Categorization       │  VAT calculation (19%, 7%, exempt, reverse charge)
Interpretation       │  Double-entry booking (debit = credit)
Prediction          │  Compliance rule enforcement
Soft constraints    │  Hard constraints
```

### How to Explain It

> "My first question for any financial AI system is: what's the boundary between what the AI decides and what the system enforces? At Finom, the AI categorizes — suggests which SKR03 account fits the transaction. The system calculates VAT — applies the deterministic rules. The AI might be uncertain about whether this is 'Travel' or 'Office Supplies,' but there's no uncertainty about what 19% of €100 is. That boundary is the architecture. Everything else follows from it."

### Why This Matters

This mental model shows you understand:
- Where to invest in AI quality (categorization)
- Where to invest in correctness (VAT, booking)
- How to reason about error modes (AI errors vs system errors)

---

## Mental Model 3: "The Market Config Is Data, Not Code"

### The Framework

```
TRADITIONAL                      DATA-DRIVEN
─────────────────────────────────────────────────────────────
Add market = add if/else         Add market = add config
Deploy code = risk              Deploy config = low-risk
Specialist knows rules          Rules are explicit in data
Manual test each market         Schema validation catches issues
```

### How to Explain It

> "If you need to deploy code to add Italy, you're doing it wrong. The market configuration — tax rates, chart of accounts, reduced VAT rates, exemption rules, invoice formats — should be data. The system loads it at startup, validates the schema, and applies it. Adding a new market is adding a JSON file, not changing the pipeline. That shifts the risk from 'will the code work' to 'is the data complete and valid.'"

### Why This Matters for Finom

Finom is expanding across Europe. The ability to scale from Germany to France to Italy without rewriting the pipeline is a competitive advantage. This mental model shows you understand operational scaling, not just technical implementation.

---

## Mental Model 4: "Calibration Is the Hidden Metric"

### The Framework

```
ACCURACY                  vs              CALIBRATION
─────────────────────────────────────────────────────────────
"What % got right"                      "When it says 90%, 
                                        what % is actually right"
                                         
Often misleading in                    The actual metric for
new markets or                         routing decisions and
edge cases                              autonomy promotion

Good for "how am I doing"             Good for "can I trust
                                      this decision"
```

### How to Explain It

> "Accuracy is the vanity metric. Calibration is the utility metric. In a new market, your model might be 85% accurate — but what does '85% confident' actually mean? If it's only right 70% of the time when it says 90%, you're over-confident. That's dangerous because you're auto-routing decisions that should be flagged. I always measure Expected Calibration Error (ECE), not just accuracy. That's the difference between 'the model works' and 'the routing decisions are safe.'"

### Real Example

```
Market: Germany (mature)
  Model confidence: 87%
  Actual accuracy: 85%
  Calibration error: 2% → OK to auto-route

Market: France (new)
  Model confidence: 87%  
  Actual accuracy: 72%
  Calibration error: 15% → NOT OK, downgrade to human review
```

---

## Mental Model 5: "Compensation Chains, Not Rollbacks"

### The Framework

```
SIMPLE ROLLBACK                  vs         COMPENSATION CHAIN
────────────────────────────────────────────────────────────────
Undo the action                       Create an action that 
                                       undoes the effect
Single operation                      Cascade across related 
                                       systems (VAT, ledger, 
                                       reports, credit)
```

### How to Explain It

> "People say 'just rollback' but in financial systems there's no simple rollback. If the agent categorized a transaction incorrectly, VAT might be wrong, the booking is wrong, the monthly report is wrong, and the cash flow analysis is wrong. You can't just 'undo' — you have to compensate. That's a new action that reverses the downstream effects. The system needs to track what would cascade, validate the compensation is possible, and execute in the right order. That's compensation chains, not rollbacks."

### Finom Application

```
User corrects: "This restaurant was a business dinner (70% deductible), 
               not a regular meal (100% deductible)"

Compensation chain:
  1. Recalculate VAT (different rate applies)
  2. Reverse booking, create new booking with correct category
  3. Recalculate monthly totals (UStVA changes)
  4. Flag for credit decision review (cash flow projection changed)
  5. Log audit trail of what changed and why
```

---

## Mental Model 6: "The Agent Is a Contract, Not a Black Box"

### The Framework

```
BLACK BOX                     vs         CONTRACT
────────────────────────────────────────────────────────────────
LLM decides everything                  Explicit input/output schema
Hard to test                             Unit-testable at boundaries
Mysterious failure modes                 Enumerated failure modes
Unstructured output                      Structured, typed output
```

### How to Explain It

> "The agent is the interface between AI capability and production reliability. That means it's a contract, not a black box. The contract is: given this input (transaction, history, market context), produce this output (category, confidence, reasoning). The contract is testable — run 1000 transactions through it, measure accuracy. The contract is monitorable — if outputs drift from the schema, alert. The contract is replaceable — swap the LLM underneath without changing the pipeline. If your agent doesn't have a contract, you don't have an architecture, you have a prototype."

---

## Mental Model 7: "Observability Is the Ability to Ask Questions After the Fact"

### The Framework

```
MONITORING                     vs         OBSERVABILITY
────────────────────────────────────────────────────────────────
Did it work?                               Why did it work that way?
Was it up?                                 What did it actually do?
Key metrics                                Full trace + context
```

### How to Explain It

> "Monitoring tells you the system is up. Observability lets you ask questions you didn't anticipate. For a financial agent, that matters because the failure mode might be subtle — it categorized something correctly but the reasoning was wrong. The correction takes weeks to surface (when tax filing is rejected). You need to be able to reconstruct what the agent saw, what it decided, and why. That's not monitoring — that's observability. It means capturing traces, not just metrics."

---

## Applying These in Interviews

### When Asked "How Would You Design X?"

1. Identify which mental model applies
2. State the model first ("My first principle is...")
3. Show how it constrains the design
4. Give a concrete example

### When Asked "Why This Way?"

1. Acknowledge alternatives existed
2. Explain what the trade-off was
3. Show why your choice favors correctness over velocity
4. Acknowledge what you might revisit

### When Asked "What Could Go Wrong?"

1. Choose failure modes relevant to the domain
2. Show you've thought in compensation chains, not single failures
3. Connect to the confidence routing architecture

---

## Summary: The Finom Mental Model Stack

| Mental Model | Core Insight |
|--------------|--------------|
| Earned Trust | It's a measurement decision, not a product decision |
| Separation of Concerns | AI decides what; system enforces what |
| Market Config Is Data | Rules are explicit, not embedded in code |
| Calibration Is Hidden | Accuracy is vanity, calibration is utility |
| Compensation Chains | Not rollback, but cascade-aware undo |
| Agent as Contract | Interfaces, not implementations |
| Observability | Ability to ask questions after the fact |

---

## Related Files

- `insights/mcp-architecture-study.md` — Technical architecture
- `insights/agent-safety-transaction-semantics.md` — Safety patterns
- `insights/observability-production-agents.md` — Production monitoring
- `code/confidence-calibration.ts` — Calibration implementation
- `code/eval-harness.ts` — Evaluation framework