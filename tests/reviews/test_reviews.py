import pytest

from data.reviews import ReviewData
from models.reviews import ReviewResponse

pytestmark = [pytest.mark.reviews]


class TestReviewsPositive:
    @pytest.mark.smoke
    @pytest.mark.contract
    def test_create_valid_review(
        self,
        api_manager,
        authenticated_user,
        created_product,
    ):
        payload = ReviewData.creation_review_data()
        response = api_manager.review_api.create_review(created_product.id, payload)

        review = ReviewResponse.model_validate(response.json())
        assert review.rating == payload.rating
        assert review.text == payload.text
        assert review.product_id == created_product.id


@pytest.mark.negative
class TestReviewsNegative:
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

    @pytest.mark.roles
    def test_user_cannot_edit_other_review(self, other_user, created_review):
        response = other_user.review_api.update_review(
            created_review.id,
            ReviewData.update_review_data(),
            expected_status=403,
        ).json()

        assert response["error"]["code"] == "NOT_REVIEW_OWNER"

    @pytest.mark.roles
    def test_user_cannot_delete_other_review(self, other_user, created_review):
        response = other_user.review_api.delete_review(
            created_review.id,
            expected_status=403,
        ).json()

        assert response["error"]["code"] == "NOT_REVIEW_OWNER"
