import pytest

from data.users import UserData
from models.users import TokenPairResponse

pytestmark = [pytest.mark.auth, pytest.mark.contract]


def test_login_returns_token_pair(api_manager, registered_user):
    response = api_manager.auth_api.login_user(
        UserData.login_data(registered_user.registration)
    )

    tokens = TokenPairResponse.model_validate(response.json())
    assert tokens.token_type == "bearer"
    assert tokens.expires_in == 43200
    assert tokens.access_token.count(".") == 2
