# Phase 1: Foundation - Research

**Researched:** 2026-03-03
**Domain:** FastAPI + SQLAlchemy 2.0 + Alembic + PyJWT + Ruff + Docker Compose
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Dependency changes:**
- Swap `python-jose` for `PyJWT` (CVE risk — alg:none bypass); remove python-jose entirely after confirming no transitive dependency conflict
- Add `alembic`, `supabase-py`, `aiosmtplib` to pyproject.toml dependencies
- Dockerfile must use `uv sync --frozen` (not `uv sync`) for reproducible builds
- Ruff replaces Black — configure both `ruff format` and `ruff check`; Ruff lint rules: enable E, W, F, I (pycodestyle errors/warnings, pyflakes, isort) as baseline; no overly strict rules that would require type annotations

**Settings hardening:**
- `jwt_secret` field has **no default value** — Settings instantiation must fail if missing
- Add validation: `jwt_secret` minimum 32 characters; raise ValueError at startup with a clear message (not at first request)
- Add new env vars to Settings: `supabase_url`, `supabase_service_key`, `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`, `refresh_token_expire_days` (default 30)
- Validation happens via Pydantic `@field_validator` on the Settings class itself

**ORM models — seven tables:** `users`, `refresh_tokens`, `interest_submissions`, `events`, `rush_info`, `org_content`, `audit_log`

- `users`: id (UUID PK), email (unique), hashed_password, full_name, role (string), is_active (bool, default True), created_at, updated_at
- Role string values: `member`, `admin`, `president`, `vp`, `treasurer`, `secretary`, `sergeant_at_arms`, `historian`
- `refresh_tokens`: id (UUID PK), user_id (FK → users), token_hash (string, unique), expires_at (timestamp), revoked (bool, default False), created_at — store hash not plaintext
- `interest_submissions`: id (UUID PK), name, email (unique), phone, year, major, created_at
- `events`: id (UUID PK), title, date (date), storage_path (string, relative path), created_at, uploaded_by (UUID FK → users)
- `rush_info`: id (UUID PK), dates, times, locations, description (all text), is_published (bool, default False), updated_at — single-row upsert pattern
- `org_content`: id (UUID PK), section (string unique), content (text), updated_at — one row per section
- `audit_log`: id (UUID PK), actor_id (UUID FK → users), action (string), target_id (UUID nullable), target_type (string nullable), metadata (JSON nullable), created_at

**Alembic migration:**
- `alembic/env.py` imports `Base` from `app.db.base`; `app.db.base` imports all models
- Single migration `001_initial_schema.py` creates all 7 tables
- Seed data: one unpublished `rush_info` row + three `org_content` rows (history, philanthropy, contacts) with empty content

**DB session:**
- Synchronous SQLAlchemy only (`create_engine`, `Session`, not AsyncSession)
- Session factory in `app/db/session.py`; `get_db()` generator dependency in `app/core/deps.py`

**Global error handlers:**
- Register exception handlers for `RequestValidationError` (422) and `HTTPException`
- Both return `{"detail": "...", "status_code": N}` format
- Internal 500 errors return generic message (no tracebacks)

**CORS:**
- `CORS_ORIGINS` env var drives allow_origins — no wildcard origins

**OpenAPI:**
- Keep FastAPI auto-generated `/docs` and `/redoc` defaults
- Set `title`, `version`, `description` on FastAPI app from settings

**Docker:**
- Add `pg_isready` healthcheck to db service; API `depends_on: db: condition: service_healthy`
- Dockerfile: replace `uv sync --no-dev` with `uv sync --frozen --no-dev`

