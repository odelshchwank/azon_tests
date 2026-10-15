import allure

from pages.base_page import BasePage

SUCCESS_CARD = "4242424242424242"
DECLINED_CARD = "4000000000000002"
PROCESSING_CARD = "4000000000003220"


class OrdersPage(BasePage):
    url = "/orders"

    def __init__(self, page):
        super().__init__(page)

        self.empty = page.get_by_test_id("orders-empty")

        self.table = page.get_by_test_id("orders-table")
        self.rows = page.get_by_test_id("order-row")

    def item_by_short_id(self, short_id: str):
        return self.rows.filter(has_text=short_id)

    def row(self, order_id):
        return self.rows.filter(has_text=str(order_id)[:8])

    @allure.step("Открываем первый заказ из списка")
    def open_first(self):
        self.rows.first.get_by_test_id("order-link").click()
