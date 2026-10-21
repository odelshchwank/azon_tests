import pytest

from data.reviews import ReviewData

pytestmark = [pytest.mark.reviews]


class TestReviews:
    @pytest.mark.negative
    def test_extra_field_is_forbidden(
        self,
        api_manager,
        authenticated_user,
        created_product,
    ):
        response = api_manager.review_api.create_review(
            created_product.id,
            ReviewData.review_with_extra_field(),
            expected_status=422,
        )

        assert response.json()["detail"][0]["type"] == "extra_forbidden"
