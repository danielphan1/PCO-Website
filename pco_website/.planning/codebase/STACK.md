# Technology Stack

**Analysis Date:** 2026-03-05

## Languages

**Primary:**
- TypeScript 5.x - Frontend (`pco_website/`) — all `.ts`/`.tsx` source files
- Python 3.11+ (runtime: 3.14.0) - Backend (`pco_backend/`) — all `.py` source files

**Secondary:**
- CSS - Global styles (`pco_website/app/globals.css`) via Tailwind utility classes

## Runtime

**Frontend:**
- Node.js v22.14.0

**Backend:**
- CPython 3.14.0 (venv pinned to >=3.11 in `pco_backend/pyproject.toml`)

## Package Managers

**Frontend:**
- pnpm 10.23.0
- Lockfile: `pco_website/pnpm-lock.yaml` (present)
- Workspace config: `pco_website/pnpm-workspace.yaml`

**Backend:**
- uv 0.9.11
- Lockfile: `pco_backend/uv.lock` (present)

## Frameworks

**Frontend Core:**
- Next.js 16.1.6 — App Router, SSR/SSG, file-based routing (`pco_website/app/`)
- React 19.2.3 — UI component layer
- React DOM 19.2.3 — Browser rendering

**Backend Core:**
- FastAPI >=0.115 — REST API framework (`pco_backend/app/main.py`)
- Uvicorn >=0.30 (standard extras) — ASGI server, runs on port 8000

**Styling:**
- Tailwind CSS ^4 — Utility-first CSS via PostCSS plugin (`pco_website/postcss.config.mjs`)
- `@tailwindcss/postcss` ^4 — PostCSS integration

**Testing:**
- pytest >=9.0.2 — Backend test runner (`pco_backend/app/tests/`)
- httpx >=0.28.1 — Async HTTP client used in pytest fixtures for API calls

## Key Dependencies

**Backend — Critical:**
- `sqlalchemy>=2.0` — ORM for all database models (`pco_backend/app/models/`, `pco_backend/app/db/`)
- `psycopg[binary]>=3.2` — PostgreSQL driver (psycopg3, async-capable)
- `alembic>=1.18.4` — Database migrations (`pco_backend/alembic/`)
- `pydantic[email]>=2.7` — Request/response validation and settings
- `pydantic-settings>=2.3` — Settings from env vars (`pco_backend/app/core/config.py`)
- `pyjwt>=2.8` — JWT encode/decode (NOT python-jose; intentional)
- `bcrypt>=4.0` — Password hashing (NOT via passlib; passlib 1.7.4 + bcrypt 5.0.0 is broken)
- `python-multipart>=0.0.9` — Multipart form/file upload support
- `aiosmtplib>=5.1.0` — Async SMTP for transactional email
- `supabase>=2.28.0` — Supabase Storage SDK for PDF file storage

**Frontend — Critical:**
- `next` 16.1.6 — Core framework
- `react` / `react-dom` 19.2.3 — UI rendering

## Configuration

**Frontend:**
- TypeScript: `pco_website/tsconfig.json` — strict mode, `@/*` path alias maps to root
- ESLint: `pco_website/eslint.config.mjs` — uses `eslint-config-next` core-web-vitals + TypeScript rules
- PostCSS/Tailwind: `pco_website/postcss.config.mjs`
- Next.js: `pco_website/next.config.ts` — minimal config (no custom options set)
- Target: ES2017, module resolution: bundler

**Backend:**
- App config: `pco_backend/app/core/config.py` — `pydantic-settings` reads from `.env`, case-insensitive
- Linting/Formatting: `ruff` (configured in `pco_backend/pyproject.toml`) — line length 100, double quotes, space indent
- DB migrations: `pco_backend/alembic.ini` + `pco_backend/alembic/versions/001_initial_schema.py`
- Test config: `testpaths = ["app/tests"]` in `pco_backend/pyproject.toml`

**Environment:**
- Backend reads `.env` from `pco_backend/` directory
- Required env vars: `JWT_SECRET` (minimum 32 chars, validated at import time)
- See `pco_backend/.env.example` for all variables

## Build / Dev

**Frontend:**
```bash
pnpm dev       # Next.js dev server (localhost:3000)
pnpm build     # Production build
pnpm start     # Serve production build
pnpm lint      # ESLint
```

**Backend:**
```bash
uv run uvicorn app.main:app --reload   # Dev server (localhost:8000)
uv run pytest                           # Tests
uv run ruff check .                     # Lint
uv run ruff format .                    # Format
uv run alembic upgrade head             # Apply migrations
```

## Containerization

- Docker Compose: `pco_backend/docker/docker-compose.yml`
- Dockerfile: `pco_backend/docker/Dockerfile` — uses `python:3.11-slim`, installs via `uv`, runs uvicorn
- Services: `db` (postgres:16 on port 5432), `api` (FastAPI on port 8000)
- PostgreSQL volume: `pco_pg` (persistent named volume)

## Platform Requirements

**Development:**
- Node.js v22+ (pnpm 10+)
- Python 3.11+ with uv 0.9.11+
- PostgreSQL 16 (via Docker or local install)

**Production:**
- Backend: Docker container (`python:3.11-slim` base)
- Frontend: Not yet deployed (Next.js build target unspecified)

---

*Stack analysis: 2026-03-05*