### Claude's Discretion
- Exact Ruff rule IDs to enable beyond the E/W/F/I baseline (e.g., whether to add UP for pyupgrade, B for bugbear)
- How to surface field-level 422 validation errors in the normalized format (flat list vs. single joined string)
- Whether to add `__repr__` or `__str__` to ORM models
- Alembic migration file naming and version ID format

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | Swap python-jose for PyJWT in pyproject.toml | PyJWT 2.11.0 API verified; CVE details documented; uv add/remove pattern confirmed |
| INFRA-02 | Add missing dependencies: alembic, supabase-py, aiosmtplib | All three are standard packages; uv add command pattern documented |
| INFRA-03 | All ORM models implemented: users, interest_submissions, events, rush_info, org_content, audit_log, refresh_tokens | SQLAlchemy 2.0 DeclarativeBase + Mapped + mapped_column pattern verified; all 7 model schemas defined |
| INFRA-04 | Initial Alembic migration creates all tables from ORM models | Alembic env.py target_metadata pattern verified; data seed in upgrade() confirmed pattern |
| INFRA-05 | Settings class hardened: jwt_secret required, no default, all new env vars added | Pydantic v2 @field_validator + no-default field pattern verified; BaseSettings behavior confirmed |
| INFRA-06 | Dockerfile uses uv.lock with --frozen flag | uv sync --frozen behavior documented; Dockerfile copy of uv.lock required |
| INFRA-07 | docker-compose.yml spins up API + local PostgreSQL with persistent volume | pg_isready healthcheck + service_healthy depends_on pattern documented |
| XCUT-01 | Consistent error response format: {"detail": "...", "status_code": N} | FastAPI exception_handler decorator pattern verified from official docs |
| XCUT-02 | All endpoints documented via FastAPI auto-generated OpenAPI/Swagger at /docs | FastAPI auto-generates /docs by default; title/version/description on app constructor |
| XCUT-03 | CORS configured for localhost:3000 and production domain — no wildcard origins | Already wired in main.py via CORSMiddleware; env var drives allow_origins |
| XCUT-05 | Ruff configured in pyproject.toml for formatting and linting — replaces Black | Ruff [tool.ruff.lint] + [tool.ruff.format] TOML structure verified |
</phase_requirements>

---

## Summary

Phase 1 is a hardening and scaffolding phase with no new business logic. The work falls into three natural tracks: (1) dependency / tooling changes (PyJWT swap, Ruff config, uv --frozen, new pip packages), (2) database layer (7 ORM models, Alembic initial migration with seed data, synchronous session factory + get_db dependency), and (3) app-level infrastructure (Settings hardening with Pydantic v2 validators, global exception handlers normalizing all errors to `{"detail": "...", "status_code": N}`, and Docker healthcheck fix).

All technologies are mature and well-documented. The project already has the skeleton in place (FastAPI app, CORS middleware, health endpoint, router, empty model files, empty alembic/versions). The work is predominantly filling in correct implementations rather than creating structure from scratch. The empty stub files (`app/db/base.py`, `app/db/session.py`, `app/core/deps.py`, `app/core/security.py`, all model files, `alembic/env.py`) confirm that the directory layout is done but none of the content is written yet.

The most nuanced decisions are: (1) how to format Pydantic validation errors for the normalized 422 response (flat joined string is simpler and sufficient for v1), (2) whether to add `uv.lock` to the Dockerfile COPY step (it is required for `--frozen` to work), and (3) ensuring alembic/env.py reads `DATABASE_URL` from settings rather than hardcoding.

**Primary recommendation:** Implement the three plans in order — 01-01 (deps + config + Docker), 01-02 (ORM + Alembic), 01-03 (security utils + error handlers + CORS + OpenAPI) — since 01-02 depends on the settings changes from 01-01, and 01-03 depends on the app structure stabilized by 01-01 and 01-02.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | >=0.115 (already in pyproject) | Web framework, OpenAPI, dependency injection | Project constraint; already installed |
| SQLAlchemy | >=2.0 (already in pyproject) | ORM with Mapped/mapped_column type-annotated style | Project constraint; already installed |
| Alembic | latest (1.13+) | Database schema migrations | Standard SQLAlchemy migration tool; needed for INFRA-04 |
| PyJWT | 2.11.0 (latest) | JWT encode/decode, HS256 | Replacing python-jose due to CVE-2024-33663 and CVE-2025-61152 |
| Pydantic v2 / pydantic-settings | >=2.7 / >=2.3 (already in pyproject) | Settings management, field validation | Project constraint; already installed |
| Ruff | latest | Linting (ruff check) + formatting (ruff format) | Replaces Black per project decision; single tool for both |
| psycopg[binary] | >=3.2 (already in pyproject) | PostgreSQL driver (sync, used by SQLAlchemy) | Already installed; works with synchronous engine |
| uv | (package manager) | Dependency management and lockfile | Project constraint; all installs via `uv add` |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| supabase-py | latest | Supabase Storage client (Phase 4 events) | Add now per INFRA-02; used in Phase 4 |
| aiosmtplib | latest | Async SMTP email (Phase 3 welcome/confirmation emails) | Add now per INFRA-02; used in Phase 3 |
| passlib[bcrypt] | >=1.7 (already in pyproject) | Password hashing | Already installed; used in Phase 2 |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyJWT | python-jose | python-jose has unfixed CVEs (alg:none, algorithm confusion); PyJWT is actively maintained and CVE-free |
| Synchronous SQLAlchemy | AsyncSession + asyncpg | Project explicitly decided against async ORM; sync + thread pool is correct for this traffic level |
| Alembic | create_all() at startup | Alembic provides migration history, rollback, versioning; create_all() has no upgrade path |
| Ruff | Black + isort + flake8 | Ruff replaces all three with one tool, 10-100x faster, same rules |

