import re

import allure
import pytest
from playwright.sync_api import expect

from data.users import UserData
from pages.catalog_page import CatalogPage
from pages.login_page import LoginPage

pytestmark = [pytest.mark.ui, pytest.mark.mobile]

MOBILE_WIDTH = 390


def page_width(page):
    return page.evaluate(
        "() => ({scroll: document.documentElement.scrollWidth,"
        " client: document.documentElement.clientWidth})"
    )


@allure.epic("Витрина AZON")
@allure.feature("Мобильная вёрстка")
class TestMobileUI:
    @allure.story("Размер экрана")
    @allure.title("Viewport соответствует iPhone 13")
    def test_viewport_is_phone_sized(self, mobile_page):
        CatalogPage(mobile_page).open()

        assert mobile_page.viewport_size["width"] == MOBILE_WIDTH

    @allure.story("Гость и корзина")
    @allure.title("Тап по «В корзину» на телефоне ведёт на /login")
    def test_tap_on_add_to_cart_sends_guest_to_login(self, mobile_page):
        catalog_page = CatalogPage(mobile_page).open()

        catalog_page.cards.first.get_by_test_id("add-to-cart").tap()

        expect(mobile_page).to_have_url(re.compile(r"/login"))
        expect(LoginPage(mobile_page).form).to_be_visible()

    @allure.story("Боковая прокрутка")
    @allure.title("У авторизованного пользователя нет боковой прокрутки")
    @pytest.mark.xfail(
        strict=True,
        reason="AZON-207: шапка авторизованного пользователя не помещается в 390 px",
    )
    def test_logged_in_catalog_has_no_side_scroll(self, mobile_page, api_manager):
        user = UserData.registration_data()
        api_manager.auth_api.register_user(user)

        login_page = LoginPage(mobile_page).open()
        login_page.login(user.email, user.password)
        expect(login_page.profile_link).to_have_text(user.email)

        CatalogPage(mobile_page).open()

        width = page_width(mobile_page)

        assert width["scroll"] <= width["client"], (
            f"Страница шире экрана: {width['scroll']} px против {width['client']} px"
        )

    @allure.story("Боковая прокрутка")
    @allure.title("У гостя нет боковой прокрутки")
    def test_unauthorized_user_has_no_side_scroll(self, mobile_page):
        CatalogPage(mobile_page).open()

        width = page_width(mobile_page)

        assert width["scroll"] <= width["client"], (
            f"Страница шире экрана: {width['scroll']} px против {width['client']} px"
        )

    @allure.story("Одна колонка")
    @allure.title("Карточка занимает всю ширину на телефоне")
    def test_catalog_is_single_column(self, mobile_page):
        catalog_page = CatalogPage(mobile_page).open()

        card = catalog_page.cards.first.bounding_box()

        assert card["width"] > MOBILE_WIDTH * 0.9, (
            f"Карточка занимает {card['width']} px - на телефоне ожидали одну колонку во всю ширину"
        )

    @allure.story("Поиск на телефоне")
    @allure.title("Поиск на телефоне находит товар")
    def test_search_on_phone_finds_products(self, mobile_page, created_product):
        catalog_page = CatalogPage(mobile_page).open()
        catalog_page.search(created_product.name)

        expect(catalog_page.cards).to_have_count(1)
        expect(catalog_page.card(created_product.name)).to_be_visible()
