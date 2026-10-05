import pytest

from config.credentials import ADMIN_INVITE_CODE, MANAGER_INVITE_CODE

requires_admin = pytest.mark.skipif(
    not ADMIN_INVITE_CODE,
    reason="в .env нет ADMIN_INVITE_CODE - админские тесты пропускаем",
)

requires_manager = pytest.mark.skipif(
    not MANAGER_INVITE_CODE,
    reason="в .env нет ADMIN_INVITE_CODE - тесты роли MANAGER пропускаем",
)
