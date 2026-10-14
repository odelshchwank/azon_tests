import re
from decimal import Decimal

import pytest
from playwright.sync_api import expect

from pages.catalog_page import CatalogPage

pytestmark = [pytest.mark.ui, pytest.mark.products]


def parse_price(text: str) -> Decimal:
    return Decimal(re.sub(r"[^\d.]", "", text))


class TestCatalogUI:
    def test_catalog_shows_products(self, page):
        catalog_page = CatalogPage(page).open()

        expect(catalog_page.title).to_have_text("Каталог")
        expect(catalog_page.total).to_contain_text("Найдено товаров")
        expect(catalog_page.cards.first).to_be_visible()

    @pytest.mark.negative
    def test_search_without_results_shows_empty_state(self, page):
        catalog_page = CatalogPage(page).open()
        catalog_page.search("хуерга плотная")

        expect(catalog_page.empty).to_be_visible()
        expect(catalog_page.cards).to_have_count(0)

    def test_category_filter_narrows_catalog(self, page):
        catalog_page = CatalogPage(page).open()
        all_products = catalog_page.total.inner_text()

        catalog_page.choose_category("Книги")

        expect(catalog_page.category_select.locator("option:checked")).to_have_text(
            "Книги"
        )
        expect(catalog_page.total).not_to_have_text(all_products)

    def test_sort_catalog_by_price_ascending(self, page):
        catalog_page = CatalogPage(page).open()
        catalog_page.sort_by("По цене", order="По возрастанию")

        expect(catalog_page.sort_select.locator("option:checked")).to_have_text(
            "По цене"
        )
        expect(catalog_page.order_select.locator("option:checked")).to_have_text(
            "По возрастанию"
        )

        prices = [
            parse_price(t)
            for t in catalog_page.cards.get_by_test_id(
                "product-price"
            ).all_inner_texts()
        ]
        assert prices == sorted(prices), f"Цены не по возрастанию: {prices}"

    def test_catalog_pagination_moves_to_second_page(self, page):
        catalog_page = CatalogPage(page).open()

        first_page_ids = catalog_page.cards.all_inner_texts()

        catalog_page.next_page_button.click()

        expect(page).to_have_url(re.compile(r"[?&]page=2(&|$)"))
        expect(catalog_page.cards.first).to_be_visible()

        second_page_ids = catalog_page.cards.all_inner_texts()
        assert first_page_ids != second_page_ids, (
            "Вторая страница показывает те же товары, что и первая"
        )

    def test_guest_add_to_cart_goes_to_login(self, page, created_product):
        catalog_page = CatalogPage(page).open()
        catalog_page.search(created_product.name)
        catalog_page.add_to_cart(created_product.name)

        expect(page).to_have_url(re.compile(r"/login"))

    def test_search_finds_created_product(self, page, created_product):
        catalog_page = CatalogPage(page).open()
        catalog_page.search(created_product.name)

        expect(catalog_page.cards).to_have_count(1)
        expect(catalog_page.card(created_product.name)).to_be_visible()
