from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderItemResponse(BaseModel):
    product_id: UUID
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    status: str
    total_amount: Decimal
    items: list[OrderItemResponse]
    created_at: datetime
    updated_at: datetime
    warnings: list[str] = Field(default_factory=list)


class OrdersPage(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    size: int
    pages: int


class PayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    card_number: str = Field(min_length=12, max_length=19, pattern=r"^\d+$")
    card_holder: str = Field(min_length=1, max_length=100)
    exp_month: int = Field(ge=1, le=12)
    exp_year: int = Field(ge=2020, le=2100)
    cvc: str = Field(pattern=r"^\d{3}$")


class PayResponse(BaseModel):
    payment_id: UUID
    status: str
    order_status: str


class PaymentBriefResponse(BaseModel):
    id: UUID
    amount: Decimal
    status: str
    card_last4: str
    decline_code: str | None
    created_at: datetime


class OrderWithPaymentsResponse(OrderResponse):
    payments: list[PaymentBriefResponse] = Field(default_factory=list)


class CheckoutRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    accept_price_changes: bool = False
