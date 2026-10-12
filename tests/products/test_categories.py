import pytest

from models.categories import CategoryResponse

pytestmark = [pytest.mark.products, pytest.mark.contract]


def test_all_categories_match_contract(api_manager):
    response = api_manager.categories_api.get_categories()

    categories = [CategoryResponse.model_validate(item) for item in response.json()]

    assert categories, "На стенде нет ни одной категории"
    assert all(category.slug for category in categories)
