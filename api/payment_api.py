from config.hosts import PAYMENT_URL
from models.orders import CheckoutRequest
from requester.custom_requester import CustomRequester


class PaymentAPI(CustomRequester):
    ORDERS_ENDPOINT = "/api/v1/orders"
    PAYMENT_ENDPOINT = "/api/v1/payments"

    def __init__(self, session, base_url=PAYMENT_URL):
        super().__init__(session, base_url)

    def get_order(self, order_id, expected_status=200):
        return self.send_request(
            "GET", f"{self.ORDERS_ENDPOINT}/{order_id}", expected_status=expected_status
        )

    def get_orders(self, params=None, expected_status=200):
        return self.send_request(
            "GET",
            self.ORDERS_ENDPOINT,
            params=params,
            expected_status=expected_status,
        )

    def checkout(
        self,
        request: CheckoutRequest | None = None,
        expected_status=201,
    ):
        return self.send_request(
            "POST",
            f"{self.ORDERS_ENDPOINT}/checkout",
            json=request or CheckoutRequest(),
            expected_status=expected_status,
        )

    def pay_order(self, order_id, pay_request, expected_status=201, **kwargs):
        return self.send_request(
            "POST",
            f"{self.ORDERS_ENDPOINT}/{order_id}/pay",
            json=pay_request,
            expected_status=expected_status,
            **kwargs,
        )

    def get_order_payments(self, order_id, expected_status=200):
        return self.send_request(
            "GET",
            f"{self.ORDERS_ENDPOINT}/{order_id}/payments",
            expected_status=expected_status,
        )

    def get_payment(self, payment_id, expected_status=200):
        return self.send_request(
            "GET",
            f"{self.PAYMENT_ENDPOINT}/{payment_id}",
            expected_status=expected_status,
        )

    def cancel_order(self, order_id, expected_status=200):
        return self.send_request(
            "POST",
            f"{self.ORDERS_ENDPOINT}/{order_id}/cancel",
            expected_status=expected_status,
        )
