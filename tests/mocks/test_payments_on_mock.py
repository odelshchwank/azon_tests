import uuid

import pytest
import requests.exceptions

from data.orders import OrderData
from mocks.stubs import PaymentStubs

pytestmark = [pytest.mark.mock, pytest.mark.payment]


def test_slow_payment_hits_read_timeout(
    wiremock,
    mock_payment_api,
):
    order_id = str(uuid.uuid4())
    wiremock.add_stub(PaymentStubs.slow_payment(order_id))
    with pytest.raises(requests.exceptions.ReadTimeout):
        mock_payment_api.pay_order(
            order_id,
            OrderData.payment_slow(),
            timeout=1,
        )
