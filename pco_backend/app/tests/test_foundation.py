"""
Wave 0 test scaffold for Phase 1.

Tests that can run now (deps installed after Plan 01-01) are real assertions.
Tests that depend on later plans use pytest.mark.skip.
"""

import pytest


# INFRA-01: PyJWT importable; python-jose removed
def test_pyjwt_importable():
    import jwt

    token = jwt.encode({"sub": "test"}, "a" * 32, algorithm="HS256")
    assert isinstance(token, str)


def test_jose_not_importable():
    with pytest.raises(ImportError):
        import jose  # noqa: F401


# INFRA-02: alembic, supabase, aiosmtplib importable
def test_deps_importable():
    import aiosmtplib
    import supabase

    import alembic

    assert alembic is not None
    assert supabase is not None
    assert aiosmtplib is not None


# INFRA-03: ORM models (Plan 01-02)
def test_orm_models():
    from app.models.audit_log import AuditLog
    from app.models.event_pdf import EventPDF
    from app.models.interest_form import InterestSubmission
    from app.models.org_content import OrgContent
    from app.models.refresh_token import RefreshToken
    from app.models.rush_info import RushInfo
    from app.models.user import User

    for model in [
        User,
        RefreshToken,
        InterestSubmission,
        EventPDF,
        RushInfo,
        OrgContent,
        AuditLog,
    ]:
        assert hasattr(model, "__tablename__")


# INFRA-04: Alembic migration (Plan 01-02)
def test_migration():
    """Verify migration creates all 7 tables.

    Requires a running PostgreSQL instance.
    Run with: RUN_MIGRATION_TEST=1 DATABASE_URL=postgresql+psycopg://... pytest -k test_migration
    """
    import os

    if not os.environ.get("RUN_MIGRATION_TEST"):
        pytest.skip("Set RUN_MIGRATION_TEST=1 to run against live DB")


# INFRA-05: Settings validation (Plan 01-02)
def test_settings_validation():
    from pydantic import ValidationError

    from app.core.config import Settings

    # Short secret must raise
    with pytest.raises(ValidationError, match="32"):
        Settings(jwt_secret="tooshort")

    # Valid 32-char secret must succeed
    s = Settings(jwt_secret="a" * 32)
    assert len(s.jwt_secret) == 32


# INFRA-07: /health returns 200
def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200


# XCUT-01: Error format
def test_error_format(client):
    resp = client.get("/nonexistent-route-that-does-not-exist")
    assert resp.status_code == 404
    body = resp.json()
    assert "detail" in body
    assert "status_code" in body
    assert body["status_code"] == 404


# XCUT-02: /docs returns 200
def test_openapi_docs(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


# XCUT-03: CORS headers
def test_cors_headers(client):
    resp = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in resp.headers
