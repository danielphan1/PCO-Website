# Testing Patterns

**Analysis Date:** 2026-03-05

## Test Framework

**Runner:**
- pytest 9.x
- Config: `pco_backend/pyproject.toml` under `[tool.pytest.ini_options]`
- Test discovery path: `app/tests`

**HTTP Client:**
- `fastapi.testclient.TestClient` (wraps `httpx` under the hood)
- httpx 0.28+ required as a dev dependency

**Assertion Library:**
- pytest built-in `assert` statements

**Mocking:**
- `unittest.mock.patch`, `MagicMock`, `AsyncMock` (standard library)

**Run Commands:**
```bash
cd pco_backend
uv run pytest                        # Run all tests
uv run pytest app/tests/test_auth.py # Run a single test file
uv run pytest -k test_login          # Run tests matching name pattern
uv run pytest -v                     # Verbose output
```

No coverage command is configured — coverage is not enforced.

## Test File Organization

**Location:**
- All tests in `pco_backend/app/tests/`
- Tests are NOT co-located with source files — centralized in one directory

**Naming:**
- Test files: `test_{domain}.py`
- Test functions: `test_{description}` (snake_case, plain English)
- Helper functions: `_{role}_headers(auth_client)` or `get_{role}_token(auth_client)` pattern

**Directory structure:**
```
pco_backend/
└── app/
    └── tests/
        ├── __init__.py
        ├── conftest.py          # Shared fixtures: client, db_session, auth_client
        ├── test_foundation.py   # Infrastructure/smoke tests (INFRA-*, XCUT-*)
        ├── test_auth.py         # Auth endpoints (AUTH-01 through AUTH-07)
        ├── test_members.py      # Member management (MEMB-01 through MEMB-05)
        ├── test_events.py       # Event endpoints (EVNT-01 through EVNT-03)
        ├── test_interest.py     # Interest form (INTR-01, INTR-02)
        ├── test_email.py        # Email service (XCUT-04)
        ├── test_rush.py         # Rush info (RUSH-01 through RUSH-03)
        └── test_content.py      # Org content (CONT-01 through CONT-05)
```

## Test ID Convention

Every test maps to a documented test ID in comments and docstrings. Format: `{DOMAIN}-{NN}`:
- `AUTH-01` through `AUTH-07` — authentication
- `MEMB-01` through `MEMB-05` — member management
- `EVNT-01` through `EVNT-03` — events
- `INTR-01`, `INTR-02` — interest forms
- `RUSH-01` through `RUSH-03` — rush info
- `CONT-01` through `CONT-05` — org content
- `XCUT-*` — cross-cutting concerns (error format, CORS, email)
- `INFRA-*` — infrastructure/dependency smoke tests

## Shared Fixtures (conftest.py)

Located at `pco_backend/app/tests/conftest.py`. All fixtures are `scope="module"` — created once per test file.

