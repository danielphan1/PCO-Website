# External Integrations

**Analysis Date:** 2026-03-05

## APIs & External Services

**File Storage:**
- Supabase Storage — stores event PDF files in the `"events"` bucket
  - SDK/Client: `supabase>=2.28.0` Python SDK
  - Client init: `pco_backend/app/storage/files.py` — lazy singleton `_get_client()`
  - Operations: upload, signed URL generation (1-hour expiry), remove
  - Auth: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` (service role key, not anon key)
  - Bucket: hardcoded `"events"` in `pco_backend/app/storage/files.py`

**Email (Transactional SMTP):**
- Generic SMTP provider (configurable) — sends welcome emails and interest form confirmations
  - SDK/Client: `aiosmtplib>=5.1.0` (async SMTP)
  - Implementation: `pco_backend/app/services/email_service.py`
  - Auth: `SMTP_HOST`, `SMTP_PORT` (default 587), `SMTP_USER`, `SMTP_PASSWORD`
  - TLS: STARTTLS on port 587 (`start_tls=True`)
  - Failure mode: errors are logged and swallowed — SMTP failures do not fail HTTP responses
  - Emails sent:
    - `send_welcome_email` — on new member account creation (with temp password)
    - `send_interest_confirmation` — on interest form submission

## Data Storage

**Databases:**
- PostgreSQL 16
  - Connection: `DATABASE_URL` env var (format: `postgresql+psycopg://user:pass@host:port/db`)
  - Default: `postgresql+psycopg://postgres:postgres@localhost:5432/pco`
  - Client: SQLAlchemy 2.0 ORM with psycopg3 driver (`pco_backend/app/db/session.py`)
  - Session: synchronous `sessionmaker`, `pool_pre_ping=True`
  - Migrations: Alembic (`pco_backend/alembic/`, `pco_backend/alembic.ini`)
  - Initial schema: `pco_backend/alembic/versions/001_initial_schema.py`
  - Docker: postgres:16 image in `pco_backend/docker/docker-compose.yml`

**File Storage:**
- Supabase Storage (remote, see above) — PDF files only
- No local filesystem file storage

**Caching:**
- None detected

## Authentication & Identity

**Auth Provider:**
- Custom (self-hosted JWT auth — NOT Supabase Auth)
  - JWT library: PyJWT (`pyjwt>=2.8`) — `pco_backend/app/core/security.py`
  - Algorithm: HS256 (configurable via `JWT_ALG`, default HS256)
  - Access token: short-lived (default 60 min), contains `sub` (UUID), `role`, `exp`, `iat`
  - Refresh token: 30-day, stored as SHA-256 hash in PostgreSQL (`pco_backend/app/models/refresh_token.py`)
  - Password hashing: bcrypt directly (`bcrypt>=4.0`), NOT via passlib
  - FastAPI dependency: `get_current_user` / `require_admin` in `pco_backend/app/core/deps.py`
  - Token validated via `HTTPBearer` scheme (visible in Swagger UI)

**Note:** Supabase SDK is used only for Storage — Supabase Auth is NOT used.

## Monitoring & Observability

**Error Tracking:**
- None (no Sentry, Datadog, or similar)

**Logs:**
- Python standard `logging` module (`pco_backend/app/core/logging.py`)
- SMTP errors logged at ERROR level in `pco_backend/app/services/email_service.py`
- Alembic logs to stderr via `pco_backend/alembic.ini` logger config

## CI/CD & Deployment

**Hosting:**
- Backend: Docker + Docker Compose (`pco_backend/docker/docker-compose.yml`, `pco_backend/docker/Dockerfile`)
- Frontend: Not yet configured for production hosting (Next.js app with `.next/` build output)

**CI Pipeline:**
- None detected (no GitHub Actions, CircleCI, etc.)

## Environment Configuration

**Required env vars (backend):**
- `JWT_SECRET` — REQUIRED, minimum 32 characters (validated at startup in `pco_backend/app/core/config.py`)
- `DATABASE_URL` — PostgreSQL connection string
- `SUPABASE_URL` — Supabase project URL (required for event PDF operations)
- `SUPABASE_SERVICE_KEY` — Supabase service role key (required for event PDF operations)
- `SMTP_HOST` — SMTP server hostname (required for email sending)
- `SMTP_USER` — SMTP login username / From address
- `SMTP_PASSWORD` — SMTP login password

**Optional env vars (with defaults):**
- `ENV` — `"dev"` default
- `CORS_ORIGINS` — comma-separated, default `"http://localhost:3000"`
- `JWT_ALG` — `"HS256"` default
- `ACCESS_TOKEN_EXPIRE_MINUTES` — `60` default
- `REFRESH_TOKEN_EXPIRE_DAYS` — `30` default
- `SMTP_PORT` — `587` default
- `FRONTEND_URL` — `"http://localhost:3000"` default (used in email body links)

**Secrets location:**
- `pco_backend/.env` file (not committed; `.env.example` committed as reference)
- Settings loaded via pydantic-settings (`pco_backend/app/core/config.py`)

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

## Internal API Communication

**Frontend → Backend:**
- REST API over HTTP (no SDK generated yet)
- Backend base URL: `http://localhost:8000` (dev) or `FRONTEND_URL` for email links
- CORS: configured via `CORS_ORIGINS` env var (comma-separated origins list in `pco_backend/app/main.py`)
- API versioned at `/v1/` prefix

**API Routes registered (`pco_backend/app/api/router.py`):**
- `GET /health` — health check (no auth)
- `/v1/public` — public content endpoints
- `/v1/interest` — interest form submissions
- `/v1/events` — event listing/PDF access
- `/v1/auth` — login, refresh, logout
- `/v1/users` — member self-service
- `/v1/rush` — rush info
- `/v1/content` — org content management
- `/v1/admin/users` — admin user management
- `/v1/admin/events` — admin event management
- `/v1/admin/settings` — admin settings

---

*Integration audit: 2026-03-05*
