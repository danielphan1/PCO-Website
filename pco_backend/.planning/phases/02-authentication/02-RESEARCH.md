# Phase 2: Authentication - Research

**Researched:** 2026-03-04
**Domain:** FastAPI + PyJWT + bcrypt — JWT authentication, refresh token rotation, RBAC dependencies
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Refresh token strategy:** Rotate on every refresh — `POST /api/auth/refresh` issues a new refresh token and revokes the old one. Replay of a revoked token returns 401 silently — no escalation, no mass-revocation. Old token marked `revoked=True`; new row inserted before responding.
- **Token response shape:** Login and refresh both return `{ access_token, refresh_token, token_type: "bearer" }`. No user info in login response — frontend calls `GET /api/users/me` separately.
- **Error messages:**
  - Bad credentials (wrong email OR password): `"Invalid email or password"` (prevents email enumeration)
  - Deactivated user at login or refresh: `"Account is deactivated"` with **403** status
  - Bad/expired/missing access token: **401** status
  - Non-admin on admin route: **403** status
- **HTTP status codes:** 401 for auth failures, 403 for deactivated or insufficient role, 422 for validation
- **Token cleanup:** No cleanup in Phase 2 — expired/revoked tokens accumulate in DB; scheduled cleanup deferred to v2
- **Refresh token storage:** Stored as a hash (raw token returned to client, hash stored in DB)
- **DB write order on refresh:** Insert new row first, then mark old row revoked, then return — no partial state if DB fails

### Claude's Discretion
- JWT payload fields (`sub`, `role`, `exp`, `iat` — standard claims)
- Exact bcrypt cost factor (default is fine, see critical note below)
- Whether `get_current_user` validates `is_active` inline or delegates to separate check
- Access token expiry: use `access_token_expire_minutes` from Settings (60 min)
- Refresh token expiry: use `refresh_token_expire_days` from Settings (30 days)

