# Diff Map — Sync Bad Example -> Async Good Example

| Sync anti-pattern | Async refactor | Interview relevance |
|---|---|---|
| Blocking per-request categorization call | `await` async categorization call | Shows clear AI-boundary execution control |
| Sequential `for` loop for batch | `asyncio.gather` with semaphore cap | Direct latency/throughput improvement |
| No concurrency policy | Explicit `max_concurrency` boundary | Prevents unbounded fan-out under load |
| Implicit/opaque failures | Typed `ErrorResponse` and per-item batch errors | Trust and debuggability in compliance workflows |
| Performance claims without proof | Latency test comparing sync vs async | Evidence-based engineering, not hand-waving |
| Refactor risk of API drift | Shared contracts used by both versions | Safe migration path for existing clients |
