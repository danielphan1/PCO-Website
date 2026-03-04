# Architecture

**Analysis Date:** 2026-03-03

## Pattern Overview

**Overall:** Layered REST API with service-oriented business logic

**Key Characteristics:**
- FastAPI-based REST API (HTTP request/response)
- Versioned API routes (/v1/) with admin-specific endpoints
- Separation of concerns: routes → services → database models
- Configuration-driven settings via environment variables
- PostgreSQL as primary persistence layer

## Layers

**API Layer (Routes):**
- Purpose: Handle HTTP requests, route to services, return JSON responses
- Location: `app/api/v1/` and `app/api/v1/admin/`
- Contains: FastAPI routers, endpoint handlers, request/response mapping
- Depends on: Service layer for business logic
- Used by: FastAPI application and HTTP clients

**Service Layer (Business Logic):**
- Purpose: Encapsulate domain logic and orchestrate database operations
- Location: `app/services/`
- Contains: Service classes (auth_service.py, user_service.py, event_service.py, interest_service.py)
- Depends on: Database models, schemas for validation
- Used by: API routes for business logic execution

**Data Layer (Persistence):**
- Purpose: Manage database connections, session lifecycle, and ORM operations
- Location: `app/db/`
- Contains: SQLAlchemy session factory, database initialization, Alembic migrations
- Depends on: PostgreSQL database, SQLAlchemy ORM
- Used by: Service layer for CRUD operations

**Models Layer (Domain Objects):**
- Purpose: Define database tables and ORM entities
- Location: `app/models/`
- Contains: SQLAlchemy declarative models (User, Event, EventPdf, InterestForm, Role)
- Depends on: SQLAlchemy base class
- Used by: Database session for querying and persistence

**Schemas Layer (Data Validation):**
- Purpose: Define request/response validation using Pydantic
- Location: `app/schemas/`
- Contains: Pydantic models for serialization/deserialization
- Depends on: Pydantic validation library
- Used by: API routes for request validation and response serialization

**Core/Infrastructure Layer:**
- Purpose: Cross-cutting concerns and configuration
- Location: `app/core/`
- Contains: Settings (config.py), security utilities (security.py), dependency injection (deps.py), logging (logging.py)
- Depends on: Environment configuration, external libraries
- Used by: All other layers

**Storage Layer (File Management):**
- Purpose: Handle file I/O and storage paths for uploaded files
- Location: `app/storage/`
- Contains: File operations (files.py), path utilities (paths.py)
- Depends on: Local filesystem (MVP phase)
- Used by: Services for file uploads (e.g., PDF uploads)

**Utilities Layer (Helpers):**
- Purpose: Reusable helper functions and validation logic
- Location: `app/utils/`
- Contains: Time utilities (time.py), validators (validators.py)
- Depends on: No external business logic
- Used by: Services and schemas for common operations

## Data Flow

**Authentication Flow:**

1. Client sends credentials to `POST /v1/auth/login`
2. API route (`app/api/v1/auth.py`) receives request
3. Route calls `auth_service` to verify credentials and generate JWT
4. Service queries User model via database session
5. Service returns token to route
6. Route returns JWT token in response

**Event Upload Flow:**

1. Admin sends POST with PDF file to `POST /v1/admin/events/upload`
2. API route (`app/api/v1/admin/events.py`) receives UploadFile
3. Route calls `event_service` with file data
4. Service validates file via `validators.py`
5. Service saves file to storage via `files.py`
6. Service creates EventPdf model record in database
7. Service returns confirmation with file metadata
8. Route returns success response

**Interest Form Submission Flow:**

1. User submits form to `POST /v1/interest/submit`
2. API route (`app/api/v1/interest.py`) receives form data
3. Route validates data via InterestForm schema
4. Route checks interest submission status (in-memory STATE in MVP)
5. Route calls `interest_service` to persist form
6. Service creates InterestForm model record in database
7. Service returns confirmation
8. Route returns response to client

**State Management:**

- Transient state: In-memory dictionaries for MVP phase (e.g., `STATE` in interest.py for open/closed status)
- Persistent state: PostgreSQL database for user data, events, forms
- Configuration state: Environment variables via `Settings` class in `app/core/config.py`

## Key Abstractions

**Settings/Configuration:**
- Purpose: Centralize environment-based application configuration
- Examples: `app/core/config.py` (Settings class)
- Pattern: Pydantic BaseSettings with .env file support

**APIRouter (Modular Endpoints):**
- Purpose: Group related endpoints and compose into main application
- Examples: `app/api/v1/auth.py`, `app/api/v1/events.py`, `app/api/v1/admin/users.py`
- Pattern: FastAPI APIRouter with prefix-based routing composition

**Service Classes:**
- Purpose: Encapsulate reusable business logic separate from HTTP concerns
- Examples: `app/services/auth_service.py`, `app/services/user_service.py`
- Pattern: Class-based services with methods for domain operations

**SQLAlchemy Models:**
- Purpose: Define database schema and ORM entity mapping
- Examples: `app/models/user.py`, `app/models/event_pdf.py`, `app/models/interest_form.py`
- Pattern: Declarative SQLAlchemy models inheriting from Base

**Pydantic Schemas:**
- Purpose: Define request/response contracts and validation rules
- Examples: `app/schemas/user.py`, `app/schemas/auth.py`
- Pattern: Pydantic BaseModel subclasses for type safety

## Entry Points

**Main Application:**
- Location: `app/main.py`
- Triggers: uvicorn server startup
- Responsibilities: FastAPI app initialization, middleware setup (CORS), router composition, health check endpoint

**Health Check Endpoint:**
- Location: `app/main.py` - `GET /health`
- Triggers: External monitoring, orchestration health probes
- Responsibilities: Return simple {"ok": True} status

**API Router Composition:**
- Location: `app/api/router.py`
- Triggers: Application initialization
- Responsibilities: Aggregate all versioned route modules (public, auth, events, interest, admin routes)

## Error Handling

**Strategy:** Minimalist MVP approach with gradual enhancement planned

**Patterns:**
- Route handlers return explicit success responses ({"created": True, "user": payload})
- Error handling logic is stubbed (TODO comments) - will be enhanced
- No global exception handlers currently in place
- Validation errors will be handled by Pydantic schema validation (automatic)

## Cross-Cutting Concerns

**Logging:** Empty module `app/core/logging.py` - infrastructure exists but not yet implemented

**Validation:**
- Route-level: Pydantic schemas in `app/schemas/`
- Business logic: Custom validators in `app/utils/validators.py` (not yet implemented)
- File validation: Planned in file service

**Authentication:**
- JWT-based approach specified in Settings (jwt_secret, jwt_alg, access_token_expire_minutes)
- Security module `app/core/security.py` exists but empty
- Login endpoint stubbed in `app/api/v1/auth.py`
- Dependency injection pattern in `app/core/deps.py` (not yet implemented) for protected routes

**CORS:**
- Middleware configured in `app/main.py` with origins from Settings
- Allows credentials and all methods/headers (MVP-permissive configuration)

---

*Architecture analysis: 2026-03-03*
