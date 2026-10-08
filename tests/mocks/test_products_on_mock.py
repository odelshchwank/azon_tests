import uuid
from decimal import Decimal

import pytest

from mocks.stubs import product_body, ProductStubs, PRODUCTS_ENDPOINT
from models.products import ProductResponse

pytestmark = [pytest.mark.mock, pytest.mark.products]


def test_stub_body_matches_contract():
    product = ProductResponse.model_validate(product_body(str(uuid.uuid4())))

    assert product.price == Decimal("19990.00")
    
def test_product_card_turns_into_model(wiremock, mock_products_api):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.product_found(product_id))

    response = mock_products_api.get_product(product_id)

    product = ProductResponse.model_validate(response.json())
    assert str(product.id) == product_id
    assert product.sku == "MOCK-0001"

def test_missing_product_returns_error_code(wiremock, mock_products_api):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.product_not_found(product_id))

    response = mock_products_api.get_product(product_id, expected_status=404)

    assert response.json()["error"]["code"] == "PRODUCT_NOT_FOUND"

def test_client_asks_for_specific_product(wiremock, mock_products_api):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.product_found(product_id))

    mock_products_api.get_product(product_id)

    sent = wiremock.find_requests(
        {
            "method": "GET",
            "urlPathPattern": f"{PRODUCTS_ENDPOINT}/.*",
        },
    )
    assert [request["url"] for request in sent] == [f"{PRODUCTS_ENDPOINT}/{product_id}"]
