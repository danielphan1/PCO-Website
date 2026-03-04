# Technology Stack

**Analysis Date:** 2026-03-03

## Languages

**Primary:**
- Python 3.11+ - FastAPI backend, all server-side logic
- SQL - PostgreSQL database queries via SQLAlchemy ORM

## Runtime

**Environment:**
- Python 3.11 (minimum requirement specified in `pyproject.toml`)
- uvicorn ASGI server for running FastAPI application

**Package Manager:**
- uv (fast Python package installer/resolver)
- Lockfile: `uv.lock` present (version 1, revision 3)

## Frameworks

**Core:**
- FastAPI 0.135.1 - Web framework and API routing
- uvicorn[standard] 0.30+ - ASGI server implementation
- Pydantic 2.12.5 - Data validation and serialization
- Pydantic Settings 2.13.1 - Environment configuration management

**Database:**
- SQLAlchemy 2.0+ - ORM and SQL query builder
- psycopg[binary] 3.3.3 - PostgreSQL database driver
- Alembic - Database migration framework (located in `alembic/` directory)

**Authentication & Security:**
- python-jose[cryptography] 3.5.0 - JWT token generation and verification
- passlib[bcrypt] 1.7.4 - Password hashing with bcrypt algorithm
- cryptography 46.0.5 - Cryptographic operations for JWT signing

**Utilities:**
- python-multipart 0.0.22 - Multipart/form-data parsing for file uploads
- python-dotenv 1.2.2 - Environment variable loading from `.env` files

## Key Dependencies

**Critical:**
- fastapi 0.135.1 - Core API framework; all endpoint routing depends on this
- uvicorn[standard] 0.30+ - Production ASGI server; required to run the application
- sqlalchemy 2.0+ - Database ORM; all data persistence depends on this
- psycopg[binary] 3.3.3 - PostgreSQL driver; database connectivity depends on this
- pydantic 2.12.5 - Request/response validation; data integrity depends on this

**Cryptography & Security:**
- python-jose[cryptography] 3.5.0 - JWT token signing and verification
- passlib[bcrypt] 1.7.4 - Secure password hashing
- bcrypt 5.0.0 - Bcrypt hashing algorithm (included via passlib)

**Transport & Network:**
- anyio 4.12.1 - Async I/O foundation for FastAPI
- h11 0.16.0 - HTTP/1.1 protocol implementation
- httptools 0.7.1 - Fast HTTP request parsing

## Configuration

**Environment:**
- Configured via `.env` file (example: `.env.example`)
- Uses Pydantic Settings with case-insensitive environment variable mapping
- Location: `app/core/config.py` defines `Settings` class

**Required Environment Variables:**
- `ENV` - Environment name (dev, prod, etc.)
- `APP_NAME` - Application display name (default: "psi-chi-omega-api")
- `CORS_ORIGINS` - Comma-separated list of allowed CORS origins (default: "http://localhost:3000")
- `DATABASE_URL` - PostgreSQL connection string (format: `postgresql+psycopg://user:password@host:port/database`)
- `JWT_SECRET` - Secret key for JWT signing and verification
- `JWT_ALG` - JWT algorithm (default: "HS256")
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration in minutes (default: 60)

**Build:**
- Dockerfile located at `docker/Dockerfile`
- Python 3.11-slim base image
- Uses multi-stage pattern: installs uv, creates venv, syncs dependencies
- Exposes port 8000 for API access

## Platform Requirements

**Development:**
- Python 3.11+
- uv package manager
- PostgreSQL 16 (via Docker Compose)
- `.env` file with configuration (copy from `.env.example`)

**Production:**
- Docker container (Python 3.11-slim base)
- PostgreSQL 16+ database server
- Port 8000 exposed for incoming traffic
- Environment variables injected at runtime

## Database

**Type:** PostgreSQL
- Version: 16 (specified in `docker-compose.yml`)
- Client Library: psycopg 3.3.3 with binary wheels for performance

**Connection String Format:**
```
postgresql+psycopg://username:password@hostname:port/database_name
```

**Default Local Connection:**
- Host: localhost:5432
- Database: pco
- User: postgres
- Password: postgres (development only)

**Volume:** `pco_pg` named volume persists data between container restarts

## Docker Deployment

**Compose Stack:**
Located in `docker/docker-compose.yml`:

**Services:**
- `db` - PostgreSQL 16 with persistent volume `pco_pg`
- `api` - FastAPI application with hot-reload development support

**Build Context:**
- Dockerfile: `docker/Dockerfile`
- App source: copied from `../app/` directory
- Alembic migrations: copied from `../alembic/` directory

**Development Mode:**
- Live code reloading via mounted volumes
- Port mapping: API on 8000, PostgreSQL on 5432
- Commands: `docker compose up --build` or `docker compose up -d db` for database-only

---

*Stack analysis: 2026-03-03*
