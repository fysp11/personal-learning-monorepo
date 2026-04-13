from __future__ import annotations

import pytest

from bad_sync_api import process_batch_sync
from contracts import BatchCategorizeRequest, CategorizeRequest
from good_async_api import process_batch_async
from mock_ai_adapter import MockAIAdapter, MockAIConfig


def build_payload() -> BatchCategorizeRequest:
    return BatchCategorizeRequest(
        items=[
            CategorizeRequest(
                id="b-1",
                merchant="GitHub Inc",
                amount=49.0,
                description="Team subscription",
                market="DE",
            ),
            CategorizeRequest(
                id="b-2",
                merchant="Restaurant Berlin",
                amount=120.0,
                description="Client dinner",
                market="DE",
            ),
            CategorizeRequest(
                id="b-3",
                merchant="Unknown Vendor",
                amount=30.0,
                description="Misc",
                market="FR",
            ),
            CategorizeRequest(
                id="b-4",
                merchant="Amazon Web Services Ireland",
                amount=320.0,
                description="Cloud compute",
                market="DE",
            ),
        ]
    )


def test_sync_batch_preserves_input_order() -> None:
    payload = build_payload()
    adapter = MockAIAdapter(MockAIConfig(delay_ms=1, fail_rate=0.0))

    response = process_batch_sync(payload, adapter)

    assert response.total == 4
    assert [item.id for item in response.items] == [r.id for r in payload.items]


@pytest.mark.anyio
async def test_async_batch_preserves_input_order_and_counts() -> None:
    payload = build_payload()
    adapter = MockAIAdapter(MockAIConfig(delay_ms=1, fail_rate=0.0))

    response = await process_batch_async(payload, adapter, max_concurrency=3)

    assert response.total == 4
    assert response.success_count == 4
    assert response.error_count == 0
    assert [item.id for item in response.items] == [r.id for r in payload.items]
