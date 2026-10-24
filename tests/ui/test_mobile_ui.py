import re

import allure
import pytest
from playwright.sync_api import expect

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
    @allure.story("Боковая прокрутка")
    @allure.title("У авторизованного пользователя нет боковой прокрутки")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason="AZON-207: шапка авторизованного пользователя не помещается в 390 px",
    )
    def test_logged_in_catalog_has_no_side_scroll(self, logged_in_mobile_user):
        CatalogPage(logged_in_mobile_user).open()
        width = page_width(logged_in_mobile_user)
        assert width["scroll"] <= width["client"], (
            f"Страница шире экрана: {width['scroll']} px против {width['client']} px"
        )

    @allure.story("Гость и корзина")
    @allure.title("Тап по «В корзину» на телефоне ведёт на /login")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_tap_on_add_to_cart_sends_guest_to_login(self, mobile_page):
        catalog_page = CatalogPage(mobile_page).open()

        catalog_page.tap_add_to_cart()

        expect(mobile_page).to_have_url(re.compile(r"/login"))
        expect(LoginPage(mobile_page).form).to_be_visible()

    @allure.story("Боковая прокрутка")
    @allure.title("У гостя нет боковой прокрутки")
    @allure.severity(allure.severity_level.MINOR)
    def test_unauthorized_user_has_no_side_scroll(self, mobile_page):
        CatalogPage(mobile_page).open()

        width = page_width(mobile_page)

        assert width["scroll"] <= width["client"], (
            f"Страница шире экрана: {width['scroll']} px против {width['client']} px"
        )

    @allure.story("Одна колонка")
    @allure.title("Карточка занимает всю ширину на телефоне")
    @allure.severity(allure.severity_level.MINOR)
    def test_catalog_is_single_column(self, mobile_page):
        catalog_page = CatalogPage(mobile_page).open()

        card = catalog_page.cards.first.bounding_box()

        assert card["width"] > MOBILE_WIDTH * 0.9, (
            f"Карточка занимает {card['width']} px - на телефоне ожидали одну колонку во всю ширину"
        )

    @allure.story("Поиск на телефоне")
    @allure.title("Поиск на телефоне находит товар")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_on_phone_finds_products(self, mobile_page, created_product):
        catalog_page = CatalogPage(mobile_page).open()
        catalog_page.search(created_product.name)

        expect(catalog_page.cards).to_have_count(1)
        expect(catalog_page.card(created_product.name)).to_be_visible()
