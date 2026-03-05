# Codebase Structure

**Analysis Date:** 2026-03-05

## Repository Layout

This is a monorepo containing two independent projects under `/Users/briannguyen/Workspace/PCO-Website/`:

```
PCO-Website/
├── pco_backend/        # FastAPI REST API (Python)
└── pco_website/        # Next.js 15 frontend (TypeScript) ← you are here
```

## Backend Directory Layout (`pco_backend/`)

```
pco_backend/
├── app/
│   ├── main.py                     # FastAPI app factory, middleware, exception handlers
│   ├── api/
│   │   ├── router.py               # Aggregates all v1 routers
│   │   └── v1/
│   │       ├── auth.py             # POST /v1/auth/login, POST /v1/auth/refresh
│   │       ├── content.py          # GET/PUT /v1/content/{section}, GET /v1/content/leadership
│   │       ├── events.py           # GET /v1/events/
│   │       ├── interest.py         # POST/GET /v1/interest/
│   │       ├── public.py           # GET /v1/public/info
│   │       ├── rush.py             # GET/PUT /v1/rush/, PATCH /v1/rush/visibility
│   │       ├── users.py            # GET /v1/users/me
│   │       └── admin/
│   │           ├── events.py       # POST/DELETE /v1/admin/events/
│   │           ├── settings.py     # Placeholder — empty router
│   │           └── users.py        # GET/POST/PATCH /v1/admin/users/
│   ├── core/
│   │   ├── config.py               # pydantic-settings Settings class (reads .env)
│   │   ├── deps.py                 # get_db, get_current_user, require_admin
│   │   ├── logging.py              # Empty stub
│   │   └── security.py             # JWT encode/decode, bcrypt password ops, refresh token ops
│   ├── db/
│   │   ├── base.py                 # Imports all ORM models — registers them for Alembic
│   │   ├── base_class.py           # DeclarativeBase (Base)
│   │   ├── init_db.py              # Empty stub
│   │   └── session.py              # SQLAlchemy engine + SessionLocal factory
│   ├── models/
│   │   ├── audit_log.py            # AuditLog — admin action history
│   │   ├── event_pdf.py            # EventPDF — event PDF metadata
│   │   ├── interest_form.py        # InterestSubmission — rush interest forms
│   │   ├── org_content.py          # OrgContent — editable org sections
│   │   ├── refresh_token.py        # RefreshToken — rotatable tokens (hashed)
│   │   ├── role.py                 # (role model file — inspect if adding role logic)
│   │   ├── rush_info.py            # RushInfo — rush week details + publish flag
│   │   └── user.py                 # User — members, ALL_ROLES, OFFICER_ROLES constants
│   ├── schemas/
│   │   ├── auth.py                 # LoginRequest, RefreshRequest, TokenResponse
│   │   ├── content.py              # ContentResponse, ContentUpdate, LeadershipEntry
│   │   ├── event.py                # EventResponse
│   │   ├── interest_form.py        # InterestFormCreate, InterestFormResponse
│   │   ├── rush.py                 # RushInfoResponse, RushInfoUpdate
│   │   └── user.py                 # UserResponse, MemberCreate, MemberRoleUpdate
│   ├── services/
│   │   ├── auth_service.py         # Empty stub (auth logic lives in router directly)
│   │   ├── email_service.py        # send_welcome_email, send_interest_confirmation (async SMTP)
│   │   ├── event_service.py        # list_events, upload_event, delete_event
│   │   ├── interest_service.py     # submit_interest, list_submissions
│   │   ├── rush_service.py         # get_rush, upsert_rush, toggle_visibility
│   │   └── user_service.py         # list_members, create_member, update_member_role, deactivate_member, reactivate_member
│   ├── storage/
│   │   ├── files.py                # StorageService (Supabase Storage wrapper), storage_service singleton
│   │   └── paths.py                # event_pdf_path() — canonical path generators
│   ├── tests/
│   │   ├── conftest.py             # Pytest fixtures, test client, DB setup
│   │   ├── test_auth.py
│   │   ├── test_content.py
│   │   ├── test_email.py
│   │   ├── test_events.py
│   │   ├── test_foundation.py
│   │   ├── test_interest.py
│   │   ├── test_members.py
│   │   └── test_rush.py
│   └── utils/
│       ├── time.py                 # Time utilities
│       └── validators.py           # Empty stub
├── alembic/
│   ├── env.py                      # Alembic env config (reads app models)
│   ├── script.py.mako              # Migration template
│   └── versions/
│       └── 001_initial_schema.py   # First migration — all tables
├── docker/
│   ├── docker-compose.yml          # Local dev compose (Postgres + app)
│   ├── Dockerfile                  # App container definition
│   └── dev.sh                      # Dev startup script
├── scripts/                        # Utility scripts
├── pyproject.toml                  # Python package config, dependencies, tool config
├── alembic.ini                     # Alembic config
└── uv.lock                         # uv lockfile
```

