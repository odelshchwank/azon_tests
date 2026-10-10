import pytest

from models.orders import OrdersPage

pytestmark = [pytest.mark.payment, pytest.mark.contract]


def test_new_user_orders_match_contract(api_manager, authenticated_user):
    response = api_manager.payment_api.get_orders()

    orders = OrdersPage.model_validate(response.json())
    assert orders.total == 0
    assert orders.items == []
