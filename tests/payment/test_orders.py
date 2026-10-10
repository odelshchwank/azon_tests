import pytest

from data.orders import Cards, OrderData
from models.orders import (
    OrderResponse,
    PaymentBriefResponse,
    PayResponse,
)

pytestmark = [pytest.mark.payment, pytest.mark.regression]


class TestOrdersPositive:
    def test_successful_payment_marks_order_paid(
        self,
        api_manager,
        authenticated_user,
        awaiting_order,
    ):
        response = api_manager.payment_api.pay_order(
            awaiting_order.id,
            OrderData.payment_success(),
        )
        body = PayResponse.model_validate(response.json())
        assert body.status == "SUCCEEDED"
        assert body.order_status == "PAID"

        order = OrderResponse.model_validate(
            api_manager.payment_api.get_order(awaiting_order.id).json()
        )
        assert order.status == "PAID"

    def test_payment_history_shows_declined_and_succeeded(
        self,
        api_manager,
        authenticated_user,
        awaiting_order,
    ):
        api_manager.payment_api.pay_order(
            awaiting_order.id, OrderData.payment_declined(), expected_status=402
        )
        api_manager.payment_api.pay_order(
            awaiting_order.id,
            OrderData.payment_success(),
        )

        history = [
            PaymentBriefResponse.model_validate(item)
            for item in api_manager.payment_api.get_order_payments(
                awaiting_order.id
            ).json()
        ]

        statuses = [payment.status for payment in history]
        assert "DECLINED" in statuses
        assert "SUCCEEDED" in statuses

        declined = next(payment for payment in history if payment.status == "DECLINED")
        assert declined.decline_code == "card_declined"
        assert declined.card_last4 == Cards.DECLINED[-4:]


@pytest.mark.negative
class TestOrdersNegative:
    def test_declined_card_returns_402_with_decline_code(
        self,
        api_manager,
        authenticated_user,
        awaiting_order,
    ):
        response = api_manager.payment_api.pay_order(
            awaiting_order.id,
            OrderData.payment_declined(),
            expected_status=402,
        )
        body = response.json()
        assert body["error"]["code"] == "PAYMENT_DECLINED"
        assert body["error"]["details"][0]["decline_code"] == "card_declined"

    def test_declined_payment_keeps_order_awaiting_payment(
        self,
        api_manager,
        authenticated_user,
        awaiting_order,
    ):
        api_manager.payment_api.pay_order(
            awaiting_order.id,
            OrderData.payment_declined(),
            expected_status=402,
        )
        order = OrderResponse.model_validate(
            api_manager.payment_api.get_order(awaiting_order.id).json()
        )
        assert order.status == "AWAITING_PAYMENT"

    def test_pay_paid_order_returns_409(
        self,
        api_manager,
        authenticated_user,
        paid_order,
    ):
        response = api_manager.payment_api.pay_order(
            paid_order.id,
            OrderData.payment_success(),
            expected_status=409,
        )
        assert response.json()["error"]["code"] == "ORDER_NOT_PAYABLE"

    def test_cancel_paid_order_returns_409(
        self,
        api_manager,
        authenticated_user,
        paid_order,
    ):
        response = api_manager.payment_api.cancel_order(
            paid_order.id,
            expected_status=409,
        )
        assert response.json()["error"]["code"] == "INVALID_ORDER_STATUS"

    def test_checkout_with_empty_cart_returns_400(
        self,
        api_manager,
        authenticated_user,
    ):
        response = api_manager.payment_api.checkout(expected_status=400)
        assert response.json()["error"]["code"] == "CART_EMPTY"

    @pytest.mark.roles
    def test_other_user_cannot_read_order(
        self,
        other_user,
        awaiting_order,
    ):
        response = other_user.payment_api.get_order(
            awaiting_order.id,
            expected_status=404,
        )
        assert response.json()["error"]["code"] == "ORDER_NOT_FOUND"

    @pytest.mark.roles
    def test_other_user_cannot_pay_order(
        self,
        other_user,
        awaiting_order,
    ):
        response = other_user.payment_api.pay_order(
            awaiting_order.id,
            OrderData.payment_success(),
            expected_status=404,
        )
        assert response.json()["error"]["code"] == "ORDER_NOT_FOUND"
