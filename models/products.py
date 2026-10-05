from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductRequest(BaseModel):
    """Тело POST api/v1/products."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    sku: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9._-]+$")
    description: str = Field(max_length=5_000)
    price: Decimal = Field(gt=0, le=1_000_000, decimal_places=2)
    stock: int = Field(ge=0, le=1_000_000)
    category_id: UUID


class ProductResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: UUID
    sku: str
    name: str
    description: str
    price: Decimal
    stock: int
    category_id: UUID
    image_url: str | None
    rating_avg: float | None
    reviews_count: int
    is_seed: bool
    is_available: bool
    created_at: datetime
    updated_at: datetime


class ProductsPage(BaseModel):
    """Страница каталог: ответ GET api/v1/products."""

    model_config = ConfigDict(extra="ignore")

    items: list[ProductResponse]
    total: int
    page: int
    size: int
    pages: int
