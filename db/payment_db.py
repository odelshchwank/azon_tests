from db.db_client import DBClient


class PaymentDB(DBClient):
    """azon_payment: заказы, позиции заказов, платежи."""

    def get_order(self, order_id):
        return self.fetch_one("SELECT * FROM orders WHERE id = %s", (order_id,))

    def get_order_items(self, order_id):
        return self.fetch_all(
            "SELECT * FROM order_items WHERE order_id = %s ORDER BY product_name",
            (order_id,),
        )

    def count_orders(self, user_id):
        row = self.fetch_one(
            "SELECT count(*) AS total FROM orders WHERE user_id = %s", (user_id,)
        )
        return row["total"]

    def get_payment_by_order(self, order_id):
        return self.fetch_one(
            """
            SELECT id, status, decline_code, card_last4, amount
            FROM payments
            WHERE order_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (order_id,),
        )

    def get_transactions_by_payment(self, payment_id):
        return self.fetch_all(
            """
            SELECT id, type, status, amount
            FROM transactions
            WHERE payment_id = %s
            ORDER BY created_at
            """,
            (payment_id,),
        )
