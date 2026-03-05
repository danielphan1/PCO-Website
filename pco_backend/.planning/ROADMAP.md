# Roadmap: PCO San Diego Backend API

## Overview

Starting from an empty scaffold (folder structure and FastAPI initialization only), the backend is built in a strict dependency-first order. Phase 1 establishes the database schema, security primitives, and config hardening that everything else depends on. Phase 2 implements authentication and authorization so that protected endpoints can be gated. Phase 3 delivers all core feature endpoints (member management, interest form, rush info, org content) over the working auth layer. Phase 4 adds the Supabase Storage integration for event PDFs and finalizes project documentation.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - Database schema, config hardening, security utilities, and infra prerequisites
- [x] **Phase 2: Authentication** - JWT login, token refresh, user profile, and RBAC enforcement (completed 2026-03-04, verified 2026-03-04)
- [x] **Phase 3: Core Features** - Member management, interest form, rush info, org content, and SMTP email (completed 2026-03-04)
- [x] **Phase 4: Storage and Finish** - Event PDF upload/listing/deletion via Supabase Storage and README (completed 2026-03-05)

## Phase Details

### Phase 1: Foundation
**Goal**: The database schema is complete, all security primitives are correct, and the project can run reproducibly in Docker with a hardened configuration
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04, INFRA-05, INFRA-06, INFRA-07, XCUT-01, XCUT-02, XCUT-03, XCUT-05
**Success Criteria** (what must be TRUE):
  1. `docker compose up` starts the API and PostgreSQL with no errors; `GET /health` returns 200
  2. All six ORM models (User, InterestSubmission, EventPDF, RushInfo, OrgContent, AuditLog) plus refresh_tokens exist as tables in the database after running the Alembic migration
  3. Starting the API without a `JWT_SECRET` environment variable (or with one shorter than 32 characters) causes the process to exit with a clear error before serving any requests
  4. `ruff check` and `ruff format --check` pass with zero violations on the codebase
  5. All endpoint errors return `{"detail": "...", "status_code": N}` consistent response format (global exception handlers registered)
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Dep swap (PyJWT), Ruff/pytest config, Docker fixes, Wave 0 test scaffold
- [ ] 01-02-PLAN.md — Settings hardening (Pydantic v2), 7 ORM models, Alembic migration, session/deps
- [ ] 01-03-PLAN.md — Global exception handlers, OpenAPI config, security stub, Phase 1 checkpoint

### Phase 2: Authentication
**Goal**: Users can log in with email/password and receive JWT tokens; all protected routes enforce authentication and role-based access
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06, AUTH-07
**Success Criteria** (what must be TRUE):
  1. An active member can POST to `/v1/auth/login` with valid email/password and receive an access token and a refresh token stored in the database
  2. A valid refresh token can be exchanged via POST `/v1/auth/refresh` for a new access token; an invalid or expired refresh token is rejected with 401
  3. An authenticated member can GET `/v1/users/me` and receive their own profile; an unauthenticated request is rejected with 401
  4. Any request to an `/v1/admin/*` route without admin role is rejected with 403
  5. A deactivated user's login attempt and refresh token exchange are both rejected with 401
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md — passlib removal, security.py utilities, auth schemas, login + refresh endpoints, test scaffold
- [x] 02-02-PLAN.md — get_current_user + require_admin deps, users/me endpoint, router wiring, full 16-test suite

### Phase 3: Core Features
**Goal**: Admins can manage members and content; the public can submit interest forms and view org info; rush details can be published and hidden
**Depends on**: Phase 2
**Requirements**: MEMB-01, MEMB-02, MEMB-03, MEMB-04, MEMB-05, INTR-01, INTR-02, RUSH-01, RUSH-02, RUSH-03, CONT-01, CONT-02, CONT-03, CONT-04, CONT-05, XCUT-04
**Success Criteria** (what must be TRUE):
  1. An admin can create a member account (POST `/v1/admin/members`); the new user receives a welcome email and can immediately log in with the generated temporary password
  2. An admin can deactivate a member (PATCH `/v1/admin/members/{id}/deactivate`) and the deactivated user's existing tokens are immediately invalidated
  3. Anyone can submit the interest form (POST `/v1/interest`); submitting the same email a second time returns 409; a successful submission sends a confirmation email without blocking the response
  4. Rush info is visible publicly when published and returns `{"status": "coming_soon"}` when hidden; admins can update and toggle visibility
  5. All four public org content endpoints (`/v1/content/history`, `/v1/content/philanthropy`, `/v1/content/contacts`, `/v1/content/leadership`) return data; leadership returns users with officer role values from the users table
**Plans**: 3 plans

Plans:
- [ ] 03-01-PLAN.md — SMTP email service, config (FRONTEND_URL), member management endpoints (MEMB-01 to MEMB-05, XCUT-04)
- [ ] 03-02-PLAN.md — Interest form endpoints (INTR-01, INTR-02), rush info endpoints (RUSH-01, RUSH-02, RUSH-03)
- [ ] 03-03-PLAN.md — Org content endpoints: history, philanthropy, contacts, leadership, admin update (CONT-01 to CONT-05)

### Phase 4: Storage and Finish
**Goal**: Authenticated users can list event PDFs; admins can upload and delete PDFs via Supabase Storage; the project is documented
**Depends on**: Phase 3
**Requirements**: EVNT-01, EVNT-02, EVNT-03, XCUT-06
**Success Criteria** (what must be TRUE):
  1. An authenticated member can GET `/v1/events` and receive a list of event PDFs with titles, dates, and access URLs
  2. An admin can upload a PDF via POST `/v1/admin/events`; a non-PDF file or a file over 10MB is rejected with a clear error; the file is stored in the private Supabase Storage bucket with a UUID-based filename
  3. An admin can delete an event PDF via DELETE `/v1/admin/events/{id}`; the file is removed from Supabase Storage and the DB record is deleted
  4. The README contains setup instructions, environment variable reference, architecture overview, and a link to `/docs`
**Plans**: 3 plans

Plans:
- [ ] 04-01-PLAN.md — StorageService singleton, event schemas, service layer (list/upload/delete), full 11-test suite
- [ ] 04-02-PLAN.md — Router wiring: GET /v1/events and POST+DELETE /v1/admin/events (depends on 04-01)
- [ ] 04-03-PLAN.md — README.md and .env.example (Wave 1 parallel with 04-01)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 1/3 | In Progress|  |
| 2. Authentication | 2/2 | Complete   | 2026-03-04 |
| 3. Core Features | 3/3 | Complete   | 2026-03-04 |
| 4. Storage and Finish | 3/3 | Complete   | 2026-03-05 |
