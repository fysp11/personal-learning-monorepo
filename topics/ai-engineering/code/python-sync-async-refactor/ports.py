from __future__ import annotations

from typing import Protocol, runtime_checkable

from contracts import CategorizeRequest, CategoryResult


@runtime_checkable
class CategorizerPort(Protocol):
    def categorize_sync(self, request: CategorizeRequest) -> CategoryResult: ...

    async def categorize_async(self, request: CategorizeRequest) -> CategoryResult: ...
