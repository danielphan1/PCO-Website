# Phase 3: Core Features - Research

**Researched:** 2026-03-04
**Domain:** FastAPI feature endpoints — member management, interest form, rush info, org content, SMTP email
**Confidence:** HIGH

## Summary

Phase 3 builds on a complete auth layer (Phase 2) to implement all remaining v1 feature endpoints. The codebase already has all ORM models defined (`User`, `InterestSubmission`, `RushInfo`, `OrgContent`, `AuditLog`, `RefreshToken`), stub routers for admin users and interest form, and empty service stubs (`user_service.py`, `interest_service.py`, `auth_service.py`). The primary work is filling in the service implementations, completing the stub routers, creating two new routers (`rush.py`, `content.py`), and implementing `email_service.py` using `aiosmtplib`.

The email service is the only cross-cutting concern. It uses `aiosmtplib.send()` — an async function — called via FastAPI `BackgroundTasks` which accepts both sync and async callables. The `secrets` module generates temp passwords. All DB operations stay synchronous (sync SQLAlchemy established in Phase 1 decisions). Rush info uses an upsert pattern (get-or-create single row). Org content similarly uses a get-or-create keyed by `section` string.

**Primary recommendation:** Implement feature domains as isolated service + router pairs in this order: (1) email service, (2) member management, (3) interest form, (4) rush info, (5) org content. Each domain is independently testable. Tests use the existing `auth_client` fixture pattern with SQLite in-memory DB.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Email — welcome (new member)**
- Full onboarding content: welcome message, their email, their temp password, and a login URL
- Login URL sourced from `FRONTEND_URL` env var — add to `Settings` class; works for dev and prod
- Non-blocking: sent via FastAPI `BackgroundTasks` (XCUT-04 already specified)

**Email — interest form confirmation**
- Simple acknowledgment only: "We received your interest form and will reach out soon."
- Non-blocking: sent via FastAPI `BackgroundTasks`

**Email — failure handling**
- Log and swallow: if the background SMTP task fails, log the error server-side only
- HTTP response is already returned; client and admin are not notified of email failure
- No `email_sent` field in responses

**Org content format**
- Plain text for all three sections (history, philanthropy, contacts)
- `PUT /v1/content/{section}` accepts and stores raw string; no processing or validation of format
- Frontend handles any display formatting

**Leadership endpoint**
- Return name + role only per officer: `{"full_name": "...", "role": "president"}`
- Omit vacant roles: if no user holds a given officer role, that role does not appear in the response
- Query: `WHERE role IN OFFICER_ROLES AND is_active = true`
- `OFFICER_ROLES` constant already defined in `app/models/user.py`

**Audit log scope**
- All member mutations write to `audit_log`:
  - Member created (POST /admin/members)
  - Role changed (PATCH /admin/members/{id}/role)
  - Member deactivated (PATCH /admin/members/{id}/deactivate)
  - Member reactivated (PATCH /admin/members/{id}/reactivate)
- Actor is the authenticated admin (`require_admin` dependency provides the user)
- Use existing `AuditLog` model: `actor_id`, `action` (string verb), `target_id` (user UUID), `target_type` ("user")

