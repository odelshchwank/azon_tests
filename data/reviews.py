from models.reviews import ReviewCreateRequest, ReviewUpdateRequest
from utils.data_generator import DataGenerator


class ReviewData:
    @staticmethod
    def creation_review_data(rating=5):
        return ReviewCreateRequest(
            rating=rating,
            text=DataGenerator.generate_review_text(),
        )

    @staticmethod
    def update_review_data(rating=None) -> ReviewUpdateRequest:
        return ReviewUpdateRequest(
            rating=rating,
            text=DataGenerator.generate_review_text(),
        )

    @staticmethod
    def review_with_extra_field() -> dict:
        return {
            "rating": 5,
            "text": DataGenerator.generate_review_text(),
            "sku": "бибабоба, этого поля быть не должно",
        }
