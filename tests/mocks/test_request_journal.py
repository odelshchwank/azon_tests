import json

import pytest

from data.users import UserData
from mocks.stubs import ME_ENDPOINT, AuthStubs, REGISTER_ENDPOINT

pytestmark = [pytest.mark.mock, pytest.mark.auth]


def test_token_goes_into_every_next_request(wiremock, mock_auth):
    auth_api, user_api = mock_auth
    wiremock.add_stub(AuthStubs.login_ok())
    wiremock.add_stub(AuthStubs.me_requires_bearer())
    data = UserData.login_data(UserData.registration_data())
    
    auth_api.authenticate(data)
    user_api.get_user_info()
    
    with_token = {
        "method": "GET",
        "urlPath": ME_ENDPOINT,
        "headers": {
            "Authorization": {
                "equalTo": "Bearer mock-access-token",
            },
        },
    }
    assert wiremock.count_requests(with_token) == 1

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