### Claude's Discretion
- Temp password length and character set (alphanumeric, ~12 chars is reasonable)
- Welcome email subject line and exact body copy (professional tone)
- Confirmation email subject line and exact body copy
- Audit log `action` string values (e.g., "member.created", "member.role_updated", etc.)
- Whether `PUT /v1/rush` upserts a single row or errors if no row exists yet

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MEMB-01 | Admin can list all members via GET /api/admin/members with active/deactivated filter | SQLAlchemy filter on `is_active`, existing `require_admin` dep; return list of `UserResponse` |
| MEMB-02 | Admin can create member account via POST /api/admin/members (name, email, role), system generates temp password, sends welcome email via SMTP | `secrets.choice()` for temp pw; `hash_password()` from security.py; `aiosmtplib.send()` via BackgroundTasks |
| MEMB-03 | Admin can update member role via PATCH /api/admin/members/{id}/role — writes entry to audit_log | Validate role in `ALL_ROLES`; `AuditLog` model write; action string e.g. "member.role_updated" |
| MEMB-04 | Admin can deactivate member via PATCH /api/admin/members/{id}/deactivate — soft-delete (is_active=false), invalidates all refresh tokens for that user | Set `is_active=False`; delete or revoke all `RefreshToken` rows for user; write AuditLog |
| MEMB-05 | Admin can reactivate member via PATCH /admin/members/{id}/reactivate — restores login access | Set `is_active=True`; write AuditLog; no token changes needed |
| INTR-01 | Anyone can submit interest form via POST /api/interest — duplicate email returns 409, sends confirmation email on success | Check `InterestSubmission` uniqueness by email; IntegrityError or pre-check; BackgroundTasks email |
| INTR-02 | Admin can list all interest submissions via GET /api/interest | Query all `InterestSubmission` rows; admin-only via `require_admin` |
| RUSH-01 | Anyone can view rush info via GET /api/rush — returns full details if published, or {"status": "coming_soon"} if hidden | Query single `RushInfo` row; return conditional response based on `is_published` |
| RUSH-02 | Admin can update rush info via PUT /api/rush (dates, times, locations, descriptions) | Upsert single `RushInfo` row (get-or-create); validate fields with Pydantic schema |
| RUSH-03 | Admin can toggle rush visibility via PATCH /api/rush/visibility | Toggle `is_published` on single `RushInfo` row |
| CONT-01 | Anyone can view org history via GET /api/content/history | Query `OrgContent` by section="history"; return empty string if not yet set |
| CONT-02 | Anyone can view philanthropy info via GET /api/content/philanthropy | Query `OrgContent` by section="philanthropy" |
| CONT-03 | Anyone can view contact info via GET /api/content/contacts | Query `OrgContent` by section="contacts" |
| CONT-04 | Anyone can view leadership (T6) via GET /api/content/leadership | Query `User` WHERE role IN OFFICER_ROLES AND is_active=True; return name+role only |
| CONT-05 | Admin can update content sections via PUT /api/content/{section} (section: history, philanthropy, contacts) | Upsert `OrgContent` row by section key; validate section value in Pydantic |
| XCUT-04 | SMTP email sends welcome and confirmation emails via FastAPI BackgroundTasks (non-blocking) | `aiosmtplib.send()` is async; BackgroundTasks.add_task() accepts async callables; log and swallow SMTP errors |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| aiosmtplib | 5.1.0 (installed) | Async SMTP client | Already in deps; async-native; BackgroundTasks compatible |
| FastAPI BackgroundTasks | (fastapi>=0.115) | Non-blocking task dispatch | Built into FastAPI; inject as function parameter |
| secrets | stdlib | Cryptographically secure random | stdlib; best practice for temp passwords |
| string | stdlib | Character sets for password generation | stdlib; alphanumeric chars |
| email.message.EmailMessage | stdlib | Email message construction | stdlib; works directly with aiosmtplib.send() |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| SQLAlchemy Session | 2.0 (installed) | Synchronous DB queries | All DB access (established pattern) |
| Pydantic v2 | 2.7+ (installed) | Request/response schemas | All input validation, all response shapes |
| bcrypt | 4.0+ (installed) | Password hashing | `hash_password()` already in security.py |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| aiosmtplib.send() | smtplib (sync) | sync blocks request thread; aiosmtplib is already installed and async |
| secrets.choice() for temp pw | uuid4 | uuid4 not human-typeable; secrets.choice with alphanumeric is readable |
| get-or-create for rush | error if no row | get-or-create is simpler and requires no pre-seeding step |

**Installation:** No new packages needed. All dependencies already installed.

## Architecture Patterns

