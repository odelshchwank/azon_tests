import allure
import pytest
from playwright.sync_api import expect

from pages.cart_page import CartPage
from pages.catalog_page import CatalogPage

pytestmark = [pytest.mark.ui, pytest.mark.cart]


@allure.epic("Витрина AZON")
@allure.feature("Корзина")
class TestCartUI:
    @allure.story("Добавление товара")
    @allure.title("Кнопка «В корзину» добавляет товар в корзину")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_shows_added_product(self, logged_in_page, created_product):
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)
        expect(catalog_page.header.cart_count).to_have_text("1")

        catalog_page.header.go_to_cart()

        cart_page = CartPage(logged_in_page)
        expect(cart_page.items).to_have_count(1)
        expect(cart_page.item(created_product.name)).to_be_visible()

    @allure.story("Добавление товара")
    @allure.title("Кнопка «В корзину» показывает тост и обновляет бейдж")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_shows_toast_and_updates_badge(
        self, logged_in_page, created_product
    ):
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.search(created_product.name)

        catalog_page.add_to_cart(created_product.name)

        expect(catalog_page.toast).to_have_text("Товар добавлен в корзину")
        expect(catalog_page.header.cart_count).to_have_text("1")

    @allure.story("Бейдж корзины")
    @allure.title("У пользователя с пустой корзиной бейдж показывает 0")
    def test_cart_badge_shows_zero(self, logged_in_page):
        CatalogPage(logged_in_page).open()
        expect(CatalogPage(logged_in_page).header.cart_count).to_have_text("0")

    @allure.story("Содержимое корзины")
    @allure.title("Смена количества пересчитывает итог")
    def test_quantity_change_updates_total(self, logged_in_page, created_product):
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)
        expect(catalog_page.header.cart_count).to_have_text("1")

        catalog_page.header.go_to_cart()

        cart_page = CartPage(logged_in_page)
        one_item_total = cart_page.total.inner_text()

        cart_page.set_quantity(created_product.name, 3)

        expect(
            cart_page.item(created_product.name).get_by_test_id("cart-item-quantity")
        ).to_have_value("3")
        expect(cart_page.total).not_to_have_text(one_item_total)

    @allure.story("Содержимое корзины")
    @allure.title("Пустая корзина показывает заглушку")
    @allure.severity(allure.severity_level.MINOR)
    def test_empty_cart_shows_empty_state(self, logged_in_page):
        cart_page = CartPage(logged_in_page).open()

        expect(cart_page.empty).to_be_visible()
        expect(cart_page.checkout_button).to_have_count(0)

    @allure.story("Удаление товара")
    @allure.title("Кнопка «Очистить корзину» очищает корзину и показывает заглушку")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_remove_item_empties_cart(self, logged_in_page, created_product):
        catalog_page = CatalogPage(logged_in_page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)
        expect(catalog_page.header.cart_count).to_have_text("1")

        catalog_page.header.go_to_cart()
        cart_page = CartPage(logged_in_page)

        cart_page.remove(created_product.name)

        expect(cart_page.empty).to_be_visible()
        expect(cart_page.items).to_have_count(0)
