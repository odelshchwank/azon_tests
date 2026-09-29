import uuid
from decimal import Decimal

import pytest

from data.products import ProductData


class TestProducts:

    def test_products_price_filter_return_items_above_min(self, api_manager):
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

    def test_create_product_positive(self, authenticated_admin, created_product):
        payload = created_product["payload"]
        product = created_product["response_body"]
        assert payload["sku"] == product["sku"]
        assert payload["name"] == product["name"]
        assert payload["stock"] == product["stock"]
        assert payload["category_id"] == product["category_id"]
        assert Decimal(str(payload["price"])) == Decimal(str(product["price"]))
        assert product["is_seed"] is False
        assert product["is_available"] is True

    # Отдельный тест для проверки структуры - не уверен нужен тут или нет(
    def test_get_products_default_pagination(self, api_manager):
        data = api_manager.products_api.get_products().json()
        assert set(data.keys()) >= {"items", "total", "page", "size", "pages"}
        assert data["page"] == 1
        assert data["size"] == 20
        assert len(data["items"]) <= 20
        assert data["pages"] == (data["total"] + data["size"] - 1) // data["size"]

    def test_update_product_positive(self, api_manager, authenticated_admin, created_product):
        new_payload = ProductData.update_product_data(name="Мистер Саничка")
        updated = api_manager.products_api.update_product(
            created_product["id"], new_payload
        ).json()

        assert updated["name"] == new_payload["name"]
        assert updated["stock"] == created_product["response_body"]["stock"]
        assert Decimal(updated["price"]) == Decimal(created_product["response_body"]["price"])

    def test_update_price_positive(self, api_manager, authenticated_admin, created_product):
        new_price = 12345.67
        updated = api_manager.products_api.update_price(
            created_product["id"], ProductData.price_data(new_price)
        ).json()

        assert Decimal(updated["price"]) == Decimal(str(new_price))

    def test_delete_product_positive(self, api_manager, authenticated_admin, created_product):
        api_manager.products_api.delete_product(created_product["id"])
        api_manager.products_api.delete_product(
            created_product["id"], expected_status=404
        )

    # Баловство с параметризацией
    @pytest.mark.parametrize("new_price", [0.01, 1, 999_999.99])
    def test_update_price_boundaries(self, api_manager, authenticated_admin, created_product, new_price):
        updated = api_manager.products_api.update_price(
            created_product["id"], ProductData.price_data(new_price)
        ).json()
        assert Decimal(updated["price"]) == Decimal(str(new_price))

    @pytest.mark.parametrize("page,size", [(1, 5), (1, 10), (2, 5)])
    def test_pagination(self, api_manager, page, size):
        data = api_manager.products_api.get_products(params={"page": page, "size": size}).json()
        assert data["page"] == page
        assert data["size"] == size
        assert len(data["items"]) <= size