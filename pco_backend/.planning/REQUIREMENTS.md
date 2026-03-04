# Requirements: PCO San Diego Backend API

**Defined:** 2026-03-03
**Core Value:** Members and admins can authenticate and access chapter resources through a secure, role-gated REST API.

## v1 Requirements

### Infrastructure

- [x] **INFRA-01**: Swap python-jose for PyJWT in pyproject.toml (python-jose has known CVEs including alg:none bypass)
- [x] **INFRA-02**: Add missing dependencies: alembic, supabase-py, aiosmtplib to pyproject.toml
- [ ] **INFRA-03**: All ORM models implemented: users, interest_submissions, events, rush_info, org_content, audit_log, refresh_tokens
- [ ] **INFRA-04**: Initial Alembic migration creates all tables from ORM models
- [ ] **INFRA-05**: Settings class hardened: jwt_secret is a required field with no default, all new env vars added (supabase_url, supabase_service_key, smtp_host, smtp_port, smtp_user, smtp_password, refresh_token_expire_days)
- [x] **INFRA-06**: Dockerfile uses uv.lock with --frozen flag for reproducible builds
- [x] **INFRA-07**: docker-compose.yml spins up API + local PostgreSQL with persistent volume

### Authentication & Authorization

- [x] **AUTH-01**: User can log in with email/password via POST /api/auth/login — returns JWT access token + refresh token (refresh token stored in DB)
- [x] **AUTH-02**: User can refresh access token via POST /api/auth/refresh — exchange valid DB-stored refresh token for new access token
- [x] **AUTH-03**: Authenticated user can view own profile via GET /api/users/me
- [x] **AUTH-04**: JWT dependency function (get_current_user) validates bearer token on all protected routes
- [x] **AUTH-05**: RBAC dependency (require_admin) enforces admin role on all /api/admin/* routes
- [x] **AUTH-06**: Deactivated users are rejected at login and token refresh
- [x] **AUTH-07**: Passwords are hashed with bcrypt via passlib before storage

### Member Management

- [x] **MEMB-01**: Admin can list all members via GET /api/admin/members with active/deactivated filter
- [x] **MEMB-02**: Admin can create member account via POST /api/admin/members (name, email, role), system generates temp password, sends welcome email via SMTP
- [x] **MEMB-03**: Admin can update member role via PATCH /api/admin/members/{id}/role — writes entry to audit_log
- [x] **MEMB-04**: Admin can deactivate member via PATCH /api/admin/members/{id}/deactivate — soft-delete (is_active=false), invalidates all refresh tokens for that user
- [x] **MEMB-05**: Admin can reactivate member via PATCH /api/admin/members/{id}/reactivate — restores login access

### Interest Form

- [x] **INTR-01**: Anyone can submit interest form via POST /api/interest (name, email, phone, year, major) — duplicate email returns 409, sends confirmation email via SMTP on success
- [x] **INTR-02**: Admin can list all interest submissions via GET /api/interest

### Events / PDFs

- [ ] **EVNT-01**: Authenticated user can list event PDFs via GET /api/events (title, date, url)
- [ ] **EVNT-02**: Admin can upload event PDF via POST /api/events to Supabase Storage — max 10MB, validates PDF magic bytes (%PDF), stores URL + metadata in DB
- [ ] **EVNT-03**: Admin can delete event PDF via DELETE /api/events/{id} — removes from Supabase Storage and DB

### Rush Week

- [x] **RUSH-01**: Anyone can view rush info via GET /api/rush — returns full details if published, or {"status": "coming_soon"} if hidden
- [x] **RUSH-02**: Admin can update rush info via PUT /api/rush (dates, times, locations, descriptions)
- [x] **RUSH-03**: Admin can toggle rush visibility via PATCH /api/rush/visibility

### Org Content

- [x] **CONT-01**: Anyone can view org history via GET /api/content/history
- [x] **CONT-02**: Anyone can view philanthropy info via GET /api/content/philanthropy
- [x] **CONT-03**: Anyone can view contact info via GET /api/content/contacts
- [x] **CONT-04**: Anyone can view leadership (T6) via GET /api/content/leadership — pulls users with officer role values from users table
- [x] **CONT-05**: Admin can update content sections via PUT /api/content/{section} (section: history | philanthropy | contacts)

### Cross-Cutting

- [ ] **XCUT-01**: All endpoints return consistent error response format: {"detail": "...", "status_code": N}
- [ ] **XCUT-02**: All endpoints are documented via FastAPI auto-generated OpenAPI/Swagger at /docs
- [ ] **XCUT-03**: CORS configured for localhost:3000 and production domain — no wildcard origins
- [x] **XCUT-04**: SMTP email (aiosmtplib) sends welcome and confirmation emails via FastAPI BackgroundTasks (non-blocking)
- [x] **XCUT-05**: Ruff configured in pyproject.toml for formatting (ruff format) and linting (ruff check) — replaces Black
- [ ] **XCUT-06**: README includes setup instructions, architecture overview, environment variable reference, and link to /docs

## v2 Requirements

### Auth Enhancements

- **AUTH-V2-01**: User can change own password
- **AUTH-V2-02**: Explicit logout endpoint that invalidates refresh token

### Observability

- **OBS-V2-01**: Structured JSON logging for all requests and errors
- **OBS-V2-02**: Rate limiting on public endpoints (interest form, login)

### Member Enhancements

- **MEMB-V2-01**: Pagination on GET /api/admin/members
- **MEMB-V2-02**: Admin can search/filter members by name or email

## Out of Scope

| Feature | Reason |
|---------|--------|
| Pledge process module | Removed from v1 scope |
| Public user registration | Admin-controlled membership only |
| OAuth / social login | Email/password sufficient for v1 |
| Frontend / UI / templates | Backend API only |
| Real-time features (WebSockets, SSE) | Not required for v1 |
| Mobile app | Web-first, mobile later |
| Async SQLAlchemy | Sync def + sync SQLAlchemy is simpler and safe for this traffic level |
| python-jose (JWT library) | Replaced by PyJWT due to known CVEs |

## Traceability

Phase mapping confirmed during roadmap creation (2026-03-03).

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 | Complete |
| INFRA-02 | Phase 1 | Complete |
| INFRA-03 | Phase 1 | Pending |
| INFRA-04 | Phase 1 | Pending |
| INFRA-05 | Phase 1 | Pending |
| INFRA-06 | Phase 1 | Complete |
| INFRA-07 | Phase 1 | Complete |
| AUTH-01 | Phase 2 | Complete |
| AUTH-02 | Phase 2 | Complete |
| AUTH-03 | Phase 2 | Complete |
| AUTH-04 | Phase 2 | Complete |
| AUTH-05 | Phase 2 | Complete |
| AUTH-06 | Phase 2 | Complete |
| AUTH-07 | Phase 2 | Complete |
| MEMB-01 | Phase 3 | Complete |
| MEMB-02 | Phase 3 | Complete |
| MEMB-03 | Phase 3 | Complete |
| MEMB-04 | Phase 3 | Complete |
| MEMB-05 | Phase 3 | Complete |
| INTR-01 | Phase 3 | Complete |
| INTR-02 | Phase 3 | Complete |
| EVNT-01 | Phase 4 | Pending |
| EVNT-02 | Phase 4 | Pending |
| EVNT-03 | Phase 4 | Pending |
| RUSH-01 | Phase 3 | Complete |
| RUSH-02 | Phase 3 | Complete |
| RUSH-03 | Phase 3 | Complete |
| CONT-01 | Phase 3 | Complete |
| CONT-02 | Phase 3 | Complete |
| CONT-03 | Phase 3 | Complete |
| CONT-04 | Phase 3 | Complete |
| CONT-05 | Phase 3 | Complete |
| XCUT-01 | Phase 1 | Pending |
| XCUT-02 | Phase 1 | Pending |
| XCUT-03 | Phase 1 | Pending |
| XCUT-04 | Phase 3 | Complete |
| XCUT-05 | Phase 1 | Complete |
| XCUT-06 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 38 total
- Mapped to phases: 38
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-03*
*Last updated: 2026-03-03 — traceability confirmed during roadmap creation*
