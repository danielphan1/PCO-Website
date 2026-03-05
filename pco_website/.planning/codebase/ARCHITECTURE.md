# Architecture

**Analysis Date:** 2026-03-05

## Pattern Overview

**Overall:** Monorepo with two independent services — a FastAPI REST backend (`pco_backend`) and a Next.js 15 App Router frontend (`pco_website`). The backend follows a layered service architecture. The frontend is currently a scaffold with no application logic.

**Key Characteristics:**
- Backend: strict layered separation — Router → Service → ORM Model → DB
- JWT access token + refresh token rotation for authentication
- Role-based access control: `member`, `admin`, officer roles (`president`, `vp`, `treasurer`, `secretary`, `historian`)
- Supabase Storage for PDF file uploads; PostgreSQL for all relational data
- Emails sent asynchronously as FastAPI `BackgroundTask` — failures are swallowed and logged

## Layers

**API Layer (Routers):**
- Purpose: HTTP request/response handling, input deserialization, dependency injection, response serialization
- Location: `pco_backend/app/api/v1/` and `pco_backend/app/api/v1/admin/`
- Contains: FastAPI `APIRouter` instances, endpoint functions, Pydantic response models
- Depends on: Service layer, `app.core.deps` for auth/DB injection, Pydantic schemas
- Used by: FastAPI app via `pco_backend/app/api/router.py`

**Service Layer:**
- Purpose: Business logic, validation, DB mutations, audit logging
- Location: `pco_backend/app/services/`
- Contains: Pure Python functions receiving `db: Session` and returning ORM models or raising `HTTPException`
- Depends on: ORM models, security utilities, storage layer
- Used by: API routers

**ORM Model Layer:**
- Purpose: Database schema definition and SQLAlchemy relationships
- Location: `pco_backend/app/models/`
- Contains: SQLAlchemy `DeclarativeBase` subclasses
- Depends on: `app.db.base_class.Base`
- Used by: Service layer, dependency injection in routers

**Schema Layer (Pydantic):**
- Purpose: Request/response validation and serialization
- Location: `pco_backend/app/schemas/`
- Contains: Pydantic `BaseModel` subclasses for request bodies and API responses
- Depends on: Nothing internal
- Used by: API routers for type annotations, service functions for input types

**Core / Cross-Cutting:**
- Purpose: Auth dependencies, config, security utilities, logging
- Location: `pco_backend/app/core/`
- Contains: `deps.py` (FastAPI dependencies), `config.py` (pydantic-settings), `security.py` (JWT + bcrypt), `logging.py`
- Depends on: Nothing internal (bottom of dependency tree)
- Used by: All other layers

**DB Layer:**
- Purpose: SQLAlchemy engine/session setup and Alembic migration support
- Location: `pco_backend/app/db/`
- Contains: `session.py` (engine + SessionLocal), `base.py` (model registry imports), `base_class.py` (DeclarativeBase), `init_db.py`
- Depends on: `app.core.config`
- Used by: `app.core.deps.get_db`, service layer indirectly

**Storage Layer:**
- Purpose: Supabase Storage SDK abstraction for PDF file operations
- Location: `pco_backend/app/storage/`
- Contains: `files.py` (StorageService singleton), `paths.py` (path generators)
- Depends on: `app.core.config` for Supabase credentials
- Used by: `app.services.event_service`

**Frontend (Next.js App Router):**
- Purpose: User interface — currently a scaffold with no application logic
- Location: `pco_website/app/`
- Contains: `layout.tsx` (root layout), `page.tsx` (placeholder home page), `globals.css`
- Status: No API integration implemented yet; default create-next-app boilerplate

## Data Flow

**Authenticated API Request:**

1. Client sends `Authorization: Bearer <access_token>` header
2. `app.core.deps.get_current_user` validates JWT via `decode_access_token`, fetches `User` from DB
3. Router endpoint receives injected `User` + `Session` via FastAPI `Depends`
4. Router calls service function (e.g., `user_service.list_members(db, ...)`)
5. Service executes SQLAlchemy query, writes audit log atomically in same commit
6. Router returns ORM model; FastAPI serializes via `response_model` Pydantic schema

**Login Flow:**

1. Client POST `/v1/auth/login` with email + password
2. `auth.py` router queries `User` by email, runs bcrypt verify (timing-safe dummy verify if user not found)
3. Creates `RefreshToken` row (stores SHA-256 hash of raw token, not raw token)
4. Returns `access_token` (JWT, short-lived) and `refresh_token` (opaque, long-lived)

**Refresh Token Rotation:**

