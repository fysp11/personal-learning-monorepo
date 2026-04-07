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