## Frontend Directory Layout (`pco_website/`)

```
pco_website/
├── app/
│   ├── layout.tsx                  # Root HTML layout, font setup
│   ├── page.tsx                    # Home page (placeholder/scaffold)
│   ├── globals.css                 # Global Tailwind CSS imports
│   └── favicon.ico
├── public/                         # Static assets (SVGs, images)
├── .planning/                      # GSD planning documents
│   └── codebase/                   # Codebase analysis docs (this directory)
├── next.config.ts                  # Next.js config
├── tsconfig.json                   # TypeScript config
├── eslint.config.mjs               # ESLint config
├── postcss.config.mjs              # PostCSS / Tailwind config
├── package.json                    # Frontend dependencies
├── pnpm-lock.yaml                  # pnpm lockfile
└── pnpm-workspace.yaml             # Workspace config
```

## Directory Purposes

**`pco_backend/app/api/v1/`:**
- Purpose: All versioned HTTP route handlers
- Contains: One file per resource domain; `admin/` subdirectory for admin-only endpoints

**`pco_backend/app/core/`:**
- Purpose: Cross-cutting infrastructure — config, auth, security primitives
- Key files: `deps.py` (inject into routes), `security.py` (JWT/bcrypt), `config.py` (settings)

**`pco_backend/app/models/`:**
- Purpose: SQLAlchemy ORM model definitions (one file per DB table)
- Key files: `user.py` (contains role constants), `base.py` in `db/` registers all models

**`pco_backend/app/schemas/`:**
- Purpose: Pydantic schemas for API request bodies and response serialization
- Pattern: Mirror structure of models — one file per domain

**`pco_backend/app/services/`:**
- Purpose: Business logic layer between routers and models
- Pattern: Functions accept `db: Session` as first arg; raise `HTTPException` on failures

**`pco_backend/app/storage/`:**
- Purpose: Abstracts Supabase Storage SDK; exposes `storage_service` singleton
- Key files: `files.py` (operations), `paths.py` (path string generators)

**`pco_backend/app/tests/`:**
- Purpose: All pytest tests, co-located in single directory (not mirroring source tree)
- Key files: `conftest.py` for shared fixtures

**`pco_backend/alembic/versions/`:**
- Purpose: Database migration scripts
- Generated: Yes (via `alembic revision`)
- Committed: Yes

## Key File Locations

**Entry Points:**
- `pco_backend/app/main.py`: FastAPI app; ASGI entry point
- `pco_website/app/layout.tsx`: Next.js App Router root layout
- `pco_website/app/page.tsx`: Home page route

**Configuration:**
- `pco_backend/app/core/config.py`: All backend config via pydantic-settings
- `pco_website/next.config.ts`: Next.js build config
- `pco_website/tsconfig.json`: TypeScript compiler config
- `pco_backend/alembic.ini`: Alembic migration config

**Auth/Security:**
- `pco_backend/app/core/security.py`: JWT encode/decode, bcrypt, refresh token ops
- `pco_backend/app/core/deps.py`: `get_current_user`, `require_admin`, `get_db`

