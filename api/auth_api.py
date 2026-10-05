from config.hosts import AUTH_URL
from models.users import LoginRequest
from requester.custom_requester import CustomRequester


class AuthAPI(CustomRequester):
    REGISTER_ENDPOINT = "/api/v1/auth/register"
    LOGIN_ENDPOINT = "/api/v1/auth/login"

    def __init__(self, session):
        super().__init__(session, base_url=AUTH_URL)

    def register_user(self, user_data, expected_status=201):
        return self.send_request(
            "POST",
            self.REGISTER_ENDPOINT,
            json=user_data,
            expected_status=expected_status,
        )

    def login_user(self, credentials, expected_status=200):
        return self.send_request(
            "POST",
            self.LOGIN_ENDPOINT,
            json=credentials,
            expected_status=expected_status,
        )

    def authenticate(self, credentials: LoginRequest):
        response = self.login_user(credentials)
        token = response.json()["access_token"]
        self._update_session_headers(Authorization=f"Bearer {token}")
        return response
