import json
import logging
from typing import Any


DEFAULT_TIMEOUT = 10

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
            hidden = self._mask_password(request.body)
            logger.info("   тело запроса: %s", hidden)
        logger.info(
            "<-- %s за %.2f с: %s",
            response.status_code,
            response.elapsed.total_seconds(),
            response.text[:500],
        )

    @staticmethod
    def _mask_password(body: Any):
        body_dict = json.loads(body)
        if "password" in body_dict:
            body_dict["password"] = "***"
        return json.dumps(body_dict)