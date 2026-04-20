# Python Sync→Async Refactor Pack (Interview 3)

A runnable drill for Finom Interview 3 showing a refactor from a **bad sync AI REST API** to a **good async API** with the **same public contract**.

Grounded references:
- `../../interviews/3-lead-ai-engineer/README.md`
- `../../prep/3-technical-answer-bank.md`
- `../../prep/3-lead-ai-hostile-followups.md`
- `../../prep/3-live-round-scenarios.md`

## What this demonstrates

- Same external API contract in both versions
- Sync anti-pattern: sequential per-item AI calls
- Async refactor: bounded concurrency for batch throughput
- Deterministic, interview-safe mock adapter
- Typed errors and explicit batch failure representation

## Files

- `contracts.py` — shared request/response models
- `mock_ai_adapter.py` — deterministic sync/async categorizer mock
- `bad_sync_api.py` — sync baseline (sequential batch)
- `good_async_api.py` — async refactor (bounded concurrent batch)
- `tests/` — contract parity, batch behavior, latency profile, failure paths
- `DIFF_MAP.md` — anti-pattern -> refactor mapping
- `INTERVIEW_DRILL.md` — short live-round talk track
- `EXPLANATION.md` — full narrative explanation focused on why async reduces time cost

## Public API (identical both versions)

- `GET /health`
- `POST /categorize`
- `POST /categorize/batch`

## Setup and verification (`uv` only)

```bash
cd /Users/fysp/personal/learning/topics/ai-engineering/code/python-sync-async-refactor
uv sync
uv run pytest -q
uv run python -m compileall .
```

Behavior checks:

```bash
uv run python bad_sync_api.py --self-check
uv run python good_async_api.py --self-check
```

Visible demo mode:

```bash
uv run python bad_sync_api.py --demo
uv run python good_async_api.py --demo
```

Optional local run:

```bash
uv run python bad_sync_api.py --port 8001
uv run python good_async_api.py --port 8002
```

## Interview anchor line

> "I kept contract parity and changed only execution strategy: sync sequential batch became bounded async concurrency, which cuts latency without changing client integration."
