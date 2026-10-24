import allure
from playwright.sync_api import Page, expect

from data.orders import Cards
from pages.base_page import BasePage


class OrderPage(BasePage):
    url = "/orders"

    def __init__(self, page: Page):
        super().__init__(page)

        self.order_id = page.get_by_test_id("order-id")
        self.status = page.get_by_test_id("order-status")
        self.order_total = page.get_by_test_id("order-total")
        self.item = page.get_by_test_id("order-item")

        self.payment_form = page.get_by_test_id("payment-form")
        self.card_number = page.get_by_test_id("card-number")
        self.card_holder = page.get_by_test_id("card-holder")
        self.exp_month = page.get_by_test_id("card-exp-month")
        self.exp_year = page.get_by_test_id("card-exp-year")
        self.cvc = page.get_by_test_id("card-cvc")
        self.pay_button = page.get_by_test_id("pay-button")

        self.processing = page.get_by_test_id("payment-processing")
        self.payments = page.get_by_test_id("payment-row")
        self.decline_code = page.get_by_test_id("payment-decline-code")
        self.cancel_button = page.get_by_test_id("cancel-order-button")

    @allure.step("Оплачиваем заказ картой {card_number}")
    def pay(
        self,
        card_number=Cards.SUCCESS,
        holder="TEST STUDENT",
        month="12",
        year="2030",
        cvc="123",
    ):
        self.card_number.fill(card_number)
        self.card_holder.fill(holder)
        self.exp_month.fill(month)
        self.exp_year.fill(year)
        self.cvc.fill(cvc)
        self.pay_button.click()

    @allure.step("Отменяем заказ")
    def cancel(self):
        self.cancel_button.click()

    def get_decline_code_for_declined_payment(self):
        row = self.payments.filter(has_text="DECLINED")
        return row.get_by_test_id("payment-decline-code")

    def get_succeeded_payment(self):
        return self.payments.filter(has_text="SUCCEEDED")
