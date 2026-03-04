"""Auth endpoint tests — AUTH-01 through AUTH-07."""
import pytest


# --- AUTH-07: password hashing ---


def test_hash_password():
    from app.core.security import hash_password

    result = hash_password("hello")
    assert result.startswith("$2b$"), f"Expected bcrypt hash, got: {result}"
    assert len(result) > 20


def test_verify_password():
    from app.core.security import hash_password, verify_password

    h = hash_password("correct")
    assert verify_password("correct", h) is True
    assert verify_password("wrong", h) is False


# --- AUTH-01: login ---


def test_login_success(auth_client):
    pytest.fail("not implemented")


def test_login_wrong_password(auth_client):
    pytest.fail("not implemented")


def test_login_wrong_email(auth_client):
    pytest.fail("not implemented")


def test_login_deactivated_user(auth_client):
    pytest.fail("not implemented")


# --- AUTH-02: refresh ---


def test_refresh_success(auth_client):
    pytest.fail("not implemented")


def test_refresh_expired(auth_client):
    pytest.fail("not implemented")


def test_refresh_revoked(auth_client):
    pytest.fail("not implemented")


def test_refresh_deactivated_user(auth_client):
    pytest.fail("not implemented")


# --- AUTH-03: /users/me ---


def test_users_me_authenticated(auth_client):
    pytest.fail("not implemented")


def test_users_me_unauthenticated(auth_client):
    pytest.fail("not implemented")


# --- AUTH-04: get_current_user dependency ---


def test_get_current_user_no_token(auth_client):
    pytest.fail("not implemented")


def test_get_current_user_expired_token(auth_client):
    pytest.fail("not implemented")


# --- AUTH-05: require_admin ---


def test_require_admin_non_admin(auth_client):
    pytest.fail("not implemented")


def test_require_admin_admin_user(auth_client):
    pytest.fail("not implemented")
