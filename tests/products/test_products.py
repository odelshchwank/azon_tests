import uuid
from decimal import Decimal


class TestProducts:

    def test_get_products_return_paginated_catalog(self, api_manager):
        response = api_manager.products_api.get_products()

        data = response.json()
        assert data["total"] > 0
        assert len(data["items"]) <= data["size"]

    def test_products_price_filter(self, api_manager):
        response = api_manager.products_api.get_products(
            params={"price_min": 5000, "size": 100}
        )

        products = response.json()["items"]
        assert products, "Ожидали хотя бы один товар дороже 5000"
        for product in products:
            assert Decimal(product["price"]) >= 5000

    def test_get_product_by_id(self, api_manager):
        products = api_manager.products_api.get_products().json()["items"]
        product_id = products[0]["id"]

        response = api_manager.products_api.get_product(product_id)

        assert response.json()["id"] == product_id

    def test_get_nonexistent_product(self, api_manager):
        response = api_manager.products_api.get_product(uuid.uuid4(), expected_status=404)
        assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"