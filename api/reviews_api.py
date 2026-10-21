from config.hosts import PRODUCT_URL
from requester.custom_requester import CustomRequester


class ReviewAPI(CustomRequester):
    REVIEW_ENDPOINT = "/api/v1/reviews"
    PRODUCTS_ENDPOINT = "/api/v1/products"

    def __init__(self, session, base_url=PRODUCT_URL):
        super().__init__(session, base_url)

    def get_reviews(
        self,
        product_id,
        params=None,
        expected_status=200,
        **kwargs,
    ):
        return self.send_request(
            "GET",
            f"{self.PRODUCTS_ENDPOINT}/{product_id}/reviews",
            params=params,
            expected_status=expected_status,
            **kwargs,
        )

    def create_review(
        self,
        product_id,
        review_data,
        expected_status=201,
        **kwargs,
    ):
        return self.send_request(
            "POST",
            f"{self.PRODUCTS_ENDPOINT}/{product_id}/reviews",
            json=review_data,
            expected_status=expected_status,
            **kwargs,
        )

    def update_review(
        self,
        review_id,
        review_data,
        expected_status=200,
        **kwargs,
    ):
        return self.send_request(
            "PATCH",
            f"{self.REVIEW_ENDPOINT}/{review_id}",
            json=review_data,
            expected_status=expected_status,
            **kwargs,
        )

    def delete_review(
        self,
        review_id,
        expected_status=204,
        **kwargs,
    ):
        return self.send_request(
            "DELETE",
            f"{self.REVIEW_ENDPOINT}/{review_id}",
            expected_status=expected_status,
            **kwargs,
        )
