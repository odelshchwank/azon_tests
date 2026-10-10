from unittest.mock import MagicMock

import pytest

from api.user_api import UserAPI
from config.hosts import AUTH_URL
from data.users import UserData
from mocks.helpers import fake_response

pytestmark = [pytest.mark.mock, pytest.mark.users]


def passwords_data():
    return UserData.change_password_data(
        UserData.registration_data(),
        "NewSecret123",
    )


def test_change_password_sends_one_post():
    session = MagicMock()
    session.request.return_value = fake_response(204)
    session.headers = {}
    passwords = passwords_data()

    UserAPI(session).change_password(passwords)

    session.request.assert_called_once_with(
        "POST",
        f"{AUTH_URL}/api/v1/users/me/password",
        json={
            "old_password": passwords.old_password,
            "new_password": passwords.new_password,
        },
        timeout=10,
    )


def test_change_password_reports_unexpected_status():
    session = MagicMock()
    session.request.return_value = fake_response(
        400,
        '{"error": {"code": "WRONG_OLD_PASSWORD"}}',
    )
    session.headers = {}

    with pytest.raises(AssertionError) as error:
        UserAPI(session).change_password(passwords_data())

    assert "ожидали статус 204, получили 400" in str(error.value)
    assert "WRONG_OLD_PASSWORD" in str(error.value)
