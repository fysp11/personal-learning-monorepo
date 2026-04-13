# Sync→Async Python Refactor — Completion Evidence

Saved: 2026-04-12

## Timestamp + Environment

- UTC timestamp: `2026-04-12T23:23:58Z`
- Working directory: `/Users/fysp/personal/learning/topics/jobs/finom/code/python-sync-async-refactor`
- Python runtime: `Python 3.12.12`
- Dependency/runtime manager: `uv`

## Exact Commands Run

1. `uv sync`
2. `uv run pytest -q`
3. `uv run python -m compileall .`
4. `uv run python bad_sync_api.py --self-check`
5. `uv run python good_async_api.py --self-check`
6. `uv run pytest -q tests/test_contract_parity.py`
7. `uv run pytest -q tests/test_latency_profile.py`
8. Timing measurement script (uv-run inline Python) for sync vs async elapsed time on 20 items @ 40ms/mock-call

## Test Summary

- Full suite: `uv run pytest -q` -> `6 passed`
- Contract parity subset: `tests/test_contract_parity.py` -> `1 passed`
- Latency profile subset: `tests/test_latency_profile.py` -> `1 passed`
- Self-check scripts:
  - `bad_sync_api.py --self-check` -> `OK`
  - `good_async_api.py --self-check` -> `OK`
- Compile check: `python -m compileall .` -> success

## Measured Sync vs Async Batch Timings

Measurement setup:
- Batch size: 20
- Mock adapter delay: 40ms per item
- Async max concurrency: 5

Observed:
- `sync_elapsed_ms=863.75`
- `async_elapsed_ms=164.26`
- `speedup_ratio=5.26`
- `sync_success=20`
- `async_success=20`

Interpretation:
- Async implementation is materially faster than sync for delayed batched categorization while preserving success outcomes.

## Contract Parity Statement

Contract parity is enforced by shared models in `contracts.py` and validated in `tests/test_contract_parity.py` for:
- `GET /health`
- `POST /categorize`
- `POST /categorize/batch`

Evidence points:
- same endpoint paths
- same top-level response key sets
- shared model validation for both implementations
- stable item ordering in batch responses

## Known Limitations

1. AI integration is mocked (deterministic adapter), not a real provider.
2. Latency profile uses synthetic sleep-based delay, not network/LLM API latency.
3. Compile command targets `.` and includes `.venv`, which is noisier than app-only compile.

## Reflect

### 1) Architectural changes

- Removed sync anti-patterns from batch path:
  - sequential blocking AI calls -> bounded async concurrency (`asyncio.gather` + semaphore)
- Preserved external API contract while changing internals.
- Kept deterministic control surfaces:
  - shared typed contracts
  - explicit structured error paths
  - per-item batch outcome semantics

### 2) Why this matters for Interview 3 scoring

- Demonstrates decomposition quality: contract layer, adapter layer, API layer, verification layer.
- Demonstrates deterministic boundaries: AI behavior behind a controlled interface, policy/error semantics in code.
- Demonstrates measurable leverage: objective sync vs async latency evidence, not just claims.

### 3) Next extensions

- Add optional real provider adapter behind same interface (env-gated).
- Add calibration hooks and routing threshold telemetry per market.
- Add queue-backed async worker mode for high-volume batch offloading.
