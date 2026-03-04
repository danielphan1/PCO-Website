# Architecture Patterns

**Domain:** FastAPI REST API backend (member auth + RBAC + file storage + email)
**Researched:** 2026-03-03
**Overall confidence:** HIGH — sourced from official FastAPI docs, existing scaffold reviewed

---

## Recommended Architecture

The existing scaffold already follows the correct production pattern: layered, dependency-injected, service-oriented. The primary work is implementing the empty stubs — not restructuring. This document captures the exact integration patterns for each cross-cutting concern.

### High-Level Component Map

```
HTTP Client
    ↓
[CORS Middleware]          app/main.py — rejects wrong-origin requests early
    ↓
[FastAPI Router]           app/api/router.py — routes to correct APIRouter
    ↓
[Dependency Chain]         app/core/deps.py — per-request auth + role checks
    │   ├── get_db()           yields SQLAlchemy Session, closes on exit
    │   ├── get_current_user() decodes JWT, loads User from DB
    │   └── require_admin()    checks user.role == "admin", raises 403 if not
    ↓
[Route Handler]            app/api/v1/**/*.py — validates request, calls service
    ↓
[Service Layer]            app/services/*.py — all business logic lives here
    │   ├── AuthService        password verify, token create/refresh
    │   ├── UserService        CRUD, soft-delete, audit log writes
    │   ├── EventService       PDF validation, Supabase Storage calls, DB record
    │   ├── InterestService    dedup check, DB persist, email trigger
    │   ├── EmailService       SMTP send (called BY other services)
    │   └── StorageService     Supabase Storage wrapper (called BY EventService)
    ↓
[Data Layer]               app/db/session.py — SQLAlchemy 2.0 sync sessions
    ↓
[PostgreSQL via Supabase]  psycopg3 driver
```

---

## Component Boundaries

### What Talks to What (strict rules)

| Component | Can Call | Cannot Call |
|-----------|----------|-------------|
| Route handlers | Services, `Depends()` dependencies | DB session directly, other routes |
| Services | DB session, StorageService, EmailService, utils | Route handlers, other services (prefer flat) |
| StorageService | supabase-py client | DB session, services |
| EmailService | smtplib / stdlib | DB session, services |
| `deps.py` | DB session, `security.py` | Services (exception: loading user row for auth) |
| `security.py` | python-jose, passlib | Everything else — pure functions |
| Models | SQLAlchemy Base | Everything — no imports from app code |
| Schemas | Pydantic only | Everything — no imports from app code |

**Key rule:** Services are the only layer that orchestrates. Routes are thin; they validate input and delegate. Models are dumb data containers. Schemas are pure Pydantic.

---

## Data Flow: Request Lifecycle

### 1. Authentication Flow (POST /v1/auth/login)

```
Client: POST /v1/auth/login {"email": "...", "password": "..."}
  → CORS middleware: origin check
  → Router: matches auth.router
  → Route handler: validates LoginRequest schema (Pydantic, auto)
  → Depends(get_db): opens SQLAlchemy session
  → Route calls: auth_service.authenticate(db, email, password)
    → UserService/auth: SELECT user WHERE email = ?
    → security.verify_password(plain, hashed): passlib bcrypt check
    → if fail: raise HTTPException(401)
    → security.create_access_token({"sub": user.id, "role": user.role})
    → security.create_refresh_token({"sub": user.id})
  → Route returns: {"access_token": "...", "refresh_token": "...", "token_type": "bearer"}
  → get_db closes session (via yield)
```

### 2. Protected Route Flow (GET /v1/users/me)

```
Client: GET /v1/users/me
  Authorization: Bearer <access_token>
  → CORS middleware
  → Router: matches events.router (auth required via dependency)
  → Depends(get_db): opens session
  → Depends(get_current_user):
    → OAuth2PasswordBearer extracts token from header
    → security.decode_token(token): jose.jwt.decode(token, secret, algorithm)
    → if expired/invalid: raise HTTPException(401)
    → payload["sub"] = user_id
    → payload["role"] = "member" | "admin"
    → SELECT user WHERE id = user_id AND is_active = True
    → if not found: raise HTTPException(401)
    → returns User ORM object
  → Route handler receives: current_user (User)
  → Returns: UserResponse schema (Pydantic serialization)
```

### 3. Admin-Only Route Flow (POST /v1/admin/members)

```
Client: POST /v1/admin/members
  Authorization: Bearer <access_token>
  → (same as above through get_current_user)
  → Depends(require_admin):
    → receives current_user from get_current_user
    → if current_user.role != "admin": raise HTTPException(403)
    → returns current_user (passes through)
  → Route handler: validates CreateMemberRequest schema
  → calls user_service.create_member(db, data)
    → generates temp password
    → security.hash_password(temp_password): passlib bcrypt
    → INSERT INTO users (...)
    → db.commit()
    → BackgroundTasks.add_task(email_service.send_welcome, email, temp_password)
  → Route returns: {"id": "...", "email": "..."}
```

