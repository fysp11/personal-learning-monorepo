# Interview Drill — Sync to Async Refactor (10-15 min)

## 1) Scope sentence (30s)

"I will preserve the same public API and only refactor execution from blocking sync to bounded async concurrency."

## 2) Architecture split (60s)

- AI step: categorization (ambiguous text)
- Deterministic control: API contract, routing field, error shape, concurrency cap

## 3) Refactor walk-through (3-4 min)

1. Keep `contracts.py` shared (no API drift)
2. Sync baseline uses sequential batch processing
3. Async version uses `asyncio.gather` + semaphore (`max_concurrency`)
4. Keep identical endpoint paths and payloads

## 4) Risk controls (2 min)

- Typed per-item error in batch responses
- Single-request 502 with structured error body
- No silent hangs, explicit completion semantics

## 5) Evidence callout (2 min)

- Contract parity tests pass
- Latency test shows async materially faster than sync under delayed mock AI
- Failure path tests show controlled behavior under 100% upstream failure

## 6) Finom-specific anchor (30s)

"This directly addresses the Interview 3 concern about synchronous per-transaction model calls causing latency and review pressure at scale."
