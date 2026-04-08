# Finom Code Examples

## Multi-Agent System (MAS) Coordination Demo

`accounting-mas-pipeline.ts` — Demonstrates the orchestration and coordination patterns for a distributed multi-agent accounting system matching Finom's public AI Accountant architecture.

### What it shows

- **Typed agent boundaries**: Each agent (classification, extraction, reconciliation, categorization) has explicit input/output contracts via Zod schemas
- **Confidence propagation**: Agents return confidence levels (high/medium/low) that propagate through the pipeline
- **Circuit breaking**: The orchestrator halts processing when upstream confidence drops below threshold
- **Escalation routing**: Low-confidence cases route to human review instead of auto-completing
- **End-to-end observability**: WorkflowTrace captures per-agent timing, confidence, and events with correlation IDs

### What it does NOT show

- LLM calls — this is a structural demo, not an AI demo
- Production error handling, retry logic, or persistence
- Real document processing or OCR

### Why this architecture

Finom publicly describes its AI Accountant as a "distributed AI multi-agent system (MAS) that consists of multiple autonomous AI agents that collaborate within a shared environment." This demo makes the coordination layer concrete and discussable.

### Run

```bash
cd /Users/fysp/personal/learning/topics/jobs/finom/code
bun install
bun run demo
```

### Expected output

```
=== Accounting MAS Pipeline Demo ===

Processing 3 documents...

--- Document DOC-001 (invoice) ---
  Status: completed
  Agents: 4
  Reconciliation: exact (score=1)
  Category: Betriebsausgabe / Vorsteuerabzug (high)

--- Document DOC-002 (receipt) ---
  Status: completed
  Agents: 4
  Reconciliation: unmatched (score=0)

--- Document DOC-003 (invoice) ---
  Status: escalated
  Reason: Extraction confidence too low for automated processing
  Agents: 2

=== Pipeline Demo Complete ===
```

### Interview talking point

"I've worked with production multi-agent pipelines that follow this exact pattern — typed boundaries between agents, confidence propagation for quality control, circuit breaking when upstream quality drops, and end-to-end trace observability. The key insight is that the coordination layer is where reliability lives, not inside any single agent."

---

## Fraud Detection Overlay

`fraud-detection-overlay.ts` — Demonstrates fraud detection as a cross-cutting concern that integrates with the MAS accounting pipeline. Not a separate system — an overlay that scores every transaction for risk.

### What it shows

- **Behavioral baselines**: Per-customer profiles (spending patterns, known counterparties, typical categories)
- **Multi-signal anomaly scoring**: Amount z-scores, new counterparties, unusual categories, velocity checks
- **Rule + ML hybrid**: Rules engine for known patterns (AML thresholds, structuring, velocity) + statistical scoring for novel anomalies
- **Risk-based routing**: 5-tier routing (clear / monitor / flag / hold / block) that minimizes customer friction
- **Portfolio monitoring**: Aggregate risk dashboard across all assessed transactions
- **Explainable decisions**: Every assessment generates a human-readable explanation (required for compliance)

### Run

```bash
bun run fraud
```

### Five test scenarios

1. **Normal transaction** → clear, no signals
2. **Large unusual transaction** → flagged (amount anomaly + new counterparty + unusual category)
3. **Near AML threshold** → flagged (proximity to reporting threshold + round amount)
4. **New account + large round amount** → held (new account risk + amount anomaly)
5. **Structuring attempt** → flagged (multiple round amounts in short window)

### Interview talking point

"Fraud detection should be a cross-cutting overlay on the existing MAS, not a separate system. Every agent already emits confidence signals — fraud risk is another signal in that same framework. The key is a hybrid approach: rules for known patterns (AML, velocity, structuring), statistical scoring for novel anomalies, and risk routing that minimizes false positive impact on legitimate customers."
