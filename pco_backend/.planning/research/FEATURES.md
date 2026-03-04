# Feature Landscape

**Domain:** REST API backend for a small membership organization (fraternity chapter website)
**Project:** PCO San Diego — Psi Chi Omega chapter backend
**Researched:** 2026-03-03
**Confidence:** HIGH — based on direct codebase analysis, PROJECT.md specification, CONCERNS.md audit, and training knowledge of FastAPI production patterns.

---

## Table Stakes

Features that must exist or the product is insecure, broken, or useless. Missing any of these means the system cannot go to production.

### Auth: JWT Token Issuance (Login)

**Why expected:** Every protected endpoint is inoperable without a working login.
**Complexity:** Medium
**Current state:** Stub only — returns `{"token": "TODO"}` with no verification or JWT generation.
**What's needed:**
- `POST /v1/auth/login` accepts `email` + `password` (typed Pydantic schema, not bare `dict`)
- Query user from DB by email
- Verify plaintext password against bcrypt hash via `passlib.verify()`
- Issue a signed JWT (access token) using `python-jose` with `JWT_SECRET`, `JWT_ALG`, `exp` claim
- Return `access_token`, `token_type: "bearer"`, and `expires_in`
- Return HTTP 401 on invalid credentials (no information leakage about which field is wrong)

**Notes:** Token expiry should be 15–60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`). The current default of 60 min is reasonable for this use case.

---

### Auth: JWT Middleware / `get_current_user` Dependency

**Why expected:** Without this, all admin endpoints accept any request — the current state in the codebase.
**Complexity:** Medium
**Current state:** `app/core/deps.py` is empty. Admin endpoints have no `Depends()` guards.
**What's needed:**
- `get_current_user()` FastAPI dependency in `app/core/deps.py`
- Extracts `Authorization: Bearer <token>` header
- Validates JWT signature, expiry, and payload using `python-jose`
- Returns the authenticated `User` ORM object or raises `HTTPException(401)`
- All protected routes use `Depends(get_current_user)`

**Notes:** Use `oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")` as the scheme extractor. This also enables Swagger UI auth testing automatically.

---

### Auth: JWT Refresh Token

**Why expected:** Short-lived access tokens require a refresh mechanism to avoid forcing re-login every hour.
**Complexity:** Medium
**What's needed:**
- `POST /v1/auth/refresh` accepts a refresh token (in request body or HttpOnly cookie)
- Server validates the refresh token is not expired and matches a stored or signed record
- Returns a new access token (optionally rotates the refresh token)
- Refresh tokens should be longer-lived: 7–30 days

**Notes:** For this use case (small fraternity site, not financial), storing refresh tokens as long-lived JWTs (with a different signing secret or `token_type: "refresh"` claim) is sufficient. Database-backed refresh token storage (revocation list) is a differentiator, not table stakes for v1. Recommend: sign refresh tokens with a separate secret or a "refresh" type claim and validate accordingly.

---

### Auth: Password Hashing

**Why expected:** Plaintext passwords in database is a critical security failure.
**Complexity:** Low
**Current state:** `passlib[bcrypt]` is installed but `app/core/security.py` is empty.
**What's needed:**
- `hash_password(plain: str) -> str` using `passlib.context.CryptContext(schemes=["bcrypt"])`
- `verify_password(plain: str, hashed: str) -> bool`
- Used at: account creation (admin creates member) and login verification

---

### RBAC: Role Enforcement on Admin Endpoints

**Why expected:** Without role enforcement, any authenticated member can create/delete/modify anything.
**Complexity:** Medium
**Current state:** Admin endpoints have no authorization checks whatsoever.
**What's needed:**
- `require_role(*roles)` dependency factory in `app/core/deps.py`
- Checks `current_user.role` against allowed roles
- Raises `HTTPException(403)` if role is insufficient
- Applied as `Depends(require_role("admin"))` on all `/v1/admin/*` endpoints
- Two roles for v1: `member` and `admin` (T6 officers are a subset of admins, not a separate role)