**Database:**
```python
# SQLite in-memory DB replaces PostgreSQL for all tests
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

**Unauthenticated client:**
```python
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c
```

**Authenticated client with seeded users:**
```python
@pytest.fixture(scope="module")
def auth_client(db_session):
    """TestClient with DB overridden to in-memory SQLite.
    Seeds one active user, one admin user, and one deactivated user.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Seeds: active@test.com (member), admin@test.com (admin), deactivated@test.com (member, inactive)
    db_session.add_all([active_user, admin_user, deactivated_user])
    db_session.commit()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
```

**Seeded test users (available in all tests using `auth_client`):**
| Email | Password | Role | Active |
|---|---|---|---|
| `active@test.com` | `correct-password` | member | True |
| `admin@test.com` | `admin-password` | admin | True |
| `deactivated@test.com` | `deactivated-password` | member | False |

## Dependency Override Pattern

The core testing pattern replaces FastAPI's `get_db` dependency with an in-memory SQLite session:
```python
app.dependency_overrides[get_db] = override_get_db
# ... tests run ...
app.dependency_overrides.clear()  # cleanup in fixture teardown
```

This means all route logic runs end-to-end through FastAPI — no unit mocking of service functions for integration tests.

## Test Structure

**Integration tests (typical pattern):**
```python
def test_login_success(auth_client):
    r = auth_client.post(
        "/v1/auth/login", json={"email": "active@test.com", "password": "correct-password"}
    )
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
```

**Tests with DB state manipulation:**
```python
def test_refresh_expired(auth_client, db_session):
    from datetime import datetime, timedelta, timezone
    from app.models.refresh_token import RefreshToken

    # Create expired token directly in DB
    expired_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(expired_token)
    db_session.commit()

    r = auth_client.post("/v1/auth/refresh", json={"refresh_token": raw})
    assert r.status_code == 401
```

**Sequential state tests (rush/content):**
Some test files depend on ordered execution — tests are written top-to-bottom where each test builds on prior state:
```python
def test_get_rush_empty(auth_client): ...       # state: no data
def test_update_rush(auth_client): ...          # state: data saved
def test_get_rush_unpublished(auth_client): ... # state: data saved, not published
def test_toggle_visibility_publish(auth_client): ...  # state: published
def test_get_rush_published(auth_client): ...   # state: published
```

## Mocking

**Framework:** `unittest.mock` (standard library)

**Mocking external storage (Supabase):**
```python
from unittest.mock import MagicMock, patch

mock_storage = MagicMock()
mock_storage.create_signed_url.return_value = "https://signed.url/file.pdf"
mock_storage.upload.return_value = None

with patch("app.services.event_service.storage_service", mock_storage):
    resp = auth_client.post("/v1/admin/events/", ...)

mock_storage.remove.assert_called_once()  # verify rollback was triggered
```

**Mocking async functions:**
```python
from unittest.mock import AsyncMock, patch

with patch("aiosmtplib.send", new_callable=AsyncMock, side_effect=Exception("SMTP down")):
    asyncio.run(email_service.send_welcome_email(...))
    # Verifies exception was swallowed
```

**Mocking BackgroundTasks:**
```python
called_with = []

def capturing_add_task(self, func, *args, **kwargs):
    called_with.append((func, args, kwargs))
    # Do not actually schedule the task

with patch.object(BackgroundTasks, "add_task", capturing_add_task):
    resp = auth_client.post("/v1/admin/users/", ...)

funcs = [c[0] for c in called_with]
assert send_welcome_email in funcs
```

**What to Mock:**
- External services: Supabase storage client (`storage_service`)
- SMTP delivery: `aiosmtplib.send`
- FastAPI BackgroundTasks when verifying task scheduling
- Direct DB commit to test rollback paths (by monkey-patching `db_session.commit`)

**What NOT to Mock:**
- Database queries — use the SQLite override instead
- FastAPI routing, middleware, or exception handlers
- Auth/JWT logic — craft real tokens using `app.core.security` helpers

## Helper Functions

Per-file helper functions (not fixtures) are defined at module level with a leading underscore:

```python
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
    ...
```

This pattern is repeated in `test_members.py`, `test_interest.py`, `test_rush.py`, and `test_content.py`.

## Seeding Test Data

**Direct DB insertion** (not via API) for fixture setup:
```python
def seed_event(db_session) -> EventPDF:
    """Insert one EventPDF row directly and return it."""
    event = EventPDF(
        id=uuid.uuid4(),
        title="Test Event",
        date=date(2024, 1, 15),
        storage_path="events/test.pdf",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event
```

**Via API** for resource creation within a test (creates realistic state):
```python
create_resp = auth_client.post(
    "/v1/admin/users/",
    json={"email": "roleupdate@test.com", "full_name": "Role Target", "role": "member"},
    headers=headers,
)
assert create_resp.status_code == 201
user_id = create_resp.json()["id"]
```

## Coverage

**Requirements:** None enforced — no coverage configuration in `pyproject.toml`

**View Coverage:**
```bash
uv run pytest --cov=app --cov-report=term-missing
```
(requires `pytest-cov` to be added as a dev dependency)

## Test Types

**Unit Tests (in `test_auth.py`, `test_foundation.py`, `test_email.py`):**
- Test individual functions in isolation
- Import the function directly and assert on output
- Example: `test_hash_password`, `test_verify_password`, `test_smtp_failure_does_not_propagate`

**Integration Tests (all other test files):**
- Full HTTP request/response cycle through FastAPI's `TestClient`
- Database operations run against real SQLite (not mocked)
- External services (storage, SMTP) mocked at the call site

**Smoke/Infrastructure Tests (`test_foundation.py`):**
- Verify correct dependencies are installed (`test_pyjwt_importable`, `test_jose_not_importable`)
- Verify all ORM models are importable and have `__tablename__`
- Verify config validation raises on bad input
- Verify basic endpoints return expected status codes (health, docs, CORS)

**Conditional Tests:**
```python
def test_migration():
    import os
    if not os.environ.get("RUN_MIGRATION_TEST"):
        pytest.skip("Set RUN_MIGRATION_TEST=1 to run against live DB")
```
Used to gate tests that require external resources not available in CI.

## Common Patterns

**RBAC testing (admin vs member):**
```python
def test_list_members(auth_client):
    # Admin can access
    headers = _admin_headers(auth_client)
    resp = auth_client.get("/v1/admin/users/", headers=headers)
    assert resp.status_code == 200

    # Non-admin gets 403
    member_headers = _member_headers(auth_client)
    resp_forbidden = auth_client.get("/v1/admin/users/", headers=member_headers)
    assert resp_forbidden.status_code == 403
```

**Negative-path testing:**
Always test the unhappy paths alongside happy paths. Common negative cases covered:
- Wrong password → 401
- Wrong/nonexistent email → 401
- Deactivated user → 403
- Duplicate resource → 409
- Invalid field value → 422
- File too large → 413
- Missing auth header → 401
- Non-admin hitting admin route → 403

**Crafting JWT tokens for auth edge cases:**
```python
import jwt
from app.core.config import settings

expired_payload = {
    "sub": "00000000-0000-0000-0000-000000000000",
    "role": "member",
    "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    "iat": datetime.now(timezone.utc) - timedelta(minutes=61),
}
expired_token = jwt.encode(expired_payload, settings.jwt_secret, algorithm=settings.jwt_alg)
```

**Testing rollback behavior:**
```python
def failing_commit():
    raise Exception("DB failure")

db_session.commit = failing_commit
try:
    with patch("app.services.event_service.storage_service", mock_storage):
        with pytest.raises(Exception):
            upload_event(...)
finally:
    db_session.commit = original_commit
    db_session.rollback()

mock_storage.remove.assert_called_once()  # Storage was cleaned up
```

---

*Testing analysis: 2026-03-05*