### Installation

```bash
# Remove python-jose (verify no transitive conflict first)
uv remove python-jose

# Add new dependencies
uv add alembic supabase-py aiosmtplib PyJWT

# Install dev/test deps (not in Dockerfile)
uv add --dev pytest pytest-httpx httpx
```

---

## Architecture Patterns

### Recommended Project Structure

The structure is already established. Phase 1 fills in these files:

```
app/
├── core/
│   ├── config.py         # Settings hardening (jwt_secret required + validator)
│   ├── deps.py           # get_db() generator dependency
│   └── security.py       # Empty stub — Phase 2 fills; Phase 1 just ensures PyJWT available
├── db/
│   ├── base.py           # DeclarativeBase + imports all models (Alembic autogenerate sees them)
│   └── session.py        # create_engine, SessionLocal, get_db()
├── models/
│   ├── user.py           # User ORM model
│   ├── refresh_token.py  # RefreshToken ORM model (new file)
│   ├── interest_form.py  # InterestSubmission ORM model
│   ├── event_pdf.py      # EventPDF (events table) ORM model
│   ├── rush_info.py      # RushInfo ORM model (new file)
│   ├── org_content.py    # OrgContent ORM model (new file)
│   └── audit_log.py      # AuditLog ORM model (new file)
└── main.py               # Register global exception handlers, set title/version/description

alembic/
├── env.py                # Import Base.metadata, read DATABASE_URL from settings
└── versions/
    └── 001_initial_schema.py   # Create 7 tables + seed rush_info + org_content rows

docker/
├── Dockerfile            # uv sync --frozen --no-dev; COPY uv.lock
└── docker-compose.yml    # Add db healthcheck + depends_on: condition: service_healthy

pyproject.toml            # Remove python-jose, add alembic/supabase-py/aiosmtplib/PyJWT
                          # Add [tool.ruff.lint] and [tool.ruff.format] sections
```

### Pattern 1: Pydantic v2 Settings with Required Field + Validator

**What:** Remove default from `jwt_secret`, add `@field_validator` to enforce minimum length. Settings instantiation fails at process startup if env var is absent or too short.

**When to use:** Any security-sensitive field that must be explicitly provided.

**Example:**

```python
# Source: https://docs.pydantic.dev/latest/concepts/validators/
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "dev"
    app_name: str = "psi-chi-omega-api"
    app_version: str = "0.1.0"
    cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/pco"

    # No default — instantiation fails if JWT_SECRET env var is missing
    jwt_secret: str
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    supabase_url: str = ""
    supabase_service_key: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    @field_validator("jwt_secret", mode="after")
    @classmethod
    def jwt_secret_min_length(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                "JWT_SECRET must be at least 32 characters long. "
                f"Got {len(v)} characters."
            )
        return v

    model_config = {"env_file": ".env", "case_sensitive": False}

settings = Settings()  # Raises ValidationError at import time if invalid
```

**Critical note:** The old `class Config:` syntax is Pydantic v1. Use `model_config = {...}` (Pydantic v2 style). The existing `config.py` uses the old style — replace it.

### Pattern 2: SQLAlchemy 2.0 ORM Model with UUID PK

