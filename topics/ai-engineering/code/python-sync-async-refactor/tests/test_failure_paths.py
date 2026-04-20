from __future__ import annotations

import time

import httpx
import pytest

from bad_sync_api import create_app as create_sync_app
from good_async_api import create_app as create_async_app
from mock_ai_adapter import MockAIAdapter, MockAIConfig


@pytest.mark.anyio
async def test_single_request_failure_is_controlled_for_both_apis() -> None:
    failing = MockAIAdapter(MockAIConfig(delay_ms=1, fail_rate=1.0))

    sync_app = create_sync_app(adapter=failing)
    async_app = create_async_app(adapter=failing)

    sync_transport = httpx.ASGITransport(app=sync_app)
    async_transport = httpx.ASGITransport(app=async_app)

    payload = {
        "id": "f-1",
        "merchant": "Any Merchant",
        "amount": 10.0,
        "description": "test",
        "market": "DE",
    }

    async with (
        httpx.AsyncClient(transport=sync_transport, base_url="http://sync") as sync_client,
        httpx.AsyncClient(transport=async_transport, base_url="http://async") as async_client,
    ):
        sync_response = await sync_client.post("/categorize", json=payload)
        async_response = await async_client.post("/categorize", json=payload)

    assert sync_response.status_code == async_response.status_code == 502
    assert sync_response.json()["detail"]["code"] == "MOCK_AI_FAILURE"
    assert async_response.json()["detail"]["code"] == "MOCK_AI_FAILURE"


@pytest.mark.anyio
async def test_batch_failure_returns_structured_errors_without_hanging() -> None:
    failing = MockAIAdapter(MockAIConfig(delay_ms=20, fail_rate=1.0))

    sync_app = create_sync_app(adapter=failing)
    async_app = create_async_app(adapter=failing, max_concurrency=5)

    sync_transport = httpx.ASGITransport(app=sync_app)
    async_transport = httpx.ASGITransport(app=async_app)

    payload = {
        "items": [
            {"id": "f-b1", "merchant": "A", "amount": 1.0, "market": "DE"},
            {"id": "f-b2", "merchant": "B", "amount": 2.0, "market": "DE"},
            {"id": "f-b3", "merchant": "C", "amount": 3.0, "market": "DE"},
        ]
    }

    async with (
        httpx.AsyncClient(transport=sync_transport, base_url="http://sync") as sync_client,
        httpx.AsyncClient(transport=async_transport, base_url="http://async") as async_client,
    ):
        start_sync = time.perf_counter()
        sync_response = await sync_client.post("/categorize/batch", json=payload)
        sync_elapsed = time.perf_counter() - start_sync

        start_async = time.perf_counter()
        async_response = await async_client.post("/categorize/batch", json=payload)
        async_elapsed = time.perf_counter() - start_async

    assert sync_response.status_code == async_response.status_code == 200

    sync_body = sync_response.json()
    async_body = async_response.json()

    assert sync_body["success_count"] == 0
    assert async_body["success_count"] == 0
    assert sync_body["error_count"] == 3
    assert async_body["error_count"] == 3
    assert all(not item["ok"] for item in sync_body["items"])
    assert all(not item["ok"] for item in async_body["items"])

    # The request paths must return quickly and never block indefinitely.
    assert sync_elapsed < 1.0
    assert async_elapsed < 1.0
