# External Integrations

**Analysis Date:** 2026-03-03

## APIs & External Services

**None Detected**

Current implementation is MVP stage with no third-party API integrations. All endpoints return stub responses marked as "TODO" or in-memory state.

## Data Storage

**Databases:**
- PostgreSQL 16
  - Connection: `DATABASE_URL` environment variable
  - Format: `postgresql+psycopg://username:password@host:port/database`
  - Default local: `postgresql+psycopg://postgres:postgres@localhost:5432/pco`
  - Client: SQLAlchemy 2.0+ ORM via psycopg 3.3.3 driver
  - Located in: `app/db/` (base.py, session.py, init_db.py)

**File Storage:**
- Local filesystem only
- Storage module stubbed in `app/storage/` (paths.py, files.py)
- PDF upload endpoint defined but not implemented
- Location: `app/api/v1/admin/events.py` has upload_pdf stub

**Caching:**
- None detected

## Authentication & Identity

**Auth Provider:**
- Custom JWT-based authentication
- Implementation: Token-based via python-jose
  - JWT Signing: Uses `JWT_SECRET` environment variable
  - Algorithm: `JWT_ALG` (default: HS256)
  - Expiration: `ACCESS_TOKEN_EXPIRE_MINUTES` (default: 60)
  - Location: `app/core/security.py` (empty stub), `app/core/deps.py` (empty stub)

**Password Hashing:**
- Framework: passlib[bcrypt]
- Algorithm: bcrypt (via passlib 1.7.4)
- Config location: `app/core/security.py`

**Auth Endpoints:**
- POST `/v1/auth/login` - Login endpoint (MVP stub, returns `{"token": "TODO"}`)
- Location: `app/api/v1/auth.py`

## Monitoring & Observability

**Error Tracking:**
- None detected

**Logs:**
- Not configured
- Logging module stub exists at `app/core/logging.py`

## CI/CD & Deployment

**Hosting:**
- Docker (containerized deployment ready)
- Local development via Docker Compose or direct uvicorn
- Dockerfile: `docker/Dockerfile`
- Compose: `docker/docker-compose.yml`

**CI Pipeline:**
- None detected
- No GitHub Actions, GitLab CI, or other CI configuration files

## Environment Configuration

**Required Environment Variables:**
- `ENV` - Environment identifier (dev, staging, prod)
- `APP_NAME` - Application name for API metadata
- `CORS_ORIGINS` - CSV of allowed CORS origins for frontend communication
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret for JWT signing (must be changed from default in production)
- `JWT_ALG` - JWT algorithm name (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token lifetime in minutes

**Secrets Location:**
- `.env` file (git-ignored via `.gitignore`)
- Configuration location: `app/core/config.py` defines Settings class with `env_file = ".env"`
- Example provided: `.env.example` with placeholder values

**Development Setup:**
```bash
# Copy example to .env
cp .env.example .env

# Modify values as needed, especially:
# - JWT_SECRET (change from "change-me")
# - DATABASE_URL if using non-local PostgreSQL
# - CORS_ORIGINS if using different frontend URL
```

## Webhooks & Callbacks

**Incoming:**
- None detected

**Outgoing:**
- None detected

## CORS Configuration

**Framework:** FastAPI CORSMiddleware
**Location:** `app/main.py`

**Configuration:**
- `allow_origins`: Loaded from `CORS_ORIGINS` env var (comma-separated list)
- `allow_credentials`: True
- `allow_methods`: ["*"] (all methods)
- `allow_headers`: ["*"] (all headers)

**Default (Development):**
- Allows requests from `http://localhost:3000` (typical React dev server)

## Data Persistence

**Migrations:**
- Framework: Alembic
- Location: `alembic/` directory
- Config: `alembic/env.py` (empty stub)
- Scripts: `alembic/script.py.mako` template
- Status: MVP setup, no migrations committed

**Session Management:**
- Location: `app/db/session.py` (empty stub)
- ORM: SQLAlchemy 2.0+
- Expected: Database session factory for dependency injection

## API Structure

**Base URL:** `http://localhost:8000` (development)

**Health Check:**
- GET `/health` - Returns `{"ok": True}`

**Versioned Endpoints (v1):**
- `/v1/public/*` - Public organization information
- `/v1/auth/*` - Authentication endpoints
- `/v1/interest/*` - Interest form submission
- `/v1/events/*` - Event listing
- `/v1/admin/users/*` - User management (admin-only stub)
- `/v1/admin/events/*` - Event administration (admin-only stub)
- `/v1/admin/settings/*` - Settings management (admin-only stub)

**API Router Location:** `app/api/router.py` aggregates all v1 routes

## Frontend Integration

**Expected Frontend:**
- URL: `http://localhost:3000` (default CORS origin)
- Framework: Likely React based on typical PCO website tech stack
- Authentication: Bearer token via JWT (client stores in localStorage/cookie)

**API Response Format:**
- JSON responses via Pydantic models
- Validation by Pydantic 2.12.5
- Error handling: FastAPI default error responses

---

*Integration audit: 2026-03-03*