**What:** Modern `DeclarativeBase` with `Mapped` type annotations, `mapped_column`, UUID primary keys generated in Python (not server-side), `server_default=func.now()` for timestamps.

**Example:**

```python
# Source: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html
import uuid
from datetime import datetime
from sqlalchemy import UUID, Boolean, String, DateTime, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="member")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="actor")
```

### Pattern 3: Alembic env.py for Autogenerate

**What:** Point Alembic at the app's `Base.metadata` so `alembic revision --autogenerate` can diff against the real schema. Read `DATABASE_URL` from app settings.

**Example:**

```python
# alembic/env.py
from alembic import context
from app.core.config import settings
from app.db.base import Base  # This import triggers all model imports

target_metadata = Base.metadata

def run_migrations_online() -> None:
    from sqlalchemy import create_engine
    connectable = create_engine(settings.database_url)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
```

**app/db/base.py must import all models:**

```python
# app/db/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# These imports register models on Base.metadata — required for autogenerate
from app.models.user import User  # noqa: E402, F401
from app.models.refresh_token import RefreshToken  # noqa: E402, F401
from app.models.interest_form import InterestSubmission  # noqa: E402, F401
from app.models.event_pdf import EventPDF  # noqa: E402, F401
from app.models.rush_info import RushInfo  # noqa: E402, F401
from app.models.org_content import OrgContent  # noqa: E402, F401
from app.models.audit_log import AuditLog  # noqa: E402, F401
```

### Pattern 4: Alembic Migration with Seed Data

**What:** A single `upgrade()` function creates all tables, then inserts seed rows for `rush_info` and `org_content`.

**Example:**

```python
# alembic/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
import uuid
from datetime import datetime, timezone

def upgrade() -> None:
    # --- Schema ---
    op.create_table("users", ...)

    # --- Seed data ---
    op.execute(
        """
        INSERT INTO rush_info (id, dates, times, locations, description, is_published, updated_at)
        VALUES (:id, '', '', '', '', false, :now)
        """,
        {"id": str(uuid.uuid4()), "now": datetime.now(timezone.utc)}
    )
    for section in ("history", "philanthropy", "contacts"):
        op.execute(
            """
            INSERT INTO org_content (id, section, content, updated_at)
            VALUES (:id, :section, '', :now)
            """,
            {"id": str(uuid.uuid4()), "section": section, "now": datetime.now(timezone.utc)}
        )

def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("org_content")
    op.drop_table("rush_info")
    op.drop_table("events")
    op.drop_table("interest_submissions")
    op.drop_table("refresh_tokens")
    op.drop_table("users")
```

### Pattern 5: Synchronous get_db Dependency

**What:** Generator that yields a SQLAlchemy `Session`, closes it after request finishes.

**Example:**

```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# app/core/deps.py
from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Usage in routes (Phase 2+):

```python
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db

DbSession = Annotated[Session, Depends(get_db)]

@router.get("/users/me")
def get_me(db: DbSession):
    ...
```

### Pattern 6: Global Exception Handlers

**What:** Override FastAPI's default handlers to normalize all errors to `{"detail": "...", "status_code": N}`.

**Example:**

```python
# app/main.py additions
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="REST API for Psi Chi Omega San Diego chapter",
)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract field-level errors into a readable string
    errors = exc.errors()
    detail = "; ".join(
        f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in errors
    )
    return JSONResponse(
        status_code=422,
        content={"detail": detail, "status_code": 422},
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Never leak tracebacks in production
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500},
    )
```

**Note:** Use `starlette.exceptions.HTTPException` (not `fastapi.HTTPException`) as the handler target to catch all HTTP exceptions including those raised by Starlette middleware.

### Pattern 7: Ruff Configuration

**What:** `[tool.ruff.lint]` and `[tool.ruff.format]` sections in pyproject.toml, separate from `[tool.ruff]`.

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "W", "F", "I"]
# E = pycodestyle errors, W = pycodestyle warnings, F = pyflakes, I = isort
# Recommendation: also add "UP" (pyupgrade) — harmless, improves idioms
# Do NOT add "ANN" (annotations) — requires type annotations everywhere
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

Run commands:
```bash
ruff check .          # Linting
ruff check --fix .    # Auto-fix safe issues
ruff format .         # Format (like Black)
ruff format --check . # Check formatting without modifying
```

### Pattern 8: Docker Compose Healthcheck

**What:** Add `pg_isready` healthcheck to the `db` service, then use `condition: service_healthy` in the `api` depends_on.

```yaml
# docker/docker-compose.yml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: pco
    ports:
      - "5432:5432"
    volumes:
      - pco_pg:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d pco"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 10s

  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    env_file:
      - ../.env
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ../app:/app/app
      - ../alembic:/app/alembic

