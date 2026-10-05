import pytest
import requests

from api.api_manager import ApiManager
from config.credentials import ADMIN_INVITE_CODE, MANAGER_INVITE_CODE
from data.products import ProductData
from data.users import UserData
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
