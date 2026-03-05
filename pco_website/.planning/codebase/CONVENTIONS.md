# Coding Conventions

**Analysis Date:** 2026-03-05

## Language Coverage

This project has two distinct codebases with separate conventions:
- **Backend** (`pco_backend/`): Python 3.11+ with FastAPI — primary codebase with established conventions
- **Frontend** (`pco_website/`): TypeScript/Next.js 16 — scaffolded only, minimal conventions to observe yet

All conventions below apply to the Python backend unless noted otherwise.

## Naming Patterns

**Files:**
- `snake_case.py` for all Python modules
- `kebab-case` not used; underscores everywhere
- Service files: `{domain}_service.py` (e.g., `user_service.py`, `email_service.py`)
- Schema files: `{domain}.py` (e.g., `auth.py`, `user.py`, `event.py`)
- API files: `{domain}.py` inside `app/api/v1/` or `app/api/v1/admin/`

**Functions:**
- `snake_case` for all public functions: `list_members`, `create_member`, `update_member_role`
- Leading underscore for private helpers: `_generate_temp_password`, `_dummy_verify`, `_admin_headers` (test helpers)
- Dependency functions named descriptively: `get_db`, `get_current_user`, `require_admin`

**Variables:**
- `snake_case` throughout
- Module-level constants in `SCREAMING_SNAKE_CASE`: `MAX_SIZE_BYTES`, `ALL_ROLES`, `OFFICER_ROLES`, `_DUMMY_HASH`, `_TEMP_PW_CHARS`
- Short locals acceptable in narrow scope: `r`, `h`, `q`

**Classes:**
- `PascalCase` for all classes: `User`, `RefreshToken`, `EventPDF`, `UserResponse`, `MemberCreate`
- Pydantic schemas suffixed with purpose: `Response`, `Create`, `Update`, `Request`
- SQLAlchemy models: plain domain name (`User`, `AuditLog`, `OrgContent`)

**Routes/Endpoints:**
- HTTP verbs match REST semantics (GET list, POST create, PATCH update, DELETE delete)
- URL slugs use `snake_case` with hyphens only where needed: `/v1/admin/users`, `/v1/auth/login`

**Frontend (TypeScript):**
- `camelCase` functions, `PascalCase` components
- Components as default exports from `PascalCase` function names

## Code Style

**Formatting (Python):**
- Tool: Ruff formatter (`ruff format`)
- Line length: 100 characters (`pyproject.toml: line-length = 100`)
- Quote style: double quotes (`quote-style = "double"`)
- Indent style: spaces (4-space indent)

**Linting (Python):**
- Tool: Ruff linter (`ruff check`)
- Rule sets enabled: `E` (pycodestyle errors), `W` (pycodestyle warnings), `F` (pyflakes), `I` (isort)
- `noqa` comments are used to suppress specific rules with explanatory inline comments

**Formatting (TypeScript):**
- No Prettier config detected — Next.js defaults apply
- ESLint via `eslint-config-next`

## Import Organization

**Python — Order (enforced by Ruff `I` rules):**
1. Standard library imports (`import uuid`, `from datetime import ...`)
2. Third-party imports (`from fastapi import ...`, `from sqlalchemy import ...`)
3. Local application imports (`from app.core.deps import ...`, `from app.models.user import ...`)

**Python — Patterns:**
- Explicit named imports preferred over star imports
- `TYPE_CHECKING` guard used for relationship type hints to avoid circular imports:
  ```python
  from typing import TYPE_CHECKING
  if TYPE_CHECKING:
      from app.models.audit_log import AuditLog
  ```
- `noqa: F401` with explanatory comment for intentional side-effect imports:
  ```python
  import app.db.base  # noqa: F401 — registers all ORM models in the mapper registry
  ```

**TypeScript — Order:**
- Framework imports first (`import type { Metadata } from "next"`)
- Third-party then local

## Error Handling

**Strategy:** Raise `HTTPException` directly from service layer and route handlers. All HTTP errors are normalized by global exception handlers in `app/main.py`.

**Error Response Format:**
All errors return JSON in the shape `{"detail": "...", "status_code": N}`:
```python
# Normalized by global handlers in app/main.py
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )
```

**Service layer errors:**
```python
# Services raise HTTPException directly
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="A member with that email already exists.",
)
```

