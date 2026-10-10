import uuid

from faker import Faker

fake = Faker("en_US")


class DataGenerator:
    @staticmethod
    def generate_email():
        return f"student-{uuid.uuid4().hex[:8]}@example.com"

    @staticmethod
    def generate_password():
        return fake.password(length=12)

    @staticmethod
    def generate_full_name():
        return fake.name()

    @staticmethod
    def generate_product_name():
        return f"Ноутбук AZON-Pro-Gamer-3000 {uuid.uuid4().hex[:6]}"

    @staticmethod
    def generate_description():
        return fake.sentence(nb_words=10)

    @staticmethod
    def generate_price_range(min_gap: int = 1_000):
        low = fake.random_int(min=1_000, max=100_000)
        high = low + fake.random_int(min=min_gap, max=50_000)
        return low, high

    @staticmethod
    def generate_price():
        return round(fake.random.uniform(50_000, 279_990), 2)

    @staticmethod
    def generate_stock():
        return fake.random_int(min=4, max=64)

    @staticmethod
    def generate_sku():
        return f"TEST-{uuid.uuid4().hex[:12]}"

    @staticmethod
    def generate_review_text():
        return fake.sentence(nb_words=10)
