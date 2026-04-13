# Interview 3 Proposal — Python Sync→Async API Refactor Pack

Saved: 2026-04-12

## Purpose

Create a compact, runnable interview-prep pack that demonstrates a concrete refactor from a **bad sync AI REST API** to a **good async API** while preserving the **same external API contract**.

This aligns with Interview 3 signals:
- latency/cost/trust discipline over demo speed
- staged workflow thinking
- deterministic controls around AI steps
- measurable operational leverage

Grounded references:
- `interviews/3-lead-ai-engineer/README.md`
- `prep/3-technical-answer-bank.md`
- `prep/3-lead-ai-hostile-followups.md`
- `prep/3-live-round-scenarios.md`

---

## Problem Framing

At Finom-scale volume, a sync per-transaction AI call path creates avoidable pain:
- **Latency**: sequential model calls multiply end-to-end response time
- **Cost pressure**: retry spikes and blocked workers increase infra overhead
- **Trust risk**: timeouts and opaque failures push bad fallback behavior into user workflows

Interview framing from prep materials is explicit: avoid synchronous per-transaction bottlenecks; use async/batching where possible; keep behavior observable and controllable.

---

## Contract Invariance Rule

The sync and async implementations must expose the exact same public contract:
- `GET /health`
- `POST /categorize`
- `POST /categorize/batch`

Shared schemas:
- `CategorizeRequest`
- `BatchCategorizeRequest`
- `CategoryResult`
- `BatchCategorizeResponse`
- `ErrorResponse`

Non-negotiable rule:
> Refactor execution model, not the API shape.

---

## Refactor Map (Before → After)

1. Blocking single call
- Before: `adapter.categorize_sync(...)`
- After: `await adapter.categorize_async(...)`

2. Sequential batch loop
- Before: `for item in batch: sync_call(item)`
- After: bounded concurrent fan-out with semaphore + `asyncio.gather`

3. Implicit failure behavior
- Before: mixed, often opaque handling
- After: explicit `ErrorResponse` and structured per-item batch errors

4. Latency hidden in implementation
- Before: no measurable contrast
- After: testable latency profile proving async throughput gain

---

## Interview Talk Track Anchors

Use these verbal anchors during live coding:
- **Latency**: "Sequential per-item model calls make throughput collapse under batch load."
- **Cost**: "Bounded concurrency reduces idle wait and improves worker utilization without unbounded fan-out."
- **Trust**: "Errors are explicit and typed; no silent hangs, no implicit behavior."
- **Calibration/Routing**: "Execution is async, but confidence/routing semantics remain deterministic and testable."
- **Deterministic boundaries**: "AI does ambiguous categorization; policy and control stay in code and contracts."

---

## Deliverables

Code pack location:
`topics/jobs/finom/code/python-sync-async-refactor/`

Includes:
- runnable sync and async FastAPI implementations
- shared contracts
- deterministic mock AI adapter
- contract parity tests
- batch behavior tests
- latency profile tests
- failure-path tests
- interview drill and diff map docs

---

## Acceptance Evidence Plan

Execution uses `uv` only:
- `uv sync`
- `uv run pytest -q`
- `uv run python -m compileall .`
- self-check scripts for both APIs

Completion evidence file:
`prep/proposals/3-sync-async-python-refactor-evidence.md`

Must include:
- exact commands
- pass/fail test summary
- measured sync vs async timings
- contract parity statement and references
- limitations and extension path
