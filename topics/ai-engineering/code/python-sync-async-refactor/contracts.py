from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CategorizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    merchant: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = Field(default="EUR", min_length=3, max_length=3)
    description: str | None = None
    market: Literal["DE", "FR"] = "DE"


class BatchCategorizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[CategorizeRequest] = Field(min_length=1)


class CategoryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    account_code: str
    category: str
    confidence: float = Field(ge=0, le=1)
    routing: Literal["auto_book", "proposal", "review"]
    reason: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    request_id: str | None = None


class BatchItemResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    ok: bool
    result: CategoryResult | None = None
    error: ErrorResponse | None = None


class BatchCategorizeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int
    success_count: int
    error_count: int
    elapsed_ms: float = Field(ge=0)
    items: list[BatchItemResult]


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    implementation: Literal["sync", "async"]
