import pytest

from config.credentials import INVITE_CODE_ADMIN, INVITE_CODE_MANAGER
from config.db import DB_PASSWORD

requires_admin = pytest.mark.skipif(
    not INVITE_CODE_ADMIN,
    reason="в .env нет INVITE_CODE_ADMIN - админские тесты пропускаем",
)

requires_manager = pytest.mark.skipif(
    not INVITE_CODE_MANAGER,
    reason="в .env нет INVITE_CODE_MANAGER - тесты роли MANAGER пропускаем",
)

requires_db = pytest.mark.skipif(
    not DB_PASSWORD, reason="в .env нет DB_PASSWORD - тесты с базой пропускаем"
)
