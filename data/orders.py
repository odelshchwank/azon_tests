from models.orders import PayRequest
from utils.data_generator import DataGenerator


class Cards:
    SUCCESS = "4242424242424242"
    DECLINED = "4000000000000002"
    INSUFFICIENT_FUNDS = "4000000000009995"
    GATEWAY_ERROR = "4000000000000119"
    PROCESSING = "4000000000003220"
    SLOW = "4000000006009999"


class OrderData:
    """Object Mother: готовые данные для запросов к Payment API."""

    @staticmethod
    def pay_request(card_number: str = Cards.SUCCESS) -> PayRequest:
        return PayRequest(
            card_number=card_number,
            card_holder=DataGenerator.generate_full_name().upper(),
            exp_month=12,
            exp_year=2028,
            cvc="123",
        )

    @staticmethod
    def payment_success() -> PayRequest:
        return OrderData.pay_request(Cards.SUCCESS)

    @staticmethod
    def payment_declined() -> PayRequest:
        return OrderData.pay_request(Cards.DECLINED)

    @staticmethod
    def payment_insufficient_funds() -> PayRequest:
        return OrderData.pay_request(Cards.INSUFFICIENT_FUNDS)

    @staticmethod
    def payment_gateway_error() -> PayRequest:
        return OrderData.pay_request(Cards.GATEWAY_ERROR)

    @staticmethod
    def payment_processing() -> PayRequest:
        return OrderData.pay_request(Cards.PROCESSING)

    @staticmethod
    def payment_slow() -> PayRequest:
        return OrderData.pay_request(Cards.SLOW)