1. Client POST `/v1/auth/refresh` with `refresh_token`
2. Router hashes token and looks up `RefreshToken` row
3. Inserts new `RefreshToken` row first (safe ordering), then marks old row `revoked=True`
4. Returns new access + refresh token pair

**Event PDF Upload:**

1. Admin POST `/v1/admin/events/` with multipart form (file, title, date)
2. Router reads file bytes, calls `event_service.upload_event`
3. Service validates size (10 MB max) and PDF magic bytes (`%PDF` header)
4. Uploads to Supabase Storage bucket `events` at path `events/{uuid}.pdf`
5. On success, inserts `EventPDF` row; on DB failure, best-effort removes file from storage
6. Returns `EventResponse` with signed URL (1-hour expiry)

**Email Delivery:**

1. Router registers `email_service.send_welcome_email` or `send_interest_confirmation` as `BackgroundTask`
2. FastAPI sends HTTP response to client immediately
3. Background task executes async SMTP send via `aiosmtplib`; SMTP errors are logged and swallowed

## Key Abstractions

**`get_current_user` dependency:**
- Purpose: Validates Bearer JWT, returns `User` ORM model or raises 401/403
- Location: `pco_backend/app/core/deps.py`
- Pattern: FastAPI `Depends()` — inject into any protected route parameter

**`require_admin` dependency:**
- Purpose: Wraps `get_current_user` and enforces `role == "admin"`; raises 403 otherwise
- Location: `pco_backend/app/core/deps.py`
- Pattern: Chain of `Depends()` — `require_admin` depends on `get_current_user`

**`get_db` dependency:**
- Purpose: Yields a SQLAlchemy `Session` scoped to the HTTP request; closes on response
- Location: `pco_backend/app/core/deps.py`
- Pattern: Generator-based `Depends()` with `try/finally` for cleanup

**`StorageService` singleton:**
- Purpose: Wraps Supabase Storage SDK for upload, signed URL creation, removal
- Location: `pco_backend/app/storage/files.py`
- Pattern: Module-level singleton `storage_service = StorageService()`, lazy Supabase client init

**`AuditLog` model:**
- Purpose: Records all admin mutations (member create/update/deactivate/reactivate) with actor, action, target
- Location: `pco_backend/app/models/audit_log.py`
- Pattern: Written atomically in the same `db.commit()` as the mutation it records

**`Base` (DeclarativeBase):**
- Purpose: Shared SQLAlchemy declarative base for all ORM models
- Location: `pco_backend/app/db/base_class.py`
- Pattern: All models import and extend `Base`; `app/db/base.py` imports all models to register them in the mapper

## Entry Points

**FastAPI Application:**
- Location: `pco_backend/app/main.py`
- Triggers: Uvicorn/ASGI server
- Responsibilities: Creates `FastAPI` app, registers global exception handlers (HTTP, validation, unhandled), configures CORS, mounts API router, exposes `/health`

**API Router Registry:**
- Location: `pco_backend/app/api/router.py`
- Triggers: Imported and mounted by `main.py`
- Responsibilities: Aggregates all versioned routers under `/v1/` prefix

**Next.js Root Layout:**
- Location: `pco_website/app/layout.tsx`
- Triggers: Next.js App Router
- Responsibilities: Sets HTML root, applies Geist/Geist Mono fonts, wraps all pages

## Error Handling

**Strategy:** Centralized exception handlers in `main.py`. All errors normalized to `{"detail": "...", "status_code": N}` JSON shape. Tracebacks never leak to clients.

**Patterns:**
- `StarletteHTTPException` handler: re-serializes to normalized JSON
- `RequestValidationError` handler: flattens Pydantic 422 errors to readable `detail` string
- Unhandled `Exception` handler: returns generic 500, prevents traceback exposure
- Service layer raises `HTTPException` directly (FastAPI pattern — no custom exception classes)
- SMTP failures: caught in `email_service`, logged via `logging.getLogger(__name__)`, not re-raised

## Cross-Cutting Concerns

**Logging:** Standard library `logging` with `logging.getLogger(__name__)` per module. No structured logging framework detected.

**Validation:** Pydantic schemas at the router boundary for request deserialization. ORM-level constraints (unique, nullable) as fallback. Role validation in service layer against `ALL_ROLES` list.

**Authentication:** JWT Bearer via `get_current_user` dependency. Short-lived access tokens (60 min default), long-lived refresh tokens (30 days), stored as SHA-256 hashes. Deactivation revokes all active refresh tokens.

**Timing Attack Prevention:** `_dummy_verify()` in `security.py` runs bcrypt on every failed login (including user-not-found) to prevent user enumeration via response timing.

---

*Architecture analysis: 2026-03-05*
