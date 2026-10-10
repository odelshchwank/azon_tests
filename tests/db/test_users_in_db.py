import pytest

from utils.marks import requires_db

pytestmark = [pytest.mark.db, pytest.mark.auth, requires_db]


class TestUserInDB:
    def test_registered_user_is_saved_in_db(self, registered_user, db):
        row = db.auth.get_user_by_email(registered_user.registration.email)

        assert row is not None
        assert row["id"] == registered_user.profile.id
        assert row["full_name"] == registered_user.registration.full_name
        assert row["role"] == "USER"
        assert row["is_active"] is True
        assert row["is_seed"] is False

    def test_password_is_stored_as_hash(self, registered_user, db):
        row = db.auth.get_user_by_email(registered_user.registration.email)

        assert row["password_hash"] != registered_user.registration.password
        assert row["password_hash"].startswith("$2b$"), (
            "пароль должен лежать bcrypt-хешем"
        )

    def test_email_column_is_case_insensitive(self, registered_user, db):
        row = db.auth.get_user_by_email(registered_user.registration.email.upper())

        assert row is not None, "email в базе должен искаться без учета регистра"
