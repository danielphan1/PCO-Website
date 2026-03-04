# Project Research Summary

**Project:** PCO San Diego Backend API (Psi Chi Omega chapter)
**Domain:** REST API backend — JWT auth, RBAC, file storage, SMTP email, PostgreSQL
**Researched:** 2026-03-03
**Confidence:** HIGH

---

## Executive Summary

The PCO San Diego backend is a small-organization REST API serving a fraternity chapter website. It is built on a well-chosen, already-partially-scaffolded FastAPI + PostgreSQL stack that follows production-grade conventions (layered architecture, dependency injection, Pydantic v2 schemas). The primary work is implementing empty stubs — every critical directory, file, and configuration key already exists; almost nothing needs to be invented. The scaffold is correct; it just has no business logic yet.

The recommended approach is a strict dependency-first build order: database models and migrations first, security utilities and auth second, protected endpoints third, external integrations (Supabase Storage, SMTP) fourth. This ordering is non-negotiable because the feature dependency graph is a straight chain: no endpoint works without a database session, no protected endpoint works without auth, no file upload works without the auth gate. Attempting to build features out of this order produces stubs that must be revisited.

The most significant risks are concentrated in the auth implementation phase, not the feature phases. Three critical security decisions must be made before writing the first line of auth code: (1) replace python-jose with PyJWT to eliminate known CVEs, (2) remove the "change-me" JWT secret default from Pydantic Settings and require a minimum-length secret at startup, and (3) establish the refresh token database table in the initial migration so deactivation can be enforced immediately. These are not refactors to do later — they are prerequisites for a correct auth implementation.

---

## Key Findings

### Recommended Stack

See full analysis: `.planning/research/STACK.md`

The installed core stack (FastAPI 0.135.1, Pydantic v2.12.5, SQLAlchemy 2.0+, psycopg3 3.3.3) is current, well-matched, and already locked in `uv.lock`. No changes to the installed base are needed or warranted.

Three runtime dependencies are NEEDED but not yet added to `pyproject.toml`:

**Core technologies:**
- FastAPI 0.135.1: primary web framework — industry-standard async Python API with automatic OpenAPI docs
- Pydantic v2 (2.12.5): request/response validation — v2 is the current generation with Rust-core performance; all schemas must use v2 syntax (`model_config = ConfigDict(from_attributes=True)`, not `orm_mode`)
- SQLAlchemy 2.0 + psycopg3: ORM + PostgreSQL driver — synchronous mode recommended for this traffic scale; async adds complexity without benefit
- Alembic (NEEDED — add with `uv add alembic`): database migrations — directory stubs exist but package is missing from `pyproject.toml` and `alembic.ini` does not exist
- supabase-py >= 2.10 (NEEDED — add with `uv add "supabase>=2.10"`): Supabase Storage client only — all database queries go through SQLAlchemy, not PostgREST
- aiosmtplib >= 3.0 (NEEDED — add with `uv add "aiosmtplib>=3.0"`): async SMTP for email; do NOT use `smtplib` directly in async context
- python-jose (REPLACE with PyJWT >= 2.8): python-jose has known CVEs and `alg: none` bypass risk; swap before writing auth code
- pytest + httpx + pytest-asyncio (NEEDED as dev deps): test infrastructure for the existing `app/tests/` stub directory

**Critical Docker gap:** The Dockerfile does not copy `uv.lock` and does not use `--frozen`, making builds non-reproducible. Must fix before any production deployment.