### Recommended Project Structure
```
app/
├── api/v1/
│   ├── admin/
│   │   └── users.py          # FILL IN: member management endpoints (stub exists)
│   ├── interest.py            # FILL IN: interest form endpoints (stub exists)
│   ├── rush.py                # CREATE: rush info endpoints (not yet created)
│   └── content.py             # CREATE: org content endpoints (not yet created)
├── services/
│   ├── user_service.py        # FILL IN: member CRUD + audit log (empty stub)
│   ├── interest_service.py    # FILL IN: interest form CRUD (empty stub)
│   ├── email_service.py       # CREATE: SMTP send functions (not yet created)
│   └── rush_service.py        # CREATE: rush info CRUD (not yet created)
│       (content logic can live inline in content router — simple enough)
├── schemas/
│   ├── user.py                # EXTEND: add MemberCreate, MemberListResponse, etc.
│   ├── interest_form.py       # CREATE: InterestFormCreate, InterestFormResponse
│   ├── rush.py                # CREATE: RushInfoUpdate, RushInfoResponse
│   └── content.py             # CREATE: ContentUpdate, ContentResponse, LeadershipEntry
└── core/
    └── config.py              # EXTEND: add frontend_url field
```

### Pattern 1: Service Layer + Router Separation
**What:** Business logic lives in service functions; router functions inject db + current_user, call service, return response.
**When to use:** All Phase 3 endpoints — consistent with auth.py pattern.
**Example:**
```python
# Source: established Phase 2 pattern (app/api/v1/auth.py)
# Router function is thin — delegates to service
@router.post("/", response_model=UserResponse, status_code=201)
def create_member(
    payload: MemberCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    return user_service.create_member(db, payload, background_tasks, actor=current_user)
```

### Pattern 2: FastAPI BackgroundTasks for Email
**What:** Inject `BackgroundTasks` as a function parameter; call `background_tasks.add_task(async_fn, *args)`.
**When to use:** MEMB-02 (welcome email) and INTR-01 (confirmation email).
**Example:**
```python
# Source: FastAPI docs — BackgroundTasks accepts both sync and async callables
from fastapi import BackgroundTasks

# In router:
def create_member(background_tasks: BackgroundTasks, ...):
    user = user_service.create_member(db, payload, actor=current_user)
    background_tasks.add_task(email_service.send_welcome, user.email, user.full_name, temp_pw)
    return user

# In email_service.py:
async def send_welcome(to_email: str, full_name: str, temp_password: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.smtp_user
    msg["To"] = to_email
    msg["Subject"] = "Welcome to Psi Chi Omega"
    msg.set_content(f"Hello {full_name}, ...")
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
    except Exception as exc:
        logger.error("Failed to send welcome email to %s: %s", to_email, exc)
```

### Pattern 3: Upsert with Get-or-Create
**What:** For single-row tables (`rush_info`, `org_content`), query for existing row; if None, create new. Update fields and commit.
**When to use:** `PUT /v1/rush` (RUSH-02), `PUT /v1/content/{section}` (CONT-05).
**Example:**
```python
# Source: SQLAlchemy 2.0 sync pattern, consistent with Phase 2 usage
def upsert_rush(db: Session, payload: RushInfoUpdate) -> RushInfo:
    rush = db.query(RushInfo).first()
    if rush is None:
        rush = RushInfo()
        db.add(rush)
    rush.dates = payload.dates
    rush.times = payload.times
    rush.locations = payload.locations
    rush.description = payload.description
    db.commit()
    db.refresh(rush)
    return rush
```

### Pattern 4: Audit Log Write
**What:** After each member mutation, create an `AuditLog` row with `actor_id`, `action`, `target_id`, `target_type`.
**When to use:** MEMB-02, MEMB-03, MEMB-04, MEMB-05.
**Example:**
```python
# Source: app/models/audit_log.py — model fields
def write_audit(db: Session, actor: User, action: str, target: User) -> None:
    log = AuditLog(
        actor_id=actor.id,
        action=action,
        target_id=target.id,
        target_type="user",
    )
    db.add(log)
    # Caller commits
```

### Pattern 5: Duplicate Email — 409 on IntegrityError
**What:** For interest form, catch `IntegrityError` from unique constraint on `email` field (or pre-check with query).
**When to use:** INTR-01 duplicate email detection.
**Example:**
```python
# Source: InterestSubmission model — email has unique=True, index=True
from sqlalchemy.exc import IntegrityError

def submit_interest(db: Session, payload: InterestFormCreate) -> InterestSubmission:
    existing = db.query(InterestSubmission).filter(
        InterestSubmission.email == payload.email
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already submitted")
    submission = InterestSubmission(**payload.model_dump())
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission
```

