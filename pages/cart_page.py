from decimal import Decimal

import allure

from pages.base_page import BasePage


class CartPage(BasePage):
    url = "/cart"

    def __init__(self, page):
        super().__init__(page)

        self.table = page.get_by_test_id("cart-table")
        self.items = page.get_by_test_id("cart-item")
        self.total = page.get_by_test_id("cart-total")
        self.empty = page.get_by_test_id("cart-empty")

        self.clear_button = page.get_by_test_id("cart-clear")
        self.checkout_button = page.get_by_test_id("checkout-button")

    def item(self, name):
        return self.items.filter(has_text=name)

    @allure.step("Изменяем количество {name} на {quantity}")
    def set_quantity(self, name, quantity):
        row = self.item(name)
        row.get_by_test_id("cart-item-quantity").fill(str(quantity))
        row.get_by_test_id("cart-item-update").click()

    @allure.step("Оформляем заказ")
    def checkout(self):
        self.checkout_button.click()

    @allure.step("Удаляем {name} из корзины")
    def remove(self, name):
        self.item(name).get_by_test_id("cart-item-remove").click()

    @allure.step("Получаем поле количества «{name}»")
    def quantity_input(self, name):
        return self.item(name).get_by_test_id("cart-item-quantity")

    @allure.step("Получаем сумму строки «{name}» в виде Decimal")
    def item_subtotal(self, name) -> Decimal:
        text = self.item(name).get_by_test_id("cart-item-subtotal").inner_text()
        return self.parse_price_text(text)

    @allure.step("Получаем общий итог корзины в виде Decimal")
    def total_amount(self) -> Decimal:
        return self.parse_price_text(self.total.inner_text())
