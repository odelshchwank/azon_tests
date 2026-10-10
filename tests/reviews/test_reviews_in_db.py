import pytest

from data.reviews import ReviewData
from tests import conftest
from utils.marks import requires_admin, requires_db, requires_manager

pytestmark = [pytest.mark.db, pytest.mark.reviews, requires_db, requires_admin]


def test_review_is_saved_in_db(created_review, db):
    row = db.product.get_review(created_review.id)

    assert row is not None
    assert row["rating"] == created_review.rating
    assert row["text"] == created_review.text
    assert row["is_seed"] == False


def test_duplicate_review_is_idempotent(
    api_manager,
    created_review,
    created_product,
    db,
):
    api_manager.review_api.create_review(
        created_product.id, ReviewData.creation_review_data(), expected_status=409
    )

    assert db.product.count_reviews(created_product.id) == 1


@requires_manager
def test_moderation_deletes_row_and_recorded(
    store_manager,
    created_review,
    db,
):
    store_manager.review_api.delete_review(created_review.id)

    assert db.product.get_review(created_review.id) is None

    record = db.product.get_moderation_record(created_review.id)
    assert record is not None
    assert record["payload"]["author"] == str(created_review.user_id)