### Pattern 6: Refresh Token Invalidation on Deactivate
**What:** When deactivating a member (MEMB-04), mark all their `RefreshToken` rows as revoked (or delete them).
**When to use:** MEMB-04 only.
**Example:**
```python
# Source: app/models/refresh_token.py — revoked field exists
def deactivate_member(db: Session, user: User, actor: User) -> User:
    user.is_active = False
    # Invalidate all refresh tokens
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.revoked == False,  # noqa: E712
    ).update({"revoked": True})
    write_audit(db, actor, "member.deactivated", user)
    db.commit()
    db.refresh(user)
    return user
```

### Pattern 7: Leadership Query
**What:** Query users WHERE role IN OFFICER_ROLES AND is_active=True. Return only full_name and role.
**When to use:** CONT-04.
**Example:**
```python
# Source: app/models/user.py — OFFICER_ROLES constant
from app.models.user import OFFICER_ROLES

officers = (
    db.query(User)
    .filter(User.role.in_(OFFICER_ROLES), User.is_active == True)  # noqa: E712
    .all()
)
# Return [{"full_name": u.full_name, "role": u.role} for u in officers]
```

### Anti-Patterns to Avoid
- **Blocking SMTP in request handler:** Never call `aiosmtplib.send()` directly in a sync route without BackgroundTasks — it will raise an event loop error or block. Always use `background_tasks.add_task()`.
- **Raising HTTP exceptions inside BackgroundTasks:** The response is already sent when the background task runs. Log and swallow errors — do not raise HTTPException.
- **Committing before adding audit log:** Write audit log entry AND user change in the same `db.commit()` call to keep them atomic.
- **Returning temp password in the response body:** The temp password goes in the welcome email only; the HTTP response returns the new `UserResponse` (no password field).
- **Using `db.query(User).filter(User.role == "admin")` for leadership:** Leadership uses `OFFICER_ROLES`, not "admin". They are separate.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SMTP email sending | Custom SMTP socket code | `aiosmtplib.send()` | Handles STARTTLS negotiation, auth, connection pooling, retries |
| Secure random passwords | `random.choice()` | `secrets.choice()` | `random` is not cryptographically secure; `secrets` is stdlib designed for this |
| Email message formatting | String concatenation | `email.message.EmailMessage` | stdlib; handles headers, encoding, multipart correctly |
| Unique constraint violation detection | Manual error string parsing | Pre-check query OR catch `sqlalchemy.exc.IntegrityError` | Pre-check is simpler and readable in this case |
| Role validation | Hand-written list comparison | `ALL_ROLES` constant from `app/models/user.py` | Constant already defined; single source of truth |

**Key insight:** The email service is the only new technical concern. Everything else is straightforward SQLAlchemy CRUD that follows Phase 2 patterns exactly.

## Common Pitfalls

### Pitfall 1: aiosmtplib in Sync Context
**What goes wrong:** `aiosmtplib.send()` is a coroutine. Calling it directly from a sync service function raises `RuntimeError: This event loop is already running` or a coroutine warning.
**Why it happens:** FastAPI routes defined with `def` (not `async def`) run in a thread pool, not the event loop.
**How to avoid:** The email-sending function must be `async def`. Pass it to `background_tasks.add_task()` — FastAPI handles running async background tasks on the event loop. The service function that adds the task can be sync.
**Warning signs:** `RuntimeError` mentioning event loop, or email silently never sends.

### Pitfall 2: SQLite UUID Column in Tests
**What goes wrong:** `sqlalchemy.dialects.postgresql.UUID` type doesn't exist in SQLite. Tests using the `auth_client` fixture (which uses SQLite) may fail when new models use PostgreSQL-specific types.
**Why it happens:** Existing conftest uses `sqlite:///./test.db`. All current models use `UUID(as_uuid=True)` from `sqlalchemy.dialects.postgresql`.
**How to avoid:** Existing models already work with SQLite in tests (Phase 2 tests pass). SQLAlchemy falls back to storing UUIDs as VARCHAR in SQLite. New schema files for rush, content, interest should follow the same pattern — no raw SQL, only ORM. This is already working.
**Warning signs:** `OperationalError` or type mismatch during `Base.metadata.create_all()` in tests.

