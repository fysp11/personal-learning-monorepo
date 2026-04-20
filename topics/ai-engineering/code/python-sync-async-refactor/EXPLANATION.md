# Python Sync→Async Refactor Pack Explained

This pack is a small interview drill for showing how to transform a **bad synchronous AI REST API** into a **good asynchronous API** without changing the public contract.

The point is not to show off framework knowledge. The point is to demonstrate:
- where the AI belongs
- where deterministic code belongs
- how to preserve API compatibility during a refactor
- why the time cost improves when independent work is allowed to overlap
- how to make the behavior visible in a demo

## What Problem This Solves

In a sync implementation, each categorization request blocks until the mock AI call finishes. That is acceptable for one request, but it becomes inefficient for batch processing because every item waits on the previous one.

At Interview 3 scale, the concern is not just correctness. It is:
- latency
- cost
- trust
- controlled failure handling

The key performance idea is simple:

> If tasks are independent, sequential waiting is wasted time. Async reduces total wall-clock time by overlapping those waits.

That is the main topic of this pack.

The async refactor addresses those concerns by keeping the same endpoints and response shapes while changing only the execution strategy.

## Public Contract

Both implementations expose the same API:
- `GET /health`
- `POST /categorize`
- `POST /categorize/batch`

The shared request and response models live in `contracts.py`:
- `CategorizeRequest`
- `BatchCategorizeRequest`
- `CategoryResult`
- `BatchCategorizeResponse`
- `ErrorResponse`

That contract parity matters because it means the client integration does not change when the execution model changes.

## The Bad Sync Version

File: `bad_sync_api.py`

This version is intentionally simple and intentionally bad for batch throughput.

What it does:
- processes batch items in a plain `for` loop
- calls the adapter synchronously for each item
- waits for each item to finish before starting the next one
- returns typed results, but only after all blocking work is done

Why it is a bad example:
- it makes batch latency grow linearly with batch size
- it does not use concurrency even when the tasks are independent
- it is the kind of code that becomes painful at higher throughput

The sync version is useful because it gives you a clean before/after story in the interview.

## The Good Async Version

File: `good_async_api.py`

This version keeps the same public contract but changes the execution model.

What it does:
- uses `async def` endpoints
- awaits the adapter instead of blocking on it
- processes batch items concurrently with `asyncio.gather`
- caps concurrency with a semaphore
- keeps errors typed and explicit

Why this is better:
- batch requests finish faster
- concurrency is bounded, so you avoid unbounded fan-out
- the same API still works for clients
- the behavior is easier to explain and test

The async version is not “more clever.” It is more appropriate for independent, delay-heavy operations.

## The Mock AI Adapter

File: `mock_ai_adapter.py`

This adapter is deterministic and interview-safe.

It exists to simulate an AI dependency without requiring:
- external credentials
- network access
- nondeterministic model output

What it provides:
- sync method: `categorize_sync()`
- async method: `categorize_async()`
- configurable artificial delay
- deterministic failure mode

The adapter returns predictable categories, confidence, routing, and rationale based on merchant text.

That lets the demo show behavior clearly:
- GitHub-like merchants map to software
- restaurant-like merchants map to proposal-zone categories
- AWS Ireland-like merchants map to review-worthy cross-border behavior

## Why Demo Mode Exists

The first version of the scripts passed self-checks but did not print much visible output. That made them less useful as a live demo.

Demo mode fixes that.

Run:
```bash
uv run python bad_sync_api.py --demo
uv run python good_async_api.py --demo
```

What the demo prints:
- the input batch
- the single-item result
- the full batch result
- elapsed time in milliseconds

That makes the sync-vs-async difference visible immediately.

## Why The Timing Difference Matters

The batch timing is the strongest proof in the pack.

Because the adapter sleeps per item, the sync version processes three items sequentially, while the async version processes them concurrently with a cap.

That means the async version shows:
- lower elapsed time
- the same business result
- the same response contract

Why the improvement happens:
- In the sync version, each request blocks the thread until its fake AI call finishes.
- In the batch path, that means item 2 cannot start until item 1 is done, and item 3 cannot start until item 2 is done.
- Total time becomes roughly the sum of all item waits.
- In the async version, the event loop can start multiple independent waits together.
- Total time becomes closer to the slowest group of waits, not the sum of every wait.
- The semaphore keeps the improvement safe by bounding concurrency instead of creating unlimited parallelism.

This is the right kind of evidence for Interview 3 because it is measurable, concrete, and easy to explain.

## Tests

The test suite covers four things:

1. Contract parity
- Both implementations return the same top-level response shapes.

2. Batch behavior
- Items preserve input order.
- Batch counts are correct.

3. Latency profile
- Async batch processing is materially faster under simulated delay.

4. Failure paths
- Upstream failures return controlled errors.
- The workflow does not hang.

## How To Run It

From anywhere:
```bash
(cd topics/ai-engineering/code/python-sync-async-refactor && uv sync && uv run pytest -q)
```

To see visible output:
```bash
(cd topics/ai-engineering/code/python-sync-async-refactor && uv run python bad_sync_api.py --demo)
```

```bash
(cd topics/ai-engineering/code/python-sync-async-refactor && uv run python good_async_api.py --demo)
```

To run the API servers:
```bash
(cd topics/ai-engineering/code/python-sync-async-refactor && uv run python bad_sync_api.py --port 8001)
```

```bash
(cd topics/ai-engineering/code/python-sync-async-refactor && uv run python good_async_api.py --port 8002)
```

## Interview Talk Track

Use this explanation in the live round:

> I kept the external contract stable and changed only the execution model. The sync version blocks per item, which is fine for a toy case but bad for batch throughput. The async version uses bounded concurrency, which reduces latency without changing client integration.

If they push on why this matters:

> The important part is not “async” as a keyword. The important part is that independent work no longer waits in line. Once you overlap those waits safely, the wall-clock cost drops, while the contract and failure semantics stay explicit.

If they ask for the core mechanism:

> Sync spends time serially. Async overlaps idle waits. The speedup comes from reducing the amount of time the system spends blocked on work it does not need to do one-at-a-time.

## What This Is Not

This is not:
- a production-grade billing service
- a real AI integration
- a benchmark framework
- a framework comparison exercise

It is an interview drill that shows the right engineering instincts under a constrained live-coding timeline.
