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
    """Verify migration creates all 7 tables and seed data.

    NOTE: This test requires a running PostgreSQL instance.
    It is skipped automatically if DATABASE_URL is not set to a live DB.
    Run manually with: DATABASE_URL=postgresql+psycopg://... pytest -k test_migration
    """
    import os

    if not os.environ.get("RUN_MIGRATION_TEST"):
        pytest.skip("Set RUN_MIGRATION_TEST=1 to run against live DB")

    from sqlalchemy import create_engine, inspect, text

    from app.core.config import settings

    engine = create_engine(settings.database_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected = {
        "users",
        "refresh_tokens",
        "interest_submissions",
        "events",
        "rush_info",
        "org_content",
        "audit_log",
    }
    assert expected.issubset(set(tables)), f"Missing tables: {expected - set(tables)}"

    with engine.connect() as conn:
        rush_count = conn.execute(text("SELECT COUNT(*) FROM rush_info")).scalar()
        assert rush_count == 1
        content_count = conn.execute(text("SELECT COUNT(*) FROM org_content")).scalar()
        assert content_count == 3


# INFRA-05: Settings validation (Plan 01-02 — hardened config)
def test_settings_validation():
    from pydantic import ValidationError

    from app.core.config import Settings

    # Short JWT_SECRET must raise ValidationError mentioning "32"
    with pytest.raises(ValidationError) as exc_info:
        Settings(jwt_secret="tooshort")
    assert "32" in str(exc_info.value)

    # Valid 32-char secret must succeed
    valid = Settings(jwt_secret="a" * 32)
    assert valid.jwt_secret == "a" * 32

    # Missing jwt_secret (no value at all) must raise ValidationError
    with pytest.raises(ValidationError):
        Settings(jwt_secret=None)  # type: ignore[arg-type]


# INFRA-07: /health returns 200
def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200


# XCUT-01: Error format (stub — Plan 01-03)
@pytest.mark.skip(reason="Plan 01-03: Error handlers not yet registered")
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


# XCUT-03: CORS headers (stub — Plan 01-03)
@pytest.mark.skip(reason="Plan 01-03: CORS verify after error handler wiring")
def test_cors_headers(client):
    resp = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in resp.headers