### Pitfall 3: Committing Audit Log Separately
**What goes wrong:** If audit log is committed in a separate transaction after the user mutation commits, and an error occurs between the two commits, the audit trail is lost.
**Why it happens:** Two `db.commit()` calls for what should be one atomic change.
**How to avoid:** Add both the user mutation AND the audit log entry to the session before calling `db.commit()` once.
**Warning signs:** AuditLog table has gaps; user changes exist without corresponding audit entries.

### Pitfall 4: Rush Info — Table Empty on First GET
**What goes wrong:** `GET /v1/rush` returns 500 or an unexpected response when `rush_info` table is empty (no rows yet seeded).
**Why it happens:** Code assumes a row exists (`db.query(RushInfo).first()` returns None) and tries to access `.is_published` on None.
**How to avoid:** `GET /v1/rush` should handle `None` result by returning `{"status": "coming_soon"}` (treat no-row as "not published").
**Warning signs:** 500 error on first `GET /v1/rush` in a fresh deployment.

### Pitfall 5: OrgContent — Empty Section Returns 500
**What goes wrong:** `GET /v1/content/history` crashes when no row exists for section="history".
**Why it happens:** Route tries to access `.content` on None result.
**How to avoid:** Return a response with `content: ""` (empty string) when no row exists for the section. Do not 404 — the content just hasn't been set yet.
**Warning signs:** 500 on content endpoints in fresh deployment.

### Pitfall 6: Section Validation for PUT /content/{section}
**What goes wrong:** `PUT /v1/content/invalid_section` creates a row with an invalid section key.
**Why it happens:** No validation on the `section` path parameter.
**How to avoid:** Use a `Literal["history", "philanthropy", "contacts"]` Pydantic type or a FastAPI `Enum` path param to restrict valid values at the router level. Return 422 on invalid section.
**Warning signs:** Unexpected section keys appearing in `org_content` table.

### Pitfall 7: Deactivate Does Not Invalidate In-Flight Access Tokens
**What goes wrong:** Admin deactivates a user but the user's short-lived access token (60-min TTL) still works for up to 60 minutes.
**Why it happens:** Access tokens are stateless JWTs. `get_current_user` checks `is_active` on each request — so deactivation IS enforced on each request. Refresh tokens are revoked by MEMB-04.
**How to avoid:** This is acceptable behavior per Phase 2 decisions. The access token check in `get_current_user` already re-fetches the user from DB and checks `is_active`, so deactivation takes effect immediately on the next request. No special handling needed — just document it.
**Warning signs:** Confusing this with "tokens still work" — they don't, because `get_current_user` re-reads `is_active` from DB.

## Code Examples

### Email Service — send_welcome
```python
# Source: aiosmtplib 5.1.0 docs + app/core/config.py pattern
import logging
from email.message import EmailMessage

import aiosmtplib

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_welcome_email(to_email: str, full_name: str, temp_password: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.smtp_user
    msg["To"] = to_email
    msg["Subject"] = "Welcome to Psi Chi Omega — Your Account"
    msg.set_content(
        f"Hello {full_name},\n\n"
        f"Your Psi Chi Omega account has been created.\n\n"
        f"Email: {to_email}\n"
        f"Temporary Password: {temp_password}\n\n"
        f"Login at: {settings.frontend_url}\n\n"
        f"Please change your password after your first login.\n\n"
        f"Psi Chi Omega San Diego"
    )
    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to send welcome email to %s: %s", to_email, exc)
```

### Temp Password Generation
```python
# Source: Python stdlib docs — secrets module
import secrets
import string

def generate_temp_password(length: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
```

### Member Create — Full Flow
```python
# Source: established Phase 2 patterns; security.py hash_password
def create_member(
    db: Session,
    payload: MemberCreate,
    actor: User,
) -> tuple[User, str]:
    """Returns (new_user, temp_password). Caller sends email via BackgroundTasks."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    temp_pw = generate_temp_password()
    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=hash_password(temp_pw),
        is_active=True,
    )
    db.add(user)
    db.flush()  # Get user.id before audit log

    log = AuditLog(
        actor_id=actor.id,
        action="member.created",
        target_id=user.id,
        target_type="user",
    )
    db.add(log)
    db.commit()
    db.refresh(user)
    return user, temp_pw
```

