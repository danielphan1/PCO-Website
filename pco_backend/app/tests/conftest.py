import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.deps import get_db
from app.db.base_class import Base
from app.models.user import User
from app.models.refresh_token import RefreshToken  # noqa: F401 — ensures table created
from app.models.audit_log import AuditLog  # noqa: F401 — ensures table created
from app.models.event_pdf import EventPDF  # noqa: F401 — ensures table created
from app.models.interest_form import InterestSubmission  # noqa: F401 — ensures table created
from app.models.org_content import OrgContent  # noqa: F401 — ensures table created
from app.models.rush_info import RushInfo  # noqa: F401 — ensures table created
from app.core.security import hash_password


TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def auth_client(db_session):
    """TestClient with DB overridden to in-memory SQLite. Seeds one active user and one deactivated user."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # Seed active user
    active_user = User(
        email="active@test.com",
        hashed_password=hash_password("correct-password"),
        full_name="Active User",
        role="member",
        is_active=True,
    )
    # Seed admin user
    admin_user = User(
        email="admin@test.com",
        hashed_password=hash_password("admin-password"),
        full_name="Admin User",
        role="admin",
        is_active=True,
    )
    # Seed deactivated user
    deactivated_user = User(
        email="deactivated@test.com",
        hashed_password=hash_password("deactivated-password"),
        full_name="Deactivated User",
        role="member",
        is_active=False,
    )
    db_session.add_all([active_user, admin_user, deactivated_user])
    db_session.commit()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
