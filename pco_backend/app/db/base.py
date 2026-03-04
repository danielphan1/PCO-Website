from app.db.base_class import Base  # noqa: F401

# Required: all models must be imported so Base.metadata has them for Alembic
from app.models.audit_log import AuditLog  # noqa: E402, F401
from app.models.event_pdf import EventPDF  # noqa: E402, F401
from app.models.interest_form import InterestSubmission  # noqa: E402, F401
from app.models.org_content import OrgContent  # noqa: E402, F401
from app.models.refresh_token import RefreshToken  # noqa: E402, F401
from app.models.rush_info import RushInfo  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
