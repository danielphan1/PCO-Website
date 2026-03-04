# Codebase Structure

**Analysis Date:** 2026-03-03

## Directory Layout

```
pco_backend/
├── app/                    # Main application package
│   ├── __init__.py
│   ├── main.py            # FastAPI app initialization, CORS, router composition
│   ├── api/               # HTTP API layer
│   │   ├── router.py      # Main router aggregator
│   │   └── v1/            # API v1 endpoints
│   │       ├── public.py  # Public endpoints (GET /info)
│   │       ├── auth.py    # Authentication (POST /login)
│   │       ├── events.py  # Event listing (GET /)
│   │       ├── interest.py # Interest form (POST /submit, GET /status)
│   │       └── admin/     # Admin-only endpoints (requires T6 role)
│   │           ├── users.py   # User management (POST /, PATCH /{id}/role)
│   │           ├── events.py  # Event admin (POST /upload, DELETE /{id})
│   │           └── settings.py # Settings admin (POST /interest/open, /close)
│   ├── core/              # Infrastructure and configuration
│   │   ├── __init__.py
│   │   ├── config.py      # Settings class for env-based configuration
│   │   ├── security.py    # JWT and auth utilities (stub)
│   │   ├── deps.py        # Dependency injection for protected routes (stub)
│   │   └── logging.py     # Logging configuration (stub)
│   ├── db/                # Database layer
│   │   ├── __init__.py
│   │   ├── session.py     # SQLAlchemy SessionLocal factory (stub)
│   │   ├── base.py        # SQLAlchemy Base declarative class (stub)
│   │   └── init_db.py     # Database initialization (stub)
│   ├── models/            # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py        # User model (stub)
│   │   ├── role.py        # Role model (stub)
│   │   ├── event_pdf.py   # Event PDF reference model (stub)
│   │   └── interest_form.py # Interest form submission model (stub)
│   ├── schemas/           # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── user.py        # User request/response schema (stub)
│   │   ├── auth.py        # Auth request schema (stub)
│   │   ├── event.py       # Event schema (stub)
│   │   └── interest_form.py # Interest form schema (stub)
│   ├── services/          # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication logic (stub)
│   │   ├── user_service.py      # User management logic (stub)
│   │   ├── event_service.py     # Event and PDF management logic (stub)
│   │   └── interest_service.py  # Interest form processing logic (stub)
│   ├── storage/           # File storage management
│   │   ├── __init__.py
│   │   ├── files.py       # File I/O operations (stub)
│   │   └── paths.py       # Storage path utilities (stub)
│   ├── utils/             # Shared utility functions
│   │   ├── __init__.py
│   │   ├── validators.py  # Custom validation logic (stub)
│   │   └── time.py        # Time utilities (stub)
│   └── tests/             # Test suite
│       ├── __init__.py
│       ├── conftest.py    # Pytest configuration (stub)
│       ├── test_auth.py   # Auth endpoint tests (stub)
│       ├── test_events.py # Events endpoint tests (stub)
│       └── test_interest.py # Interest form tests (stub)
├── alembic/               # Database migration configuration
│   ├── env.py            # Alembic environment setup (stub)
│   └── script.py.mako    # Migration template (stub)
├── docker/                # Containerization
│   ├── Dockerfile        # API container definition
│   └── docker-compose.yml # Multi-container orchestration (db + api)
├── scripts/               # Utility scripts
│   └── dev.sh            # Development server startup script
├── pyproject.toml        # UV package manager config, project metadata
├── uv.lock              # Dependency lock file
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

## Directory Purposes

**app/:**
- Purpose: Main application package containing all business logic and API code
- Contains: Python modules organized by function (api, core, db, models, schemas, services, storage, utils, tests)
- Key files: `main.py` (entry point), `api/router.py` (route aggregator)

**app/api/v1/:**
- Purpose: Version 1 API endpoints organized by feature domain
- Contains: Individual route modules for public endpoints, auth, events, interest forms
- Key files: `app/api/router.py` aggregates all sub-routers with v1 prefix

**app/api/v1/admin/:**
- Purpose: Admin-only API endpoints requiring authentication and T6 role
- Contains: Admin user management, event upload/delete, settings toggles
- Key files: `users.py`, `events.py`, `settings.py`

**app/core/:**
- Purpose: Cross-cutting infrastructure and configuration
- Contains: Settings management, security utilities, dependency injection, logging
- Key files: `config.py` (Settings class - central config source)

**app/db/:**
- Purpose: Database connection and ORM setup
- Contains: SQLAlchemy session factory, base model class, database initialization
- Key files: `session.py` (SessionLocal), `base.py` (Base declarative class)

**app/models/:**
- Purpose: SQLAlchemy ORM entity definitions
- Contains: User, Role, EventPdf, InterestForm database models
- Key files: Each model in separate file (user.py, event_pdf.py, etc.)

**app/schemas/:**
- Purpose: Pydantic request/response validation models
- Contains: Schemas for each entity (User, Auth, Event, InterestForm)
- Key files: One schema file per domain area

**app/services/:**
- Purpose: Business logic encapsulation separate from HTTP layer
- Contains: Service classes implementing domain operations (auth, users, events, interest)
- Key files: `auth_service.py`, `user_service.py`, `event_service.py`, `interest_service.py`

**app/storage/:**
- Purpose: File storage operations and path management
- Contains: File I/O abstractions and path utilities
- Key files: `files.py` (file operations), `paths.py` (path helpers)

**app/utils/:**
- Purpose: Reusable utility functions and helpers
- Contains: Custom validators, time utilities, common functions
- Key files: `validators.py` (validation logic), `time.py` (time helpers)

**app/tests/:**
- Purpose: Test suite for API endpoints and business logic
- Contains: Unit and integration tests
- Key files: `conftest.py` (pytest fixtures), `test_*.py` (test modules by feature)

**alembic/:**
- Purpose: Database schema versioning and migrations
- Contains: Alembic configuration and migration scripts
- Key files: `env.py` (environment setup), `versions/` (migration files - created during development)

**docker/:**
- Purpose: Container configuration for local and production deployment
- Contains: Dockerfile for API, docker-compose.yml for multi-container setup
- Key files: `docker-compose.yml` (orchestrates db + api services)

**scripts/:**
- Purpose: Automation scripts for development and operations
- Contains: Helper scripts for common tasks
- Key files: `dev.sh` (runs uvicorn with reload)

## Key File Locations

**Entry Points:**
- `app/main.py`: FastAPI application creation, middleware setup, router inclusion, health check
- `docker/docker-compose.yml`: Container orchestration entry point
- `scripts/dev.sh`: Development server startup

**Configuration:**
- `app/core/config.py`: Settings class with environment variable mapping
- `.env`: Environment variables (not committed - use .env.example as template)
- `pyproject.toml`: Project metadata, dependencies, tool configuration
- `docker/docker-compose.yml`: Infrastructure configuration

**Core Logic:**
- `app/api/router.py`: API route aggregation and versioning
- `app/api/v1/*.py`: Feature-specific endpoint routes
- `app/api/v1/admin/*.py`: Admin endpoint routes
- `app/services/*.py`: Business logic implementation

**Database:**
- `app/db/session.py`: Database connection factory
- `app/db/base.py`: SQLAlchemy declarative base
- `app/models/*.py`: ORM entity definitions
- `alembic/`: Migration infrastructure

**Testing:**
- `app/tests/conftest.py`: Test fixtures and configuration
- `app/tests/test_*.py`: Test files organized by feature

## Naming Conventions

**Files:**
- API routes: lowercase with underscores, no prefix (e.g., `events.py`, `auth.py`)
- Service files: `{domain}_service.py` pattern (e.g., `user_service.py`, `auth_service.py`)
- Model files: singular entity name lowercase (e.g., `user.py`, `event_pdf.py`)
- Schema files: singular entity name lowercase (e.g., `user.py`, `auth.py`)
- Test files: `test_{feature}.py` pattern (e.g., `test_auth.py`, `test_events.py`)
- Migration files: Alembic auto-generates with timestamps (e.g., `001_initial.py`)

**Directories:**
- Feature domains: plural lowercase (e.g., `models/`, `services/`, `schemas/`, `tests/`)
- Admin features: grouped under `admin/` subdirectory in API routes
- Versioned APIs: `v1/`, `v2/`, etc. pattern for backward compatibility

## Where to Add New Code

**New Feature (e.g., "member directory"):**
1. Create API route in `app/api/v1/member_directory.py` with APIRouter
2. Create schema in `app/schemas/member_directory.py` with Pydantic models
3. Create service in `app/services/member_directory_service.py` with business logic
4. Create model in `app/models/member.py` (ORM entity if persisting)
5. Add schema tests in `app/tests/test_member_directory.py`
6. Include router in `app/api/router.py` with appropriate prefix and tags

**New Admin Feature (e.g., "bulk user import"):**
1. Create route in `app/api/v1/admin/users.py` (extend existing if same entity)
2. Or create new file `app/api/v1/admin/bulk_import.py` if separate concern
3. Follow same pattern as above for service, schema, model

**New Model/Entity:**
1. Define SQLAlchemy model in `app/models/{entity}.py`
2. Add to `app/models/__init__.py` for easy import
3. Create migration in `alembic/versions/` (will be auto-generated by Alembic)
4. Create Pydantic schema in `app/schemas/{entity}.py`

**Utility Function:**
- Shared validators: `app/utils/validators.py`
- Time-related helpers: `app/utils/time.py`
- Create new file only for distinct concern (e.g., `app/utils/email.py`)

**Test for Existing Code:**
- Endpoint test: `app/tests/test_{feature}.py`
- Import fixtures from `conftest.py`
- Use existing patterns in test files as templates

## Special Directories

**app/tests/:**
- Purpose: Contains all test files and test configuration
- Generated: No (manually created)
- Committed: Yes (code is committed)
- Note: Fixtures and mocks defined in `conftest.py` for reuse

**.planning/codebase/:**
- Purpose: GSD codebase analysis documents
- Generated: Yes (auto-generated by mapping process)
- Committed: Yes (documentation is committed)
- Note: Contains ARCHITECTURE.md, STRUCTURE.md, and other analysis docs

**docker/:**
- Purpose: Container definitions for local development and production
- Generated: No (manually maintained)
- Committed: Yes (docker files are committed)
- Note: Use docker-compose for local development, push images for production

**alembic/versions/:**
- Purpose: Database migration scripts
- Generated: Yes (auto-generated by Alembic with manual editing)
- Committed: Yes (migrations are committed for reproducibility)
- Note: Run `alembic upgrade head` to apply migrations

**app/core/ (infrastructure):**
- Purpose: Singleton/shared infrastructure like config, security, logging
- Generated: No (manually maintained)
- Committed: Yes (infrastructure code is committed)
- Note: Dependency injection pattern for injectable services in deps.py

---

*Structure analysis: 2026-03-03*
