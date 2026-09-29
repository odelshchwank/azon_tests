import pytest
import requests

from api.api_manager import ApiManager
from config.credentials import MANAGER_INVITE_CODE, ADMIN_INVITE_CODE
from data.products import ProductData
from data.users import UserData


@pytest.fixture(scope="session")
def api_manager():
    session = requests.Session()
    yield ApiManager(session)
    session.close()

@pytest.fixture(autouse=True)
def reset_auth_token(api_manager):
    yield
    api_manager.session.headers.pop("Authorization", None)

def _register_and_authenticate(api_manager, invite_code=None):
    user_data = UserData.registration_data(invite_code)
    response = api_manager.auth_api.register_user(user_data)
    api_manager.auth_api.authenticate((user_data["email"], user_data["password"]))
    return {**user_data, "id": response.json()["id"]}

@pytest.fixture
def registered_user(api_manager):
    user_data = UserData.registration_data()
    response = api_manager.auth_api.register_user(user_data)
    return {**user_data, "id": response.json()["id"]}

@pytest.fixture
def authenticated_user(api_manager):
    return _register_and_authenticate(api_manager)

@pytest.fixture
def authenticated_manager(api_manager):
    return _register_and_authenticate(api_manager, MANAGER_INVITE_CODE)

@pytest.fixture
def admin_manager():
    admin_session = requests.Session()
    manager = ApiManager(admin_session)
    admin_credentials = UserData.registration_data(ADMIN_INVITE_CODE)
    manager.auth_api.register_user(admin_credentials)
    manager.auth_api.authenticate((admin_credentials["email"], admin_credentials["password"]))
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
def created_product(admin_manager, category_id):
    payload = ProductData.create_product_data(category_id)
    product = admin_manager.products_api.create_product(payload).json()
    yield {"id": product["id"], "payload": payload, "response_body": product}
    admin_manager.products_api.delete_product(product["id"], expected_status=[204, 404])