# Agent Safety Harness — Transactional Agent Architecture

A proof-of-concept implementation of the commit/rollback pattern for agentic workflows,
inspired by the Delphyr interview discussion about safety in clinical AI systems.

## Core Concept
Agent actions are treated like database transactions:
- **STAGED**: Action proposed but not executed
- **COMMITTED**: Action approved and executed
- **ROLLED_BACK**: Action rejected or reversed

Routing is confidence-based:
- High confidence (>0.95): Auto-commit with audit log
- Medium confidence (0.70-0.95): Queue for human review
- Low confidence (<0.70): Auto-reject with reasoning

## Setup
```bash
cd topics/jobs/delphyr/experiments/agent-safety-harness
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
# Run the demo MDT preparation scenario
python -m safety_harness.demo

# Run tests
python -m pytest tests/
```

## Key Design Decisions
1. **Actions are staged before execution** — nothing is irreversible until committed
2. **Confidence scoring drives routing** — the system knows what it doesn't know
3. **Full audit trail** — every action, decision, and outcome is logged
4. **Cascading rollback** — if a downstream action fails, upstream actions can be reversed
5. **Clinical context** — the demo simulates MDT meeting preparation with mock patient data
