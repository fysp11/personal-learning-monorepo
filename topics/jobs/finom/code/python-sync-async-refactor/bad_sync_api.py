from __future__ import annotations

import argparse
import os
from pprint import pprint

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException

from contracts import (
    BatchCategorizeRequest,
    BatchCategorizeResponse,
    CategorizeRequest,
    CategoryResult,
    ErrorResponse,
    HealthResponse,
)
from mock_ai_adapter import MockAIAdapter, MockAIConfig, MockAIError
from services import SyncBatchProcessor, default_demo_scenario, print_demo_header


def adapter_from_env() -> MockAIAdapter:
    delay_ms = int(os.getenv("MOCK_DELAY_MS", "80"))
    fail_rate = float(os.getenv("MOCK_FAIL_RATE", "0"))
    return MockAIAdapter(MockAIConfig(delay_ms=delay_ms, fail_rate=fail_rate))


def process_batch_sync(
    payload: BatchCategorizeRequest, adapter: MockAIAdapter
) -> BatchCategorizeResponse:
    return SyncBatchProcessor(adapter).process(payload)


def create_app(adapter: MockAIAdapter | None = None) -> FastAPI:
    local_adapter = adapter or adapter_from_env()
    batch_processor = SyncBatchProcessor(local_adapter)

    app = FastAPI(title="Finom Sync AI API (Bad Example)", version="0.1.0")
    app.state.adapter = local_adapter
    app.state.batch_processor = batch_processor

    @app.get("/health", response_model=HealthResponse)
    def health() -> HealthResponse:
        return HealthResponse(status="ok", implementation="sync")

    @app.post("/categorize", response_model=CategoryResult)
    def categorize(request: CategorizeRequest) -> CategoryResult:
        try:
            return app.state.adapter.categorize_sync(request)
        except MockAIError as exc:
            raise HTTPException(
                status_code=502,
                detail=ErrorResponse(
                    code=exc.code,
                    message=str(exc),
                    request_id=request.id,
                ).model_dump(),
            ) from exc

    @app.post("/categorize/batch", response_model=BatchCategorizeResponse)
    def categorize_batch(payload: BatchCategorizeRequest) -> BatchCategorizeResponse:
        return process_batch_sync(payload, app.state.adapter)

    return app


app = create_app()


async def run_self_check() -> int:
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/health")
        assert health.status_code == 200

        single = await client.post(
            "/categorize",
            json={
                "id": "sync-1",
                "merchant": "GitHub Inc",
                "amount": 49.0,
                "description": "Team subscription",
                "market": "DE",
            },
        )
        assert single.status_code == 200

        batch = await client.post(
            "/categorize/batch",
            json={
                "items": [
                    {
                        "id": "sync-b1",
                        "merchant": "Adobe",
                        "amount": 30.0,
                        "description": "License",
                        "market": "DE",
                    },
                    {
                        "id": "sync-b2",
                        "merchant": "Restaurant Berlin",
                        "amount": 120.0,
                        "description": "Client dinner",
                        "market": "DE",
                    },
                ]
            },
        )
        assert batch.status_code == 200
        body = batch.json()
        assert body["total"] == 2
        assert body["success_count"] == 2

    print("bad_sync_api self-check: OK")
    return 0


def run_demo() -> int:
    adapter = adapter_from_env()
    payload = default_demo_scenario().payload
    batch_processor = SyncBatchProcessor(adapter)

    print_demo_header("Sync demo", payload)

    single = adapter.categorize_sync(payload.items[0])
    print("Single categorize result:")
    pprint(single.model_dump())

    batch = batch_processor.process(payload)
    print("Batch result:")
    pprint(batch.model_dump())
    print(f"Elapsed ms: {batch.elapsed_ms:.2f}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync API demo")
    parser.add_argument("--self-check", action="store_true", help="Run local API checks")
    parser.add_argument("--demo", action="store_true", help="Print visible demo output")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    if args.self_check:
        import asyncio

        return asyncio.run(run_self_check())
    if args.demo:
        return run_demo()

    uvicorn.run("bad_sync_api:app", host=args.host, port=args.port, reload=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
