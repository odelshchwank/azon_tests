import allure
import pytest
from playwright.sync_api import expect

from data.orders import Cards
from pages.cart_page import CartPage
from pages.order_page import OrderPage

pytestmark = [pytest.mark.ui, pytest.mark.payment_ui]


@allure.epic("Витрина AZON")
@allure.feature("Оформление заказа")
class TestCheckoutUI:
    @allure.story("Успешная оплата")
    @allure.title("Оплата успешной картой переводит заказ в PAID")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_successful_payment_marks_order_paid(
        self, created_product, product_in_cart
    ):
        CartPage(product_in_cart.page).open().checkout()
        order_page = OrderPage(product_in_cart.page)

        order_page.pay()

        expect(order_page.flash).to_have_text("Оплата прошла успешно!")
        expect(order_page.status).to_have_text("PAID")
        expect(order_page.payments).to_have_count(1)

    @allure.story("Отказ банка")
    @allure.title("Отклонённая карта оставляет заказ неоплаченным")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_declined_card_leaves_order_unpaid(self, created_product, product_in_cart):
        CartPage(product_in_cart.page).open().checkout()
        order_page = OrderPage(product_in_cart.page)

        order_page.pay(card_number=Cards.DECLINED)

        expect(order_page.flash).to_have_text("Платёж отклонён банком (card_declined)")
        expect(order_page.status).to_have_text("AWAITING_PAYMENT")
        expect(order_page.get_decline_code_for_declined_payment()).to_have_text(
            "card_declined"
        )

    @allure.story("История платежей")
    @allure.title("История хранит и DECLINED, и SUCCEEDED")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_payment_history_keeps_declined_and_successful_attempts(
        self, created_product, product_in_cart
    ):
        CartPage(product_in_cart.page).open().checkout()
        order_page = OrderPage(product_in_cart.page)

        order_page.pay(card_number=Cards.DECLINED)
        expect(order_page.status).to_have_text("AWAITING_PAYMENT")

        order_page.pay()
        expect(order_page.status).to_have_text("PAID")

        expect(order_page.payments).to_have_count(2)

        expect(order_page.get_decline_code_for_declined_payment()).to_have_text(
            "card_declined"
        )

        expect(order_page.get_succeeded_payment()).to_have_count(1)

    @allure.story("Отмена заказа")
    @allure.title("Неоплаченный заказ можно отменить")
    @allure.severity(allure.severity_level.NORMAL)
    def test_order_can_be_cancelled(self, created_product, product_in_cart):
        CartPage(product_in_cart.page).open().checkout()
        order_page = OrderPage(product_in_cart.page)

        order_page.cancel()

        expect(order_page.flash).to_have_text("Заказ отменён")
        expect(order_page.status).to_have_text("CANCELLED")