**Notes:** The PROJECT.md specifies "member / admin roles only" for v1. T6 officers are identified by specific role field values (president, vp, treasurer, etc.) on the users table — these are used by the `/api/content/leadership` endpoint, not as access control gates. Admin endpoints require `role == "admin"`.

**Feature dependency:** Requires `get_current_user` dependency to be working first.

---

### Database Models (All Six)

**Why expected:** Every endpoint in the system depends on persistent data. Current state: all model files are empty.
**Complexity:** Medium
**What's needed (six SQLAlchemy ORM models):**

| Model | Table | Purpose |
|-------|-------|---------|
| `User` | `users` | Members + admins. Columns: id, email, password_hash, name, role (enum), is_active, created_at |
| `InterestSubmission` | `interest_submissions` | Rush interest form submissions |
| `EventPDF` | `event_pdfs` | Event PDF metadata (filename, title, date, storage_path) |
| `RushInfo` | `rush_info` | Rush week dates, times, locations, is_published flag |
| `OrgContent` | `org_content` | Key-value or sectioned content: history, philanthropy, contacts |
| `AuditLog` | `audit_log` | Admin action log: actor_id, action, target_id, timestamp |

**Notes:** Role on `User` should be a string enum or PostgreSQL ENUM type. `is_active` boolean enables soft delete (deactivation without data loss). `AuditLog` is required by PROJECT.md for role-change operations.

---

### Alembic Initial Migration

**Why expected:** Without a migration, the database has no schema and nothing works.
**Complexity:** Low
**Current state:** `alembic/env.py` is an empty stub, no migrations exist.
**What's needed:**
- `alembic/env.py` wired to `Base.metadata` from `app/db/base.py`
- Initial migration generating all six tables
- `alembic upgrade head` runnable in Docker startup

**Feature dependency:** Requires all ORM models to be defined first.

---

### Pydantic Request/Response Schemas (All Endpoints)

**Why expected:** FastAPI without typed schemas is not FastAPI — it's just unvalidated dict-passing. No OpenAPI docs, no type safety, no validation.
**Complexity:** Low-Medium
**Current state:** All schema files in `app/schemas/` are empty.
**What's needed:**

| Schema | File | Used By |
|--------|------|---------|
| `LoginRequest`, `TokenResponse` | `auth.py` | POST /auth/login |
| `UserCreate`, `UserOut`, `RoleUpdate` | `user.py` | Admin user CRUD |
| `EventOut`, `EventCreate` | `event.py` | Event listing + upload |
| `InterestFormIn`, `InterestFormOut` | `interest_form.py` | Interest form |
| `RushInfoOut`, `RushInfoUpdate` | `rush.py` (new) | Rush week |
| `OrgContentOut`, `OrgContentUpdate` | `content.py` (new) | Org content sections |