### 4. PDF Upload Flow (POST /v1/admin/events)

```
Client: POST /v1/admin/events
  Content-Type: multipart/form-data
  Authorization: Bearer <access_token>
  → (auth + admin check via dependencies)
  → Route handler: receives UploadFile
  → calls event_service.upload_event_pdf(db, file, title, date)
    → validate: content_type == "application/pdf"
    → validate: file.size <= 10MB
    → storage_service.upload(file_bytes, filename, bucket="events")
      → supabase.storage.from_("events").upload(path, file_bytes)
      → returns public_url
    → INSERT INTO events (title, date, storage_path, public_url)
    → db.commit()
  → Route returns: EventResponse
```

### 5. Email Flow (POST /v1/interest — interest form)

```
Client: POST /v1/interest {"name": "...", "email": "...", ...}
  → CORS (no auth required — public endpoint)
  → Route handler: validates InterestFormRequest schema
  → Depends(get_db): opens session
  → calls interest_service.submit(db, data, background_tasks)
    → SELECT interest_submissions WHERE email = ? (dedup check)
    → if duplicate: raise HTTPException(409, "already submitted")
    → INSERT INTO interest_submissions (...)
    → db.commit()
    → background_tasks.add_task(email_service.send_confirmation, data.email)
  → Route returns: {"submitted": True}
  → [after response sent] email_service.send_confirmation runs in background
```

---

## Patterns to Follow

### Pattern 1: Dependency Injection for DB Session

The `get_db` generator uses `yield` to tie session lifecycle to request lifecycle. FastAPI closes the session automatically after response (or error).

```python
# app/core/deps.py
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Usage in route:
@router.get("/me")
def read_me(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ...
```

### Pattern 2: Chained Auth Dependencies (RBAC)

Build a dependency chain: get_db → get_current_user → require_admin. Each step adds a gate. Routes declare which gate they need.

```python
# app/core/deps.py

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = decode_token(token)          # raises if expired/invalid
        user_id = payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Inactive or missing user")
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Route declarations:
@router.get("/me")                                        # any authed user
def me(user: User = Depends(get_current_user)): ...

@router.get("/admin/members")                             # admin only
def list_members(admin: User = Depends(require_admin)): ...
```

### Pattern 3: Router-Level Dependency Application

Apply auth dependencies at the router level (not per-route) for admin routers. This eliminates forgetting to add `Depends` on individual routes.

```python
# app/api/v1/admin/users.py
from fastapi import APIRouter, Depends
from app.core.deps import require_admin

router = APIRouter(dependencies=[Depends(require_admin)])

@router.get("/")          # require_admin runs automatically on every route
def list_members(): ...

@router.post("/")
def create_member(): ...
```

### Pattern 4: JWT Security Utilities as Pure Functions

`app/core/security.py` should contain only pure functions with no side effects — no DB access, no imports from app business logic. This keeps security utilities testable and dependency-free.

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext

SECRET_KEY = ...  # from settings, not hardcoded
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_minutes: int) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(days=30)
    payload["type"] = "refresh"
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    # Raises jose.JWTError on invalid/expired — caller handles
```

### Pattern 5: Supabase Storage Integration

StorageService is a thin wrapper around supabase-py. It is called only from EventService — never directly from routes.

```python
# app/storage/files.py  (or app/services/storage_service.py)
from supabase import create_client, Client
from app.core.config import settings

def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_service_key)

class StorageService:
    BUCKET = "events"

    def __init__(self):
        self.client = get_supabase()

    def upload_pdf(self, file_bytes: bytes, path: str) -> str:
        """Upload bytes to Supabase Storage, return public URL."""
        self.client.storage.from_(self.BUCKET).upload(
            path=path,
            file=file_bytes,
            file_options={"content-type": "application/pdf"},
        )
        result = self.client.storage.from_(self.BUCKET).get_public_url(path)
        return result

    def delete_pdf(self, path: str) -> None:
        """Remove file from Supabase Storage."""
        self.client.storage.from_(self.BUCKET).remove([path])
```

**Configuration additions needed in `app/core/config.py`:**
- `supabase_url: str`
- `supabase_service_key: str` (service role key — not anon key, needed for admin operations)

### Pattern 6: Email as Background Task

EmailService wraps smtplib/SMTP. It is always called via `BackgroundTasks.add_task()` so the HTTP response is not delayed by SMTP latency.

```python
# app/services/email_service.py
import smtplib
from email.message import EmailMessage
from app.core.config import settings

