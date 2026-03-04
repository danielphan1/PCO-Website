"""Integration tests for member management endpoints (MEMB-01 through MEMB-05).

All tests use the auth_client fixture which seeds:
  - active_user:      email="active@test.com",      role="member", is_active=True
  - admin_user:       email="admin@test.com",        role="admin",  is_active=True
  - deactivated_user: email="deactivated@test.com",  role="member", is_active=False
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


def test_list_members(auth_client):
    """GET /v1/admin/users returns 200 list for admin; 403 for non-admin."""
    # Admin can list members
    headers = _admin_headers(auth_client)
    resp = auth_client.get("/v1/admin/users/", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)

    # Non-admin gets 403
    member_headers = _member_headers(auth_client)
    resp_forbidden = auth_client.get("/v1/admin/users/", headers=member_headers)
    assert resp_forbidden.status_code == 403


def test_create_member(auth_client):
    """POST /v1/admin/users with valid payload returns 201 UserResponse; no password in response."""
    headers = _admin_headers(auth_client)
    payload = {
        "email": "newmember@test.com",
        "full_name": "New Member",
        "role": "member",
    }
    resp = auth_client.post("/v1/admin/users/", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "newmember@test.com"
    assert body["full_name"] == "New Member"
    assert body["role"] == "member"
    assert body["is_active"] is True
    # Temp password must NOT be in the response body
    assert "password" not in body
    assert "temp_password" not in body


def test_create_member_duplicate_email(auth_client):
    """POST /v1/admin/users with an already-used email returns 409."""
    headers = _admin_headers(auth_client)
    payload = {
        "email": "duplicate@test.com",
        "full_name": "Dup One",
        "role": "member",
    }
    resp1 = auth_client.post("/v1/admin/users/", json=payload, headers=headers)
    assert resp1.status_code == 201

    # Second POST with same email must fail with 409
    payload2 = {
        "email": "duplicate@test.com",
        "full_name": "Dup Two",
        "role": "member",
    }
    resp2 = auth_client.post("/v1/admin/users/", json=payload2, headers=headers)
    assert resp2.status_code == 409


def test_update_role(auth_client):
    """PATCH /v1/admin/users/{id}/role with a valid role returns 200 with updated role."""
    headers = _admin_headers(auth_client)

    # Create a member to update
    create_resp = auth_client.post(
        "/v1/admin/users/",
        json={"email": "roleupdate@test.com", "full_name": "Role Target", "role": "member"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    # Update role to treasurer
    resp = auth_client.patch(
        f"/v1/admin/users/{user_id}/role",
        json={"role": "treasurer"},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "treasurer"
    assert body["id"] == user_id


def test_update_role_invalid(auth_client):
    """PATCH /v1/admin/users/{id}/role with an invalid role value returns 422."""
    headers = _admin_headers(auth_client)

    # Create a member to target
    create_resp = auth_client.post(
        "/v1/admin/users/",
        json={"email": "invalidrole@test.com", "full_name": "Role Invalid", "role": "member"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    resp = auth_client.patch(
        f"/v1/admin/users/{user_id}/role",
        json={"role": "supreme-overlord"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_deactivate_member(auth_client):
    """PATCH /v1/admin/users/{id}/deactivate returns 200 with is_active=false."""
    headers = _admin_headers(auth_client)

    # Create an active member to deactivate
    create_resp = auth_client.post(
        "/v1/admin/users/",
        json={"email": "todeactivate@test.com", "full_name": "To Deactivate", "role": "member"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    resp = auth_client.patch(f"/v1/admin/users/{user_id}/deactivate", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_active"] is False
    assert body["id"] == user_id


def test_deactivate_already_inactive(auth_client):
    """PATCH deactivate on an already-deactivated user returns 409."""
    headers = _admin_headers(auth_client)

    # The seeded deactivated_user can be looked up; first get their id via list
    list_resp = auth_client.get("/v1/admin/users/", headers=headers)
    assert list_resp.status_code == 200
    members = list_resp.json()
    deactivated = next((m for m in members if m["email"] == "deactivated@test.com"), None)
    assert deactivated is not None, "Seeded deactivated user not found in list"
    user_id = deactivated["id"]

    resp = auth_client.patch(f"/v1/admin/users/{user_id}/deactivate", headers=headers)
    assert resp.status_code in (400, 409)


def test_reactivate_member(auth_client):
    """PATCH /v1/admin/users/{id}/reactivate returns 200 with is_active=true."""
    headers = _admin_headers(auth_client)

    # Create and immediately deactivate a member, then reactivate
    create_resp = auth_client.post(
        "/v1/admin/users/",
        json={"email": "toreactivate@test.com", "full_name": "To Reactivate", "role": "member"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    user_id = create_resp.json()["id"]

    deact_resp = auth_client.patch(f"/v1/admin/users/{user_id}/deactivate", headers=headers)
    assert deact_resp.status_code == 200

    resp = auth_client.patch(f"/v1/admin/users/{user_id}/reactivate", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_active"] is True
    assert body["id"] == user_id
