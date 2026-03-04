"""Integration tests for interest form endpoints (INTR-01 and INTR-02).

All tests use the auth_client fixture which seeds:
  - active_user:  email="active@test.com",  role="member", is_active=True
  - admin_user:   email="admin@test.com",    role="admin",  is_active=True
"""


def _admin_headers(auth_client) -> dict:
    """Log in as admin and return Authorization headers."""
    resp = auth_client.post(
        "/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin-password"},
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _member_headers(auth_client) -> dict:
    """Log in as active member and return Authorization headers."""
    resp = auth_client.post(
        "/v1/auth/login",
        json={"email": "active@test.com", "password": "correct-password"},
    )
    assert resp.status_code == 200, f"Member login failed: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_submit_interest(auth_client):
    """POST /v1/interest with valid fields returns 201 with id/email/name fields."""
    payload = {
        "name": "Test Person",
        "email": "testperson@example.com",
        "phone": "555-1234",
        "year": "Sophomore",
        "major": "Computer Science",
    }
    resp = auth_client.post("/v1/interest/", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    assert body["email"] == "testperson@example.com"
    assert body["name"] == "Test Person"


def test_submit_interest_duplicate_email(auth_client):
    """Second POST with same email returns 409."""
    payload = {
        "name": "Duplicate Person",
        "email": "duplicate@example.com",
        "phone": "555-5678",
        "year": "Junior",
        "major": "Biology",
    }
    # First submission — should succeed
    resp1 = auth_client.post("/v1/interest/", json=payload)
    assert resp1.status_code == 201

    # Second submission with same email — should fail with 409
    resp2 = auth_client.post("/v1/interest/", json=payload)
    assert resp2.status_code == 409


def test_submit_interest_missing_fields(auth_client):
    """POST without required field returns 422."""
    payload = {
        "email": "missing@example.com",
        # name, phone, year, major omitted
    }
    resp = auth_client.post("/v1/interest/", json=payload)
    assert resp.status_code == 422


def test_list_interest_admin(auth_client):
    """GET /v1/interest with admin token returns 200 list."""
    headers = _admin_headers(auth_client)
    resp = auth_client.get("/v1/interest/", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)


def test_list_interest_member(auth_client):
    """GET /v1/interest with member (non-admin) token returns 403."""
    headers = _member_headers(auth_client)
    resp = auth_client.get("/v1/interest/", headers=headers)
    assert resp.status_code == 403


def test_list_interest_unauthenticated(auth_client):
    """GET /v1/interest without any token returns 401."""
    resp = auth_client.get("/v1/interest/")
    assert resp.status_code == 401
