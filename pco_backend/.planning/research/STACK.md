# Technology Stack

**Project:** PCO San Diego Backend API
**Researched:** 2026-03-03
**Confidence:** HIGH (versions confirmed from uv.lock, lockfile upload-times verified against PyPI)

---

## Status Key

- **INSTALLED** — In `pyproject.toml` + `uv.lock`, resolved and pinned
- **PLANNED** — Directory/config stub exists but package not in dependencies yet
- **NEEDED** — Must be added before the feature phase that uses it

---

## Recommended Stack

### Core Framework

| Technology | Version (locked) | Status | Why |
|------------|-----------------|--------|-----|
| FastAPI | 0.135.1 | INSTALLED | Industry-standard async Python API framework; automatic OpenAPI docs; native Pydantic v2 integration |
| uvicorn[standard] | 0.30+ | INSTALLED | Production ASGI server; `[standard]` extra includes uvloop (Linux perf) + watchfiles (dev reload) |
| Pydantic | 2.12.5 | INSTALLED | v2 is the current generation; ~5-50x faster validation than v1 due to Rust core |
| Pydantic Settings | 2.13.1 | INSTALLED | Typed env-var config with `.env` support; already wired in `app/core/config.py` |

### Database

| Technology | Version (locked) | Status | Why |
|------------|-----------------|--------|-----|
| SQLAlchemy | 2.0+ | INSTALLED | Industry ORM; 2.0 style (no legacy Session patterns); async-capable; well-matched to Pydantic v2 |
| psycopg[binary] | 3.3.3 | INSTALLED | psycopg3 is the current-generation PostgreSQL driver; binary wheels avoid libpq dependency; Feb 2026 release |
| Alembic | latest (`>=1.13`) | NEEDED | Migration tool for SQLAlchemy. `alembic/` directory and `script.py.mako` exist but **Alembic is not in `pyproject.toml`**. Must be added before any migration is run. |

Note: `alembic/` exists as a folder with `env.py` and `script.py.mako` stubs, but there is no `alembic.ini` and Alembic is not listed in project dependencies. This is a gap.

### Authentication and Security

| Technology | Version (locked) | Status | Why |
|------------|-----------------|--------|-----|
| python-jose[cryptography] | 3.5.0 | INSTALLED | JWT encode/decode. 3.5.0 released May 2025 after a long dormancy — acceptable for v1 scope. See note below. |
| passlib[bcrypt] | 1.7.4 | INSTALLED | Password hashing wrapper. Last released 2020; stale but functional for bcrypt specifically. See note below. |
| bcrypt | 5.0.0 | INSTALLED (transitive) | The actual bcrypt C implementation; actively maintained (Sept 2025 release). |
| cryptography | 46.0.5 | INSTALLED (transitive) | Required by python-jose[cryptography] for RS256/ES256; also provides HS256 HMAC support. |

**JWT library note (python-jose vs PyJWT):** python-jose was unmaintained from 2021-2024; 3.5.0 in May 2025 renewed activity. PyJWT 2.x is more actively maintained and widely recommended in current FastAPI community. However, python-jose is already installed, pinned, and functional for HS256. The cost of switching mid-project is not justified for v1. Stick with python-jose. If this project grows past v1, migrate to PyJWT or Authlib.

**passlib note:** passlib 1.7.4 is from 2020 and receives no updates. The project only uses it for bcrypt (via `passlib[bcrypt]`). The bcrypt C extension (5.0.0) is current and the wrapper still works. Acceptable for v1. A future migration to `bcrypt` directly or `argon2-cffi` is recommended for v2.

### Storage (Supabase)

| Technology | Version | Status | Why |
|------------|---------|--------|-----|
| supabase | `>=2.10` | NEEDED | Official Python client for Supabase Storage and Supabase Realtime. Wraps `storage3`, `postgrest-py`, `gotrue`. Use for PDF upload/delete to Supabase Storage buckets. Do NOT use for database queries — use SQLAlchemy + psycopg directly. |

**Rationale:** The project uses Supabase as a hosted PostgreSQL provider and for object storage. The database connection goes through SQLAlchemy (not Supabase PostgREST), so the supabase-py client is needed only for Storage operations. The `app/storage/` directory exists as stubs (`files.py`, `paths.py`) but supabase-py is not installed.

**Version guidance:** supabase-py 2.x is the current major version (introduced async support). Specify `supabase>=2.10` to get current Storage v2 API.

### Email (SMTP)

| Technology | Version | Status | Why |
|------------|---------|--------|-----|
| aiosmtplib | `>=3.0` | NEEDED | Async SMTP client; native asyncio, no threading; works directly with FastAPI's async handlers. Lightweight and no vendor lock-in — configured purely via env vars (host, port, user, password). |

**Rationale:** The project specifies generic SMTP (configurable provider). Do NOT use fastapi-mail — it is a heavier abstraction with Jinja2 template dependencies and less granular control. Do NOT use smtplib (stdlib) in async context — it blocks the event loop. aiosmtplib is the standard async SMTP choice for FastAPI projects as of 2026.

**Install:** `aiosmtplib>=3.0` (3.x supports Python 3.11+, uses modern asyncio patterns).

### Infrastructure