### Deferred Ideas (OUT OF SCOPE)
- Refresh token cleanup / expiry purge — scheduled cleanup is a v2 concern
- Explicit logout endpoint — v2 requirement (AUTH-V2-02)
- User-initiated password change — v2 requirement (AUTH-V2-01)
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AUTH-01 | User logs in via POST /api/auth/login — returns JWT access token + refresh token (stored in DB) | PyJWT encode, passlib/bcrypt hash verify, RefreshToken model ready |
| AUTH-02 | User refreshes via POST /api/auth/refresh — exchange valid DB-stored refresh token for new access token | Token rotation pattern, SHA-256 hash lookup, revocation logic |
| AUTH-03 | Authenticated user views own profile via GET /api/users/me | OAuth2PasswordBearer + get_current_user dependency, new users.py router needed |
| AUTH-04 | `get_current_user` dependency validates bearer token on all protected routes | FastAPI Depends + JWT decode + InvalidTokenError handling pattern |
| AUTH-05 | `require_admin` dependency enforces admin role on all /api/admin/* routes | Role check against User.role, 403 on insufficient role |
| AUTH-06 | Deactivated users rejected at login and token refresh | is_active check in both endpoints, 403 "Account is deactivated" |
| AUTH-07 | Passwords hashed with bcrypt via passlib before storage | CRITICAL: passlib 1.7.4 is broken with bcrypt 5.0.0 — must use bcrypt directly |
</phase_requirements>

---

## Summary

Phase 2 implements JWT-based authentication on top of Phase 1's foundation. The stack (FastAPI, PyJWT, bcrypt) is well-established, and the ORM models (`User`, `RefreshToken`) are already complete in the codebase. The implementation pattern is: fill `app/core/security.py` with JWT and password utilities, add `get_current_user` and `require_admin` to `app/core/deps.py`, replace the auth router stub, create the `app/api/v1/users.py` router for `/me`, and register it in `app/api/router.py`.

**Critical discovery:** The lockfile pins `passlib==1.7.4` alongside `bcrypt==5.0.0`. These two are fundamentally incompatible — bcrypt 5.0.0 removed the `__about__` attribute that passlib relies on for backend detection, causing `CryptContext.hash()` and `CryptContext.verify()` to raise `ValueError: password cannot be longer than 72 bytes` even for short passwords. The project must use **bcrypt directly** (not via passlib) for `hash_password` and `verify_password`. The `passlib[bcrypt]` dependency in `pyproject.toml` should be replaced with `bcrypt>=4.0,<6`.

The refresh token strategy is: generate a cryptographically secure random token with `secrets.token_urlsafe(32)`, store its SHA-256 hex digest in the DB, return the raw token to the client. On refresh: compute the digest of the incoming raw token, look up the row, check not-revoked and not-expired, insert new row, mark old row revoked, return new tokens.

**Primary recommendation:** Use bcrypt directly (not passlib), PyJWT directly for JWT operations, and `OAuth2PasswordBearer` for the dependency injection pattern. All other patterns are standard FastAPI.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyJWT | >=2.8 (locked) | JWT encode/decode, HS256 | Already installed; replaces python-jose for CVE reasons (INFRA-01 complete) |
| bcrypt | 5.0.0 (locked) | bcrypt password hashing | Already installed; used directly (NOT via passlib — see critical note) |
| FastAPI security | via fastapi>=0.115 | OAuth2PasswordBearer, HTTPException | Built-in; standard pattern for Bearer token extraction |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| secrets | stdlib | Cryptographically secure token generation | Generating raw refresh token values |
| hashlib | stdlib | SHA-256 digest for token storage | Hashing refresh tokens before DB storage |
| datetime / timezone | stdlib | Token expiry calculation | Creating `exp` claims and `expires_at` columns |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `bcrypt` directly | `pwdlib[argon2]` | pwdlib is the new FastAPI-recommended approach, but requires adding a dependency; bcrypt is already locked and works fine used directly |
| `secrets.token_urlsafe(32)` | `uuid4()` | UUID4 is not designed for secret tokens; `secrets` module is the stdlib recommendation for security tokens |
| SHA-256 for refresh token hash | bcrypt for refresh token hash | SHA-256 is fast (appropriate for random tokens — no brute-force risk), bcrypt is slow (appropriate for passwords); use SHA-256 for token lookup |

**CRITICAL — Do NOT use passlib:**
```bash
# Remove from pyproject.toml:
# "passlib[bcrypt]>=1.7",

# Add:
# "bcrypt>=4.0",
```

The lockfile has `passlib==1.7.4` + `bcrypt==5.0.0` — this combination is completely broken. `bcrypt 5.0.0` removed `__about__`, causing passlib's backend detection to raise `ValueError: password cannot be longer than 72 bytes` on every hash/verify call regardless of actual password length.

---

## Architecture Patterns

### Recommended Project Structure

```
app/
├── core/
│   ├── security.py      # Fill: create_access_token, decode_access_token,
│   │                    #        hash_password, verify_password
│   ├── deps.py          # Add: get_current_user, require_admin
│   └── config.py        # Already complete — jwt_secret, jwt_alg, expire settings
├── api/v1/
│   ├── auth.py          # Replace stub: login + refresh endpoints
│   └── users.py         # New file: GET /users/me endpoint
├── schemas/
│   └── auth.py          # Fill: LoginRequest, TokenResponse, RefreshRequest
└── models/
    ├── user.py           # Complete — no changes needed
    └── refresh_token.py  # Complete — no changes needed
```

### Pattern 1: security.py Utilities

**What:** Pure functions for JWT and password operations. No DB access, no FastAPI types.
**When to use:** Always import from here into routes and deps — never inline jwt/bcrypt calls.

```python
# Source: https://pyjwt.readthedocs.io/en/latest/usage.html
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError  # noqa: F401 — re-export for deps.py

from app.core.config import settings


# --- JWT ---

def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload = {
        "sub": subject,       # user UUID as string
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_alg)


def decode_access_token(token: str) -> dict:
    """Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError on failure."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])


# --- Passwords (bcrypt direct — NOT via passlib) ---

def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# --- Refresh tokens ---

def generate_refresh_token() -> str:
    """Return a URL-safe random token (raw value, returned to client)."""
    return secrets.token_urlsafe(32)


def hash_refresh_token(raw_token: str) -> str:
    """SHA-256 digest stored in DB. Fast lookup; brute-force not a risk for random tokens."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
```

### Pattern 2: get_current_user and require_admin Dependencies

**What:** FastAPI Depends callables that extract and validate the Bearer token, then load the User from DB.
**When to use:** Inject via `Depends` into any protected route.

```python
# Source: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise _credentials_exception
    except jwt.InvalidTokenError:
        raise _credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise _credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    return user


def require_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user
```

### Pattern 3: Login Endpoint

**What:** Validate credentials, create tokens, store refresh token hash in DB.
**When to use:** POST /v1/auth/login

```python
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.security import (
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    create_access_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()

    # Always run verify to prevent timing attacks; use dummy hash if user not found
    _DUMMY_HASH = hash_password("dummy-timing-padding")
    stored_hash = user.hashed_password if user else _DUMMY_HASH
    password_ok = verify_password(payload.password, stored_hash)

    if not user or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    raw_token = generate_refresh_token()
    token_hash = hash_refresh_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

    db_token = RefreshToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(db_token)
    db.commit()

    access_token = create_access_token(subject=str(user.id), role=user.role)
    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_token,
        token_type="bearer",
    )
```

### Pattern 4: Refresh Endpoint (Token Rotation)

**What:** Exchange a valid refresh token for new access + refresh tokens, revoke the old one.
**DB write order:** Insert new row first, then mark old revoked — client keeps old token if any DB error occurs.

```python
@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token_hash = hash_refresh_token(payload.refresh_token)
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()

    now = datetime.now(timezone.utc)

    if (
        db_token is None
        or db_token.revoked
        or db_token.expires_at.replace(tzinfo=timezone.utc) < now
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = db_token.user  # relationship already loaded or lazy-loaded
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    # Insert new token row BEFORE revoking old one
    new_raw = generate_refresh_token()
    new_hash = hash_refresh_token(new_raw)
    new_expires = now + timedelta(days=settings.refresh_token_expire_days)
    new_db_token = RefreshToken(user_id=user.id, token_hash=new_hash, expires_at=new_expires)
    db.add(new_db_token)

    # Revoke old token
    db_token.revoked = True
    db.commit()

    access_token = create_access_token(subject=str(user.id), role=user.role)
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_raw,
        token_type="bearer",
    )
```

### Anti-Patterns to Avoid

- **Using passlib CryptContext with bcrypt:** `passlib 1.7.4` + `bcrypt 5.0.0` raises `ValueError: password cannot be longer than 72 bytes` on every call. Use `bcrypt.hashpw` / `bcrypt.checkpw` directly.
- **Checking user existence before password verification:** Always compute `verify_password()` even if user is not found (timing attack). Use a precomputed dummy hash.
- **Returning 401 for deactivated users:** User decisions specify 403 for deactivated accounts — do not return 401 for that case.
- **Returning 401 for non-admin on admin route:** User decisions specify 403 for insufficient role.
- **Storing raw refresh token in DB:** Always store the SHA-256 hex digest; return raw token to client.
- **Embedding user info in login response:** The locked decision is minimal token-only response; frontend calls `/me` separately.
- **Registering `users` router before adding the file:** `app/api/router.py` must import from `app.api.v1.users` — that module does not yet exist.
- **Using `async def` for route handlers or dependencies:** Project is sync-only (sync SQLAlchemy, sync def). Using `async def` with sync DB calls blocks the event loop.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Bearer token extraction from Authorization header | Manual header parsing | `OAuth2PasswordBearer` from `fastapi.security` | Handles missing token → 401, Swagger UI integration, standard format |
| JWT signature verification | Manual HMAC | `jwt.decode()` from PyJWT | Handles `exp`, `iat`, signature, algorithm pinning — many edge cases |
| Cryptographically secure random bytes | `random.random()` | `secrets.token_urlsafe()` | `random` is not CSPRNG; `secrets` uses OS entropy source |
| Constant-time hash comparison | `==` string comparison | `bcrypt.checkpw()` | bcrypt comparison is constant-time by design |
| bcrypt salt generation | Manual salt string | `bcrypt.gensalt()` | Handles rounds, prefix format (2b), OS entropy |

**Key insight:** JWT and bcrypt each contain subtle timing and encoding pitfalls. PyJWT and bcrypt's native functions handle the entirety of the safe path; any custom reimplementation introduces risk.

---

## Common Pitfalls

### Pitfall 1: passlib + bcrypt 5.0.0 Breakage (CONFIRMED IN THIS PROJECT)

**What goes wrong:** `CryptContext(schemes=["bcrypt"]).hash("any string")` raises `ValueError: password cannot be longer than 72 bytes` even for short strings like "hello". The error is misleading — it is caused by passlib's backend detection failing, not actual password length.

**Why it happens:** bcrypt 5.0.0 removed `bcrypt.__about__` (the version attribute). passlib 1.7.4 checks this attribute during backend initialization. The detection failure corrupts passlib's internal bcrypt handler state, causing every subsequent hash/verify call to fail.

**How to avoid:** Do not use `passlib`. Use `bcrypt.hashpw()` and `bcrypt.checkpw()` directly. Update `pyproject.toml` to remove `passlib[bcrypt]` and add `bcrypt>=4.0` (bcrypt is already in the lockfile as a transitive dep; making it direct is cleaner).

**Warning signs:** `(trapped) error reading bcrypt version` warning in logs; `ValueError: password cannot be longer than 72 bytes` on passwords shorter than 72 bytes.

### Pitfall 2: Timezone-Naive Datetime Comparison for Token Expiry

**What goes wrong:** `RefreshToken.expires_at` is stored as `DateTime(timezone=True)` (timezone-aware). Comparing it against `datetime.utcnow()` (timezone-naive) raises `TypeError: can't compare offset-naive and offset-aware datetimes`.

**Why it happens:** SQLAlchemy returns timezone-aware datetimes from `DateTime(timezone=True)` columns when using PostgreSQL.

**How to avoid:** Always use `datetime.now(timezone.utc)` (not `datetime.utcnow()`) for comparisons. When comparing, ensure both sides are timezone-aware: `db_token.expires_at.replace(tzinfo=timezone.utc)` if the returned value is naive, or simply use `datetime.now(timezone.utc)` directly.

### Pitfall 3: OAuth2PasswordBearer tokenUrl Must Match Actual Route

**What goes wrong:** Swagger UI "Authorize" button sends login request to the wrong URL, breaking interactive docs.

**Why it happens:** `OAuth2PasswordBearer(tokenUrl="token")` defaults assume a root-level `/token` endpoint. This project uses `/v1/auth/login`.

**How to avoid:** `OAuth2PasswordBearer(tokenUrl="/v1/auth/login")`. Note that `OAuth2PasswordBearer` also implies form-encoded request body (username/password fields) for Swagger compatibility. Since this project uses JSON body (`LoginRequest` schema), the `tokenUrl` is only used for Swagger UI documentation linking — the actual token extraction from Bearer headers still works with JSON login.

### Pitfall 4: JWT `sub` Claim Type Mismatch (UUID vs str)

**What goes wrong:** `jwt.encode({"sub": user.id, ...})` where `user.id` is a `uuid.UUID` object fails or produces non-string sub claim. `jwt.decode()` returns `sub` as string; subsequent `db.query(User).filter(User.id == payload["sub"])` fails with type mismatch.

**Why it happens:** PyJWT expects JSON-serializable values. `uuid.UUID` is not JSON-serializable by default. SQLAlchemy `UUID` column accepts both `uuid.UUID` objects and strings.

**How to avoid:** Always convert: `"sub": str(user.id)` in `create_access_token`. On decode, pass the string directly to the UUID-typed filter — SQLAlchemy handles the cast.

### Pitfall 5: Refresh Token Expiry Comparison with UTC

**What goes wrong:** `db_token.expires_at < datetime.now()` — if the stored datetime is UTC but `datetime.now()` returns local time, the comparison may be wrong by hours.

**Why it happens:** `datetime.now()` returns local system time without timezone info.

**How to avoid:** Consistently use `datetime.now(timezone.utc)` everywhere, and store `expires_at` as UTC.

### Pitfall 6: Missing `users.py` Router in `router.py`

**What goes wrong:** `GET /v1/users/me` returns 404 because the router is never registered.

**Why it happens:** The context notes `app/api/v1/users.py` does not yet exist and is not in `router.py`.

**How to avoid:** Create `app/api/v1/users.py`, then add `from app.api.v1 import users` and `router.include_router(users.router, prefix="/v1/users", tags=["users"])` to `app/api/router.py`.

---

## Code Examples

Verified patterns from official sources:

### PyJWT Encode/Decode (HS256)

```python
# Source: https://pyjwt.readthedocs.io/en/latest/usage.html
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone

payload = {
    "sub": "user-uuid-string",
    "role": "admin",
    "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
    "iat": datetime.now(timezone.utc),
}

# Encode
token = jwt.encode(payload, "secret-at-least-32-chars", algorithm="HS256")
# Returns: str (PyJWT >= 2.0 returns str, not bytes)

# Decode
try:
    decoded = jwt.decode(token, "secret-at-least-32-chars", algorithms=["HS256"])
    # decoded["sub"], decoded["role"] are accessible
except ExpiredSignatureError:
    # Token expired — raise 401
    ...
except InvalidTokenError:
    # Any other JWT error — raise 401
    ...
```

### bcrypt Direct Usage (NOT passlib)

```python
# Source: https://pypi.org/project/bcrypt/ (bcrypt 5.0.0)
import bcrypt

# Hash (registration / password set)
hashed_bytes = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
hashed_str = hashed_bytes.decode("utf-8")  # store in DB as varchar

# Verify
is_valid = bcrypt.checkpw(
    plain_password.encode("utf-8"),
    stored_hash.encode("utf-8"),  # retrieve from DB, encode back to bytes
)
```

### Secure Refresh Token Generation and Storage

```python
# stdlib only — no extra dependencies
import hashlib
import secrets

# Generate raw token (returned to client)
raw_token = secrets.token_urlsafe(32)  # ~43 URL-safe chars, 256 bits entropy

# Hash for DB storage (fast lookup; brute-force not a concern for random tokens)
token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

# Lookup on refresh endpoint
incoming_hash = hashlib.sha256(incoming_raw.encode("utf-8")).hexdigest()
db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == incoming_hash).first()
```

### OAuth2PasswordBearer + Sync get_current_user

```python
# Source: https://fastapi.tiangolo.com/tutorial/security/get-current-user/
# Adapted for sync SQLAlchemy pattern used in this project
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    # sync def — runs in FastAPI thread pool (correct for sync SQLAlchemy)
    ...
```

### Schemas (Pydantic v2 pattern matching project convention)

```python
# app/schemas/auth.py
from pydantic import BaseModel, EmailStr, model_config


class LoginRequest(BaseModel):
    email: str       # plain str is fine; EmailStr adds email_validator dep
    password: str

    model_config = model_config = {"str_strip_whitespace": True}


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| python-jose for JWT | PyJWT | Phase 1 (complete) | CVE eliminated; already done |
| passlib[bcrypt] for password hashing | bcrypt directly | bcrypt 5.0.0 (Sep 2025) | Must use bcrypt.hashpw/checkpw directly |
| `datetime.utcnow()` | `datetime.now(timezone.utc)` | Python 3.12 deprecation | utcnow() deprecated; use timezone-aware now() |
| FastAPI docs recommend passlib | FastAPI docs now recommend pwdlib | 2024–2025 | Passlib abandoned; either bcrypt direct or pwdlib |

**Deprecated/outdated:**
- `python-jose`: Removed in Phase 1 due to CVE (alg:none bypass). Do not use.
- `passlib.context.CryptContext` with bcrypt scheme: Incompatible with bcrypt 5.0.0. Do not use.
- `datetime.utcnow()`: Deprecated in Python 3.12. Use `datetime.now(timezone.utc)`.

---

## Open Questions

1. **passlib removal from pyproject.toml**
   - What we know: `passlib[bcrypt]>=1.7` is in `pyproject.toml`; `passlib 1.7.4` + `bcrypt 5.0.0` is broken
   - What's unclear: Whether any other code in the project currently imports passlib
   - Recommendation: Phase 2 Plan 02-01 should remove the passlib dep and add `bcrypt>=4.0` as a direct dep; grep the codebase first to confirm no other passlib usage

2. **`EmailStr` vs plain `str` for login email field**
   - What we know: `EmailStr` requires `email-validator` package (not currently in pyproject.toml)
   - What's unclear: Whether strict email format validation is desired at the schema level
   - Recommendation: Use plain `str` in `LoginRequest` — wrong email format already returns "Invalid email or password" which is the desired behavior

3. **`_DUMMY_HASH` timing attack prevention**
   - What we know: A precomputed dummy hash is needed to prevent timing attacks on the "user not found" branch
   - What's unclear: Whether a module-level constant (computed once at import time) or a local computation per request is cleaner
   - Recommendation: Compute once at module level as a constant to avoid any overhead; bcrypt.gensalt() is slow, so pre-hashing "dummy" once is the right approach

---

## Validation Architecture

> `nyquist_validation: true` in `.planning/config.json` — this section is required.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `pyproject.toml` → `[tool.pytest.ini_options]` → `testpaths = ["app/tests"]` |
| Quick run command | `uv run pytest app/tests/test_auth.py -x -q` |
| Full suite command | `uv run pytest app/tests/ -x -q` |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTH-01 | POST /v1/auth/login with valid creds returns access_token + refresh_token | integration | `uv run pytest app/tests/test_auth.py::test_login_success -x` | Wave 0 |
| AUTH-01 | POST /v1/auth/login with wrong password returns 401 | integration | `uv run pytest app/tests/test_auth.py::test_login_wrong_password -x` | Wave 0 |
| AUTH-01 | POST /v1/auth/login with wrong email returns 401 (same message) | integration | `uv run pytest app/tests/test_auth.py::test_login_wrong_email -x` | Wave 0 |
| AUTH-02 | POST /v1/auth/refresh with valid token returns new tokens, old token revoked | integration | `uv run pytest app/tests/test_auth.py::test_refresh_success -x` | Wave 0 |
| AUTH-02 | POST /v1/auth/refresh with expired token returns 401 | integration | `uv run pytest app/tests/test_auth.py::test_refresh_expired -x` | Wave 0 |
| AUTH-02 | POST /v1/auth/refresh with revoked token returns 401 | integration | `uv run pytest app/tests/test_auth.py::test_refresh_revoked -x` | Wave 0 |
| AUTH-03 | GET /v1/users/me with valid token returns user profile | integration | `uv run pytest app/tests/test_auth.py::test_users_me_authenticated -x` | Wave 0 |
| AUTH-03 | GET /v1/users/me without token returns 401 | integration | `uv run pytest app/tests/test_auth.py::test_users_me_unauthenticated -x` | Wave 0 |
| AUTH-04 | Protected route with missing bearer token returns 401 | integration | `uv run pytest app/tests/test_auth.py::test_get_current_user_no_token -x` | Wave 0 |
| AUTH-04 | Protected route with expired access token returns 401 | integration | `uv run pytest app/tests/test_auth.py::test_get_current_user_expired_token -x` | Wave 0 |
| AUTH-05 | Admin route with non-admin user returns 403 | integration | `uv run pytest app/tests/test_auth.py::test_require_admin_non_admin -x` | Wave 0 |
| AUTH-05 | Admin route with admin user succeeds (2xx) | integration | `uv run pytest app/tests/test_auth.py::test_require_admin_admin_user -x` | Wave 0 |
| AUTH-06 | Deactivated user login attempt returns 403 | integration | `uv run pytest app/tests/test_auth.py::test_login_deactivated_user -x` | Wave 0 |
| AUTH-06 | Deactivated user refresh token exchange returns 403 | integration | `uv run pytest app/tests/test_auth.py::test_refresh_deactivated_user -x` | Wave 0 |
| AUTH-07 | hash_password returns bcrypt-formatted string | unit | `uv run pytest app/tests/test_auth.py::test_hash_password -x` | Wave 0 |
| AUTH-07 | verify_password confirms correct password | unit | `uv run pytest app/tests/test_auth.py::test_verify_password -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `uv run pytest app/tests/test_auth.py -x -q`
- **Per wave merge:** `uv run pytest app/tests/ -x -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

`app/tests/test_auth.py` currently exists but is empty (1 line). It needs all 16 test stubs above created before implementation begins.

The `conftest.py` uses a real `TestClient` against `app.main.app`. For auth tests this requires a seeded in-memory or test DB, or dependency overrides. Key gap: **test database fixture** — the current `conftest.py` uses the real `SessionLocal` which connects to the `.env` database. Tests need either:
- A DB override via `app.dependency_overrides[get_db] = lambda: test_db_session`, OR
- A separate test database configured via `TEST_DATABASE_URL` env var

- [ ] `app/tests/test_auth.py` — all 16 test cases (AUTH-01 through AUTH-07)
- [ ] `app/tests/conftest.py` — add DB override fixture or test DB session fixture for auth tests that need real user/token data

*(If running against a real PostgreSQL, a test user must be seeded in a fixture before auth tests run.)*

---

## Sources

### Primary (HIGH confidence)

- [PyJWT 2.11.0 Usage Docs](https://pyjwt.readthedocs.io/en/latest/usage.html) — encode/decode patterns, exception types, algorithm parameter
- [FastAPI Security: OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) — OAuth2PasswordBearer, get_current_user, dependency injection pattern
- [bcrypt 5.0.0 PyPI](https://pypi.org/project/bcrypt/) — hashpw, checkpw, gensalt API
- [Python secrets module docs](https://docs.python.org/3/library/secrets.html) — token_urlsafe for CSPRNG token generation
- [Python hashlib docs](https://docs.python.org/3/library/hashlib.html) — sha256.hexdigest for token hashing

### Secondary (MEDIUM confidence)

- [bcrypt issue #1079: Passlib 1.7.4 + bcrypt 5.0.0 broken](https://github.com/pyca/bcrypt/issues/1079) — confirmed by uv.lock inspection (passlib 1.7.4, bcrypt 5.0.0)
- [FastAPI discussion #11773: passlib unmaintained](https://github.com/fastapi/fastapi/discussions/11773) — community confirmation of passlib maintenance status

### Tertiary (LOW confidence, flagged)

- WebSearch results on refresh token rotation patterns — consistent with decision in CONTEXT.md but not from a single authoritative source

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — PyJWT and bcrypt APIs verified against official docs; passlib breakage confirmed in uv.lock
- Architecture: HIGH — FastAPI patterns verified against official docs; project conventions observed from Phase 1 code
- Pitfalls: HIGH for passlib/bcrypt issue (directly confirmed in lockfile); MEDIUM for others (well-documented FastAPI patterns)

**Research date:** 2026-03-04
**Valid until:** 2026-06-04 (90 days — PyJWT and FastAPI APIs are stable; bcrypt/passlib situation is settled)