volumes:
  pco_pg:
```

### Pattern 9: Dockerfile with uv --frozen

**What:** Must COPY `uv.lock` into the image before running `uv sync --frozen`.

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml uv.lock /app/

RUN pip install --no-cache-dir uv && uv venv && uv sync --frozen --no-dev

COPY app /app/app
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Critical:** Without `COPY uv.lock`, the `--frozen` flag will fail because the lockfile does not exist in the build context.

### Anti-Patterns to Avoid

- **Using `uv sync --no-dev` without `--frozen`:** Non-reproducible; may install different versions than development. Always use `--frozen` in Dockerfile.
- **`jwt_secret: str = "change-me"`:** The current code has this. This default means the app will start with an insecure secret even if the env var is missing. Remove the default entirely.
- **Pydantic v1 `class Config:`:** The existing `config.py` uses v1 syntax. Replace with `model_config = {...}` (Pydantic v2).
- **Importing `fastapi.HTTPException` as exception handler target:** Must use `starlette.exceptions.HTTPException` to catch all HTTP exceptions including Starlette middleware errors.
- **Writing `settings = Settings()` at the bottom of config.py before validators fire:** This is correct Python behavior — `Settings()` triggers validation immediately; putting it at module level means startup fails fast. This is the correct pattern.
- **`app/db/base.py` without model imports:** Alembic autogenerate only sees models that have been imported and registered on `Base.metadata`. All model files must be imported in `base.py`.
- **Alembic env.py hardcoding database URL:** Should read from `settings.database_url` so Docker and local environments use the correct connection string from `.env`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| JWT encode/decode | Custom base64 + HMAC | `PyJWT` (jwt.encode / jwt.decode) | Signature validation, expiry, claims — many edge cases |
| Settings validation | Custom env var parsing | Pydantic `@field_validator` on `BaseSettings` | Automatic env var loading, type coercion, error messages |
| Database connection lifecycle | Manual open/close | SQLAlchemy `sessionmaker` + `get_db()` generator | Proper connection pool, rollback on exception |
| Schema migrations | `Base.metadata.create_all()` at startup | Alembic versioned migrations | Cannot upgrade from create_all; no rollback; loses data on schema changes |
| Error normalization | Try/except in every route | FastAPI `@app.exception_handler()` global handlers | Catches all exceptions including framework-raised ones |
| Import ordering | Manual rules | Ruff `I` rules (isort-compatible) | Consistent, auto-fixable |

**Key insight:** In this phase all problems have standard, well-maintained solutions. Custom implementations add maintenance burden with no benefit.

---

## Common Pitfalls

### Pitfall 1: python-jose Transitive Dependency Conflict
**What goes wrong:** Running `uv remove python-jose` fails or another package still imports it.
**Why it happens:** Some packages (e.g., older versions of `python-multipart` or indirect deps) may list python-jose as a dependency.
**How to avoid:** Before removing, run `uv tree | grep python-jose` to check if any other package depends on it. If a conflict exists, add `PyJWT` first, update any code that imported from `jose`, then remove `python-jose`.
**Warning signs:** Import errors mentioning `jose` module after removal.

### Pitfall 2: Alembic Cannot Find Models for Autogenerate
**What goes wrong:** `alembic revision --autogenerate` generates an empty migration (no tables detected).
**Why it happens:** `env.py` sets `target_metadata = Base.metadata` but the model files are never imported, so `Base.metadata` has no tables registered.
**How to avoid:** `app/db/base.py` must import all model modules after defining `Base`. Then `env.py` imports from `app.db.base`, which triggers all model imports.
**Warning signs:** Generated migration file has empty `upgrade()` function.

### Pitfall 3: uv sync --frozen Fails in Docker Because uv.lock Not Copied
**What goes wrong:** Docker build fails with "No lockfile found" or similar error.
**Why it happens:** The original Dockerfile only copies `pyproject.toml`, not `uv.lock`. The `--frozen` flag requires the lockfile to exist.
**How to avoid:** `COPY pyproject.toml uv.lock /app/` in the Dockerfile before the `uv sync` step.
**Warning signs:** Build error: `error: No lockfile found; run \`uv lock\` to create one`.

