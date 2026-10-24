import allure
import pytest
from playwright.sync_api import expect

from data.users import UserData
from pages.login_page import LoginPage
from pages.register_page import RegisterPage

pytestmark = [pytest.mark.ui, pytest.mark.auth]


@allure.epic("Витрина AZON")
@allure.feature("Авторизация")
class TestAuthUI:
    @allure.story("Вход в аккаунт")
    @allure.title("Успешный вход меняет шапку на пользовательскую")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_login_positive(self, page, ui_user):
        login_page = LoginPage(page).open()
        login_page.login(ui_user.email, ui_user.password)

        expect(login_page.header.profile_link).to_have_text(ui_user.email)
        expect(login_page.header.logout_button).to_be_visible()
        expect(login_page.header.login_link).to_have_count(0)

        login_page.header.logout()
        expect(login_page.header.login_link).to_be_visible()

    @allure.story("Вход в аккаунт")
    @allure.title("Неверный пароль показывает ошибку")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.negative
    def test_login_with_wrong_password(self, page, ui_user, api_manager):
        login_page = LoginPage(page).open()
        login_page.login(ui_user.email, "wrong-password-123")

        expect(login_page.error).to_be_visible()
        expect(login_page.error).to_have_text("Invalid email or password")

    @allure.story("Регистрация")
    @allure.title("После регистрации витрина ведёт на страницу входа")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_registration_through_form_leads_to_login(self, page):
        user = UserData.registration_data()
        register_page = RegisterPage(page).open()

        register_page.register(user.full_name, user.email, user.password)

        login_page = LoginPage(page)
        expect(login_page.flash).to_have_text("Аккаунт создан — войдите")
        expect(login_page.form).to_be_visible()
