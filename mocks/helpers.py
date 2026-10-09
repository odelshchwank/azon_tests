from unittest.mock import MagicMock

from config.hosts import AUTH_URL


def fake_response(
    status_code,
    text="",
    method="POST",
    url=f"{AUTH_URL}/api/v1/users/me/password",
):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.elapsed.total_seconds.return_value = 0.01
    response.request.method = method
    response.request.url = url
    response.request.body = None
    return response