**Notes:** All schemas using Pydantic v2 syntax (`model_config = ConfigDict(from_attributes=True)` instead of v1's `orm_mode = True`). Pydantic v2 is already installed (2.12.5).

---

### SQLAlchemy DB Session Dependency

**Why expected:** Without a DB session factory, no endpoint can read or write data.
**Complexity:** Low
**Current state:** `app/db/session.py` is empty. No engine or session factory exists.
**What's needed:**
- `engine = create_engine(settings.database_url)` in `app/db/session.py`
- `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`
- `get_db()` generator dependency in `app/core/deps.py` yielding a session and closing on exit
- All service calls receive `db: Session = Depends(get_db)`

**Notes:** Use synchronous SQLAlchemy (not async) for simplicity. The CONCERNS.md flags async as a performance concern, but for this traffic level (small fraternity site), sync is correct. Adding async would add complexity without meaningful gain.

---

### Member Management (Admin-Only CRUD)

**Why expected:** Admin-created accounts is the stated auth model — without this, no one can log in at all.
**Complexity:** Medium
**What's needed:**
- `GET /v1/admin/members` — list members, filterable by `active` / `deactivated` query param
- `POST /v1/admin/members` — create member, auto-generate temporary password, send welcome email
- `PATCH /v1/admin/members/{id}/role` — update role field, write audit log entry
- `PATCH /v1/admin/members/{id}/deactivate` — set `is_active = False` (soft delete)
- `PATCH /v1/admin/members/{id}/reactivate` — set `is_active = True`
- `GET /v1/users/me` — current user profile (any authenticated user)

**Notes:** Deactivated users must be blocked at login (check `is_active` before issuing token). Temp password generation: use `secrets.token_urlsafe(12)` — hash it before storage, send plaintext in the welcome email with a "please change your password" note. No self-service password reset for v1.

**Feature dependency:** Requires User model, DB session dependency, auth JWT, SMTP email service.

---

### Interest Form Submission + Persistence

**Why expected:** This is publicly listed as a core feature in PROJECT.md. Currently echoes data without saving.
**Complexity:** Low-Medium
**What's needed:**
- `POST /v1/interest` — public endpoint, validates form fields, checks for duplicate email, saves to DB, sends confirmation email
- `GET /v1/interest` — admin-only, lists all submissions with pagination
- Duplicate email detection: query DB, return 409 Conflict with clear message if duplicate
- Fields: name, email, year/major (validate with regex or Pydantic field validators)

**Feature dependency:** Requires InterestSubmission model, DB session, SMTP email service.

---

### Event PDF Upload + Listing (Supabase Storage)

**Why expected:** The events section is a stated core feature. Currently returns empty array and does not save uploads.
**Complexity:** Medium-High
**What's needed:**
- `GET /v1/events` — auth-required, returns list of events (title, date, storage URL) from DB
- `POST /v1/admin/events` — admin-only, validates file is PDF, enforces 10MB size limit, uploads to Supabase Storage, creates EventPDF DB record
- `DELETE /v1/admin/events/{id}` — admin-only, deletes from Supabase Storage and removes DB record
- `supabase-py` client added to dependencies for storage operations

**Security requirements (table stakes):**
- Validate MIME type: reject if not `application/pdf` (check both content-type header AND magic bytes — do not trust content-type header alone)
- Enforce 10MB limit before reading entire file into memory (check `Content-Length` header or stream and count bytes)
- Generate a safe storage filename: `{uuid4()}.pdf` — never use the user-supplied filename as the storage key
- Store user-supplied title separately in the DB record

**Notes:** CONCERNS.md flags the current stub as echoing `file.filename` directly — this is a path traversal risk. The fix is to never use the original filename as a storage path.

**Feature dependency:** Requires EventPDF model, DB session, supabase-py client, auth/admin RBAC.

---

### Rush Week Management

**Why expected:** Rush info is a core public-facing feature. Admins need to toggle visibility and update details.
**Complexity:** Low-Medium
**What's needed:**
- `GET /v1/rush` — public, returns rush details if `is_published = True`, returns "coming soon" stub if not
- `PUT /v1/rush` — admin-only, updates dates/times/locations/descriptions in DB
- `PATCH /v1/rush/visibility` — admin-only, toggles `is_published` flag
- Replaces the in-memory `STATE` dict (currently in `interest.py` / `settings.py`) with a DB-backed record

**Feature dependency:** Requires RushInfo model, DB session, admin RBAC.

---

### Org Content Management

**Why expected:** The public website needs editable content (history, philanthropy, contacts, leadership).
**Complexity:** Low
**What's needed:**
- `GET /v1/content/history` — public, returns org history text from DB
- `GET /v1/content/philanthropy` — public, returns philanthropy info from DB
- `GET /v1/content/contacts` — public, returns rush chair contact info from DB
- `GET /v1/content/leadership` — public, queries `users` table for records with officer roles (president, vp, treasurer, secretary, marshal, historian), returns structured list
- `PUT /v1/content/{section}` — admin-only, updates content for a given section key

**Notes:** OrgContent can be a simple key-value table: `(section: str, content: str, updated_at)`. Leadership endpoint does not need a separate table — query `users` where `role IN ('president', 'vp', ...)` and only return public-safe fields (name, role — never email or password_hash).

**Feature dependency:** Requires OrgContent model, User model, DB session, admin RBAC.

---

### SMTP Email Service

**Why expected:** Two features depend on it: welcome email on account creation, confirmation email on interest form submission.
**Complexity:** Low-Medium
**What's needed:**
- Generic SMTP client configured via env vars: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`
- `send_email(to: str, subject: str, body: str)` utility in `app/utils/email.py` or `app/services/email_service.py`
- Uses Python stdlib `smtplib` + `email.mime` — no third-party email library needed for basic SMTP
- Graceful failure: log the error, do not crash the endpoint if SMTP fails (especially for interest form confirmation)

**Notes:** For welcome emails containing temporary passwords, the email send should succeed before the account is committed, or the account creation should be rolled back if email fails (to avoid creating an account nobody knows about). For interest form confirmation, email failure should not fail the form submission — just log it.

---

### Consistent Error Response Format

**Why expected:** Without a standard error format, clients cannot reliably handle errors.
**Complexity:** Low
**What's needed:**
- Global exception handler in `app/main.py` for `HTTPException` → standard JSON: `{"error": {"code": 404, "message": "Not found"}}`
- Global handler for unhandled `Exception` → HTTP 500 with generic message (never expose internal details)
- Pydantic `RequestValidationError` handler → HTTP 422 with field-level error details
- Applied project-wide via `@app.exception_handler()`

---

### Required Environment Variable Validation at Startup

**Why expected:** CONCERNS.md flags the default `jwt_secret: str = "change-me"` as a critical security issue. The server must refuse to start with insecure defaults.
**Complexity:** Low
**What's needed:**
- `JWT_SECRET` must be required with no default — use `jwt_secret: str` without a default value in Pydantic Settings, which will raise at startup if missing
- Add validators for minimum secret length (e.g., 32 characters)
- Add `model_validator` in `Settings` to block startup in `ENV=production` if any critical value is a known-bad default

---

## Differentiators

Features that are valuable for this specific use case but not strictly required for the system to function. Build after table stakes are solid.

### Refresh Token Revocation (Token Blacklist)

**Value:** Allows admins to force-logout a user (e.g., after deactivating their account). Without this, a deactivated user's existing access token remains valid until expiry.
**Complexity:** Medium
**What's needed:** Store issued refresh tokens in a `refresh_tokens` table. On deactivation or explicit logout, mark the token as revoked. On `/auth/refresh`, check revocation status. On deactivation, clean up all tokens for that user.
**When to build:** After the basic auth flow is working end-to-end.

---

### `POST /v1/auth/logout`

**Value:** Explicit logout endpoint. Without it, clients must just discard the token locally (fine for most use cases, but no server-side revocation).
**Complexity:** Low (if refresh token DB is implemented; trivial otherwise)
**What's needed:** Accepts refresh token, marks it revoked in DB. Returns 204.

---

### Password Change Endpoint

**Value:** Members should be able to change their temporary password after first login without needing admin intervention.
**Complexity:** Low
**What's needed:** `POST /v1/users/me/change-password` — requires current password + new password, bcrypt hashes new password, updates DB.

---

### Audit Log for All Admin Actions

**Why valuable:** PROJECT.md requires audit logging for role changes specifically. Extending it to all admin actions (member create, deactivate, content update, event upload/delete) gives the chapter leadership an accountability trail.
**Complexity:** Low
**What's needed:** `AuditLog` model (required anyway per PROJECT.md). Write an entry in every admin endpoint: actor_id, action string, target_id, old_value (optional), new_value (optional), timestamp.

---

### Structured Logging

**Value:** Debugging production issues without structured logs is painful. FastAPI + uvicorn emit basic access logs; structured logs let you filter by request_id, user_id, endpoint, etc.
**Complexity:** Low
**What's needed:** Configure Python's `logging` module in `app/core/logging.py`. Use JSON format in production (`ENV=production`), human-readable in dev. Log request IDs (generate per-request UUID, attach to context). Log auth failures with user email (no password).

---

### Request Rate Limiting on Public Endpoints

**Value:** The interest form submit endpoint and the login endpoint are public-facing and invite abuse (form spam, brute-force password attempts).
**Complexity:** Medium
**What's needed:** `slowapi` (FastAPI-compatible wrapper around `limits`) or IP-based rate limiting in an upstream reverse proxy (nginx). For a small org site, upstream limiting is simpler.
**Recommendation:** Use nginx rate limiting in production rather than application-level. Skip for v1 unless spam is a concern.

---

### Pagination on List Endpoints

**Value:** `GET /v1/admin/members` and `GET /v1/interest` will have bounded data volumes for a fraternity chapter (likely never more than 200 members or 1000 submissions). Pagination is good practice but not urgent.
**Complexity:** Low
**What's needed:** Standard `?page=1&page_size=20` query params, add `total`, `page`, `items` envelope to responses.

---

### `GET /v1/users/me` + Profile Update

**Value:** Members want to see and update their own profile (display name, contact info).
**Complexity:** Low
**What's needed:** `GET /v1/users/me` (already in PROJECT.md). Optionally `PATCH /v1/users/me` for self-service name/phone updates.

---

### PDF MIME Type Magic Byte Validation

**Value:** Content-type header is user-controlled. A malicious actor can upload an EXE with `Content-Type: application/pdf`. Checking the first 4 bytes (`%PDF`) is a meaningful additional check.
**Complexity:** Low
**What's needed:** In the upload handler, read the first 4 bytes and check `== b"%PDF"`. Reject with 415 if not.
**Note:** This is borderline table stakes for file upload security, but listed here because the immediate danger is primarily size abuse and MIME header spoofing, which are caught by the table stakes controls.

---

## Anti-Features

Things to deliberately NOT build for v1 (and possibly never).

### Public User Self-Registration

**Why avoid:** PROJECT.md explicitly excludes this. Admin-created accounts is the security model — chapter membership is curated. Open registration would undermine the entire access control model.
**What to do instead:** Admin creates account, emails temporary password via SMTP.

---

### OAuth / Social Login (Google, GitHub, etc.)

**Why avoid:** Adds OAuth client complexity, callback URL management, token exchange, and external service dependency. For a fraternity backend with admin-controlled accounts, it solves no real problem.
**What to do instead:** Email/password with secure JWT. Members are created by admins — they don't "sign up".

---

### Password Reset via Email Link (Forgot Password Flow)

**Why avoid:** Requires token-signed reset links with expiry, secure URL generation, one-time-use enforcement, and a frontend page to handle the callback. Significant complexity for a use case covered by "admin resets your password".
**What to do instead:** Admin deactivates and recreates the account, or implements a simple password change endpoint for logged-in users (differentiator above). If needed in v2, build it then.

---

### Real-Time Features (WebSockets, SSE)

**Why avoid:** PROJECT.md explicitly excludes this. Nothing in the feature set requires real-time updates.
**What to do instead:** Standard request/response REST API.

---

### Rich Text / CMS Editing

**Why avoid:** The org content sections (history, philanthropy, contacts) are plain text or simple structured data. A full CMS (with WYSIWYG editors, image uploads, versioning) is massive scope creep.
**What to do instead:** `PUT /v1/content/{section}` accepts a `content` string. The frontend handles display formatting. Markdown is acceptable; full HTML is not (XSS risk if rendered directly).

---

### Image Uploads (Member Photos, Event Banners)

**Why avoid:** Only PDF uploads are in scope. Image uploads require additional validation (image format, dimensions, size), separate storage path management, and potentially image resizing. Not needed for v1.
**What to do instead:** Store a URL field on officer records or content sections if linking to external images is needed.

---

### Pledge Process Module

**Why avoid:** Explicitly removed from v1 scope per PROJECT.md. Premature to design a pledge tracking system before the core auth + content system exists.
**What to do instead:** Leave the schema extensible (the `role` field on users can accommodate future pledge status). Design the v2 pledge module when v1 is stable.

---

### Admin Dashboard API (Analytics, Stats Endpoints)

**Why avoid:** Requires aggregation queries, potentially complex joins, and provides marginal value for a small chapter. Member count and submission counts can be added to existing list endpoints as metadata.
**What to do instead:** Simple `total` field on paginated list responses is sufficient.

---

### Multi-Tenancy (Multiple Chapters)

**Why avoid:** This is a single-chapter backend. Building multi-tenancy now (org_id scoping, chapter isolation) adds significant schema and query complexity for zero near-term value.
**What to do instead:** Single-tenant design. If expansion to other chapters is needed, it's a re-architecture, not an addition.

---

## Feature Dependencies

```
bcrypt password hashing
    └── JWT token issuance (login)
        └── get_current_user dependency
            └── RBAC role enforcement
                └── all admin endpoints

ORM models (User, Event, etc.)
    └── Alembic initial migration
    └── DB session dependency (get_db)
        └── member management endpoints
        └── interest form persistence
        └── rush info management
        └── org content management
        └── event PDF listing

Supabase storage client
    └── PDF upload/delete endpoints

SMTP email service
    └── interest form confirmation email
    └── welcome email (member creation)

Pydantic schemas (all)
    └── every endpoint (replaces bare dict params)
    └── OpenAPI documentation
```

---

## MVP Recommendation

### Must ship in Phase 1 (nothing works without these):

1. **Pydantic schemas** — every other feature needs these
2. **DB session dependency** + **ORM models** + **Alembic migration** — database foundation
3. **Password hashing utilities** — needed before any user can be created
4. **JWT token issuance** (login endpoint, real implementation)
5. **`get_current_user` dependency** + **RBAC enforcement**
6. **Required env var validation** at startup (kill the "change-me" default)
7. **Consistent error response format**

### Must ship in Phase 2 (core feature set):

8. **Member management** (admin CRUD + deactivation)
9. **SMTP email service**
10. **Interest form persistence** + confirmation email
11. **Rush info management** (DB-backed, replaces in-memory STATE)
12. **Org content management**
13. **JWT refresh token** endpoint

### Must ship in Phase 3 (file uploads, complete feature surface):

14. **Event PDF upload** (Supabase Storage, MIME validation, size limit)
15. **Event listing** (from DB)
16. **Audit log** writes (role change, deactivation, content edits)

### Defer to later:

- Password change endpoint (self-service)
- Refresh token revocation / explicit logout
- Structured JSON logging
- Rate limiting
- Pagination

---

## Sources

- `/Users/dp/Workspace/PCO-Website/pco_backend/.planning/PROJECT.md` — authoritative requirements spec (HIGH confidence)
- `/Users/dp/Workspace/PCO-Website/pco_backend/.planning/codebase/CONCERNS.md` — security and tech debt audit (HIGH confidence)
- `/Users/dp/Workspace/PCO-Website/pco_backend/.planning/codebase/ARCHITECTURE.md` — layer structure (HIGH confidence)
- `/Users/dp/Workspace/PCO-Website/pco_backend/.planning/codebase/STACK.md` — installed dependencies (HIGH confidence)
- Direct codebase inspection: `app/core/config.py`, `app/api/v1/*.py`, `app/api/v1/admin/*.py`, `app/api/router.py`, `app/main.py` (HIGH confidence)
- FastAPI production patterns (training knowledge, HIGH confidence — FastAPI patterns are stable and well-documented as of 2025)
- python-jose, passlib, SQLAlchemy 2.0 patterns (training knowledge, HIGH confidence)
