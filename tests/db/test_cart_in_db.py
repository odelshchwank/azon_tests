from decimal import Decimal

import pytest

from data.products import ProductData
from utils.marks import requires_admin, requires_db

pytestmark = [pytest.mark.db, pytest.mark.products, requires_db, requires_admin]


def test_cart_item_keeps_price_at_add(
    api_manager, admin_manager, authenticated_user, created_product, db
):
    original_price = created_product.price
    new_price = original_price + Decimal("1000.00")

    api_manager.cart_api.add_item(
        ProductData.cart_item_data(created_product.id, quantity=2)
    )

    admin_manager.products_api.update_price(
        created_product.id,
        ProductData.price_data(new_price=new_price),
    )

    items = db.product.get_cart_items(authenticated_user.profile.id)
    assert len(items) == 1
    assert items[0]["quantity"] == 2
    assert items[0]["price_at_add"] == original_price

    cart = api_manager.cart_api.get_cart().json()
    assert cart["items"][0]["current_price"] == str(new_price)
    assert cart["items"][0]["price_changed"] is True
