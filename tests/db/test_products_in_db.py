from decimal import Decimal

import pytest

from data.products import ProductData
from utils.marks import requires_admin, requires_db

pytestmark = [pytest.mark.db, pytest.mark.products, requires_db, requires_admin]


class TestProductsInDB:
    def test_created_product_is_saved_in_db(self, created_product, db):
        row = db.product.get_product(created_product.id)

        assert row is not None, "товар создан через API, но строки в базе нет"
        assert row["sku"] == created_product.sku
        assert row["price"] == created_product.price
        assert row["stock"] == created_product.stock
        assert row["deleted_at"] is None
        assert row["is_seed"] is False

    def test_product_author_lives_in_another_database(self, created_product, db):
        product = db.product.get_product(created_product.id)

        author = db.auth.get_user(product["created_by"])

        assert author is not None, "автор товара должен существовать в azon_auth"
        assert author["role"] in ("MANAGER", "ADMIN")

    def test_deleted_product_stays_in_db(
        self, api_manager, admin_manager, created_product, db
    ):
        admin_manager.products_api.delete_product(created_product.id)

        api_manager.products_api.get_product(created_product.id, expected_status=404)

        row = db.product.get_product(created_product.id)

        assert row is not None, "soft delete: строка должна остаться в базе"
        assert row["deleted_at"] is not None, (
            "у удаленного товара проставляется deleted_at"
        )

    def test_price_update_changes_only_price(self, admin_manager, created_product, db):
        before = db.product.get_product(created_product.id)
        new_price = created_product.price + Decimal("1000.00")

        admin_manager.products_api.update_price(
            created_product.id,
            ProductData.price_data(new_price=new_price),
        )

        after = db.product.get_product(created_product.id)
        assert after["price"] == new_price, "цена в базе обновилась"
        assert after["updated_at"] > before["updated_at"], "updated_at сдвинулся"

        unchanged = (
            "sku",
            "name",
            "description",
            "stock",
            "category_id",
            "created_by",
            "deleted_at",
        )
        assert {key: after[key] for key in unchanged} == {
            key: before[key] for key in unchanged
        }
