"""Integration tests for rush info endpoints (RUSH-01, RUSH-02, RUSH-03).

Tests are ordered sequentially — each test depends on prior state.
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


def test_get_rush_empty(auth_client):
    """GET /v1/rush with no data returns 200 {"status": "coming_soon"}."""
    resp = auth_client.get("/v1/rush/")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"status": "coming_soon"}


def test_update_rush(auth_client):
    """PUT /v1/rush with valid payload as admin returns 200 with full RushInfoResponse."""
    headers = _admin_headers(auth_client)
    payload = {
        "dates": "September 1-7",
        "times": "6:00 PM - 9:00 PM",
        "locations": "Student Union Room 101",
        "description": "Join us for rush week!",
    }
    resp = auth_client.put("/v1/rush/", json=payload, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["dates"] == "September 1-7"
    assert body["times"] == "6:00 PM - 9:00 PM"
    assert body["locations"] == "Student Union Room 101"
    assert body["description"] == "Join us for rush week!"
    assert "id" in body
    assert "is_published" in body
    assert "updated_at" in body


def test_get_rush_unpublished(auth_client):
    """GET /v1/rush after update (before publish) returns {"status": "coming_soon"}."""
    resp = auth_client.get("/v1/rush/")
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"status": "coming_soon"}


def test_toggle_visibility_publish(auth_client):
    """PATCH /v1/rush/visibility as admin returns 200 with is_published=true."""
    headers = _admin_headers(auth_client)
    resp = auth_client.patch("/v1/rush/visibility", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_published"] is True


def test_get_rush_published(auth_client):
    """GET /v1/rush after publish returns full RushInfoResponse (not coming_soon)."""
    resp = auth_client.get("/v1/rush/")
    assert resp.status_code == 200
    body = resp.json()
    assert "status" not in body or body.get("status") != "coming_soon"
    assert "dates" in body
    assert "times" in body
    assert "locations" in body
    assert "description" in body
    assert body["is_published"] is True


def test_toggle_visibility_unpublish(auth_client):
    """PATCH /v1/rush/visibility again returns 200 with is_published=false."""
    headers = _admin_headers(auth_client)
    resp = auth_client.patch("/v1/rush/visibility", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_published"] is False


def test_update_rush_non_admin(auth_client):
    """PUT /v1/rush with member token returns 403."""
    headers = _member_headers(auth_client)
    payload = {
        "dates": "October 1-7",
        "times": "7:00 PM",
        "locations": "Library",
        "description": "Unauthorized update attempt",
    }
    resp = auth_client.put("/v1/rush/", json=payload, headers=headers)
    assert resp.status_code == 403