### Rush Info — GET with Empty Table Handling
```python
# Source: RushInfo model; RUSH-01 requirement
@router.get("/")
def get_rush(db: Session = Depends(get_db)):
    rush = db.query(RushInfo).first()
    if rush is None or not rush.is_published:
        return {"status": "coming_soon"}
    return RushInfoResponse.model_validate(rush)
```

### OrgContent — GET with Empty Row Handling
```python
# Source: OrgContent model; CONT-01 through CONT-03
@router.get("/{section}")
def get_content(section: str, db: Session = Depends(get_db)):
    row = db.query(OrgContent).filter(OrgContent.section == section).first()
    return {"section": section, "content": row.content if row else ""}
```

### config.py — Add frontend_url
```python
# Source: app/core/config.py — existing Settings class pattern
class Settings(BaseSettings):
    # ... existing fields ...
    frontend_url: str = "http://localhost:3000"
    # ... rest of fields ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| smtplib (sync blocking) | aiosmtplib (async) | Python 3.5+ / async ecosystem | Non-blocking email; works with FastAPI BackgroundTasks |
| passlib for bcrypt | direct bcrypt + security.py | Phase 2 decision | passlib 1.7.4 + bcrypt 5.0.0 broken; already resolved |

**Deprecated/outdated:**
- `app/api/v1/interest.py` stub: current stub has unrelated `STATE` dict and wrong route paths (`/status`, `/submit`). This file must be fully replaced with correct routes (`POST /` and `GET /`).
- `app/api/v1/admin/users.py` stub: current stub has placeholder route bodies. All three routes need real implementations, plus two new routes (`/deactivate`, `/reactivate`).

## Open Questions

1. **Rush upsert vs. error if empty**
   - What we know: Claude's discretion; CONTEXT.md leaves this to implementation
   - What's unclear: Should `GET /v1/rush` 404 or return `{"status": "coming_soon"}` when table is empty?
   - Recommendation: Return `{"status": "coming_soon"}` when table is empty (treat no-row same as `is_published=False`). This avoids a 404 on a valid public endpoint and makes the behavior predictable.

2. **interest.py stub path mismatch**
   - What we know: Current stub has `/status` and `/submit` paths; requirements need `POST /` and `GET /`
   - What's unclear: Whether existing routes break any tests (test_interest.py is empty)
   - Recommendation: Replace stub entirely. `test_interest.py` is empty so no existing tests break.

3. **aiosmtplib start_tls vs use_tls**
   - What we know: Port 587 uses STARTTLS; port 465 uses TLS-from-start
   - What's unclear: Which SMTP provider will be used in production
   - Recommendation: Default to `start_tls=True` for port 587 (most common for Gmail, SendGrid, etc.). Make it configurable via `smtp_use_tls: bool = False` in Settings if needed, but `start_tls=True` is the right default.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["app/tests"]`) |
