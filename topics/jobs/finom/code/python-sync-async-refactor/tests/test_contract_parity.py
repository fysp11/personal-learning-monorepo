from __future__ import annotations

import httpx
import pytest

from bad_sync_api import create_app as create_sync_app
from contracts import BatchCategorizeResponse, CategoryResult, HealthResponse
from good_async_api import create_app as create_async_app
from mock_ai_adapter import MockAIAdapter, MockAIConfig


@pytest.mark.anyio
async def test_contract_parity_for_all_endpoints() -> None:
    adapter_config = MockAIConfig(delay_ms=1, fail_rate=0.0)
    sync_app = create_sync_app(adapter=MockAIAdapter(adapter_config))
    async_app = create_async_app(adapter=MockAIAdapter(adapter_config), max_concurrency=5)

    sync_transport = httpx.ASGITransport(app=sync_app)
    async_transport = httpx.ASGITransport(app=async_app)

    async with (
        httpx.AsyncClient(transport=sync_transport, base_url="http://sync") as sync_client,
        httpx.AsyncClient(transport=async_transport, base_url="http://async") as async_client,
    ):
        sync_health = await sync_client.get("/health")
        async_health = await async_client.get("/health")

        assert sync_health.status_code == async_health.status_code == 200
        assert set(sync_health.json().keys()) == set(async_health.json().keys())
        HealthResponse.model_validate(sync_health.json())
        HealthResponse.model_validate(async_health.json())

        payload = {
            "id": "tx-1",
            "merchant": "GitHub Inc",
            "amount": 49.0,
            "description": "Team subscription",
            "market": "DE",
        }
        sync_single = await sync_client.post("/categorize", json=payload)
        async_single = await async_client.post("/categorize", json=payload)

        assert sync_single.status_code == async_single.status_code == 200
        assert set(sync_single.json().keys()) == set(async_single.json().keys())
        assert sync_single.json()["id"] == async_single.json()["id"]
        CategoryResult.model_validate(sync_single.json())
        CategoryResult.model_validate(async_single.json())

        batch_payload = {
            "items": [
                payload,
                {
                    "id": "tx-2",
                    "merchant": "Restaurant Berlin",
                    "amount": 120.0,
                    "description": "Client dinner",
                    "market": "DE",
                },
                {
                    "id": "tx-3",
                    "merchant": "Unknown Vendor",
                    "amount": 30.0,
                    "description": "Misc",
                    "market": "FR",
                },
            ]
        }
        sync_batch = await sync_client.post("/categorize/batch", json=batch_payload)
        async_batch = await async_client.post("/categorize/batch", json=batch_payload)

        assert sync_batch.status_code == async_batch.status_code == 200
        assert set(sync_batch.json().keys()) == set(async_batch.json().keys())

        sync_batch_model = BatchCategorizeResponse.model_validate(sync_batch.json())
        async_batch_model = BatchCategorizeResponse.model_validate(async_batch.json())

        assert sync_batch_model.total == async_batch_model.total == 3
        assert [item.id for item in sync_batch_model.items] == [
            item.id for item in async_batch_model.items
        ]
