# Phase 1: Foundation - Context

**Gathered:** 2026-03-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the database schema, config hardening, security utilities, and infrastructure prerequisites that all subsequent phases depend on. This includes: ORM models + Alembic migration, PyJWT swap, hardened Settings, Docker reproducibility, global error handlers, CORS, OpenAPI config, and Ruff linting. No endpoints beyond /health; no auth logic.

</domain>

<decisions>
## Implementation Decisions

### Dependency changes
- Swap `python-jose` for `PyJWT` (CVE risk — alg:none bypass); remove python-jose entirely after confirming no transitive dependency conflict
- Add `alembic`, `supabase-py`, `aiosmtplib` to pyproject.toml dependencies
- Dockerfile must use `uv sync --frozen` (not `uv sync`) for reproducible builds
- Ruff replaces Black — configure both `ruff format` and `ruff check`; Ruff lint rules: enable E, W, F, I (pycodestyle errors/warnings, pyflakes, isort) as baseline; no overly strict rules that would require type annotations

### Settings hardening
- `jwt_secret` field has **no default value** — Settings instantiation must fail if missing
- Add validation: `jwt_secret` minimum 32 characters; raise ValueError at startup with a clear message (not at first request)
- Add new env vars to Settings: `supabase_url`, `supabase_service_key`, `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`, `refresh_token_expire_days` (default 30)
- Validation happens via Pydantic `@field_validator` on the Settings class itself

### ORM models
Seven tables: `users`, `refresh_tokens`, `interest_submissions`, `events`, `rush_info`, `org_content`, `audit_log`

**users table:**
- `id` (UUID, PK), `email` (unique), `hashed_password`, `full_name`, `role` (string), `is_active` (bool, default True), `created_at`, `updated_at`
- Role string values: `member`, `admin`, `president`, `vp`, `treasurer`, `secretary`, `sergeant_at_arms`, `historian` — T6 officer roles are specific strings; leadership endpoint queries users WHERE role IN (officer list)

**refresh_tokens table:**
- `id` (UUID, PK), `user_id` (FK → users), `token_hash` (string, unique), `expires_at` (timestamp), `revoked` (bool, default False), `created_at`
- Store token hash, not plaintext; revoked flag allows explicit invalidation without waiting for expiry

**interest_submissions table:**
- `id` (UUID, PK), `name`, `email` (unique), `phone`, `year`, `major`, `created_at`

**events table (event PDFs):**
- `id` (UUID, PK), `title`, `date` (date), `storage_path` (string — relative path in Supabase Storage, NOT full URL), `created_at`, `uploaded_by` (UUID FK → users)

**rush_info table:**
- `id` (UUID, PK), `dates`, `times`, `locations`, `description` (all text), `is_published` (bool, default False), `updated_at`
- Single row (upsert pattern); initialize with one empty unpublished row via Alembic data migration

**org_content table:**
- `id` (UUID, PK), `section` (string — enum key: `history` | `philanthropy` | `contacts`), `content` (text), `updated_at`
- One row per section; section column is a unique key; seed initial empty rows in Alembic data migration

**audit_log table:**
- `id` (UUID, PK), `actor_id` (UUID FK → users), `action` (string), `target_id` (UUID, nullable), `target_type` (string, nullable), `metadata` (JSON, nullable), `created_at`
- Scope: log admin writes only — role changes, deactivations, reactivations (per MEMB-03); content updates and member creation are out of scope for audit log in this phase

### Alembic migration
- `alembic/env.py` must import `Base` from `app.db.base` and point to `Base.metadata`
- `app/db/base.py` imports all models so Alembic sees them for autogenerate
- Single migration `001_initial_schema.py` — creates all 7 tables
- Seed data: one unpublished `rush_info` row + three `org_content` rows (history, philanthropy, contacts) with empty content strings

### DB session
- Synchronous SQLAlchemy (`create_engine`, `Session`, not AsyncSession) — sync def endpoints run in FastAPI thread pool
- Session factory in `app/db/session.py`; `get_db()` generator dependency in `app/core/deps.py`

### Global error handlers
- Register exception handlers on `app` for `RequestValidationError` (422) and `HTTPException`
- Both return `{"detail": "...", "status_code": N}` format — normalize Pydantic 422 errors to this format (extract field errors into detail string or list)
- Internal 500 errors return generic message (don't leak tracebacks in production)

### CORS
- `CORS_ORIGINS` env var drives the allow_origins list (already in config)
- No wildcard origins — existing config reads from Settings correctly

### OpenAPI / Swagger
- FastAPI auto-generates `/docs` (Swagger) and `/redoc` — keep defaults
- Set `title`, `version`, `description` on FastAPI app from settings

### Docker
- `docker-compose.yml` already exists with API + PostgreSQL; add db healthcheck (`pg_isready`) and make API `depends_on: db: condition: service_healthy` so API waits for DB
- Dockerfile: replace `uv sync --no-dev` with `uv sync --frozen --no-dev`

### Claude's Discretion
- Exact Ruff rule IDs to enable beyond the E/W/F/I baseline (e.g., whether to add UP for pyupgrade, B for bugbear)
- How to surface field-level 422 validation errors in the normalized format (flat list vs. single joined string)
- Whether to add `__repr__` or `__str__` to ORM models
- Alembic migration file naming and version ID format

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/core/config.py` — Settings class exists; needs hardening (remove jwt_secret default, add new fields, add validator). Extend in place.
- `app/main.py` — FastAPI app init, CORS middleware, health endpoint already registered. Register global exception handlers here.
- `app/api/router.py` — Router with v1 prefix already wires all sub-routers. No changes needed in Phase 1.
- `docker/docker-compose.yml` — Exists with db + api services. Add healthcheck + depends_on condition.
- `docker/Dockerfile` — Exists; fix `uv sync` → `uv sync --frozen`.

### Established Patterns
- Synchronous SQLAlchemy only (project constraint — no async)
- All routes under `/v1/` prefix (router already configured this way)
- `uv` package manager — all installs via `uv add`, not pip
- Pydantic v2 — use `model_config`, `@field_validator` (not v1 validators)

### Integration Points
- `app/db/base.py` — Import all models here so Alembic can autogenerate migrations
- `alembic/env.py` — Must import `Base.metadata` from `app.db.base`
- `app/core/deps.py` — Add `get_db()` dependency here; Phase 2 adds `get_current_user` and `require_admin` here
- `app/core/security.py` — Empty stub; Phase 2 fills this with JWT sign/verify helpers. Phase 1 just ensures PyJWT is available.

</code_context>

<specifics>
## Specific Ideas

- T6 officer role values are specific strings stored directly on `users.role`: `president`, `vp`, `treasurer`, `secretary`, `sergeant_at_arms`, `historian` (plus `member` and `admin` for non-officer roles). The leadership endpoint in Phase 3 will query WHERE role IN this officer list.
- `refresh_tokens` stores a hash of the token (not plaintext) — same pattern as storing hashed passwords
- `events.storage_path` stores relative paths (e.g., `events/uuid.pdf`) not full Supabase Storage URLs — signed URLs are generated on-demand in Phase 4

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-03*
