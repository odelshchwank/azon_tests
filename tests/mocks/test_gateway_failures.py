import uuid

import pytest
import requests.exceptions

from mocks.stubs import ProductStubs

pytestmark = [pytest.mark.mock, pytest.mark.negative]


def test_gateway_error_is_reported_clearly(wiremock, mock_products_api):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.gateway_error(product_id))

    with pytest.raises(AssertionError) as error:
        mock_products_api.get_product(product_id)

    assert "ожидали статус 200, получили 503" in str(error.value)
    assert "GATEWAY_ERROR" in str(error.value)


def test_client_gives_up_after_two_seconds(wiremock, mock_products_api):
    product_id = str(uuid.uuid4())
    wiremock.add_stub(ProductStubs.slow_product(product_id, delay_ms=5000))

    with pytest.raises(requests.exceptions.ReadTimeout):
        mock_products_api.get_product(product_id, timeout=2)
