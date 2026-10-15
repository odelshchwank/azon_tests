import allure
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage
from pages.order_page import OrderPage
from pages.orders_page import OrdersPage

pytestmark = [pytest.mark.ui, pytest.mark.payment]

DECLINED_CARD = "4000000000000002"


def put_product_in_cart(page, product):
    catalog_page = CatalogPage(page).open()
    catalog_page.search(product.name)
    catalog_page.add_to_cart(product.name)
    expect(catalog_page.header.cart_count).to_have_text("1")


@allure.epic("Витрина AZON")
@allure.feature("Оформление заказа")
class TestCheckoutUI:
    @allure.story("Успешная оплата")
    @allure.title("Оплата успешной картой переводит заказ в PAID")
    def test_successful_payment_marks_order_paid(self, logged_in_page, created_product):
        put_product_in_cart(logged_in_page, created_product)
        CartPage(logged_in_page).open().checkout()
        order_page = OrderPage(logged_in_page)

        order_page.pay()

        expect(order_page.flash).to_have_text("Оплата прошла успешно!")
        expect(order_page.status).to_have_text("PAID")
        expect(order_page.payments).to_have_count(1)

    @allure.story("Отказ банка")
    @allure.title("Отклонённая карта оставляет заказ неоплаченным")
    def test_declined_card_leaves_order_unpaid(self, logged_in_page, created_product):
        put_product_in_cart(logged_in_page, created_product)
        CartPage(logged_in_page).open().checkout()
        order_page = OrderPage(logged_in_page)

        order_page.pay(card_number=DECLINED_CARD)

        expect(order_page.flash).to_have_text("Платёж отклонён банком (card_declined)")
        expect(order_page.status).to_have_text("AWAITING_PAYMENT")
        expect(
            order_page.payments.filter(has_text="DECLINED").get_by_test_id(
                "payment-decline-code"
            )
        ).to_have_text("card_declined")

    @allure.story("История платежей")
    @allure.title("История хранит и DECLINED, и SUCCEEDED")
    def test_payment_history_keeps_declined_and_successful_attempts(
        self, logged_in_page, created_product
    ):
        put_product_in_cart(logged_in_page, created_product)
        CartPage(logged_in_page).open().checkout()
        order_page = OrderPage(logged_in_page)

        order_page.pay(card_number=DECLINED_CARD)
        expect(order_page.status).to_have_text("AWAITING_PAYMENT")

        order_page.pay()
        expect(order_page.status).to_have_text("PAID")

        expect(order_page.payments).to_have_count(2)

        declined_row = order_page.payments.filter(has_text="DECLINED")
        expect(declined_row).to_have_count(1)
        expect(declined_row.get_by_test_id("payment-decline-code")).to_have_text(
            "card_declined"
        )

        expect(order_page.payments.filter(has_text="SUCCEEDED")).to_have_count(1)

    @allure.story("Отмена заказа")
    @allure.title("Неоплаченный заказ можно отменить")
    def test_order_can_be_cancelled(self, logged_in_page, created_product):
        put_product_in_cart(logged_in_page, created_product)
        CartPage(logged_in_page).open().checkout()
        order_page = OrderPage(logged_in_page)

        order_page.cancel()

        expect(order_page.flash).to_have_text("Заказ отменён")
        expect(order_page.status).to_have_text("CANCELLED")
