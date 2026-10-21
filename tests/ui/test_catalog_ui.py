import re
import uuid

import allure
import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage

pytestmark = [pytest.mark.ui, pytest.mark.products]


@allure.epic("Витрина AZON")
@allure.feature("Каталог")
class TestCatalogUI:
    @allure.story("Отображение каталога")
    @allure.title("Каталог показывает товары и счётчик")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_catalog_shows_products(self, page):
        catalog_page = CatalogPage(page).open()

        expect(catalog_page.title).to_have_text("Каталог")
        expect(catalog_page.total).to_contain_text("Найдено товаров")
        expect(catalog_page.cards.first).to_be_visible()

    @allure.story("Поиск товара")
    @allure.title("Поиск несуществующего товара показывает заглушку")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.negative
    def test_search_without_results_shows_empty_state(self, page):
        catalog_page = CatalogPage(page).open()
        catalog_page.search(str(uuid.uuid4()))

        expect(catalog_page.empty).to_be_visible()
        expect(catalog_page.cards).to_have_count(0)

    @allure.story("Фильтр по категории")
    @allure.title("Фильтр «Дом и кухня» сужает выдачу")
    @allure.severity(allure.severity_level.NORMAL)
    def test_category_filter_narrows_catalog(self, page, api_manager, created_product):
        catalog_page = CatalogPage(page).open()

        categories = api_manager.categories_api.get_categories().json()
        my_category = next(
            c for c in categories if c["id"] == str(created_product.category_id)
        )
        category_name = my_category["name"]

        all_products = int(re.sub(r"\D", "", catalog_page.total.inner_text()))

        catalog_page.choose_category(category_name)
        expect(catalog_page.selected_category).to_have_text(category_name)

        filtered_products = int(re.sub(r"\D", "", catalog_page.total.inner_text()))
        assert filtered_products < all_products, "Фильтр не сузил выдачу"

        expect(catalog_page.card(created_product.name)).to_be_visible()

    @allure.story("Сортировка")
    @allure.title("Сортировка по цене по возрастанию")
    @allure.severity(allure.severity_level.NORMAL)
    def test_sort_catalog_by_price_ascending(self, page):
        catalog_page = CatalogPage(page).open()
        catalog_page.sort_by("По цене", order="По возрастанию")

        expect(catalog_page.selected_sort).to_have_text("По цене")
        expect(catalog_page.selected_order).to_have_text("По возрастанию")

        prices = catalog_page.prices()
        assert prices == sorted(prices), f"Цены не по возрастанию: {prices}"

    @allure.story("Пагинация")
    @allure.title("Кнопка «Вперёд» открывает вторую страницу")
    @allure.severity(allure.severity_level.NORMAL)
    def test_catalog_pagination_moves_to_second_page(self, page):
        catalog_page = CatalogPage(page).open()

        first_page_ids = catalog_page.cards.all_inner_texts()

        catalog_page.go_to_next_page()

        expect(page).to_have_url(re.compile(r"[?&]page=2(&|$)"))
        expect(catalog_page.cards.first).to_be_visible()

        second_page_ids = catalog_page.cards.all_inner_texts()
        assert first_page_ids != second_page_ids, (
            "Вторая страница показывает те же товары, что и первая"
        )

    @allure.story("Гость и корзина")
    @allure.title("Гость, нажавший «В корзину», попадает на /login")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_guest_add_to_cart_goes_to_login(self, page, created_product):
        catalog_page = CatalogPage(page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)

        expect(page).to_have_url(re.compile(r"/login"))

    @allure.story("Поиск товара")
    @allure.title("Поиск находит товар из фикстуры")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_finds_created_product(self, page, created_product):
        catalog_page = CatalogPage(page).open()
        catalog_page.search(created_product.name)

        expect(catalog_page.cards).to_have_count(1)
        expect(catalog_page.card(created_product.name)).to_be_visible()
