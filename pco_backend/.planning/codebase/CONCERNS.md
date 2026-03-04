# Codebase Concerns

**Analysis Date:** 2026-03-03

## Critical Security Issues

**Authentication Not Implemented:**
- Issue: Login endpoint at `app/api/v1/auth.py` is a stub that returns `{"token": "TODO"}` with no password verification or JWT generation
- Files: `app/api/v1/auth.py`, `app/core/security.py`, `app/core/deps.py`
- Impact: No users can authenticate; all admin endpoints are unprotected; anyone can access `/v1/admin/*` endpoints
- Fix approach: Implement JWT token generation in `app/api/v1/auth.py`, add password verification with `passlib`, create `get_current_user()` dependency in `app/core/deps.py`, add `Depends(get_current_user)` to all admin endpoints

**Weak Default JWT Secret:**
- Issue: `app/core/config.py` line 8 hardcodes `jwt_secret: str = "change-me"`
- Files: `app/core/config.py`, `.env.example`
- Impact: Production deployments using default `.env` will have a compromised secret; JWT tokens can be forged
- Fix approach: Require `JWT_SECRET` environment variable without default; fail startup if not set; document secret generation in README

**No Authorization/Permission Checks:**
- Issue: Admin endpoints in `app/api/v1/admin/` accept any request with no role verification
- Files: `app/api/v1/admin/users.py`, `app/api/v1/admin/events.py`, `app/api/v1/admin/settings.py`
- Impact: Any authenticated user (if auth ever works) can create users, delete events, modify settings regardless of role
- Fix approach: Create role-based access control (RBAC) decorator; add role checking to all admin endpoints; define T6/admin roles in `app/models/role.py`

**Unvalidated File Upload:**
- Issue: `app/api/v1/admin/events.py` line 6-8 accepts any file with no validation
- Files: `app/api/v1/admin/events.py`
- Impact: No file type checking; no size limits; PDFs may be arbitrary content; file not actually saved (TODO stub)
- Fix approach: Add file size limit check; validate MIME type (application/pdf); implement actual file storage to `app/storage/`; add virus scanning

**CORS Misconfiguration:**
- Issue: `app/main.py` line 13 allows `allow_methods=["*"]` and `allow_headers=["*"]`
- Files: `app/main.py`
- Impact: Overly permissive CORS headers allow cross-origin requests from anywhere; exposes endpoints to browser-based attacks
- Fix approach: Restrict to specific HTTP methods (GET, POST, PATCH, DELETE); restrict headers to needed ones (Authorization, Content-Type); tighten `cors_origins`

## Tech Debt

**No Input Validation:**
- Issue: Multiple endpoints accept `dict` parameters with no validation or schema enforcement
- Files: `app/api/v1/auth.py` line 6, `app/api/v1/interest.py` line 13, `app/api/v1/admin/users.py` lines 6 and 11
- Impact: No type safety; no required field validation; invalid data accepted and echoed/stored; breaks API contract
- Fix approach: Define Pydantic schemas in `app/schemas/` (currently empty); use schemas instead of `dict` in endpoint parameters; add validation rules

**In-Memory State Management:**
- Issue: Interest form open/closed state stored in memory as `STATE = {"open": True}` in `app/api/v1/interest.py` line 6
- Files: `app/api/v1/interest.py`, `app/api/v1/admin/settings.py`
- Impact: State lost on restart; not accessible across multiple instances; modified by `app/api/v1/admin/settings.py` but no persistence
- Fix approach: Move to database table; create ORM model in `app/models/`; use session management from `app/core/deps.py`

**No Database Connection:**
- Issue: Database URL configured in `app/core/config.py` line 7 but never used; no SQLAlchemy session/engine initialized
- Files: `app/core/config.py`, `app/core/deps.py`, entire `app/models/` directory
- Impact: No actual data persistence; form submissions echoed but not saved; user data not stored; migrations in `alembic/` never run
- Fix approach: Initialize SQLAlchemy engine and session factory in `app/core/deps.py`; implement `get_db()` dependency; create database models

**Empty Model Files:**
- Issue: All files in `app/models/` are empty (0 bytes): `user.py`, `role.py`, `event_pdf.py`, `interest_form.py`
- Files: `app/models/user.py`, `app/models/role.py`, `app/models/event_pdf.py`, `app/models/interest_form.py`
- Impact: No ORM models to map to database; schema definitions only in `alembic/` (also empty)
- Fix approach: Define SQLAlchemy ORM classes for User, Role, Event, InterestForm; add relationships; populate `alembic/` migrations

**Empty Schema Files:**
- Issue: All Pydantic schema files are empty: `app/schemas/auth.py`, `user.py`, `event.py`, `interest_form.py`
- Files: `app/schemas/auth.py`, `app/schemas/user.py`, `app/schemas/event.py`, `app/schemas/interest_form.py`
- Impact: No request/response validation; endpoints accept bare `dict` instead of typed schemas
- Fix approach: Define LoginRequest, UserCreate, EventCreate, InterestFormSubmit Pydantic models

**Empty Core Modules:**
- Issue: `app/core/security.py`, `app/core/deps.py`, `app/core/logging.py` are empty (1 line each)
- Files: `app/core/security.py`, `app/core/deps.py`, `app/core/logging.py`
- Impact: No JWT/password utilities; no dependency injection setup; no structured logging
- Fix approach: Implement token generation/verification in `security.py`; add `get_db()` and `get_current_user()` in `deps.py`; configure logging