| Quick run command | `uv run python -m pytest app/tests/test_members.py app/tests/test_interest.py app/tests/test_rush.py app/tests/test_content.py -x` |
| Full suite command | `uv run python -m pytest app/tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MEMB-01 | GET /v1/admin/members returns member list with filter | integration | `uv run python -m pytest app/tests/test_members.py::test_list_members -x` | Wave 0 |
| MEMB-02 | POST /v1/admin/members creates user, 201, email queued | integration | `uv run python -m pytest app/tests/test_members.py::test_create_member -x` | Wave 0 |
| MEMB-03 | PATCH /v1/admin/members/{id}/role updates role, writes audit | integration | `uv run python -m pytest app/tests/test_members.py::test_update_role -x` | Wave 0 |
| MEMB-04 | PATCH /v1/admin/members/{id}/deactivate sets is_active=False, revokes tokens | integration | `uv run python -m pytest app/tests/test_members.py::test_deactivate_member -x` | Wave 0 |
| MEMB-05 | PATCH /v1/admin/members/{id}/reactivate sets is_active=True | integration | `uv run python -m pytest app/tests/test_members.py::test_reactivate_member -x` | Wave 0 |
| INTR-01 | POST /v1/interest accepts form, 409 on duplicate email | integration | `uv run python -m pytest app/tests/test_interest.py::test_submit_interest -x` | Wave 0 |
| INTR-02 | GET /v1/interest returns all submissions (admin only) | integration | `uv run python -m pytest app/tests/test_interest.py::test_list_interest -x` | Wave 0 |
| RUSH-01 | GET /v1/rush returns full data or coming_soon | integration | `uv run python -m pytest app/tests/test_rush.py::test_get_rush -x` | Wave 0 |
| RUSH-02 | PUT /v1/rush updates rush info (admin only) | integration | `uv run python -m pytest app/tests/test_rush.py::test_update_rush -x` | Wave 0 |
| RUSH-03 | PATCH /v1/rush/visibility toggles is_published | integration | `uv run python -m pytest app/tests/test_rush.py::test_toggle_visibility -x` | Wave 0 |
| CONT-01 | GET /v1/content/history returns content | integration | `uv run python -m pytest app/tests/test_content.py::test_get_history -x` | Wave 0 |
| CONT-02 | GET /v1/content/philanthropy returns content | integration | `uv run python -m pytest app/tests/test_content.py::test_get_philanthropy -x` | Wave 0 |
| CONT-03 | GET /v1/content/contacts returns content | integration | `uv run python -m pytest app/tests/test_content.py::test_get_contacts -x` | Wave 0 |
| CONT-04 | GET /v1/content/leadership returns active officers only | integration | `uv run python -m pytest app/tests/test_content.py::test_get_leadership -x` | Wave 0 |
| CONT-05 | PUT /v1/content/{section} upserts content (admin only) | integration | `uv run python -m pytest app/tests/test_content.py::test_update_content -x` | Wave 0 |
| XCUT-04 | Email send does not block HTTP response | unit | `uv run python -m pytest app/tests/test_email.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `uv run python -m pytest app/tests/ -x -q`
- **Per wave merge:** `uv run python -m pytest app/tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `app/tests/test_members.py` — covers MEMB-01 through MEMB-05
- [ ] `app/tests/test_interest.py` — currently empty (file exists); covers INTR-01, INTR-02
- [ ] `app/tests/test_rush.py` — covers RUSH-01, RUSH-02, RUSH-03
- [ ] `app/tests/test_content.py` — covers CONT-01 through CONT-05
- [ ] `app/tests/test_email.py` — covers XCUT-04 (mock SMTP, verify BackgroundTasks.add_task called)
- Note: `conftest.py` already has `auth_client` fixture with admin user seeded — reuse for all admin endpoint tests

**conftest.py extension needed:** Add `member_token` and `admin_token` helper fixtures (or inline login in each test) so test functions can hit admin-only routes without repeating login boilerplate.

## Sources

### Primary (HIGH confidence)
- Verified by running `uv run python -c "import aiosmtplib; help(aiosmtplib.send)"` against installed aiosmtplib 5.1.0
- Verified by reading all existing source files directly (models, services, routers, conftest)
- Verified by running `uv run python -m pytest app/tests/ -v` — all 25 tests pass

### Secondary (MEDIUM confidence)
- FastAPI BackgroundTasks behavior with async callables — verified by reading FastAPI source signature (`BackgroundTasks.add_task` accepts `Callable[P, Any]`)
- SQLite compatibility with `postgresql.UUID` type — verified empirically (existing tests run with SQLite)

### Tertiary (LOW confidence)
- aiosmtplib `start_tls=True` being the correct default for port 587 — standard SMTP convention, not verified against a live SMTP server

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all libraries already installed; verified with import checks
- Architecture patterns: HIGH — derived directly from existing Phase 2 code that already works
- Pitfalls: HIGH — derived from code reading and empirical test runs; aiosmtplib async pitfall is HIGH based on aiosmtplib API inspection
- Test map: HIGH — pytest infrastructure verified working; test files correctly identified as missing

**Research date:** 2026-03-04
**Valid until:** 2026-06-04 (stable ecosystem; aiosmtplib API unlikely to change at patch level)