| Technology | Version (locked) | Status | Why |
|------------|-----------------|--------|-----|
| python-multipart | 0.0.22 | INSTALLED | Required by FastAPI for `Form(...)` and `UploadFile` — already installed |
| python-dotenv | 1.2.2 | INSTALLED (transitive) | Loaded via Pydantic Settings for `.env` file support |

### Testing (Not Yet Installed)

| Library | Version | Status | Why |
|---------|---------|--------|-----|
| pytest | `>=8.0` | NEEDED | Standard Python test runner; `app/tests/` directory exists with stubs |
| httpx | `>=0.28` | NEEDED | Required for FastAPI's `TestClient` in async mode; replaces `requests` for API testing |
| pytest-asyncio | `>=0.24` | NEEDED | Enables `async def test_*` functions in pytest for async FastAPI endpoints |
| anyio | already installed | INSTALLED | Already pulled in by FastAPI/starlette |

**Add to `[project.optional-dependencies]` or a `[dependency-groups]` dev section in `pyproject.toml`.** Do not add test deps to `[project.dependencies]` — they should not land in the production Docker image.

### Code Quality (Dev Tools)

| Tool | Version | Status | Why |
|------|---------|--------|-----|
| ruff | latest | CONFIGURED (not in lockfile) | Linter + formatter; `[tool.ruff]` already in `pyproject.toml` with `line-length = 100`. Add as dev dependency. |
| black | — | NOT NEEDED | PROJECT.md lists "Black + Ruff" but Ruff now includes a Black-compatible formatter (`ruff format`). No need for both. Use Ruff only. |

---

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| JWT | python-jose (keep) | PyJWT 2.x | Already installed; switching cost not worth it for v1 scope |
| Password hashing | passlib[bcrypt] (keep) | bcrypt directly, argon2-cffi | passlib works; migration is a v2 concern |
| SMTP | aiosmtplib | fastapi-mail | fastapi-mail adds Jinja2 + heavy abstractions; overkill for plain-text/simple HTML emails |
| SMTP | aiosmtplib | smtplib (stdlib) | stdlib is synchronous; blocks the event loop in FastAPI async handlers |
| Storage | supabase-py | boto3 (S3 compat) | Project is already on Supabase; supabase-py is the right client |
| Database ORM | SQLAlchemy 2.0 (keep) | Supabase PostgREST | PostgREST is for JS/frontend clients; SQLAlchemy gives proper Python ORM, type safety, and migrations |
| Migrations | Alembic | Supabase migrations UI | Alembic gives version-controlled, code-reviewed migration files alongside the app |
| Testing | pytest + httpx | unittest | pytest is idiomatic Python; httpx is required for FastAPI async test client |
| Formatter | ruff format | black | Ruff format is Black-compatible; no need to run both |

---

## Packages to Add (Summary)

These packages are NOT yet in `pyproject.toml` and must be added:

```bash
# Runtime dependencies (add to [project.dependencies])
uv add alembic
uv add "supabase>=2.10"
uv add "aiosmtplib>=3.0"

# Dev/test dependencies (add to [dependency-groups] or tool.uv.dev-dependencies)
uv add --dev pytest
uv add --dev httpx
uv add --dev pytest-asyncio
uv add --dev ruff
```

---

## Configuration Gaps

The `app/core/config.py` `Settings` class will need new environment variables for:

| Variable | For | Example |
|----------|-----|---------|
| `SUPABASE_URL` | supabase-py client init | `https://xyz.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | supabase-py client auth (service role bypasses RLS) | `eyJ...` |
| `SUPABASE_STORAGE_BUCKET` | Which bucket to use for event PDFs | `event-pdfs` |
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | SMTP auth username | `noreply@pcosandiego.com` |
| `SMTP_PASSWORD` | SMTP auth password | `...` |
| `SMTP_FROM` | From address in sent emails | `PCO San Diego <noreply@pcosandiego.com>` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `30` |

The existing `access_token_expire_minutes` (default: 60) is correct for short-lived access tokens. A separate `REFRESH_TOKEN_EXPIRE_DAYS` config is needed once refresh tokens are implemented.

---

## Docker Notes

The current Dockerfile (`docker/Dockerfile`) does NOT copy `uv.lock` and uses `uv sync --no-dev` without the lockfile. This means Docker builds resolve fresh from PyPI constraints (not pinned). The fix:

```dockerfile
# Correct pattern — copy lockfile for reproducible builds
COPY uv.lock /app/uv.lock
RUN uv sync --frozen --no-dev
```

This is a **critical production concern** — without `--frozen`, the Docker image is not reproducible.

---

## Sources

- `uv.lock` — all locked versions extracted directly from lockfile (upload-time fields confirm PyPI release dates)
- `pyproject.toml` — installed dependency declarations
- `app/core/config.py` — existing config structure
- `docker/Dockerfile` — current build pattern
- Pydantic v2 docs: https://docs.pydantic.dev/latest/
- FastAPI docs: https://fastapi.tiangolo.com/
- psycopg 3 changelog: upload-time 2026-02-18 in lockfile confirms current release
- bcrypt 5.0.0: upload-time 2025-09-25 in lockfile confirms current release
- python-jose 3.5.0: upload-time 2025-05-28 in lockfile (renewed activity after long dormancy)
- passlib: upload-time 2020-10-08 in lockfile (stale but functional for bcrypt use case)
- Confidence: HIGH for installed packages (from lockfile), MEDIUM for recommended additions (standard ecosystem choices, no external verification available in this session)
