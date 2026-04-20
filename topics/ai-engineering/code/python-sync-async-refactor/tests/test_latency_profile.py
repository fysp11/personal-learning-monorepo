from __future__ import annotations

import time

import pytest

from bad_sync_api import process_batch_sync
from contracts import BatchCategorizeRequest, CategorizeRequest
from good_async_api import process_batch_async
from mock_ai_adapter import MockAIAdapter, MockAIConfig


def build_batch(size: int = 20) -> BatchCategorizeRequest:
    items = [
        CategorizeRequest(
            id=f"lat-{i}",
            merchant="GitHub Inc",
            amount=10 + i,
            description="Subscription",
            market="DE",
        )
        for i in range(size)
    ]
    return BatchCategorizeRequest(items=items)


@pytest.mark.anyio
async def test_async_batch_is_materially_faster_than_sync_with_delay() -> None:
    payload = build_batch(size=20)
    delay_ms = 40

    sync_adapter = MockAIAdapter(MockAIConfig(delay_ms=delay_ms, fail_rate=0.0))
    async_adapter = MockAIAdapter(MockAIConfig(delay_ms=delay_ms, fail_rate=0.0))

    sync_start = time.perf_counter()
    sync_response = process_batch_sync(payload, sync_adapter)
    sync_elapsed = time.perf_counter() - sync_start

    async_start = time.perf_counter()
    async_response = await process_batch_async(payload, async_adapter, max_concurrency=5)
    async_elapsed = time.perf_counter() - async_start

    assert sync_response.success_count == async_response.success_count == 20

    # Bounded-concurrent async should substantially outperform sequential sync.
    assert async_elapsed < sync_elapsed * 0.7, (
        f"Expected async ({async_elapsed:.3f}s) to beat sync ({sync_elapsed:.3f}s) by >=30%"
    )
