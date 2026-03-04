"""Integration tests for org content endpoints (CONT-01 through CONT-05)."""


def get_admin_token(auth_client):
    resp = auth_client.post(
        "/v1/auth/login",
        json={"email": "admin@test.com", "password": "admin-password"},
    )
    assert resp.status_code == 200, f"Admin login failed: {resp.text}"
    return resp.json()["access_token"]


def get_member_token(auth_client):
    resp = auth_client.post(
        "/v1/auth/login",
        json={"email": "active@test.com", "password": "correct-password"},
    )
    assert resp.status_code == 200, f"Member login failed: {resp.text}"
    return resp.json()["access_token"]


def test_get_history_empty(auth_client):
    """CONT-01: GET /v1/content/history returns {section: 'history', content: ''}."""
    resp = auth_client.get("/v1/content/history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["section"] == "history"
    assert data["content"] == ""


def test_get_philanthropy_empty(auth_client):
    """CONT-02: GET /v1/content/philanthropy returns {section: 'philanthropy', content: ''}."""
    resp = auth_client.get("/v1/content/philanthropy")
    assert resp.status_code == 200
    data = resp.json()
    assert data["section"] == "philanthropy"
    assert data["content"] == ""


def test_get_contacts_empty(auth_client):
    """CONT-03: GET /v1/content/contacts returns {section: 'contacts', content: ''}."""
    resp = auth_client.get("/v1/content/contacts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["section"] == "contacts"
    assert data["content"] == ""


def test_update_history(auth_client):
    """CONT-04: Admin PUT /v1/content/history upserts plain text; returns updated content."""
    token = get_admin_token(auth_client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = auth_client.put(
        "/v1/content/history",
        json={"content": "Our history..."},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["section"] == "history"
    assert data["content"] == "Our history..."


def test_get_history_after_update(auth_client):
    """CONT-04: Subsequent GET returns the content that was PUT."""
    resp = auth_client.get("/v1/content/history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["section"] == "history"
    assert data["content"] == "Our history..."


def test_update_invalid_section(auth_client):
    """CONT-05: PUT /v1/content/invalid_section returns 422 (section validated)."""
    token = get_admin_token(auth_client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = auth_client.put(
        "/v1/content/invalid_section",
        json={"content": "Some content"},
        headers=headers,
    )
    assert resp.status_code == 422


def test_update_content_non_admin(auth_client):
    """CONT-04: PUT /v1/content/history without admin token returns 403."""
    token = get_member_token(auth_client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = auth_client.put(
        "/v1/content/history",
        json={"content": "Unauthorized update"},
        headers=headers,
    )
    assert resp.status_code == 403


def test_get_leadership_empty(auth_client):
    """CONT-05: GET /v1/content/leadership returns [] when no officer roles in DB."""
    resp = auth_client.get("/v1/content/leadership")
    assert resp.status_code == 200
    data = resp.json()
    assert data == []


def test_get_leadership_public(auth_client):
    """CONT-05: GET /v1/content/leadership is publicly accessible (no auth required)."""
    resp = auth_client.get("/v1/content/leadership")
    assert resp.status_code == 200
