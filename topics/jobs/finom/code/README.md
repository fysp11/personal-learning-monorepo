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

---

## Confidence Calibration Experiment

`confidence-calibration.ts` — Demonstrates the math behind confidence-based routing: ECE calculation, Platt scaling, per-market calibration, and threshold analysis.

### What it shows

- **Calibration analysis**: Bins predictions by confidence level, compares predicted vs actual accuracy
- **ECE/MCE calculation**: Expected and Maximum Calibration Error — the key metrics for trusting confidence scores
- **Platt scaling**: Post-hoc calibration that maps over-confident raw scores to calibrated probabilities
- **Per-market comparison**: Simulates DE (mature), FR (new), IT (zero-shot) with increasing calibration bias
- **Threshold analysis**: Shows how auto-book accuracy changes at different thresholds before/after calibration
- **ASCII calibration chart**: Visual reliability diagram for quick interpretation

### Run

```bash
bun run calibration
```

### Interview talking point

> "Confidence is just a number until you calibrate it. In a new market, the model may say 90% but only be right 70% of the time — that's over-confidence. Platt scaling fixes the mapping without retraining. The earned autonomy ratchet: start conservative, calibrate, then widen thresholds as trust is measured."

---

## Multi-Market Expansion Drill

`multi-market-expansion-drill.ts` — A 15-minute drill demonstrating data-driven market configuration: adding new countries without code changes.

### What it shows

- **Zod-validated market config**: Tax rates, chart of accounts, reduced rates, exemptions, invoice requirements
- **Composable tax rules**: Standard → reduced → exempt → reverse charge cascade
- **Same transaction across markets**: Shows how €100 software purchase is taxed differently in DE/FR/IT
- **Italy SDI complexity**: Market-specific post-processing hooks for electronic invoicing
- **Adding Netherlands**: Zero code changes — just one config object

### Run

```bash
bun run multi-market
```

### Interview talking point

> "Market config is data, not code. You shouldn't need a deploy to add Italy. The configuration schema validates the new market's data structure at startup — if a field is missing or a rule overlaps, validation catches it before any transaction is processed."

---

### Interview talking point (MAS Demo)

"I've worked with production multi-agent pipelines that follow this exact pattern — typed boundaries between agents, confidence propagation for quality control, circuit breaking when upstream quality drops, and end-to-end trace observability. The key insight is that the coordination layer is where reliability lives, not inside any single agent."
