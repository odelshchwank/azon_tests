from db.db_client import DBClient


class ProductDB(DBClient):
    """azon_product: каталог, корзина, отзывы."""

    def get_product(self, product_id):
        return self.fetch_one("SELECT * FROM products WHERE id = %s", (product_id,))

    def get_product_by_sku(self, sku):
        return self.fetch_one("SELECT * FROM products WHERE sku = %s", (sku,))

    def get_cart_items(self, user_id):
        return self.fetch_all(
            """
            SELECT ci.product_id, ci.quantity, ci.price_at_add, p.name
            FROM cart_items ci
            JOIN carts c ON c.id = ci.cart_id
            JOIN product p ON p.id = ci.product_id
            WHERE user_id = %s
            ORDER BY ci.added_at
            """,
            (user_id,),
        )
