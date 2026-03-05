# PCO San Diego Backend API

FastAPI REST API for the Psi Chi Omega (PCO) San Diego chapter — handles member authentication, event PDF storage, interest form submissions, rush info, and organization content for the chapter website.

## Setup

1. Copy `.env.example` to `.env` and fill in the required values:

   ```bash
   cp .env.example .env
   ```

2. Start the API and database with Docker:

   ```bash
   docker compose up
   ```

3. The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

**Note:** `JWT_SECRET` is required and has no default — the server will refuse to start without it (minimum 32 characters). `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` are optional for local development but required for event PDF upload/delete in production. `SMTP_*` variables are optional locally but required for welcome and confirmation emails in production.

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ENV` | No | `dev` | Runtime environment (`dev` / `prod`) |
| `APP_NAME` | No | `psi-chi-omega-api` | Application name |
| `APP_VERSION` | No | `0.1.0` | Application version |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Comma-separated list of allowed CORS origins |
| `DATABASE_URL` | No | `postgresql+psycopg://postgres:postgres@localhost:5432/pco` | SQLAlchemy database connection URL |
| `JWT_SECRET` | **Yes** | — | JWT signing secret (minimum 32 characters) |
| `JWT_ALG` | No | `HS256` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | `30` | Refresh token lifetime in days |
| `SUPABASE_URL` | No | — | Supabase project URL (required for event PDF uploads) |
| `SUPABASE_SERVICE_KEY` | No | — | Supabase service role key (required for event PDF uploads) |
| `SMTP_HOST` | No | — | SMTP server hostname (required for email sending) |
| `SMTP_PORT` | No | `587` | SMTP server port |
| `SMTP_USER` | No | — | SMTP username / sender address |
| `SMTP_PASSWORD` | No | — | SMTP password |
| `FRONTEND_URL` | No | `http://localhost:3000` | Frontend origin used in email links |

## Architecture

The API is built with **FastAPI** and **SQLAlchemy** (synchronous session, running in FastAPI's thread pool) on **PostgreSQL**. Schema migrations are managed by **Alembic**. Authentication uses **PyJWT** for token signing and **bcrypt** for password hashing, with short-lived JWT access tokens and rotating refresh tokens stored as SHA-256 hashes. Event PDF files are stored in a private **Supabase Storage** bucket; the database holds relative paths, and signed URLs are generated per-request for access. Email (welcome messages and interest-form confirmations) is sent non-blocking via **aiosmtplib** through FastAPI `BackgroundTasks` so the HTTP response is returned before SMTP completes.

Code layout:

- `app/api/` — route handlers (routers)
- `app/services/` — business logic
- `app/models/` — SQLAlchemy ORM models
- `app/schemas/` — Pydantic request/response schemas
- `app/storage/` — Supabase Storage wrapper
- `app/core/` — configuration, dependencies, security utilities

## API Reference

Full interactive docs (Swagger UI) at `http://localhost:8000/docs`.

| Method | Path | Auth | Description |
|---|---|---|---|
| **Auth** | | | |
| `POST` | `/v1/auth/login` | public | Login with email/password; returns access + refresh tokens |
| `POST` | `/v1/auth/refresh` | public | Exchange refresh token for a new access token |
| **Users** | | | |
| `GET` | `/v1/users/me` | member | Get own profile |
| **Events** | | | |
| `GET` | `/v1/events` | member | List event PDFs with signed download URLs (newest first) |
| `POST` | `/v1/admin/events` | admin | Upload event PDF (multipart/form-data; max 10 MB; PDF only) |
| `DELETE` | `/v1/admin/events/{id}` | admin | Delete event PDF from storage and database |
| **Members** | | | |
| `GET` | `/v1/admin/users` | admin | List all members (filter by active/deactivated) |
| `POST` | `/v1/admin/users` | admin | Create member account (generates temp password, sends welcome email) |
| `PATCH` | `/v1/admin/users/{id}/role` | admin | Update member role (writes to audit log) |
| `PATCH` | `/v1/admin/users/{id}/deactivate` | admin | Deactivate member (invalidates all refresh tokens) |
| `PATCH` | `/v1/admin/users/{id}/reactivate` | admin | Reactivate member |
| **Interest Form** | | | |
| `POST` | `/v1/interest` | public | Submit interest form (duplicate email returns 409; sends confirmation email) |
| `GET` | `/v1/interest` | admin | List all interest submissions |
| **Rush Info** | | | |
| `GET` | `/v1/rush` | public | View rush info (full details if published, or `{"status": "coming_soon"}`) |
| `PUT` | `/v1/rush` | admin | Update rush info |
| `PATCH` | `/v1/rush/visibility` | admin | Toggle rush info published/hidden |
| **Org Content** | | | |
| `GET` | `/v1/content/history` | public | View org history |
| `GET` | `/v1/content/philanthropy` | public | View philanthropy info |
| `GET` | `/v1/content/contacts` | public | View contact info |
| `GET` | `/v1/content/leadership` | public | View leadership (officer roles from users table) |
| `PUT` | `/v1/content/{section}` | admin | Update content section (`history` \| `philanthropy` \| `contacts`) |
