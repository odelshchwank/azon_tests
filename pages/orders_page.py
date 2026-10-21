from pages.base_page import BasePage


class OrdersPage(BasePage):
    url = "/orders"

    def __init__(self, page):
        super().__init__(page)

        self.empty = page.get_by_test_id("orders-empty")

        self.table = page.get_by_test_id("orders-table")
        self.rows = page.get_by_test_id("order-row")

    def row(self, order_id):
        return self.rows.filter(has_text=str(order_id)[:8])

    def get_order_status(self, order_id):
        row = self.row(order_id)
        return row.get_by_test_id("order-status")
