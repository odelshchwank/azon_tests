import json
import logging
from typing import Any


DEFAULT_TIMEOUT = 10
SECRET_FIELDS = ("password", "new_password", "old_password", "invite_code",
                 "access_token", "refresh_token", "token")

logger = logging.getLogger("azon_tests")

class CustomRequester:

    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def get_health(self, expected_status=200):
        return self.send_request(
            "GET", "/health", expected_status=expected_status
        )

    def send_request(self, method, endpoint, expected_status=200, **kwargs):
        url = f"{self.base_url}{endpoint}"
        kwargs.setdefault("timeout", DEFAULT_TIMEOUT)

        response = self.session.request(method, url, **kwargs)
        self._log_request_and_response(response)

        if isinstance(expected_status, int):
            allowed = {expected_status}
        else:
            allowed = set(expected_status)

        if response.status_code not in allowed:
            raise AssertionError(
                f"{method} {url}: ожидали статус {expected_status}, "
                f"получили {response.status_code}. Тело ответа: {response.text}"
            )
        return response

    def _update_session_headers(self, **headers):
        self.session.headers.update(headers)

    def _log_request_and_response(self, response):
        request = response.request
        logger.info("--> %s %s", request.method, request.url)
        if request.body:
            logger.info("   тело запроса: %s", self._mask_secrets(request.body))
        logger.info(
            "<-- %s за %.2f с: %s",
            response.status_code,
            response.elapsed.total_seconds(),
            self._mask_secrets(response.text)[:500],
        )

    @staticmethod
    def _mask_secrets(body: Any):
        body_dict = json.loads(body)
        for field in SECRET_FIELDS:
            if field in body_dict:
                body_dict[field] = "***"
        return json.dumps(body_dict, ensure_ascii=False)