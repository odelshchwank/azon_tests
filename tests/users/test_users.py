import pytest

from data.users import UserData
from models.users import UserResponse
from utils.data_generator import DataGenerator

pytestmark = [pytest.mark.users, pytest.mark.regression]


class TestUser:
    @pytest.mark.negative
    @pytest.mark.roles
    def test_get_user_info_without_token(self, api_manager):
        response = api_manager.user_api.get_user_info(expected_status=401)
        assert response.json()["error"]["code"] == "TOKEN_MISSING"

    def test_get_user_info(self, api_manager, authenticated_user):
        body = UserResponse.model_validate(
            api_manager.user_api.get_user_info(expected_status=200).json()
        )

        assert body.email == authenticated_user.registration.email
        assert body.id == authenticated_user.profile.id

    def test_update_full_name(self, api_manager, authenticated_user):
        new_profile = UserData.update_profile_data()

        response = api_manager.user_api.update_user_info(new_profile).json()

        assert response["full_name"] == new_profile["full_name"]
        expected_name = api_manager.user_api.get_user_info().json()["full_name"]
        assert expected_name == new_profile["full_name"]

    @pytest.mark.slow
    def test_change_password(self, api_manager, authenticated_user):
        new_password = DataGenerator.generate_password()

        api_manager.user_api.change_password(
            UserData.change_password_data(authenticated_user.registration, new_password)
        )

        old_credentials = UserData.login_data(authenticated_user.registration)
        response = api_manager.auth_api.login_user(old_credentials, expected_status=401)
        assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"

        api_manager.auth_api.authenticate(
            UserData.login_data(authenticated_user.registration).model_copy(
                update={"password": new_password}
            )
        )
