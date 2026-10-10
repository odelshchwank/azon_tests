import pytest

from data.users import UserData
from models.users import UserResponse

pytestmark = [pytest.mark.auth, pytest.mark.regression]


class TestAuth:
    @pytest.mark.smoke
    def test_register_and_login(self, api_manager):
        registration = UserData.registration_data()

        register_response = api_manager.auth_api.register_user(registration)
        assert (
            UserResponse.model_validate(register_response.json()).email
            == registration.email
        )

        api_manager.auth_api.authenticate(UserData.login_data(registration))

        me_response = api_manager.user_api.get_user_info()
        assert (
            UserResponse.model_validate(me_response.json()).email == registration.email
        )

    @pytest.mark.negative
    def test_register_with_existing_email(self, api_manager, registered_user):
        registration = UserData.registration_data().model_copy(
            update={"email": registered_user.registration.email}
        )

        response = api_manager.auth_api.register_user(registration, expected_status=409)
        assert response.json()["error"]["code"] == "EMAIL_EXISTS"

    @pytest.mark.negative
    def test_login_with_wrong_password(self, api_manager, registered_user):
        credentials = UserData.login_data(registered_user.registration).model_copy(
            update={"password": "Totally-Wrong-Password"}
        )

        response = api_manager.auth_api.login_user(credentials, expected_status=401)
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"
