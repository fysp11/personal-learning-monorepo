from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pprint import pprint

from contracts import (
    BatchCategorizeRequest,
    BatchCategorizeResponse,
    BatchItemResult,
    CategorizeRequest,
    ErrorResponse,
)
from mock_ai_adapter import MockAIError
from ports import CategorizerPort


@dataclass(frozen=True)
class DemoScenario:
    payload: BatchCategorizeRequest


def default_demo_scenario() -> DemoScenario:
    return DemoScenario(
        payload=BatchCategorizeRequest(
            items=[
                CategorizeRequest(
                    id="demo-1",
                    merchant="GitHub Inc",
                    amount=49.0,
                    description="Team subscription",
                    market="DE",
                ),
                CategorizeRequest(
                    id="demo-2",
                    merchant="Restaurant Berlin",
                    amount=120.0,
                    description="Client dinner",
                    market="DE",
                ),
                CategorizeRequest(
                    id="demo-3",
                    merchant="Amazon Web Services Ireland",
                    amount=320.0,
                    description="Cloud compute",
                    market="DE",
                ),
            ]
        )
    )


def error_response(exc: MockAIError, request_id: str) -> ErrorResponse:
    return ErrorResponse(code=exc.code, message=str(exc), request_id=request_id)


def print_demo_header(title: str, payload: BatchCategorizeRequest) -> None:
    print(f"=== {title} ===")
    print("Input:")
    pprint(payload.model_dump())


class SyncBatchProcessor:
    def __init__(self, categorizer: CategorizerPort) -> None:
        self._categorizer = categorizer

    def process(self, payload: BatchCategorizeRequest) -> BatchCategorizeResponse:
        start = time.perf_counter()
        items: list[BatchItemResult] = []

        for request in payload.items:
            try:
                result = self._categorizer.categorize_sync(request)
                items.append(BatchItemResult(id=request.id, ok=True, result=result))
            except MockAIError as exc:
                items.append(
                    BatchItemResult(
                        id=request.id,
                        ok=False,
                        error=error_response(exc, request.id),
                    )
                )

        elapsed_ms = (time.perf_counter() - start) * 1000
        success_count = sum(1 for item in items if item.ok)

        return BatchCategorizeResponse(
            total=len(items),
            success_count=success_count,
            error_count=len(items) - success_count,
            elapsed_ms=elapsed_ms,
            items=items,
        )


class AsyncBatchProcessor:
    def __init__(self, categorizer: CategorizerPort, max_concurrency: int) -> None:
        self._categorizer = categorizer
        self._max_concurrency = max_concurrency

    async def process(self, payload: BatchCategorizeRequest) -> BatchCategorizeResponse:
        start = time.perf_counter()
        semaphore = asyncio.Semaphore(self._max_concurrency)

        async def process_one(request: CategorizeRequest) -> BatchItemResult:
            try:
                async with semaphore:
                    result = await self._categorizer.categorize_async(request)
                return BatchItemResult(id=request.id, ok=True, result=result)
            except MockAIError as exc:
                return BatchItemResult(
                    id=request.id,
                    ok=False,
                    error=error_response(exc, request.id),
                )

        items = await asyncio.gather(*(process_one(request) for request in payload.items))
        elapsed_ms = (time.perf_counter() - start) * 1000
        success_count = sum(1 for item in items if item.ok)

        return BatchCategorizeResponse(
            total=len(items),
            success_count=success_count,
            error_count=len(items) - success_count,
            elapsed_ms=elapsed_ms,
            items=items,
        )
