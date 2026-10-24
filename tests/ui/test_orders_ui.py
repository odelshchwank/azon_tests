import allure
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.orders_page import OrdersPage

pytestmark = [pytest.mark.ui, pytest.mark.orders]


@allure.epic("Витрина AZON")
@allure.feature("Мои заказы")
class TestOrdersUI:
    @allure.story("Список заказов")
    @allure.title("Свежий заказ появляется в списке со статусом AWAITING_PAYMENT")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_new_order_appears_in_list(self, product_in_cart):
        CartPage(product_in_cart.page).open().checkout()
        order_id = product_in_cart.page.url.rsplit("/", 1)[-1]

        orders_page = OrdersPage(product_in_cart.page).open()

        expect(orders_page.row(order_id)).to_be_visible()
        expect(orders_page.get_order_status(order_id)).to_have_text("AWAITING_PAYMENT")