class EmailService:
    def send(self, to: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = settings.smtp_from
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
            if settings.smtp_tls:
                smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_password)
            smtp.send_message(msg)

    def send_welcome(self, to: str, temp_password: str) -> None:
        self.send(to, "Welcome to PCO", f"Your temp password: {temp_password}")

    def send_confirmation(self, to: str) -> None:
        self.send(to, "Interest Form Received", "We'll be in touch!")

email_service = EmailService()  # module-level singleton
```

**Route usage:**
```python
@router.post("/")
def create_member(
    data: CreateMemberRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    member = user_service.create_member(db, data)
    background_tasks.add_task(email_service.send_welcome, data.email, member.temp_password)
    return member
```

### Pattern 7: Consistent Error Response Format

Register global exception handlers in `app/main.py` so all errors — Pydantic validation, JWT failures, HTTP exceptions — share the same JSON envelope.

```python
# app/main.py
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status": exc.status_code},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "details": exc.errors()},
    )
```

### Pattern 8: SQLAlchemy 2.0 Session Factory

The project uses SQLAlchemy 2.0 + psycopg3. Session management is synchronous (not async) — simpler to manage correctly and sufficient for this traffic scale.

```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

```python
# app/db/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### Pattern 9: Alembic Migration Workflow

`alembic/env.py` must import all models and point to the Base metadata so autogenerate works. The engine is constructed from settings (not hardcoded URL).

```python
# alembic/env.py (key parts)
from app.core.config import settings
from app.db.base import Base
import app.models  # ensures all models are imported so Base.metadata is populated

config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata
```

Migration workflow:
1. Edit model in `app/models/`
2. `alembic revision --autogenerate -m "description"` — generates migration script
3. Review generated script for correctness
4. `alembic upgrade head` — applies to DB

### Pattern 10: Audit Log Writes

The audit log (for role changes, deactivations) is written in the service layer — never in routes. Service receives the acting admin's user_id and writes the log entry within the same DB transaction.

```python
# Inside user_service.update_role(db, target_id, new_role, acting_admin_id):
user.role = new_role
log = AuditLog(
    action="role_change",
    target_user_id=target_id,
    acting_user_id=acting_admin_id,
    detail=f"role set to {new_role}",
)
db.add(user)
db.add(log)
db.commit()  # both changes in one transaction
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: DB Session in Middleware

**What:** Opening a SQLAlchemy session in middleware (e.g., to pre-load user in all requests).

**Why bad:** Middleware runs before routing. Sessions opened there may not be closed correctly on errors. FastAPI's `Depends(get_db)` with `yield` is purpose-built for per-request session lifecycle.

**Instead:** Always use `Depends(get_db)` in dependencies and route handlers. Never open sessions in middleware.

### Anti-Pattern 2: Business Logic in Route Handlers

**What:** Putting password verification, DB queries, email sends, or storage calls directly in the route handler function.

**Why bad:** Route handlers become untestable monoliths. Services can be unit-tested independently. Routes should only: validate schema, call service, return response.

**Instead:** Route handlers are 5-15 lines. All logic is in services.

### Anti-Pattern 3: Long-Lived Access Tokens as Refresh Strategy

**What:** Issuing 24-hour or 7-day access tokens to avoid implementing refresh.

**Why bad:** Compromised token gives attacker long-lived access. No ability to revoke without blocklist infrastructure.

**Instead:** Short-lived access tokens (60 min per existing config) + refresh token pattern. Refresh tokens are 30 days; access tokens are re-issued via `POST /v1/auth/refresh`.

### Anti-Pattern 4: Supabase Anon Key for Server-Side Storage

**What:** Using the Supabase anon key for server-side storage operations.

**Why bad:** Anon key respects RLS policies and bucket-level permissions that may block uploads. Server-side code needs the service role key to bypass RLS.

**Instead:** Use `supabase_service_key` (service role key) in the backend. Never expose this key to the frontend.

### Anti-Pattern 5: Synchronous SMTP in Request Path

**What:** Calling `email_service.send()` directly in the route handler (blocking).

**Why bad:** SMTP handshake takes 200-2000ms. Request hangs waiting for email. Under load, this exhausts workers.

**Instead:** Always use `background_tasks.add_task(email_service.send_*, ...)`. Response is returned immediately; email sends after.

### Anti-Pattern 6: Raw SQL Strings with String Formatting

**What:** `db.execute(f"SELECT * FROM users WHERE email = '{email}'")`

**Why bad:** SQL injection. SQLAlchemy ORM and text() with bound parameters exist for this reason.

**Instead:** Always use ORM queries or `sqlalchemy.text()` with `:param` bound parameters.

### Anti-Pattern 7: Storing Storage Paths vs. Full URLs

**What:** Storing only the Supabase Storage filename/path in the events table.

**Why bad:** If Supabase project URL changes (bucket rename, project migration), all stored paths break.