### Pitfall 4: Settings Validator Not Running at Startup
**What goes wrong:** App starts successfully with a short/missing JWT_SECRET and only fails when a JWT is first created.
**Why it happens:** `settings = Settings()` is not at module level, or the validator is `mode='before'` which may not run when the env var is absent.
**How to avoid:** Keep `settings = Settings()` at module level in `config.py`. Pydantic will raise `ValidationError` during module import. FastAPI/uvicorn will catch this during startup and exit. Use `mode='after'` for the length validator (runs after Pydantic's built-in required-field check confirms a value exists).
**Warning signs:** App starts with no error; JWT operations fail at runtime.

### Pitfall 5: Pydantic v1 Config Syntax Still Present
**What goes wrong:** `class Config:` in `BaseSettings` may work in pydantic-settings 2.x for backward compatibility, but `env_file` may not be honored correctly; also triggers deprecation warnings.
**Why it happens:** Original `config.py` was written with v1 syntax.
**How to avoid:** Replace `class Config:` with `model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)`. Import `SettingsConfigDict` from `pydantic_settings`.
**Warning signs:** Deprecation warnings in logs: `PydanticDeprecatedSince20`.

### Pitfall 6: FastAPI HTTPException vs StarletteHTTPException
**What goes wrong:** Exception handler registered for `fastapi.HTTPException` misses exceptions raised by Starlette middleware (e.g., 404 for unknown routes).
**Why it happens:** `fastapi.HTTPException` is a subclass of `starlette.exceptions.HTTPException`. Registering the handler on the FastAPI subclass only catches explicitly raised `fastapi.HTTPException`, not the Starlette parent.
**How to avoid:** Register the handler on `starlette.exceptions.HTTPException` (or on `Exception` for a catch-all).
**Warning signs:** 404 responses from unknown routes do not follow the `{"detail": "...", "status_code": N}` format.

### Pitfall 7: Alembic env.py Reads DATABASE_URL from os.environ Instead of Settings
**What goes wrong:** Migration command fails in Docker because `DATABASE_URL` uses a different host name than what's in `.env` (e.g., `localhost` vs `db`).
**Why it happens:** env.py reads the URL directly from environment variable rather than via the Settings class.
**How to avoid:** `from app.core.config import settings` and use `settings.database_url` in env.py. The Settings class reads from `.env` via pydantic-settings, so the correct URL is always used.
**Warning signs:** Alembic connects to wrong host; `Connection refused` during `alembic upgrade head`.

---

## Code Examples

### PyJWT Basic Usage

```python
# Source: https://pyjwt.readthedocs.io/en/latest/usage.html
# PyJWT 2.11.0
import jwt

# Encode
token = jwt.encode({"sub": str(user_id), "exp": expiry}, settings.jwt_secret, algorithm="HS256")

# Decode (always hard-code algorithms list — never derive from token header)
try:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="Token has expired")
except jwt.InvalidTokenError:
    raise HTTPException(status_code=401, detail="Invalid token")
```

### Alembic create_table with UUID columns

```python
# In migration upgrade() function
import sqlalchemy as sa

op.create_table(
    "users",
    sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
    sa.Column("email", sa.String(), nullable=False, unique=True),
    sa.Column("hashed_password", sa.String(), nullable=False),
    sa.Column("full_name", sa.String(), nullable=False),
    sa.Column("role", sa.String(), nullable=False, server_default="member"),
    sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
)
op.create_index("ix_users_email", "users", ["email"], unique=True)
```

### Pydantic v2 Settings with SettingsConfigDict

```python
# Source: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    jwt_secret: str  # No default — required

    @field_validator("jwt_secret", mode="after")
    @classmethod
    def validate_jwt_secret(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError(
                f"JWT_SECRET must be at least 32 characters. Got {len(v)}."
            )
        return v

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
```

### FastAPI Global Exception Handlers

```python
# Source: https://fastapi.tiangolo.com/tutorial/handling-errors/
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    detail = "; ".join(
        f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content={"detail": detail, "status_code": 422},
    )
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `class Config:` in BaseSettings | `model_config = SettingsConfigDict(...)` | Pydantic v2 (2023) | Old syntax deprecated; produces warnings |
| `@validator` | `@field_validator` | Pydantic v2 (2023) | Old decorator removed in v2 |
| python-jose | PyJWT | CVE-2024-33663 (2024), CVE-2025-61152 (2025) | python-jose has unfixed alg:none bypass |
| `uv sync` (no flag) | `uv sync --frozen` | uv design (lockfile always shipped) | Without `--frozen`, lockfile may be ignored in container |
| `Column(UUID)` SQLAlchemy 1.x style | `mapped_column(UUID(as_uuid=True))` with `Mapped` | SQLAlchemy 2.0 (2023) | 1.x style still works but bypasses type safety |
| `depends_on: - db` (Docker) | `depends_on: db: condition: service_healthy` | Docker Compose 3.x | Old form does not wait for DB to be ready, causes race condition |

**Deprecated/outdated in this codebase:**
- `python-jose`: Replaced by PyJWT — CVE risk.
- `jwt_secret: str = "change-me"`: Default value must be removed entirely.
- `class Config: env_file = ".env"`: Replace with `model_config = SettingsConfigDict(...)`.
- `uv sync --no-dev` (in Dockerfile without `--frozen`): Non-reproducible.
- `depends_on: - db` (without healthcheck): Race condition — API starts before DB is ready.

---

## Open Questions

1. **python-jose transitive dependency check**
   - What we know: `pyproject.toml` currently lists `python-jose[cryptography]>=3.3` directly
   - What's unclear: Whether any other installed package (e.g., via supabase-py) also depends on python-jose
   - Recommendation: Run `uv tree | grep python-jose` before removing; if a transitive conflict exists, use `uv remove python-jose` which will error and tell you which package requires it

2. **Alembic migration: autogenerate vs hand-written**
   - What we know: All models are new (empty stub files); autogenerate would produce a correct migration
   - What's unclear: Whether to use `alembic revision --autogenerate` and review/edit the output, or write the migration entirely by hand
   - Recommendation: Write the migration by hand (`001_initial_schema.py`) for precision and to include seed data; autogenerate is useful for diffs, less clean for initial full-schema migrations

3. **supabase-py and aiosmtplib — correct package names on PyPI**
   - What we know: The package names specified in CONTEXT.md are `supabase-py` and `aiosmtplib`
   - What's unclear: `supabase-py` is the PyPI name but the import is `from supabase import create_client` — verify before Phase 4
   - Recommendation: `uv add supabase aiosmtplib` (the PyPI package is `supabase`, not `supabase-py`); flag this in the plan

---

## Validation Architecture

> nyquist_validation is enabled in .planning/config.json

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest (not yet installed — Wave 0 gap) |
| Config file | None — add `[tool.pytest.ini_options]` to pyproject.toml in Wave 0 |
| Quick run command | `pytest app/tests/ -x -q` |
| Full suite command | `pytest app/tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | PyJWT importable; python-jose not importable | smoke | `pytest app/tests/test_foundation.py::test_pyjwt_importable -x` | ❌ Wave 0 |
| INFRA-02 | alembic, supabase, aiosmtplib importable | smoke | `pytest app/tests/test_foundation.py::test_deps_importable -x` | ❌ Wave 0 |
| INFRA-03 | All 7 ORM models importable; __tablename__ correct | unit | `pytest app/tests/test_foundation.py::test_orm_models -x` | ❌ Wave 0 |
| INFRA-04 | Alembic migration runs; all tables exist in test DB | integration | `pytest app/tests/test_foundation.py::test_migration -x` | ❌ Wave 0 |
| INFRA-05 | Settings fails without JWT_SECRET; fails with <32 chars; succeeds with valid secret | unit | `pytest app/tests/test_foundation.py::test_settings_validation -x` | ❌ Wave 0 |
| INFRA-06 | Dockerfile syntax check (no automated runtime test; manual verify) | manual-only | N/A — manual `docker build` | N/A |
| INFRA-07 | `GET /health` returns 200 via TestClient | smoke | `pytest app/tests/test_foundation.py::test_health_endpoint -x` | ❌ Wave 0 |
| XCUT-01 | HTTPException returns `{"detail": ..., "status_code": N}` | unit | `pytest app/tests/test_foundation.py::test_error_format -x` | ❌ Wave 0 |
| XCUT-02 | `/docs` returns 200 | smoke | `pytest app/tests/test_foundation.py::test_openapi_docs -x` | ❌ Wave 0 |
| XCUT-03 | CORS headers present on CORS-triggering request | unit | `pytest app/tests/test_foundation.py::test_cors_headers -x` | ❌ Wave 0 |
| XCUT-05 | `ruff check .` exits 0; `ruff format --check .` exits 0 | tool | `ruff check . && ruff format --check .` | N/A — command not file |

### Sampling Rate

- **Per task commit:** `ruff check . && ruff format --check . && pytest app/tests/test_foundation.py -x -q`
- **Per wave merge:** `pytest app/tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `app/tests/test_foundation.py` — covers INFRA-01 through INFRA-05, INFRA-07, XCUT-01 through XCUT-03
- [ ] `app/tests/conftest.py` — shared fixtures (TestClient, in-memory or test DB session)
- [ ] Framework install: `uv add --dev pytest httpx` — pytest and httpx not in pyproject.toml
- [ ] `pyproject.toml` pytest config: add `[tool.pytest.ini_options]` with `testpaths = ["app/tests"]`

---

## Sources

### Primary (HIGH confidence)
- PyJWT 2.11.0 official docs — https://pyjwt.readthedocs.io/en/latest/usage.html — encode/decode API, exception types, key length requirements
- FastAPI official docs — https://fastapi.tiangolo.com/tutorial/handling-errors/ — exception_handler decorator, StarletteHTTPException import
- FastAPI official docs — https://fastapi.tiangolo.com/tutorial/sql-databases/ — get_db generator pattern, SessionDep Annotated pattern
- SQLAlchemy 2.0 official docs — https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html — DeclarativeBase, Mapped, mapped_column, UUID PK, DateTime, JSON
- Alembic official docs — https://alembic.sqlalchemy.org/en/latest/autogenerate.html — target_metadata setup, autogenerate limitations
- Ruff official docs — https://docs.astral.sh/ruff/configuration/ — pyproject.toml structure, [tool.ruff.lint] vs [tool.ruff.format]
- Pydantic v2 official docs — https://docs.pydantic.dev/latest/concepts/validators/ — @field_validator, mode='after', raising ValueError

### Secondary (MEDIUM confidence)
- CVE-2024-33663 — https://www.vicarius.io/vsociety/posts/algorithm-confusion-in-python-jose-cve-2024-33663 — algorithm confusion in python-jose; verified against multiple CVE databases
- CVE-2025-61152 — WebSearch result — alg:none bypass in python-jose; newer CVE, single source, HIGH plausibility given CVE pattern
- uv --frozen documentation — https://docs.astral.sh/uv/concepts/projects/sync/ — --frozen vs --locked distinction, Dockerfile pattern
- Docker Compose healthcheck — https://docs.docker.com/compose/how-tos/startup-order/ — service_healthy condition for depends_on

### Tertiary (LOW confidence)
- supabase-py PyPI package name: WebSearch indicates the import is `supabase` not `supabase-py`; not verified against PyPI directly — flag for plan

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all packages verified against official docs; versions confirmed
- Architecture: HIGH — all patterns sourced from official FastAPI/SQLAlchemy/Alembic/Pydantic docs
- Pitfalls: HIGH — identified from code inspection (existing config.py has jwt_secret default, v1 Config syntax, no uv.lock copy) + official doc verification
- CVE justification for PyJWT: HIGH — CVE-2024-33663 documented in multiple CVE databases; CVE-2025-61152 is MEDIUM (newer, fewer sources)

**Research date:** 2026-03-03
**Valid until:** 2026-09-03 (stable libraries; Ruff and uv move fast, re-verify flags if >60 days)