**Config gaps:** 9 new environment variables must be added to `Settings` before Supabase Storage and SMTP can be used (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_STORAGE_BUCKET`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `REFRESH_TOKEN_EXPIRE_DAYS`).

### Expected Features

See full analysis: `.planning/research/FEATURES.md`

**Must have (table stakes — system is broken or insecure without these):**
- Password hashing utilities (passlib bcrypt) — `app/core/security.py` is empty; plaintext passwords is a critical failure
- JWT login endpoint (`POST /v1/auth/login`) — current stub returns `{"token": "TODO"}`
- `get_current_user` dependency — `app/core/deps.py` is empty; all admin endpoints are currently unguarded
- RBAC role enforcement (`require_role("admin")`) — no authorization checks exist anywhere
- JWT refresh token (`POST /v1/auth/refresh`) — needed with short-lived access tokens
- All six SQLAlchemy ORM models (User, InterestSubmission, EventPDF, RushInfo, OrgContent, AuditLog)
- Alembic initial migration — without this, the database has no schema
- Pydantic request/response schemas for all endpoints — all `app/schemas/` files are empty
- SQLAlchemy DB session dependency (`get_db`) — `app/db/session.py` is empty
- Member management admin CRUD — without this, no accounts can be created and no one can log in
- Interest form persistence — currently echoes data without saving
- Event PDF upload + listing via Supabase Storage — currently returns empty array, does not save uploads
- Rush week management (DB-backed, replacing in-memory `STATE` dict)
- Org content management (history, philanthropy, contacts, leadership endpoints)
- SMTP email service (welcome email on account creation, confirmation email on interest form)
- Consistent error response format (global exception handlers in `main.py`)
- Startup env var validation — kill the `jwt_secret = "change-me"` default

**Should have (differentiators — valuable but not blocking launch):**
- Refresh token revocation / token blacklist table (enables immediate deactivation enforcement)
- Explicit logout endpoint (`POST /v1/auth/logout`)
- Self-service password change (`POST /v1/users/me/change-password`)
- Audit log for all admin actions (role changes, deactivations, content edits)
- Structured JSON logging with request IDs
- Rate limiting on public endpoints (recommend nginx-level rather than application-level)
- Pagination on list endpoints

**Defer (v2+ — explicitly excluded or out of scope):**
- Public user self-registration — security model is admin-created accounts; open registration breaks it
- OAuth / social login — adds complexity for no real benefit given admin-controlled accounts
- Password reset via email link — significant complexity; admin reset covers the use case
- Real-time features (WebSockets, SSE) — explicitly excluded by PROJECT.md
- Rich text / CMS editing — plain text is sufficient; full CMS is scope creep
- Image uploads — only PDF uploads are in scope
- Pledge process module — explicitly removed from v1 scope
- Multi-tenancy — this is a single-chapter backend

### Architecture Approach

See full analysis: `.planning/research/ARCHITECTURE.md`

The scaffold already implements the correct production architecture: layered, dependency-injected, service-oriented. The component boundaries are well-defined. Routes are thin (validate schema, call service, return response). Services orchestrate business logic. The dependency chain (`get_db` → `get_current_user` → `require_admin`) gates all protected routes. No restructuring is needed.

**Major components:**
1. Route handlers (`app/api/v1/**/*.py`) — validate input via Pydantic schemas, call services, return typed responses; 5-15 lines each
2. Dependency layer (`app/core/deps.py`) — per-request DB session, JWT decode + user load, role enforcement; currently empty stubs that must be implemented first
3. Service layer (`app/services/`) — all business logic: AuthService, UserService, EventService, InterestService, EmailService, StorageService
4. Security utilities (`app/core/security.py`) — pure functions only: `hash_password`, `verify_password`, `create_access_token`, `decode_token`; no DB or service imports
5. Data layer (`app/db/session.py`) — SQLAlchemy sync engine + session factory; sync `def` endpoints (not `async def`) to avoid blocking the event loop with sync ORM calls
6. Email as background tasks — always use `BackgroundTasks.add_task()` for SMTP; never call email synchronously in the request path
7. StorageService (`app/storage/files.py`) — thin supabase-py wrapper; called only from EventService, never directly from routes

**Key architectural decision: sync vs. async.** Use synchronous SQLAlchemy (`create_engine`) with synchronous route handlers (`def`, not `async def`). FastAPI runs sync handlers in a thread pool, making blocking safe. Async ORM adds significant complexity for no benefit at this traffic scale (small fraternity chapter, dozens to hundreds of concurrent users maximum).

### Critical Pitfalls

See full analysis: `.planning/research/PITFALLS.md` (24 pitfalls documented)

**Top 5 — must prevent before writing code in each phase:**

1. **Weak JWT secret default survives to production** — remove the `jwt_secret: str = "change-me"` default entirely; require `JWT_SECRET` with no fallback and a startup validator enforcing >= 32 characters. Fix this in the config refactor before writing any auth logic.

2. **python-jose has CVEs including `alg: none` bypass** — replace with PyJWT >= 2.8 before writing the auth implementation. Always pass `algorithms=["HS256"]` explicitly to `jwt.decode()`. python-jose 3.5.0 is installed but has a history of critical vulnerabilities.

3. **Deactivated user retains active session** — `get_current_user` must always query the database and check `is_active == True`; never trust JWT claims alone. On deactivation, revoke all refresh tokens for that user in the same transaction. Reduce access token TTL to 15 minutes.

4. **File upload validation bypassed via Content-Type spoofing** — check PDF magic bytes (`%PDF`, first 4 bytes) in addition to the `Content-Type` header; enforce the 10MB size limit in application code by reading with a cap; generate UUID-based storage filenames (never use user-supplied filenames as storage paths).

5. **Supabase Storage bucket accidentally left public** — configure the bucket as private from day one; all file access must be mediated by the API using the service role key; store only relative paths in the database (not full Supabase URLs) to survive bucket or project migration.

**Additional high-priority pitfalls:**
- Sync SQLAlchemy called inside `async def` handlers blocks the event loop — use `def` for all DB-accessing endpoints
- SQLAlchemy sessions created outside `get_db()` dependency leak connections — only create sessions via the dependency
- Supabase service role key must use Pydantic `SecretStr` type and must never appear in logs, error responses, or committed `.env` files
- SMTP exceptions must be caught specifically and return generic error messages — `str(e)` from `smtplib` can expose credentials

---

## Implications for Roadmap

Based on the combined research, the feature dependency graph and architectural build order dictate a clear 4-phase structure. This is not arbitrary — each phase is a prerequisite for the next.

### Phase 1: Foundation — Config, Database, and Security Utilities

**Rationale:** Nothing else can be built without a working database schema and correct security primitives. This phase eliminates all critical security defaults before any auth logic is written. The PITFALLS research is unusually clear: fix the JWT secret and swap the JWT library first, or everything built on top is insecure by default.

**Delivers:**
- Config refactored: `jwt_secret` has no default, startup validation enforces minimum length; `SettingsConfigDict` replaces old Pydantic v1 `class Config` syntax; all new env vars added (`SUPABASE_*`, `SMTP_*`, `REFRESH_TOKEN_EXPIRE_DAYS`)
- Dependencies added: `alembic`, `supabase>=2.10`, `aiosmtplib>=3.0`; python-jose replaced with `PyJWT>=2.8`; dev deps added (`pytest`, `httpx`, `pytest-asyncio`, `ruff`)
- Docker fixed: `uv.lock` copied and `--frozen` flag used for reproducible builds
- Six ORM models defined (User, InterestSubmission, EventPDF, RushInfo, OrgContent, AuditLog) plus `refresh_tokens` table
- Alembic configured (`alembic.ini`, `env.py` wired to `Base.metadata`) and initial migration generated and verified
- DB session dependency (`get_db`) implemented in `app/core/deps.py`
- Security utilities (`hash_password`, `verify_password`, `create_access_token`, `create_refresh_token`, `decode_token`) implemented in `app/core/security.py` as pure functions
- Global exception handlers registered in `main.py` for consistent error response format
- OpenAPI docs disabled in production (`ENV=prod`)

**Avoids pitfalls:** #1 (weak JWT default), #3 (python-jose CVEs), #5 (session leak), #6 (async/sync mismatch), #7-8 (Alembic autogenerate misses, migration head conflicts), #20 (circular imports in Alembic), #22 (Pydantic v1 config syntax)

**Research flag:** Standard patterns — well-documented FastAPI and SQLAlchemy conventions. No additional research phase needed.

---

### Phase 2: Authentication and Authorization

**Rationale:** Auth is the load-bearing gate for all protected endpoints. Nothing in Phase 3 or 4 can be built or tested without working login, token verification, and role enforcement. The refresh token infrastructure must be built here — not in Phase 3 — because deactivation enforcement depends on it.

**Delivers:**
- `POST /v1/auth/login` — real implementation (bcrypt verify, JWT issue, is_active check)
- `POST /v1/auth/refresh` — refresh token exchange with database-backed revocation
- `get_current_user` dependency — JWT decode, database user load, is_active enforcement
- `require_admin` dependency — role check, raises 403 if insufficient
- Router-level dependency application on all admin routers (not per-route)
- Timing-safe login (dummy bcrypt run when user not found, identical 401 for all failure modes)
- All admin routers declare `dependencies=[Depends(require_admin)]`

**Implements:** Auth dependencies layer, security utilities, refresh_tokens table integration

**Avoids pitfalls:** #1 (weak secret), #2 (refresh token no expiry/revocation), #3 (JWT library CVE), #4 (timing attack), #14 (RBAC route-only), #16 (deactivated user retains session)

**Research flag:** Standard patterns — FastAPI OAuth2 + JWT is extremely well-documented. No additional research phase needed.

---

### Phase 3: Core Feature Endpoints

**Rationale:** With auth working, all protected endpoints can now be built and tested end-to-end. Member management must come first within this phase because it is the only way to create accounts (admin-created account model). SMTP email is a dependency of member creation (welcome email) and interest form (confirmation email), so it must precede both.

**Delivers:**
- SMTP email service (`app/services/email_service.py`) — aiosmtplib, `SecretStr` password, generic error handling
- Member management (list, create with temp password + welcome email, role update + audit log, deactivate/reactivate)
- `GET /v1/users/me` — current user profile
- Interest form persistence (`POST /v1/interest`, `GET /v1/interest`) — DB save, duplicate handling (silent, no enumeration), confirmation email via background task
- Rush info management (`GET /v1/rush` public, `PUT /v1/rush` admin, `PATCH /v1/rush/visibility`) — replaces in-memory STATE dict
- Org content management (`GET /v1/content/{section}` public, `PUT /v1/content/{section}` admin, leadership endpoint querying users table)
- Audit log writes in member management service functions (same transaction as the change)

**Implements:** UserService, InterestService, EmailService (via BackgroundTasks), RBAC enforcement on all admin endpoints

**Avoids pitfalls:** #13 (SMTP credentials in logs), #17 (in-memory state lost on restart), #18 (weak temp password entropy), #19 (email enumeration via duplicate detection), #23 (audit log not atomic)

**Research flag:** Standard patterns. SMTP and SQLAlchemy CRUD are well-documented. No additional research phase needed.

---

### Phase 4: File Upload and Storage Integration

**Rationale:** Supabase Storage integration is the most complex external dependency and has the most pitfalls concentrated in one place. Isolating it to its own phase limits risk blast radius. The event PDF feature depends on auth (Phase 2) and the ORM model (Phase 1), so it cannot come earlier.

**Delivers:**
- StorageService (`app/storage/files.py`) — supabase-py wrapper, service role key, private bucket, relative path storage
- `POST /v1/admin/events` — PDF upload with magic byte validation, 10MB cap enforced in application code, UUID-based storage filename
- `GET /v1/events` — event listing from DB (auth-required)
- `DELETE /v1/admin/events/{id}` — delete from Supabase Storage and DB record atomically

**Implements:** StorageService, EventService, Supabase Storage bucket configuration

**Avoids pitfalls:** #9 (public bucket), #10 (service role key exposure), #11 (Content-Type spoofing, magic byte validation), #12 (no body size limit), #24 (full URL stored in DB)

**Research flag:** Supabase Storage Python API — verify `supabase-py` bucket upload/signed URL method signatures against supabase-py 2.x changelog when implementing. The interface is known but version-specific details need confirmation at implementation time.

---

### Phase 5: Hardening and Observability (Differentiators)

**Rationale:** These features improve security posture and operability but do not block launch. Build after the core feature surface is complete and tested.

**Delivers:**
- Self-service password change (`POST /v1/users/me/change-password`)
- Explicit logout (`POST /v1/auth/logout`) with refresh token revocation
- Structured JSON logging with request IDs (production mode)
- Pagination on member list and interest submission list endpoints
- CORS restriction to exact production domain; restrict `allow_methods` and `allow_headers`
- Rate limiting (nginx `limit_req_zone` recommended over application-level `slowapi`)
- Test suite for auth flow, member management, interest form, file upload

**Research flag:** Standard patterns. nginx rate limiting is well-documented. No research phase needed.

---

### Phase Ordering Rationale

- Phases 1-2 are load-bearing: no endpoint can be built or correctly tested without working schema and auth
- Phase 3 is gated by SMTP (member creation and interest form both need it) — SMTP must be the first service implemented in Phase 3
- Phase 4 is isolated because it has the highest concentration of pitfalls (5 critical pitfalls in one feature) and the only external service dependency (Supabase Storage API) with medium-confidence method signatures
- Phase 5 contains exclusively differentiators with no cross-dependencies — they can be built in any order

### Research Flags

Phases needing deeper research at planning time:
- **Phase 4 (Supabase Storage):** Verify `supabase-py 2.x` Storage API method signatures (`upload()`, `get_public_url()`, `create_signed_url()`, `remove()`) against the current changelog before writing StorageService. The interface is directionally known but exact parameter names and return types may have changed in v2.x.

Phases with standard patterns (skip research-phase):
- **Phase 1:** FastAPI + SQLAlchemy + Alembic patterns are extensively documented and stable
- **Phase 2:** FastAPI JWT auth with OAuth2PasswordBearer is the canonical FastAPI auth pattern
- **Phase 3:** SQLAlchemy CRUD, aiosmtplib, and FastAPI BackgroundTasks are well-documented
- **Phase 5:** nginx rate limiting, Python logging, and JWT revocation patterns are standard

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Installed packages verified from `uv.lock` with PyPI upload timestamps; NEEDED packages are ecosystem standards |
| Features | HIGH | Based on direct codebase inspection, `PROJECT.md` spec, and `CONCERNS.md` audit; all findings grounded in actual code |
| Architecture | HIGH | Sourced from official FastAPI docs + direct scaffold review; all patterns are from canonical documentation |
| Pitfalls | HIGH | Grounded in specific CVEs, codebase inspection (actual `"change-me"` default found), FastAPI session docs, OWASP |

**Overall confidence:** HIGH

### Gaps to Address

- **python-jose to PyJWT migration:** PITFALLS.md recommends replacing python-jose (CVEs) but STACK.md notes it is already installed and functional. The recommendation is clear (swap to PyJWT), but the exact migration path must be verified at implementation time — specifically whether any other installed package declares a transitive dependency on python-jose that would conflict.

- **Supabase Storage method signatures:** `supabase-py` 2.x Storage API is MEDIUM confidence. Verify `upload()` return type, `get_public_url()` vs `create_signed_url()` for private buckets, and `remove()` parameter format against the current SDK changelog before writing StorageService.

- **SMTP library choice:** STACK.md recommends `aiosmtplib` but FEATURES.md describes using `smtplib` (stdlib). The resolution is `aiosmtplib` (for async correctness), but both files must be reconciled when writing the email service. ARCHITECTURE.md's email pattern shows `smtplib` — this is a documentation inconsistency; use `aiosmtplib` in implementation.

- **Supabase bucket RLS configuration:** The correct RLS policy for a private bucket accessible only via service role is not fully specified in the research. Confirm bucket configuration in the Supabase dashboard before testing storage integration.

- **Refresh token storage schema:** Whether to use opaque hashed tokens or signed JWTs with a revocation table is documented in PITFALLS.md (recommends opaque hashed tokens). This is the right call but adds complexity. Validate the schema design before writing the Alembic migration.

---

## Sources

### Primary (HIGH confidence)
- `uv.lock` — all installed package versions with PyPI upload timestamps
- `pyproject.toml` — declared dependencies and tool configuration
- `.planning/PROJECT.md` — authoritative requirements specification
- `.planning/codebase/CONCERNS.md` — security and tech debt audit of current codebase
- `app/core/config.py`, `app/main.py`, `app/api/v1/**` — direct codebase inspection
- FastAPI official docs (JWT, dependencies, background tasks, error handling, SQL databases, bigger applications)
- SQLAlchemy 2.0 official session lifecycle documentation
- Alembic official documentation (`compare_type`, `alembic check`, merge heads)
- Pydantic v2 migration guide (`SettingsConfigDict`)

### Secondary (MEDIUM confidence)
- Supabase Storage Python API — `supabase-py` 2.x interface (training data; verify against changelog at implementation time)
- python-jose CVE history — known but exact CVE identifiers not verified in this session
- psycopg3 async vs. sync behavior — from training data; confirmed by FastAPI + psycopg3 community patterns

### Tertiary (LOW confidence)
- nginx rate limiting configuration for this specific deployment topology — standard nginx docs apply but deployment topology (Docker Compose specifics) not fully specified

---

*Research completed: 2026-03-03*
*Ready for roadmap: yes*
