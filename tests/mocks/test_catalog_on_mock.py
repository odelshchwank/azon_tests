from decimal import Decimal

import pytest

from mocks.stubs import ProductStubs, product_body
from models.products import ProductsPage

pytestmark = [pytest.mark.mock, pytest.mark.products]


def test_catalog_page_turns_into_model(wiremock, mock_products_api):
    items = [
        product_body("11111111111111111111111111111111", sku="MOCK-1"),
        product_body("22222222222222222222222222222222", sku="MOCK-2", price="1000.00"),
    ]
    wiremock.add_stub(ProductStubs.catalog_page(items))

    response = mock_products_api.get_products(params={"page": 1, "size": 2})

    page = ProductsPage.model_validate(response.json())
    assert page.total == 2
    assert [product.sku for product in page.items] == ["MOCK-1", "MOCK-2"]
    assert page.items[1].price == Decimal("1000.00")
