import json
import uuid
from unittest.mock import MagicMock

import pytest
import requests

from api.reviews_api import ReviewAPI
from config.hosts import PRODUCT_URL, MOCK_URL
from data.reviews import ReviewData
from mocks.helpers import fake_response
from mocks.stubs import PRODUCT_ID, ReviewStubs, JSON_HEADERS
from models.reviews import ReviewsPage

pytestmark = [pytest.mark.mock, pytest.mark.reviews]

REVIEW_ID = "22222222222222222222222222222222"


def test_delete_review_without_net():
    session = MagicMock()
    session.request.return_value = fake_response(
        204,
        url=f"{PRODUCT_URL}/api/v1/reviews/{REVIEW_ID}",
        method="DELETE",
    )
    session.headers = {}

    ReviewAPI(session).delete_review(REVIEW_ID)

    session.request.assert_called_once_with(
        "DELETE",
        f"{PRODUCT_URL}/api/v1/reviews/{REVIEW_ID}",
        timeout=10,
    )


def test_reviews_page_turns_into_model(wiremock, mock_reviews_api):
    wiremock.add_stub(
        ReviewStubs.reviews_page_stub(
            [
                ReviewStubs.review_body(5),
                ReviewStubs.review_body(
                    rating=1,
                    id=str(uuid.uuid4()),
                ),
            ],
        )
    )

    response = mock_reviews_api.get_reviews(PRODUCT_ID)

    page = ReviewsPage.model_validate(response.json())
    assert page.total == 2
    assert [review.rating for review in page.items] == [5, 1]


@pytest.mark.negative
def test_server_error_message_is_readable_reviews(wiremock, mock_reviews_api):
    wiremock.add_stub(ReviewStubs.reviews_server_error())

    with pytest.raises(AssertionError) as error:
        mock_reviews_api.get_reviews(PRODUCT_ID)

    assert "ожидали статус 200, получили 500" in str(error.value)
    assert "INTERNAL_ERROR" in str(error.value)


def test_update_ignores_none_fields(wiremock):
    wiremock.add_stub(
        {
            "request": {
                "method": "PATCH",
                "urlPathPattern": "/api/v1/reviews/.+",
            },
            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": ReviewStubs.review_body(),
            },
        },
    )

    review_id = uuid.uuid4()
    update = ReviewData.update_review_data()

    with requests.Session() as session:
        ReviewAPI(
            session,
            base_url=MOCK_URL,
        ).update_review(review_id, update)

    sent = wiremock.find_requests(
        {"method": "PATCH", "urlPath": f"/api/v1/reviews/{review_id}"}
    )[0]
    assert json.loads(sent["body"]) == {"text": update.text}
