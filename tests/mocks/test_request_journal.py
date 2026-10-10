import json

import pytest

from data.users import UserData
from mocks.stubs import ME_ENDPOINT, REGISTER_ENDPOINT, AuthStubs, LOGIN_ENDPOINT
from tests.conftest import mock_auth

pytestmark = [pytest.mark.mock, pytest.mark.auth]


def test_token_goes_with_every_request(wiremock, mock_auth):
    auth_api, user_api = mock_auth
    wiremock.add_stub(AuthStubs.login_ok())
    wiremock.add_stub(AuthStubs.me_requires_bearer())
    wiremock.add_stub(AuthStubs.me_accepts_patch())
    data = UserData.login_data(UserData.registration_data())

    auth_api.authenticate(data)
    user_api.get_user_info()
    user_api.update_user_info(UserData.update_profile_data())

    with_token = {
        "urlPath": ME_ENDPOINT,
        "headers": {
            "Authorization": {
                "equalTo": "Bearer mock-access-token",
            },
        },
    }
    assert wiremock.count_requests(with_token) == 2


def test_registration_body_has_no_nulls(wiremock, mock_auth):
    auth_api, _ = mock_auth
    wiremock.add_stub(AuthStubs.register_ok())
    registration = UserData.registration_data()

    auth_api.register_user(registration)

    sent = wiremock.find_requests(
        {
            "method": "POST",
            "urlPath": REGISTER_ENDPOINT,
        },
    )[0]
    assert json.loads(sent["body"]) == {
        "email": registration.email,
        "password": registration.password,
        "full_name": registration.full_name,
    }


def test_password_goes_only_into_the_body(wiremock, mock_auth):
    auth_api, _ = mock_auth
    wiremock.add_stub(AuthStubs.login_ok())
    data = UserData.login_data(UserData.registration_data())

    auth_api.authenticate(data)

    sent = wiremock.find_requests(
        {
            "method": "POST",
            "urlPath": LOGIN_ENDPOINT,
        }
    )[0]
    assert sent["url"] == LOGIN_ENDPOINT
    assert data.password not in json.dumps(sent["headers"], ensure_ascii=False)
    assert json.loads(sent["body"])["password"] == data.password
