# Finom Code Examples

## 1. Multi-Agent System (MAS) Coordination Demo

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
bun run demo
```

### Interview talking point

"I've worked with production multi-agent pipelines that follow this exact pattern — typed boundaries between agents, confidence propagation for quality control, circuit breaking when upstream quality drops, and end-to-end trace observability. The key insight is that the coordination layer is where reliability lives, not inside any single agent."

---

## 2. Live Round Rehearsal

`live-round-rehearsal.ts` — A compact, self-contained orchestrator for the interview live-coding warm-up.

### What it shows

- **Deterministic vs AI split**: VAT calculation is deterministic; categorization simulates AI
- **Market configuration**: Germany (SKR03) and France (PCG) with different account codes and VAT rates
- **Confidence-based routing**: auto-book / propose / reject based on confidence thresholds
- **Proposal mode**: medium-confidence cases produce structured proposals for human approval
- **Trace per stage**: every stage logs its decision and duration

### Run

```bash
bun run rehearsal
```

---

## 3. Evaluation Harness

`eval-harness.ts` — Production-grade evaluation framework for financial agent accuracy.

### What it shows

- **Field-level accuracy**: per-field comparison (account code, VAT rate, amounts, mechanism)
- **Severity-weighted scoring**: critical errors (wrong VAT, missed reverse charge) weigh 4x more than low-severity
- **Per-market breakdown**: separate accuracy metrics for DE and FR
- **Confidence calibration**: Expected Calibration Error (ECE) measuring whether confidence scores are trustworthy
- **Realistic failure modes**: simulated agent that misses reverse charge and mixed-VAT cases

### Why this matters

Before any categorization agent goes to production, you need to know: Is it accurate enough? Are its confidence scores calibrated? Where does it fail? This harness answers all three.

### Test cases cover

| Case | Severity | What it tests |
|------|----------|---------------|
| Standard office supplies (DE) | Low | Happy path |
| SaaS subscription (DE) | Low | Software category matching |
| Reverse charge B2B (DE) | Critical | Cross-border VAT mechanism |
| Train ticket (FR) | Medium | French reduced VAT rate |
| Business dinner (DE) | Low | Entertainment categorization |
| Mixed VAT receipt (DE) | High | Multi-rate handling |
| Mobile plan (FR) | Low | French telecom |
| Kleinunternehmer §19 (DE) | Critical | VAT exemption detection |

### Run

```bash
bun run eval
```

### Interview talking point

"I always build severity-weighted evaluation before trusting any agent in production. Raw accuracy hides the difference between a wrong description and a wrong VAT rate — but in compliance, that difference is everything. Calibration tells us whether the confidence scores are actually useful for routing decisions."
