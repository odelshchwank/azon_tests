import uuid
from decimal import Decimal

from models.products import (
    ProductRequest,
    CartItemAddRequest,
    ProductPriceUpdateRequest,
)
from utils.data_generator import DataGenerator


class ProductData:
    """Object Mother: готовые данные для запросов к Product API."""

    @staticmethod
    def creation_product_data(
        category_id: uuid.UUID | str, **overrides
    ) -> ProductRequest:
        base = ProductRequest(
            name=DataGenerator.generate_product_name(),
            sku=DataGenerator.generate_sku(),
            description=DataGenerator.generate_description(),
            price=DataGenerator.generate_price(),
            stock=DataGenerator.generate_stock(),
            category_id=category_id,
        )
        if overrides:
            return base.model_copy(update=overrides)
        return base

    @staticmethod
    def update_product_data(**overrides) -> dict:
        return dict(overrides)

    @staticmethod
    def nonexistent_category_id() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def cart_item_data(product_id: uuid.UUID, quantity: int = 1) -> CartItemAddRequest:
        return CartItemAddRequest(product_id=product_id, quantity=quantity)

    @staticmethod
    def price_data(
        current_price: Decimal | str | None = None,
    ) -> ProductPriceUpdateRequest:
        price = Decimal("19990.00")
        if current_price is not None and Decimal(str(current_price)) == price:
            price = Decimal("19991.00")

        return ProductPriceUpdateRequest(price=price)