**Status codes in use:**
- 200 OK, 201 Created — success
- 401 Unauthorized — missing/invalid/expired token
- 403 Forbidden — wrong role or deactivated account
- 404 Not Found — resource not found
- 409 Conflict — duplicate resource
- 413 Request Entity Too Large — file size exceeded
- 422 Unprocessable Entity — validation failure
- 500 Internal Server Error — unhandled failures (never leaks tracebacks)

**Unhandled exceptions:**
```python
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )
```

**Storage rollback pattern:**
```python
storage_service.upload(path, data)
try:
    db.add(event)
    db.commit()
except Exception:
    try:
        storage_service.remove(path)  # rollback storage on DB failure
    except Exception:
        pass
    raise HTTPException(status_code=500, detail="Failed to save event record.")
```

## Logging

**Framework:** Python standard library `logging` module

**Pattern:**
```python
import logging
logger = logging.getLogger(__name__)
# Then use:
logger.error("Failed to send welcome email to %s: %s", to_email, exc)
logger.warning("Storage removal failed for %s: %s", event.storage_path, exc)
```

**When to log:**
- External service failures (SMTP, Supabase storage) that are swallowed
- Non-fatal warnings where an operation degrades gracefully
- Do NOT log normal request flow — FastAPI/uvicorn handles access logs

## Comments and Docstrings

**Module docstrings:**
Every module file starts with a docstring explaining purpose and listing key endpoints or responsibilities:
```python
"""Authentication endpoints — login and refresh token rotation.

POST /v1/auth/login  → returns access + refresh tokens
POST /v1/auth/refresh → rotates refresh token, returns new access + refresh tokens
"""
```

**Function docstrings:**
All public functions have docstrings. Service functions document raised exceptions:
```python
def create_member(db: Session, payload: MemberCreate, actor: User) -> tuple[User, str]:
    """Create a new member, write audit log, and return (user, temp_password).

    Raises:
        409 — email already in use
    """
```

**Inline comments:**
Used for security rationale, non-obvious behavior, and workarounds:
```python
# Always run a bcrypt verify to prevent timing-based user enumeration.
# Precomputed dummy hash to prevent timing attacks on login when user is not found.
# Insert new token row BEFORE revoking old one
```

**Section dividers:**
Long files use `# ---` separator lines to group related functions visually:
```python
# ---------------------------------------------------------------------------
# JWT
# ---------------------------------------------------------------------------
```

## Type Annotations

**Python — Usage:**
- All function signatures have full type annotations (parameters and return types)
- SQLAlchemy models use `Mapped[T]` and `mapped_column()` (SQLAlchemy 2.0 style)
- FastAPI dependencies use `Annotated[T, Depends(...)]`:
  ```python
  def get_current_user(
      credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
      db: Annotated[Session, Depends(get_db)],
  ) -> User:
  ```
- Union types use `X | Y` syntax (Python 3.10+): `str | None`, `bool | None`, `tuple[User, str]`
- `list[T]` (lowercase) preferred over `List[T]` from `typing` (though `List` appears in some route handlers)

## Module Design

**Exports:**
- No barrel `__init__.py` re-exports in most packages — callers import directly from the module
- `app/services/__init__.py` is empty — import as `from app.services import email_service, user_service`
- `app/db/base.py` is a side-effect-only aggregator that imports all models to register them

**Singleton pattern:**
Module-level singletons for shared resources:
```python
settings = Settings()  # in app/core/config.py
logger = logging.getLogger(__name__)  # in each module
storage_service = SupabaseStorage(...)  # in app/storage/files.py
```

**FastAPI routers:**
Each domain file creates its own `router = APIRouter()` and registers no prefix — prefix is set in `app/api/router.py`.

## Pydantic Schema Conventions

- All schemas use Pydantic v2 `BaseModel`
- ORM-backed response schemas set `model_config = {"from_attributes": True}`
- Input schemas use `EmailStr` for email validation
- Literal types used for validated enum-like fields:
  ```python
  _AllRolesLiteral = Literal["member", "admin", "president", "vp", "treasurer", "secretary", "historian"]
  ```
- Private type aliases prefixed with underscore: `_AllRolesLiteral`

## Audit Logging Pattern

All database mutations that change member state write an `AuditLog` row in the same DB transaction:
```python
audit = AuditLog(
    actor_id=actor.id,
    action="member.created",   # dot-notation action name
    target_id=new_user.id,
    target_type="user",
)
db.add(audit)
db.commit()  # audit + mutation committed atomically
```

Action names use `domain.action` dot notation: `"member.created"`, `"member.role_updated"`, `"member.deactivated"`.

---

*Convention analysis: 2026-03-05*