**Empty Test Files:**
- Issue: Test files exist but are empty (0 bytes): `test_auth.py`, `test_interest.py`, `test_events.py`, `conftest.py`
- Files: `app/tests/test_auth.py`, `app/tests/test_interest.py`, `app/tests/test_events.py`, `app/tests/conftest.py`
- Impact: Zero test coverage; no validation of endpoint behavior; no regression protection
- Fix approach: Create unit tests for all endpoints; mock database; add integration tests with test database

## Known Implementation Gaps

**Incomplete TODO Markers:**
- Issue: Multiple endpoints have hardcoded `"TODO"` strings returned to clients
- Files: `app/api/v1/public.py` lines 10-19, `app/api/v1/auth.py` line 8
- Impact: Public info endpoint returns placeholder text instead of real data; authentication returns invalid token
- Fix approach: Implement actual endpoint logic; fetch public info from database; implement JWT token generation

**No PDF Storage:**
- Issue: Event PDF upload endpoint in `app/api/v1/admin/events.py` has no file handling beyond echoing filename
- Files: `app/api/v1/admin/events.py`, `app/storage/paths.py` (empty)
- Impact: Uploaded PDFs not saved; event listing returns empty array
- Fix approach: Configure file storage path; implement file save to `app/storage/`; validate PDF format; store reference in database

**No Interest Form Persistence:**
- Issue: `/v1/interest/submit` endpoint echoes form data but doesn't save it
- Files: `app/api/v1/interest.py`, `app/schemas/interest_form.py`
- Impact: Submitted forms lost immediately; no data collection
- Fix approach: Create `InterestFormDB` model and ORM class; save to database with timestamp

## Performance Concerns

**Inefficient CORS Wildcard Configuration:**
- Issue: `allow_methods=["*"]` and `allow_headers=["*"]` are overly broad
- Files: `app/main.py` lines 12-14
- Impact: Browser will send preflight requests for all methods/headers; increases latency; security risk
- Fix approach: Whitelist specific methods and headers

**No Async Database Calls:**
- Issue: While endpoints use `async def`, there's no actual async database driver configured
- Files: `app/core/config.py` uses `psycopg` (sync); `app/core/deps.py` is empty
- Impact: If database integration is added, sync queries will block event loop
- Fix approach: Use async driver (psycopg async or asyncpg); ensure dependencies are awaited

## Dependencies at Risk

**Missing Production Readiness:**
- Issue: `pyproject.toml` includes security-critical packages (python-jose, passlib) but they're unused; JWT_SECRET default is weak
- Files: `pyproject.toml`
- Impact: Dependencies installed but unused; weak defaults expose production
- Fix approach: Implement token utilities before production; change JWT_SECRET to environment-required

**Deprecated Pattern (dict parameters):**
- Issue: Using bare `dict` for request bodies instead of Pydantic models is deprecated best practice
- Files: All endpoint files in `app/api/v1/`
- Impact: No OpenAPI/Swagger documentation; no validation; IDE support limited
- Fix approach: Replace all `dict` with Pydantic schema classes

## Missing Critical Features

**No User Role System:**
- Issue: Admin endpoints assume "T6" and "admin" roles but `app/models/role.py` is empty; no role model or permission checks
- Files: `app/models/role.py`, `app/api/v1/admin/users.py`
- Impact: Cannot create roles; cannot enforce access control
- Fix approach: Define Role ORM model with name/permissions; create User-Role relationship

**No Event Management:**
- Issue: Event listing returns empty array; no event creation/editing except PDF upload stub
- Files: `app/api/v1/events.py`, `app/models/event_pdf.py`
- Impact: Cannot view or manage events
- Fix approach: Create Event ORM model; implement CRUD endpoints

**No Data Validation/Sanitization:**
- Issue: No validators for email, phone, names, URLs in submissions
- Files: `app/utils/validators.py` (empty)
- Impact: Invalid data accepted; no protection against injection attacks
- Fix approach: Populate `validators.py` with email, phone, URL validators; use in schemas

## Fragile Areas

**Shared Mutable State:**
- Issue: `STATE` dictionary in `app/api/v1/interest.py` is shared across requests and modified by another module
- Files: `app/api/v1/interest.py` line 6, `app/api/v1/admin/settings.py` lines 8 and 13
- Impact: Race conditions possible; state lost on restart; implicit coupling between modules
- Fix approach: Move to database; add proper state management with transaction support

**Missing Error Handling:**
- Issue: No try/except blocks in any endpoint; no error response formatting
- Files: All endpoints in `app/api/v1/`
- Impact: Unhandled exceptions crash endpoints; no graceful error messages to clients
- Fix approach: Add exception handlers in `app/main.py`; return consistent error responses

**Direct Filename Echo:**
- Issue: PDF upload echoes `file.filename` directly without sanitization
- Files: `app/api/v1/admin/events.py` line 8
- Impact: Path traversal possible; user input echoed without validation
- Fix approach: Validate filename; generate safe storage name; never trust user input

## Test Coverage Gaps

**Zero Automated Testing:**
- Issue: All test files empty; no CI/CD test execution
- Files: `app/tests/`
- Impact: Endpoints untested; changes break without detection; no regression protection
- Risk: High - any refactoring could silently break functionality
- Priority: High - test coverage must be established before production

**No Authentication Tests:**
- Issue: JWT/password logic not implemented and untested
- Files: `app/tests/test_auth.py` (empty), `app/api/v1/auth.py` (stub)
- Impact: Auth system has no validation
- Priority: Critical - auth is foundation for all security

**No Database Tests:**
- Issue: No database layer or tests; models and schemas undefined
- Files: `app/models/`, `app/schemas/`, `app/tests/`
- Impact: Cannot verify persistence logic
- Priority: Critical - core functionality depends on this

---

*Concerns audit: 2026-03-03*
