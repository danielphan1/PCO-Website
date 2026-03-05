# PCO San Diego Backend API

## What This Is

A REST API backend for the Psi Chi Omega (PCO) San Diego chapter website. Built with FastAPI + PostgreSQL (Supabase) and deployed via Docker. Serves a future frontend at localhost:3000 (dev) and a production domain. No UI, no templates — pure API. v1.0 shipped 2026-03-05 with full authentication, member management, interest forms, rush info, org content, and Supabase Storage event PDF management.

## Core Value

Members and admins can authenticate and access chapter resources (events, rush info, org content) through a secure, role-gated API.

## Requirements

### Validated

- ✓ Layered project scaffold (routers → services → models → schemas) — existing
- ✓ Docker + docker-compose setup (API + PostgreSQL) — existing
- ✓ FastAPI app initialization with CORS middleware — existing
- ✓ Environment-based configuration via Pydantic Settings — existing
- ✓ SQLAlchemy ORM + Alembic migrations infrastructure — existing
- ✓ uv package manager with pyproject.toml — existing
- ✓ Health check endpoint (GET /health) — existing
- ✓ PyJWT replacing python-jose (CVE elimination) — v1.0
- ✓ All ORM models: User, RefreshToken, InterestSubmission, EventPDF, RushInfo, OrgContent, AuditLog — v1.0
- ✓ Alembic migration for initial schema — v1.0
- ✓ Pydantic v2 Settings with jwt_secret enforcement (min 32 chars, no default) — v1.0
- ✓ Dockerfile with uv.lock --frozen flag for reproducible builds — v1.0
- ✓ docker-compose.yml with API + PostgreSQL + persistent volume — v1.0
- ✓ POST /v1/auth/login — email/password → JWT access + refresh tokens — v1.0
- ✓ POST /v1/auth/refresh — token rotation with replay prevention — v1.0
- ✓ GET /v1/users/me — current user profile (auth required) — v1.0
- ✓ get_current_user JWT validation dep on all protected routes — v1.0
- ✓ require_admin RBAC dep on all /v1/admin/* routes — v1.0
- ✓ Deactivated users rejected at login and refresh — v1.0
- ✓ bcrypt password hashing (direct, passlib removed) — v1.0
- ✓ GET /v1/admin/users — list members, filter active/deactivated — v1.0
- ✓ POST /v1/admin/users — create member, generate temp password, send welcome email — v1.0
- ✓ PATCH /v1/admin/users/{id}/role — update role, write audit log entry — v1.0
- ✓ PATCH /v1/admin/users/{id}/deactivate — soft-delete, invalidate all refresh tokens — v1.0
- ✓ PATCH /v1/admin/users/{id}/reactivate — restore access — v1.0
- ✓ POST /v1/interest — submit interest form (public), duplicate email 409, confirmation email — v1.0
- ✓ GET /v1/interest — list all submissions (admin only) — v1.0
- ✓ GET /v1/events — list event PDFs with titles and dates (auth required) — v1.0
- ✓ POST /v1/admin/events — upload PDF to Supabase Storage, 10MB limit, PDF-only — v1.0
- ✓ DELETE /v1/admin/events/{id} — remove PDF from Supabase Storage — v1.0
- ✓ GET /v1/rush — rush details if published, "coming soon" if hidden (public) — v1.0
- ✓ PUT /v1/rush — update rush info (admin only) — v1.0
- ✓ PATCH /v1/rush/visibility — toggle published/hidden (admin only) — v1.0
- ✓ GET /v1/content/history — org history (public) — v1.0
- ✓ GET /v1/content/philanthropy — philanthropy info (public) — v1.0
- ✓ GET /v1/content/contacts — contact info (public) — v1.0
- ✓ GET /v1/content/leadership — T6 officers from users table by role field (public) — v1.0
- ✓ PUT /v1/content/{section} — update content sections (admin only) — v1.0
- ✓ SMTP email via BackgroundTasks (non-blocking, log-and-swallow on failure) — v1.0
- ✓ Consistent error response format via global exception handlers — v1.0
- ✓ ruff lint + format enforcement — v1.0
- ✓ README with setup, env vars, architecture, API reference — v1.0

### Active

*(None — v1.0 complete. Define v1.1 requirements via `/gsd:new-milestone`.)*

### Out of Scope

- Pledge process module — removed from v1
- Public user registration — admin-created accounts only
- Mobile app / frontend — backend API only
- Real-time features (websockets, SSE)
- OAuth / social login — email/password only for v1
- Async SQLAlchemy — sync def + thread pool is safe at this traffic level
- python-jose — replaced by PyJWT due to known CVEs

## Context

**Shipped v1.0 with 3,029 LOC Python across 64 files.**

Tech stack: FastAPI 0.115, SQLAlchemy 2.0 (sync), Pydantic v2, PostgreSQL 16, PyJWT, bcrypt (direct), aiosmtplib, supabase-py 2.x, pytest 9, ruff, uv, Docker.

All 38 v1 requirements satisfied. 68 automated tests (pytest), all passing. Full audit: 4/4 phases verified, 38/38 integration wired, 5/5 E2E flows complete.

**Known tech debt (non-blocking):**
- `app/services/auth_service.py` — empty stub, never imported (auth lives in api/v1/auth.py)
- `app/api/v1/admin/settings.py` — empty placeholder router registered at /v1/admin/settings (returns 404)
- `app/models/role.py` — empty stub, never imported (role constants in user.py)
- `app/api/v1/public.py` — GET /v1/public/info returns TODO-filled static dict
- SUPABASE_URL/SUPABASE_SERVICE_KEY have no startup validation (StorageService throws RuntimeError on first use if empty)
- alembic.ini not COPY'd into Docker image (volume mount required for standalone container)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| No public registration | Admin-controlled membership roster | ✓ Good — roster quality maintained |
| SMTP (generic) for email | Flexible provider, no vendor lock-in | ✓ Good — aiosmtplib + BackgroundTasks worked well |
| Supabase Storage for PDFs | Leverages existing Supabase infra | ✓ Good — lazy client init solved test isolation |
| Roles: member / admin only | Pledge removed from v1 scope | ✓ Good — simpler RBAC |
| T6 identified by role field on users | No separate leadership table needed | ✓ Good — clean query |
| Short-lived JWT + refresh tokens | Better security than long-lived tokens | ✓ Good — rotation prevents replay |
| PyJWT over python-jose | python-jose has alg:none CVE | ✓ Good — no transitive conflict found |
| bcrypt direct over passlib | passlib 1.7.4 + bcrypt 5.0.0 broken upstream | ✓ Good — simpler dep, same security |
| SHA-256 for refresh token hash | 256-bit token entropy makes brute-force infeasible | ✓ Good — faster than bcrypt, equally secure for tokens |
| Sync SQLAlchemy | Simpler, safe in FastAPI thread pool for this traffic | ✓ Good — no async complexity |
| Lazy Supabase client init | Avoids import-time failure with empty env vars in tests | ✓ Good — clean test isolation |
| BackgroundTasks for SMTP | HTTP response not blocked by email delivery | ✓ Good — log-and-swallow on failure works |

## Constraints

- **Tech Stack**: FastAPI + SQLAlchemy + psycopg3 + Pydantic v2
- **Auth**: JWT with short-lived access tokens + refresh tokens; bcrypt direct
- **Storage**: Supabase Storage for event PDFs (supabase-py 2.x)
- **Email**: Generic SMTP (aiosmtplib, configured via env vars)
- **Database**: PostgreSQL 16 via Supabase in production; local Docker PostgreSQL for dev
- **Package Manager**: uv (not pip)
- **CORS**: localhost:3000 (dev) + production domain

---
*Last updated: 2026-03-05 after v1.0 milestone*