**Instead:** Store both `storage_path` (for delete operations) and `public_url` (for serving). The path is used only for Supabase API calls; the URL is what clients receive.

---

## Suggested Build Order

Dependencies determine order. Each layer depends on layers below it.

```
1. [Foundation]     DB models + Alembic migration (everything depends on schema)
   └── User, Event, InterestSubmission, RushInfo, OrgContent, AuditLog models
   └── Initial Alembic migration (creates all tables)

2. [Core Utilities]  security.py + deps.py (auth depends on these)
   └── hash_password, verify_password, create_access_token, decode_token
   └── get_db, get_current_user, require_admin

3. [Auth Routes]    POST /v1/auth/login + POST /v1/auth/refresh
   └── Validates the entire auth + dep chain works end-to-end
   └── Required before any other protected endpoint can be tested

4. [User Routes]    GET /v1/users/me + admin member management
   └── Depends on auth working (step 3)
   └── Email service needed for create_member (can stub initially)

5. [Email Service]  SMTP email service
   └── Standalone — no DB deps — can be built any time after step 2
   └── Required by: member create, interest form confirmation

6. [Interest Form]  POST /v1/interest + GET /v1/interest (admin)
   └── Public endpoint + email confirmation (requires step 5)

7. [Storage + Events] Supabase Storage client + event PDF routes
   └── Storage service is standalone (no DB)
   └── Event routes need storage + DB

8. [Rush + Content] Rush info + org content routes
   └── Simple CRUD — no external dependencies

9. [Error Handling]  Global exception handlers + consistent error format
   └── Can be added at any point but ideally before first production deploy

10. [Audit Log]     Write audit entries in user_service role/deactivate ops
    └── Depends on user management being functional (step 4)
```

**Phase boundary implication:** Steps 1-3 (models, core security, auth) should be one phase — they are the load-bearing foundation. Nothing else works without them.

---

## Scalability Considerations

This is a small-org API (dozens to hundreds of concurrent users maximum). The current synchronous SQLAlchemy approach is correct — async SQLAlchemy adds complexity without benefit at this scale.

| Concern | At current scale | If scale increases |
|---------|------------------|-------------------|
| DB connections | `pool_pre_ping=True` + default pool size (5) is sufficient | Increase pool size or use pgBouncer |
| Email | BackgroundTasks (in-process) sufficient | Move to Celery + Redis queue |
| File storage | Supabase Storage (CDN-backed) — no scale concern | Already CDN-backed |
| Auth tokens | In-memory verification (stateless JWT) sufficient | Add token blocklist (Redis) only if revocation needed |
| Session management | Sync sessions + `yield` pattern handles concurrent requests via thread pool | Migrate to async SQLAlchemy if I/O becomes bottleneck |

---

## Config Additions Required

The existing `Settings` class in `app/core/config.py` needs these additions before all components can be built:

```python
class Settings(BaseSettings):
    # existing...
    env: str = "dev"
    app_name: str = "psi-chi-omega-api"
    cors_origins: str = "http://localhost:3000"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/pco"
    jwt_secret: str = "change-me"
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 60

    # additions needed:
    refresh_token_expire_days: int = 30

    # Supabase Storage
    supabase_url: str = ""
    supabase_service_key: str = ""  # service role key, not anon key
    supabase_storage_bucket: str = "events"

    # SMTP Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_tls: bool = True
```

---

## Sources

- FastAPI official docs — JWT authentication: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ (HIGH confidence)
- FastAPI official docs — Dependency injection: https://fastapi.tiangolo.com/tutorial/dependencies/ (HIGH confidence)
- FastAPI official docs — Bigger applications / router composition: https://fastapi.tiangolo.com/tutorial/bigger-applications/ (HIGH confidence)
- FastAPI official docs — SQL database session management: https://fastapi.tiangolo.com/tutorial/sql-databases/ (HIGH confidence)
- FastAPI official docs — Background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/ (HIGH confidence)
- FastAPI official docs — Error handling: https://fastapi.tiangolo.com/tutorial/handling-errors/ (HIGH confidence)
- FastAPI official docs — OAuth2 scopes / RBAC: https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/ (HIGH confidence)
- FastAPI official docs — Middleware: https://fastapi.tiangolo.com/advanced/middleware/ (HIGH confidence)
- Supabase Storage Python API: training data + supabase-py known interface (MEDIUM confidence — verify bucket/upload method signatures against supabase-py changelog when implementing)
- python-jose JWT library: training data (MEDIUM confidence — in pyproject.toml already, verify decode() signature)
- passlib bcrypt CryptContext: training data (MEDIUM confidence — in pyproject.toml already, standard pattern)
- Existing scaffold reviewed: app/main.py, app/api/router.py, app/core/config.py (HIGH confidence — current code)

---

*Architecture analysis: 2026-03-03*
