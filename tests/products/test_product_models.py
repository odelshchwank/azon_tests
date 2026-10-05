import uuid

import pytest
from pydantic import ValidationError

from data.products import ProductData
from models.products import ProductRequest

pytestmark = pytest.mark.products


def test_model_rejects_zero_price():
    product_request = ProductData.creation_product_data(uuid.uuid4())

    with pytest.raises(ValidationError) as error:
        ProductRequest.model_validate({**product_request.model_dump(), "price": 0})

    assert error.value.errors()[0]["type"] == "greater_than"
