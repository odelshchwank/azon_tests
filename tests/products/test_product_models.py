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


@pytest.mark.parametrize(
    "field, value, expected_type",
    [
        ("sku", "Скебобчик дикий с пробелами", "string_pattern_mismatch"),
        ("name", "", "string_too_short"),
        ("stock", -1, "greater_than_equal"),
        ("price", "1000001", "less_than_equal"),
    ],
)
def test_model_rejects_bad_field(field, value, expected_type):
    positive = ProductData.creation_product_data(uuid.uuid4()).model_dump()

    with pytest.raises(ValidationError) as error:
        ProductRequest.model_validate({**positive, field: value})

    assert error.value.errors()[0]["type"] == expected_type
    assert error.value.errors()[0]["loc"] == (field,)
