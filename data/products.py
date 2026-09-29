import uuid

from utils.data_generator import DataGenerator


class ProductData:

    @staticmethod
    def create_product_data(category_id, **overrides) -> dict:
        payload = {
            "name": DataGenerator.generate_product_name(),
            "sku": DataGenerator.generate_sku(),
            "description": DataGenerator.generate_description(),
            "price": DataGenerator.generate_price(),
            "stock": DataGenerator.generate_stock(),
            "category_id": category_id,
        }
        payload.update(overrides)
        return payload

    @staticmethod
    def update_product_data(**overrides) -> dict:
        return dict(overrides)

    @staticmethod
    def price_data(price=None) -> dict:
        return {"price": price if price is not None else DataGenerator.generate_price()}


    @staticmethod
    def nonexistent_category_id() -> str:
        return str(uuid.uuid4())