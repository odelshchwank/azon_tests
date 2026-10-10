import pytest
import requests

from api.api_manager import ApiManager
from api.auth_api import AuthAPI
from api.payment_api import PaymentAPI
from api.products_api import ProductsAPI
from api.reviews_api import ReviewAPI
from api.user_api import UserAPI
from config.credentials import ADMIN_INVITE_CODE, MANAGER_INVITE_CODE
from config.hosts import MOCK_URL
from data.orders import OrderData
from data.products import ProductData
from data.reviews import ReviewData
from data.users import UserData
from db.db_manager import DBManager
from mocks.wiremock_admin import WireMockAdmin
from models.orders import OrderResponse
from models.products import ProductResponse
from models.reviews import ReviewResponse
from models.users import RegisteredUser, UserResponse


@pytest.fixture(scope="session")
def api_manager():
    session = requests.Session()
    yield ApiManager(session)
    session.close()


@pytest.fixture(autouse=True)
def reset_auth_token(api_manager):
    yield
    api_manager.session.headers.pop("Authorization", None)


def _register_and_authenticate(api_manager, invite_code=None) -> RegisteredUser:
    registration = UserData.registration_data(invite_code)
    response = api_manager.auth_api.register_user(registration)
    api_manager.auth_api.authenticate(UserData.login_data(registration))
    return RegisteredUser(
        registration=registration,
        profile=UserResponse.model_validate(response.json()),
    )


@pytest.fixture
def registered_user(api_manager) -> RegisteredUser:
    user_data = UserData.registration_data()

    response = api_manager.auth_api.register_user(user_data)

    return RegisteredUser(
        registration=user_data, profile=UserResponse.model_validate(response.json())
    )


@pytest.fixture
def authenticated_user(api_manager):
    return _register_and_authenticate(api_manager)


@pytest.fixture
def authenticated_manager(api_manager):
    return _register_and_authenticate(api_manager, MANAGER_INVITE_CODE)


@pytest.fixture(scope="session")
def admin_manager():
    manager, session = _manager_with_role(ADMIN_INVITE_CODE)
    yield manager
    session.close()


@pytest.fixture
def authenticated_admin(api_manager):
    return _register_and_authenticate(api_manager, ADMIN_INVITE_CODE)


@pytest.fixture(scope="session")
def category_id():
    session = requests.Session()
    categories = ApiManager(session).categories_api.get_categories().json()
    session.close()
    return categories[0]["id"]


@pytest.fixture
def created_product(admin_manager, category_id) -> ProductResponse:
    product_request = ProductData.creation_product_data(category_id)

    response = admin_manager.products_api.create_product(product_request)
    product = ProductResponse.model_validate(response.json())

    yield product

    admin_manager.products_api.delete_product(product.id, expected_status=[204, 404])


@pytest.fixture
def out_of_stock_product(admin_manager, category_id):
    product_request = ProductData.creation_product_data(category_id)
    product = ProductResponse.model_validate(
        admin_manager.products_api.create_product(product_request).json()
    )
    admin_manager.products_api.update_product(
        product.id, ProductData.update_product_data(stock=0)
    )

    yield product

    admin_manager.products_api.delete_product(product.id, expected_status=[204, 404])


def pytest_collection_modifyitems(items):
    if ADMIN_INVITE_CODE and MANAGER_INVITE_CODE:
        return
    skip_admin = pytest.mark.skip(reason="в .env нет ADMIN_INVITE_CODE")
    for item in items:
        if "admin_manager" in item.fixturenames:
            item.add_marker(skip_admin)


@pytest.fixture(scope="session")
def db():
    manager = DBManager()
    yield manager
    manager.close()


@pytest.fixture
def wiremock():
    """Чистый WireMock перед каждым тестом: свои стабы, свой журнал запросов."""
    admin = WireMockAdmin()

    if not admin.is_running():
        pytest.skip(f"WireMock не отвечает на {MOCK_URL} - тесты с моками пропускаем")

    admin.reset()
    yield admin
    admin.session.close()


@pytest.fixture
def mock_products_api(wiremock):
    """ProductsAPI, но смотрит на мок."""
    session = requests.Session()
    yield ProductsAPI(session, base_url=MOCK_URL)
    session.close()


@pytest.fixture
def mock_auth(wiremock):
    """AuthAPI и UserAPI на одной сессии, но оба смотрят в мок."""
    session = requests.Session()
    yield AuthAPI(session, base_url=MOCK_URL), UserAPI(session, base_url=MOCK_URL)
    session.close()


@pytest.fixture
def mock_reviews_api(wiremock):
    session = requests.Session()
    yield ReviewAPI(session, base_url=MOCK_URL)
    session.close()


@pytest.fixture
def created_review(
    api_manager,
    authenticated_user,
    created_product,
) -> ReviewResponse:
    response = api_manager.review_api.create_review(
        created_product.id,
        ReviewData.creation_review_data(),
    )
    return ReviewResponse.model_validate(response.json())


def _manager_with_role(invite_code):
    session = requests.Session()
    manager = ApiManager(session)
    user_data = UserData.registration_data(invite_code)
    manager.auth_api.register_user(user_data)
    manager.auth_api.authenticate(UserData.login_data(user_data))
    return manager, session


@pytest.fixture
def store_manager():
    manager, session = _manager_with_role(MANAGER_INVITE_CODE)
    yield manager
    session.close()


@pytest.fixture
def other_user():
    manager, session = _manager_with_role(None)
    yield manager
    session.close()


@pytest.fixture
def awaiting_order(
    api_manager,
    authenticated_user,
    created_product,
):
    api_manager.cart_api.add_item(ProductData.cart_item_data(created_product.id))
    response = api_manager.payment_api.checkout()
    order = OrderResponse.model_validate(response.json())

    assert order.status == "AWAITING_PAYMENT"

    yield order

    api_manager.payment_api.cancel_order(
        order.id,
        expected_status=[200, 404, 409],
    )


@pytest.fixture
def paid_order(
    api_manager,
    authenticated_user,
    created_product,
):
    api_manager.cart_api.add_item(ProductData.cart_item_data(created_product.id))
    response = api_manager.payment_api.checkout()
    order = OrderResponse.model_validate(response.json())
    api_manager.payment_api.pay_order(order.id, OrderData.payment_success())

    yield order


@pytest.fixture
def mock_payment_api(wiremock):
    session = requests.Session()
    yield PaymentAPI(session, base_url=MOCK_URL)
    session.close()
