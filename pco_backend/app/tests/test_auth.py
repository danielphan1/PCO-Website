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
    r = auth_client.post(
        "/v1/auth/login", json={"email": "active@test.com", "password": "correct-password"}
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(auth_client):
    r = auth_client.post("/v1/auth/login", json={"email": "active@test.com", "password": "wrong"})
    assert r.status_code == 401
    assert "Invalid email or password" in r.json()["detail"]


def test_login_wrong_email(auth_client):
    r = auth_client.post("/v1/auth/login", json={"email": "nobody@test.com", "password": "wrong"})
    assert r.status_code == 401
    assert "Invalid email or password" in r.json()["detail"]


def test_login_deactivated_user(auth_client):
    r = auth_client.post(
        "/v1/auth/login", json={"email": "deactivated@test.com", "password": "deactivated-password"}
    )
    assert r.status_code == 403
    assert "deactivated" in r.json()["detail"].lower()


# --- AUTH-02: refresh ---


def test_refresh_success(auth_client):
    # Login first to get a refresh token
    r = auth_client.post(
        "/v1/auth/login", json={"email": "active@test.com", "password": "correct-password"}
    )
    assert r.status_code == 200
    refresh_token = r.json()["refresh_token"]

    r2 = auth_client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert r2.status_code == 200
    data = r2.json()
    assert "access_token" in data
    assert "refresh_token" in data
    # Old token should be revoked — replaying it returns 401
    r3 = auth_client.post("/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert r3.status_code == 401


def test_refresh_expired(auth_client, db_session):
    from datetime import datetime, timedelta, timezone

    from app.core.security import generate_refresh_token, hash_refresh_token
    from app.models.refresh_token import RefreshToken
    from app.models.user import User

    user = db_session.query(User).filter(User.email == "active@test.com").first()
    raw = generate_refresh_token()
    token_hash = hash_refresh_token(raw)
    expired_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(expired_token)
    db_session.commit()

    r = auth_client.post("/v1/auth/refresh", json={"refresh_token": raw})
    assert r.status_code == 401


def test_refresh_revoked(auth_client, db_session):
    from datetime import datetime, timedelta, timezone

    from app.core.security import generate_refresh_token, hash_refresh_token
    from app.models.refresh_token import RefreshToken
    from app.models.user import User

    user = db_session.query(User).filter(User.email == "active@test.com").first()
    raw = generate_refresh_token()
    token_hash = hash_refresh_token(raw)
    revoked_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        revoked=True,
    )
    db_session.add(revoked_token)
    db_session.commit()

    r = auth_client.post("/v1/auth/refresh", json={"refresh_token": raw})
    assert r.status_code == 401


def test_refresh_deactivated_user(auth_client, db_session):
    from datetime import datetime, timedelta, timezone

    from app.core.security import generate_refresh_token, hash_refresh_token
    from app.models.refresh_token import RefreshToken
    from app.models.user import User

    deactivated = db_session.query(User).filter(User.email == "deactivated@test.com").first()
    raw = generate_refresh_token()
    token_hash = hash_refresh_token(raw)
    token = RefreshToken(
        user_id=deactivated.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db_session.add(token)
    db_session.commit()

    r = auth_client.post("/v1/auth/refresh", json={"refresh_token": raw})
    assert r.status_code == 403
    assert "deactivated" in r.json()["detail"].lower()


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
