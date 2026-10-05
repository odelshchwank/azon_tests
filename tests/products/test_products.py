import uuid
from decimal import Decimal

import pytest

from data.products import ProductData
from models.products import ProductResponse, ProductsPage
from utils.data_generator import DataGenerator
from utils.marks import requires_admin, requires_manager

pytestmark = [pytest.mark.products, pytest.mark.regression]


class TestProducts:
    def test_get_created_product(self, api_manager, created_product):
        response = api_manager.products_api.get_product(created_product.id)

        assert ProductResponse.model_validate(response.json()) == created_product

    @pytest.mark.slow
    def test_catalog_keeps_all_created_products(
        self,
        admin_manager,
        category_id,
    ):
        created = []
        for _ in range(10):
            product_data = ProductData.creation_product_data(category_id)

        created.append(admin_manager.products_api.create_product(product_data).json())
        response = admin_manager.products_api.get_products(
            params={
                "category_id": category_id,
                "size": 100,
                "sort_by": "created_at",
            }
        )
        catalog_ids = {item["id"] for item in response.json()["items"]}

        try:
            assert {product["id"] for product in created} <= catalog_ids
        finally:
            for product in created:
                admin_manager.products_api.delete_product(product["id"])

    def test_products_price_filter_return_items_above_min(self, api_manager):
        page = ProductsPage.model_validate(
            api_manager.products_api.get_products(
                params={"price_min": 5000, "size": 100}
            ).json()
        )
        assert page.items
        assert all(product.price >= 5000 for product in page.items)

    def test_get_product_by_id(self, api_manager):
        products = api_manager.products_api.get_products().json()["items"]
        product_id = products[0]["id"]

        response = api_manager.products_api.get_product(product_id)

        assert response.json()["id"] == product_id

    @requires_admin
    @pytest.mark.roles
    @pytest.mark.slow
    def test_create_product_positive(self, admin_manager, category_id):
        product_request = ProductData.creation_product_data(category_id)

        response = admin_manager.products_api.create_product(product_request)

        product = ProductResponse.model_validate(response.json())

        try:
            assert product.name == product_request.name
            assert product.sku == product_request.sku
            assert product.stock == product_request.stock
            assert product.category_id == product_request.category_id
            assert product.price == product_request.price
            assert product.is_seed is False
            assert product.is_available is True
        finally:
            admin_manager.products_api.delete_product(product.id)

    def test_get_products_default_pagination(self, api_manager):
        data = api_manager.products_api.get_products().json()
        assert set(data.keys()) >= {"items", "total", "page", "size", "pages"}
        assert data["page"] == 1
        assert data["size"] == 20
        assert len(data["items"]) <= 20
        expected_pages = (data["total"] + data["size"] - 1) // data["size"]
        assert data["pages"] == expected_pages

    @requires_admin
    @pytest.mark.roles
    def test_update_product_positive(
        self, api_manager, authenticated_admin, created_product
    ):
        new_payload = ProductData.update_product_data(name="Мистер Саничка")
        updated = api_manager.products_api.update_product(
            created_product.id, new_payload
        ).json()

        assert updated["name"] == new_payload["name"]
        assert updated["stock"] == created_product.stock
        assert Decimal(updated["price"]) == created_product.price

    @requires_admin
    @pytest.mark.roles
    def test_update_price_positive(
        self, api_manager, authenticated_admin, created_product
    ):
        new_price = 12345.67
        updated = api_manager.products_api.update_price(
            created_product.id, ProductData.price_data(new_price)
        ).json()

        assert Decimal(updated["price"]) == Decimal(str(new_price))

    @requires_admin
    @pytest.mark.roles
    def test_delete_product_positive(
        self, api_manager, authenticated_admin, created_product
    ):
        api_manager.products_api.delete_product(created_product.id)
        api_manager.products_api.delete_product(created_product.id, expected_status=404)

    @requires_admin
    @pytest.mark.roles
    @pytest.mark.parametrize("new_price", [0.01, 1, 999_999.99])
    def test_update_price_boundaries(
        self, api_manager, authenticated_admin, created_product, new_price
    ):
        updated = api_manager.products_api.update_price(
            created_product.id, ProductData.price_data(new_price)
        ).json()
        assert Decimal(updated["price"]) == Decimal(str(new_price))

    @pytest.mark.parametrize("page,size", [(1, 5), (1, 10), (2, 5)])
    def test_pagination(self, api_manager, page, size):
        data = api_manager.products_api.get_products(
            params={"page": page, "size": size}
        ).json()
        assert data["page"] == page
        assert data["size"] == size
        assert len(data["items"]) <= size

    @requires_admin
    @pytest.mark.roles
    def test_filter_search(self, api_manager, admin_manager, category_id):
        unique_name = DataGenerator.generate_product_name()
        payload = ProductData.creation_product_data(category_id, name=unique_name)
        created = admin_manager.products_api.create_product(payload).json()

        try:
            response = api_manager.products_api.get_products(
                params={"search": unique_name}
            )
            items = response.json()["items"]

            assert all(unique_name.lower() in item["name"].lower() for item in items)
            assert any(item["id"] == created["id"] for item in items)
        finally:
            admin_manager.products_api.delete_product(
                created["id"], expected_status=[204, 404]
            )

    def test_filter_category_id(self, api_manager, admin_manager, category_id):
        product_request = ProductData.creation_product_data(category_id)
        created = admin_manager.products_api.create_product(product_request).json()

        try:
            items = api_manager.products_api.get_products(
                params={"category_id": category_id, "size": 100}
            ).json()["items"]

            assert items
            assert all(item["category_id"] == category_id for item in items)
            assert any(item["id"] == created["id"] for item in items)
        finally:
            admin_manager.products_api.delete_product(
                created["id"], expected_status=[204, 404]
            )

    def test_filter_in_stock(self, api_manager, admin_manager, category_id):
        product_request = ProductData.creation_product_data(category_id)
        created = admin_manager.products_api.create_product(product_request).json()

        try:
            items = api_manager.products_api.get_products(
                params={"in_stock": True, "size": 100}
            ).json()["items"]

            assert items
            assert all(item["stock"] > 0 for item in items)
            assert any(item["id"] == created["id"] for item in items)
        finally:
            admin_manager.products_api.delete_product(
                created["id"], expected_status=[204, 404]
            )

    def test_filter_price_range(self, api_manager, admin_manager, category_id):
        price_min, price_max = DataGenerator.generate_price_range()
        price_in_range = Decimal(str((price_min + price_max) / 2))
        product_request = ProductData.creation_product_data(
            category_id, price=price_in_range
        )
        created = admin_manager.products_api.create_product(product_request).json()

        try:
            page = ProductsPage.model_validate(
                api_manager.products_api.get_products(
                    params={
                        "price_min": price_min,
                        "price_max": price_max,
                        "size": 100,
                    }
                ).json()
            )

            assert page.items
            assert all(
                Decimal(str(price_min)) <= product.price <= Decimal(str(price_max))
                for product in page.items
            )
            assert any(product.id == uuid.UUID(created["id"]) for product in page.items)
        finally:
            admin_manager.products_api.delete_product(
                created["id"], expected_status=[204, 404]
            )

    @pytest.mark.unstable
    @pytest.mark.xfail(
        reason="AZON-142: фильтр in_stock=false не отбирает товары без остатка"
    )
    def test_filter_out_of_stock(self, api_manager):
        items = api_manager.products_api.get_products(
            params={"in_stock": False, "size": 100}
        ).json()["items"]

        assert all(item["stock"] == 0 for item in items)


