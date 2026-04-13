from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import dataclass

from contracts import CategorizeRequest, CategoryResult
from ports import CategorizerPort


class MockAIError(RuntimeError):
    def __init__(self, message: str, code: str = "UPSTREAM_AI_ERROR") -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class MockAIConfig:
    delay_ms: int = 80
    fail_rate: float = 0.0
    seed: str = "finom-interview-3"


class MockAIAdapter(CategorizerPort):
    """Deterministic adapter used by both sync and async implementations.

    The same input always maps to the same category/confidence.
    Failure behavior is deterministic via a stable hash and configured fail_rate.
    """

    def __init__(self, config: MockAIConfig | None = None) -> None:
        self.config = config or MockAIConfig()

    def categorize_sync(self, request: CategorizeRequest) -> CategoryResult:
        self._sleep_sync()
        return self._categorize(request)

    async def categorize_async(self, request: CategorizeRequest) -> CategoryResult:
        await self._sleep_async()
        return self._categorize(request)

    def _sleep_sync(self) -> None:
        time.sleep(self.config.delay_ms / 1000)

    async def _sleep_async(self) -> None:
        await asyncio.sleep(self.config.delay_ms / 1000)

    def _categorize(self, request: CategorizeRequest) -> CategoryResult:
        if self._should_fail(request):
            raise MockAIError(
                message="Mocked upstream categorizer failed deterministically",
                code="MOCK_AI_FAILURE",
            )

        merchant = request.merchant.lower()
        description = (request.description or "").lower()
        text = f"{merchant} {description}"

        if any(k in text for k in ["adobe", "github", "notion", "openai", "software"]):
            category = "software"
            account = "4920" if request.market == "DE" else "6060"
            confidence = 0.93
            reason = "Known SaaS vendor signature"
        elif any(k in text for k in ["cowork", "wework", "rent", "office"]):
            category = "office"
            account = "4210" if request.market == "DE" else "6130"
            confidence = 0.88
            reason = "Office/coworking descriptor"
        elif any(k in text for k in ["restaurant", "cafe", "meal", "dinner"]):
            category = "entertainment"
            account = "4650" if request.market == "DE" else "6230"
            confidence = 0.67
            reason = "Hospitality terms trigger proposal-zone confidence"
        elif any(k in text for k in ["ireland", "reverse charge", "aws"]):
            category = "cross_border_services"
            account = "3125" if request.market == "DE" else "6280"
            confidence = 0.81
            reason = "Cross-border indicator; requires explicit review"
        else:
            category = "other"
            account = "4900" if request.market == "DE" else "6280"
            confidence = 0.42
            reason = "Unknown merchant signature"

        routing = self._route(confidence, category)

        return CategoryResult(
            id=request.id,
            account_code=account,
            category=category,
            confidence=confidence,
            routing=routing,
            reason=reason,
        )

    def _route(self, confidence: float, category: str) -> str:
        if category == "cross_border_services":
            return "review"
        if confidence >= 0.85:
            return "auto_book"
        if confidence >= 0.55:
            return "proposal"
        return "review"

    def _should_fail(self, request: CategorizeRequest) -> bool:
        if self.config.fail_rate <= 0:
            return False

        key = f"{self.config.seed}:{request.id}:{request.merchant}:{request.amount:.2f}".encode(
            "utf-8"
        )
        digest = hashlib.sha256(key).hexdigest()
        stable_score = int(digest[:8], 16) / 0xFFFFFFFF
        return stable_score < self.config.fail_rate
