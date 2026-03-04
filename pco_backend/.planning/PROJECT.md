# PCO San Diego Backend API

## What This Is

A REST API backend for the Psi Chi Omega (PCO) San Diego chapter website. Built with FastAPI + PostgreSQL (Supabase) and deployed via Docker. Serves a future frontend at localhost:3000 (dev) and a production domain. No UI, no templates — pure API.

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

### Active

**Auth**
- [ ] POST /api/auth/login — email/password → JWT access + refresh tokens
- [ ] POST /api/auth/refresh — exchange refresh token for new access token
- [ ] GET /api/users/me — current user profile (auth required)
- [ ] JWT middleware with RBAC (member / admin roles)
- [ ] bcrypt password hashing via passlib

**Member Management (admin only)**
- [ ] GET /api/admin/members — list members, filter active/deactivated
- [ ] POST /api/admin/members — create member, generate temp password, send welcome email via SMTP
- [ ] PATCH /api/admin/members/{id}/role — update role, write audit log entry
- [ ] PATCH /api/admin/members/{id}/deactivate — soft-delete (block login, preserve data)
- [ ] PATCH /api/admin/members/{id}/reactivate — restore access

**Interest Form**
- [ ] POST /api/interest — submit interest form (public), duplicate email detection, send confirmation email via SMTP
- [ ] GET /api/interest — list all submissions (admin only)

**Events / PDFs**
- [ ] GET /api/events — list event PDFs with titles and dates (auth required)
- [ ] POST /api/events — upload PDF to Supabase Storage, 10MB limit, PDF-only (admin only)
- [ ] DELETE /api/events/{id} — remove PDF from Supabase Storage (admin only)

**Rush Week**
- [ ] GET /api/rush — return rush details if published, or "coming soon" status (public)
- [ ] PUT /api/rush — update dates, times, locations, descriptions (admin only)
- [ ] PATCH /api/rush/visibility — toggle published/hidden (admin only)

**Org Content**
- [ ] GET /api/content/history — org history (public)
- [ ] GET /api/content/philanthropy — philanthropy info (public)
- [ ] GET /api/content/contacts — rush chair contact info (public)
- [ ] GET /api/content/leadership — T6 officers pulled from users table by role field (public)
- [ ] PUT /api/content/{section} — update history/philanthropy/contacts content (admin only)

**Infrastructure**
- [ ] All database models implemented (users, interest_submissions, events, rush_info, org_content, audit_log)
- [ ] Alembic migration for initial schema
- [ ] SMTP email service (generic — configurable provider)
- [ ] Supabase Storage client for PDF uploads
- [ ] Consistent error response format across all endpoints
- [ ] Black + Ruff code style enforcement
- [ ] README with setup instructions and API docs link

### Out of Scope

- Pledge process module — removed from v1
- Public user registration — admin-created accounts only
- Mobile app / frontend — backend API only
- Real-time features (websockets, SSE)
- OAuth / social login — email/password only for v1

## Context

Existing scaffold is stubs-only: folder structure, docker config, and FastAPI app initialization are in place, but all endpoints, services, models, and middleware are unimplemented. The scaffold uses `/v1/` API versioning prefix (routes mount at `/v1/`).

T6 officers are identified by specific role values on the `users` table (e.g., president, vp, treasurer, etc.) — the `/api/content/leadership` endpoint queries users by these roles.

Admin-only content (org history, philanthropy, contacts, pledge info) is editable via PUT endpoints — not seeded-only.

## Constraints

- **Tech Stack**: FastAPI + SQLAlchemy + psycopg3 + Pydantic v2 — already in pyproject.toml
- **Auth**: JWT with short-lived access tokens + refresh tokens; bcrypt via passlib (already installed)
- **Storage**: Supabase Storage for event PDFs (supabase-py client to be added)
- **Email**: Generic SMTP (configurable via env vars — host, port, user, password)
- **Database**: PostgreSQL 16 via Supabase in production; local Docker PostgreSQL for dev
- **Package Manager**: uv (not pip)
- **CORS**: localhost:3000 (dev) + production domain

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| No public registration | Admin-controlled membership roster | — Pending |
| SMTP (generic) for email | Flexible provider, no vendor lock-in | — Pending |
| Supabase Storage for PDFs | Leverages existing Supabase infra | — Pending |
| Roles: member / admin only | Pledge removed from v1 scope | — Pending |
| T6 identified by role field on users | No separate leadership table needed | — Pending |
| Short-lived JWT + refresh tokens | Better security than long-lived tokens | — Pending |

---
*Last updated: 2026-03-03 after initialization*
