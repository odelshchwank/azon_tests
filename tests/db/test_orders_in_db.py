from decimal import Decimal

import pytest

from data.orders import OrderData, Cards
from data.products import ProductData
from utils.marks import requires_admin, requires_db

pytestmark = [pytest.mark.db, pytest.mark.payment, requires_db, requires_admin]


class TestOrdersInDB:
    def test_order_and_items_are_saved_in_db(self, awaiting_order, created_product, db):
        order = db.payment.get_order(awaiting_order.id)

        assert order is not None, "заказ оформлен, но строки в azon_payment.orders нет"
        assert order["status"] == "AWAITING_PAYMENT"
        assert order["total_amount"] == created_product.price

        items = db.payment.get_order_items(order["id"])
        assert len(items) == 1
        assert items[0]["product_id"] == created_product.id
        assert items[0]["quantity"] == 1
        assert items[0]["subtotal"] == created_product.price

    def test_order_item_keeps_price_snapshot(
        self, admin_manager, awaiting_order, created_product, db
    ):
        original_price = created_product.price
        new_price = original_price + Decimal("1000.00")

        admin_manager.products_api.update_price(
            created_product.id,
            ProductData.price_data(new_price=new_price),
        )

        product_row = db.product.get_product(created_product.id)
        item = db.payment.get_order_items(awaiting_order.id)[0]

        assert product_row["price"] == new_price, "в каталоге новая цена"
        assert item["unit_price"] == original_price, "в заказе цена осталась прежней"

    def test_checkout_reserves_stock(self, awaiting_order, created_product, db):
        row = db.product.get_product(created_product.id)

        assert row["stock"] == created_product.stock - 1, (
            "оформление заказа списывает сток"
        )

    def test_declined_payment_saved_in_db(
        self, api_manager, authenticated_user, awaiting_order, db
    ):
        api_manager.payment_api.pay_order(
            awaiting_order.id,
            OrderData.payment_declined(),
            expected_status=402,
        )

        payment = db.payment.get_payment_by_order(awaiting_order.id)
        assert payment["status"] == "DECLINED"
        assert payment["decline_code"] == "card_declined"
        assert payment["card_last4"] == Cards.DECLINED[-4:]
        assert len(payment["card_last4"]) == 4

        transactions = db.payment.get_transactions_by_payment(payment["id"])
        assert any(transaction["status"] == "FAILED" for transaction in transactions)
