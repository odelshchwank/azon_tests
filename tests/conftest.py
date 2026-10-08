import pytest
import requests
from requests import session

from api.api_manager import ApiManager
from api.auth_api import AuthAPI
from api.products_api import ProductsAPI
from api.user_api import UserAPI
from config.credentials import ADMIN_INVITE_CODE, MANAGER_INVITE_CODE
from config.hosts import MOCK_URL
from data.products import ProductData
from data.users import UserData
from db.db_manager import DBManager
from mocks.wiremock_admin import WireMockAdmin
from models.products import ProductResponse
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
    admin_session = requests.Session()
    manager = ApiManager(admin_session)
    admin_credentials = UserData.registration_data(ADMIN_INVITE_CODE)
    manager.auth_api.register_user(admin_credentials)
    manager.auth_api.authenticate(UserData.login_data(admin_credentials))
    yield manager
    admin_session.close()


@pytest.fixture
def authenticated_admin(api_manager):
    return _register_and_authenticate(api_manager, ADMIN_INVITE_CODE)


@pytest.fixture
def category_id(api_manager):
    categories = api_manager.categories_api.get_categories().json()
    assert categories, "Список категорий пуст"
    return categories[0]["id"]


@pytest.fixture
def created_product(admin_manager, category_id) -> ProductResponse:
    product_request = ProductData.creation_product_data(category_id)

    response = admin_manager.products_api.create_product(product_request)
    product = ProductResponse.model_validate(response.json())

    yield product

    admin_manager.products_api.delete_product(product.id, expected_status=[204, 404])


def pytest_collection_modifyitems(items):
    if ADMIN_INVITE_CODE and MANAGER_INVITE_CODE:
        return
    skip_admin = pytest.mark.skip(reason="в env. нет ADMIN_INVITE_CODE")
    for item in items:
        if "admin_manager" in item.fixturenames:
            item.add_marker(skip_admin)


@pytest.fixture(scope="session")
def db():
    manager = DBManager()
    yield manager
    manager.close()


@pytest.fixture
def created_order(api_manager, authenticated_user, created_product):
    api_manager.cart_api.add_item(ProductData.cart_item_data(created_product.id))

    response = api_manager.payment_api.checkout()
    order = response.json()

    yield order

    try:
        api_manager.payment_api.cancel_order(order["id"])
    except AssertionError:
        pass


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