@pytest.mark.negative
class TestProductsNegative:
    @pytest.mark.roles
    def test_create_product_without_token(self, api_manager, category_id):
        payload = ProductData.creation_product_data(category_id)
        response = api_manager.products_api.create_product(
            payload, expected_status=401
        ).json()
        assert response["error"]["code"] == "TOKEN_MISSING"

    @pytest.mark.roles
    def test_create_product_forbidden_for_user(
        self, api_manager, authenticated_user, category_id
    ):
        payload = ProductData.creation_product_data(category_id)
        response = api_manager.products_api.create_product(
            payload, expected_status=403
        ).json()
        assert response["error"]["code"] == "FORBIDDEN"

    @requires_manager
    @pytest.mark.roles
    def test_create_product_duplicates_sku(
        self,
        api_manager,
        authenticated_manager,
        created_product,
        category_id,
    ):
        payload = ProductData.creation_product_data(
            category_id, sku=created_product.sku
        )
        response = api_manager.products_api.create_product(
            payload, expected_status=409
        ).json()
        assert response["error"]["code"] == "SKU_EXISTS"

    @requires_manager
    @pytest.mark.roles
    def test_create_product_nonexistent_category(
        self, api_manager, authenticated_manager
    ):
        payload = ProductData.creation_product_data(str(uuid.uuid4()))
        response = api_manager.products_api.create_product(
            payload, expected_status=404
        ).json()
        assert response["error"]["code"] == "CATEGORY_NOT_FOUND"

    def test_get_nonexistent_product(self, api_manager):
        response = api_manager.products_api.get_product(
            uuid.uuid4(), expected_status=404
        )
        assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"

    @pytest.mark.roles
    def test_include_inactive_without_token(self, api_manager):
        response = api_manager.products_api.get_products(
            params={"include_inactive": True},
            expected_status=401,
        ).json()
        assert response["error"]["code"] == "TOKEN_MISSING"

    @pytest.mark.negative
    @pytest.mark.roles
    def test_include_inactive_forbidden_for_user(self, api_manager, authenticated_user):
        response = api_manager.products_api.get_products(
            params={"include_inactive": True},
            expected_status=403,
        ).json()
        assert response["error"]["code"] == "FORBIDDEN"

    @requires_manager
    @pytest.mark.roles
    def test_update_price_forbidden_for_manager(
        self, api_manager, authenticated_manager, created_product
    ):
        response = api_manager.products_api.update_price(
            created_product.id,
            ProductData.price_data(),
            expected_status=403,
        ).json()
        assert response["error"]["code"] == "FORBIDDEN"

    @requires_admin
    @pytest.mark.roles
    @pytest.mark.slow
    def test_update_product_with_price_returns_422(
        self, api_manager, authenticated_admin, created_product
    ):
        payload = ProductData.update_product_data(price=100)
        details = api_manager.products_api.update_product(
            created_product.id, payload, expected_status=422
        ).json()["detail"]

        assert any(
            detail["type"] == "extra_forbidden" and "price" in detail["loc"]
            for detail in details
        )

    @requires_admin
    @pytest.mark.roles
    @pytest.mark.slow
    def test_delete_seed_product_forbidden(self, api_manager, authenticated_admin):
        response = api_manager.products_api.get_products(
            params={
                "size": 100,
                "include_inactive": True,
                "sort_by": "created_at",
                "order": "asc",
            }
        )
        items = response.json()["items"]
        seed = next((item for item in items if item["is_seed"]), None)
        assert seed is not None, "На стенде нет seed-товаров"

        response = api_manager.products_api.delete_product(
            seed["id"], expected_status=403
        ).json()
        assert response["error"]["code"] == "SEED_PROTECTED"

    @staticmethod
    def product_with_invalid_price(category_id) -> dict:
        product = ProductData.creation_product_data(category_id)
        return {**product.model_dump(mode="json"), "price": 0}
