PRODUCTS_ENDPOINT = "/api/v1/products"
REGISTER_ENDPOINT = "/api/v1/auth/register"
LOGIN_ENDPOINT = "/api/v1/auth/login"
ME_ENDPOINT = "/api/v1/users/me"

MOCK_TOKEN = "mock-access-token"
JSON_HEADERS = {"Content-Type": "application/json"}


def product_body(product_id, **overrides):
    """Тело товара ровно в том виде, в каком его отдает AZON."""
    body = {
        "id": product_id,
        "sku": "MOCK-0001",
        "name": "Умные часы AZON Watch 5",
        "description": "GPS, пульсоксиметр, 7 дней без подзарядки.",
        "price": "19990.00",
        "stock": 10,
        "category_id": "4ca772c1-bdb7-5e5f-9987-16fe30e499c8",
        "image_url": None,
        "rating_avg": 4.67,
        "reviews_count": 3,
        "is_seed": False,
        "is_available": True,
        "created_at": "2026-08-06T12:00:00Z",
        "updated_at": "2026-08-06T12:00:00Z",
    }
    return {**body, **overrides}


def user_body(**overrides):
    """Профиль пользователя в том виде, в каком его отдаёт Auth API."""
    body = {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "mock@example.com",
        "full_name": "Мок Пользователь",
        "phone": None,
        "role": "USER",
        "is_active": True,
        "created_at": "2026-08-06T12:00:00Z",
    }
    return {**body, **overrides}


def token_body(access_token=MOCK_TOKEN):
    """Ответ POST /api/v1/auth/login: пара токенов"""
    return {
        "access_token": access_token,
        "refresh_token": "mock-refresh-token",
        "token-type": "bearer",
        "expires_in": 43200,
    }


def error_body(code, message):
    """Тело ошибки AZON"""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": [],
            "request_id": "00000000-0000-0000-0000-000000000000",
        }
    }


class ProductStubs:
    """Стабы Product API: метод возвращает готовый мэппинг для WireMock."""

    @staticmethod
    def product_found(product_id, body=None):
        return {
            "request": {
                "method": "GET",
                "urlPath": f"{PRODUCTS_ENDPOINT}/{product_id}",
            },
            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": body or product_body(product_id),
            },
        }

    @staticmethod
    def product_not_found(product_id):
        return {
            "request": {
                "method": "GET",
                "urlPath": f"{PRODUCTS_ENDPOINT}/{product_id}",
            },
            "response": {
                "status": 404,
                "headers": JSON_HEADERS,
                "jsonBody": error_body("PRODUCT_NOT_FOUND", "Product not found"),
            },
        }

    @staticmethod
    def server_error(product_id):
        return {
            "request": {
                "method": "GET",
                "urlPath": f"{PRODUCTS_ENDPOINT}/{product_id}",
            },
            "response": {
                "status": 500,
                "headers": JSON_HEADERS,
                "jsonBody": error_body("INTERNAL_ERROR", "Internal server error"),
            },
        }

    @staticmethod
    def slow_product(product_id, delay_ms=3000, body=None):
        return {
            "request": {
                "method": "GET",
                "urlPath": f"{PRODUCTS_ENDPOINT}/{product_id}",
            },
            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": body or product_body(product_id),
                "fixedDelayMilliseconds": delay_ms,
            },
        }

    @staticmethod
    def connection_reset(product_id):
        return {
            "request": {
                "method": "GET",
                "urlPath": f"{PRODUCTS_ENDPOINT}/{product_id}",
            },
            "response": {
                "fault": "CONNECTION_RESET_BY_PEER",
            },
        }

    @staticmethod
    def catalog_page(items):
        """Стаб страницы каталога"""
        return {
            "request": {
                "method": "GET",
                "urlPath": PRODUCTS_ENDPOINT,
                "queryParameters": {
                    "page": {"equalTo": "1"},
                    "size": {"equalTo": "2"},
                },
            },
            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": {
                    "items": items,
                    "total": len(items),
                    "page": 1,
                    "size": 2,
                    "pages": 1,
                },
            },
        }

    @staticmethod
    def gateway_error(product_id):
        return {
            "request": {
                "method": "GET",
                "urlPath": f"{PRODUCTS_ENDPOINT}/api/v1/{product_id}",
            },
            "response": {
                "status": 503,
                "headers": JSON_HEADERS,
                "jsonBody": error_body("GATEWAY_ERROR", "Upstream is unavailable"),
            },
        }


class AuthStubs:
    """Стабы Auth и User API: регистрация, вход, профиль."""

    @staticmethod
    def register_ok():
        """201 и профиль, в котором email и full_name взяты из тела запроса."""
        return {
            "request": {
                "method": "POST",
                "urlPath": REGISTER_ENDPOINT,
            },
            "response": {
                "status": 201,
                "headers": JSON_HEADERS,
                "jsonBody": user_body(
                    email="{{jsonPath request.body '$.email'}}",
                    password="{{jsonPath request.body '$.password'}}",
                ),
                "transformers": ["response-template"],
            },
        }

    @staticmethod
    def login_ok(access_token=MOCK_TOKEN):
        return {
            "request": {
                "method": "POST",
                "urlPath": LOGIN_ENDPOINT,
            },
            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": token_body(access_token),
            },
        }

    @staticmethod
    def me_requires_bearer(access_token=MOCK_TOKEN):
        return {
            "request": {
                "method": "GET",
                "urlPath": ME_ENDPOINT,
                "headers": {
                    "Authorization": {
                        "equalTo": f"Bearer {access_token}",
                    },
                },
            },
            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": user_body(),
            },
        }

    @staticmethod
    def me_accepts_patch(access_token=MOCK_TOKEN):
        return {
            "request": {
                "method": "PATCH",
                "urlPath": ME_ENDPOINT,
                "headers": {
                    "Authorization": {"equalTo": f"Bearer {access_token}"},
                },
            },
            "response": {
                "status": 200,
                "headers": JSON_HEADERS,
                "jsonBody": user_body(),
            },
        }