**Database:**
- `pco_backend/app/db/session.py`: Engine and `SessionLocal`
- `pco_backend/app/db/base.py`: Model registry (must import all models here)
- `pco_backend/alembic/versions/001_initial_schema.py`: Schema migration

**Storage:**
- `pco_backend/app/storage/files.py`: `storage_service` singleton (Supabase Storage)
- `pco_backend/app/storage/paths.py`: Path generators (`event_pdf_path`)

**Role Definitions:**
- `pco_backend/app/models/user.py`: `ALL_ROLES`, `OFFICER_ROLES` constants

## Naming Conventions

**Backend Files:**
- Router files: `snake_case.py` matching the resource noun (e.g., `users.py`, `events.py`)
- Service files: `{noun}_service.py` (e.g., `user_service.py`, `email_service.py`)
- Model files: `{noun}.py` matching the resource (e.g., `user.py`, `audit_log.py`)
- Schema files: `{noun}.py` matching the resource (e.g., `user.py`, `auth.py`)

**Backend Classes:**
- ORM models: PascalCase noun (e.g., `User`, `EventPDF`, `AuditLog`, `RefreshToken`)
- Pydantic schemas: PascalCase with suffix `Request`, `Response`, `Create`, `Update` (e.g., `UserResponse`, `MemberCreate`, `LoginRequest`)

**Backend Functions:**
- Service functions: `snake_case` verb+noun (e.g., `list_members`, `create_member`, `upload_event`, `delete_event`)
- Dependency functions: `get_{noun}` or `require_{role}` (e.g., `get_current_user`, `require_admin`)

**Frontend Files:**
- Next.js pages: `page.tsx` (App Router convention)
- Next.js layouts: `layout.tsx` (App Router convention)
- Components: PascalCase (convention — no components exist yet)

## Where to Add New Code

**New API endpoint (authenticated):**
1. Create or update router file in `pco_backend/app/api/v1/{resource}.py`
2. Add business logic in `pco_backend/app/services/{resource}_service.py`
3. Add request/response schemas in `pco_backend/app/schemas/{resource}.py`
4. Register router in `pco_backend/app/api/router.py`
5. Add tests in `pco_backend/app/tests/test_{resource}.py`

**New admin-only endpoint:**
1. Create or update router file in `pco_backend/app/api/v1/admin/{resource}.py`
2. Use `require_admin` dependency (from `app.core.deps`)
3. Register in `pco_backend/app/api/router.py` with `/v1/admin/{resource}` prefix

**New database table:**
1. Create ORM model in `pco_backend/app/models/{noun}.py` extending `Base`
2. Import model in `pco_backend/app/db/base.py` (required for Alembic to detect it)
3. Run `alembic revision --autogenerate -m "description"` to generate migration
4. Apply with `alembic upgrade head`

**New Pydantic schema:**
- Add to `pco_backend/app/schemas/{domain}.py` matching the router it serves

**New frontend page:**
- Create `pco_website/app/{route}/page.tsx` following Next.js App Router conventions
- Shared layouts: `pco_website/app/{route}/layout.tsx`
- Components: `pco_website/components/{ComponentName}.tsx` (directory does not exist yet — create it)

**New utility:**
- Backend shared helpers: `pco_backend/app/utils/{category}.py`
- Storage path functions: `pco_backend/app/storage/paths.py`

## Special Directories

**`pco_backend/alembic/versions/`:**
- Purpose: Sequentially numbered DB migration scripts
- Generated: Yes (`alembic revision`)
- Committed: Yes

**`pco_website/.planning/`:**
- Purpose: GSD planning documents (phases, codebase analysis)
- Generated: Yes (by Claude GSD agents)
- Committed: Yes

**`pco_backend/docker/`:**
- Purpose: Local development Docker setup (Postgres container + app container)
- Contains: `Dockerfile`, `docker-compose.yml`, `dev.sh`

---

*Structure analysis: 2026-03-05*
