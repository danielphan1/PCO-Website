---
phase: 02-authentication
plan: "01"
subsystem: auth
tags: [jwt, bcrypt, pyjwt, fastapi, sqlalchemy, sqlite, pytest]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: PyJWT installed, SQLAlchemy models (User, RefreshToken), config with jwt_secret, get_db dependency
provides:
  - bcrypt direct dependency replacing passlib
  - app/core/security.py with 6 utility functions (hash_password, verify_password, create_access_token, decode_access_token, generate_refresh_token, hash_refresh_token)
  - app/schemas/auth.py with LoginRequest, RefreshRequest, TokenResponse Pydantic v2 schemas
  - app/api/v1/auth.py with POST /v1/auth/login and POST /v1/auth/refresh endpoints
  - app/tests/conftest.py with db_session and auth_client fixtures using SQLite test DB
  - app/tests/test_auth.py with 16 test stubs (10 passing, 6 remaining stubs for Plan 02-02)
affects: [02-02, 02-03, 02-04, get_current_user, require_admin, users-me]

# Tech tracking
tech-stack:
  added: [bcrypt>=4.0 (direct, replaces passlib[bcrypt]>=1.7)]
  patterns:
    - bcrypt.hashpw/checkpw direct usage (NOT passlib — passlib 1.7.4 + bcrypt 5.0.0 broken)
    - _DUMMY_HASH + _dummy_verify() pattern for timing-attack prevention on login
    - Refresh token rotation — insert new row BEFORE revoking old, single db.commit()
    - SHA-256 hex digest for refresh token storage (not bcrypt — 256-bit token entropy makes brute-force infeasible)
    - SQLite test DB with all ORM models imported for relationship resolution

key-files:
  created:
    - app/schemas/auth.py
    - app/tests/test_auth.py
  modified:
    - app/core/security.py
    - app/api/v1/auth.py
    - app/tests/conftest.py
    - pyproject.toml
    - uv.lock

key-decisions:
  - "bcrypt direct dependency replaces passlib — passlib 1.7.4 + bcrypt 5.0.0 is broken upstream"
  - "_dummy_verify() runs bcrypt.checkpw (not just hash comparison) on user-not-found path to prevent timing-based user enumeration"
  - "DB write order on refresh: insert new token row first, revoke old token second, then single commit — client retains old token if DB fails mid-way"
  - "SQLite test DB with explicit import of all ORM models (AuditLog, EventPDF, InterestSubmission, OrgContent, RushInfo) required for Base.metadata.create_all to resolve string relationships"
  - "SHA-256 for refresh token hashing (not bcrypt) — tokens have 256 bits of entropy, brute-force pre-image is infeasible"

patterns-established:
  - "Login pattern: query user → dummy_verify if not found → verify_password → check is_active → generate tokens → persist RefreshToken → return TokenResponse"
  - "Refresh pattern: hash lookup → check revoked → check expiry → check is_active → insert new → revoke old → commit → return new tokens"
  - "Test DB pattern: import all models before Base.metadata.create_all to avoid string relationship resolution errors with SQLite"

requirements-completed: [AUTH-01, AUTH-02, AUTH-06, AUTH-07]

# Metrics
duration: 6min
completed: 2026-03-04
---

# Phase 2 Plan 01: Security Utilities and Auth Endpoints Summary

**bcrypt-direct login/refresh endpoints with timing-safe user enumeration prevention and refresh token rotation backed by SQLite test fixtures**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-04T10:16:58Z
- **Completed:** 2026-03-04T10:22:23Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- Replaced passlib with direct bcrypt dependency; implemented all 6 security utility functions
- Implemented POST /v1/auth/login with timing-safe user enumeration prevention (_dummy_verify)
- Implemented POST /v1/auth/refresh with safe token rotation (insert-new-before-revoke-old pattern)
- Created SQLite-backed test fixtures with seeded users; 10 of 16 auth tests now pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Test scaffold — conftest DB override + 16 test stubs** - `87abc31` (feat)
2. **Task 2: security.py — bcrypt swap + JWT and password utilities (GREEN)** - `1dc583c` (feat)
3. **Task 3: schemas/auth.py + implement login and refresh endpoints** - `864a879` (feat)

**Plan metadata:** (docs commit below)

_Note: Task 1 and Task 2 were partially combined because conftest.py imports hash_password at module load time, requiring security.py to be implemented before pytest collection succeeds._

## Files Created/Modified

- `app/core/security.py` - 6 utility functions: hash_password, verify_password, create_access_token, decode_access_token, generate_refresh_token, hash_refresh_token; _DUMMY_HASH + _dummy_verify for timing safety
- `app/schemas/auth.py` - LoginRequest, RefreshRequest, TokenResponse Pydantic v2 schemas
- `app/api/v1/auth.py` - POST /v1/auth/login and POST /v1/auth/refresh with full error handling
- `app/tests/conftest.py` - db_session (SQLite), auth_client (DB override + seeded users) fixtures; imports all ORM models
- `app/tests/test_auth.py` - 16 test stubs; 10 implemented and passing (AUTH-01, AUTH-02, AUTH-06, AUTH-07); 6 stubs for Plan 02-02
- `pyproject.toml` - replaced passlib[bcrypt]>=1.7 with bcrypt>=4.0
- `uv.lock` - updated lockfile (passlib removed)

## Decisions Made

- Used bcrypt directly instead of passlib because passlib 1.7.4 + bcrypt 5.0.0 has a known breaking compatibility issue
- Added `_dummy_verify()` function that runs actual `bcrypt.checkpw` (not just hash comparison) to ensure login timing is identical whether user exists or not
- Chose SHA-256 for refresh token storage hash (not bcrypt) because the raw token has 256-bit entropy — brute-force pre-image attacks are computationally infeasible
- Refresh token write order: insert new row first, commit together with revoke — if DB fails after insert but before revoke, client retains old working token

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added all ORM model imports to conftest.py**
- **Found during:** Task 1 (Test scaffold)
- **Issue:** `Base.metadata.create_all` triggered SQLAlchemy relationship resolution for User's `uploaded_events` (EventPDF) and `audit_logs` (AuditLog) relationships, which were string references not resolvable without those models imported
- **Fix:** Added imports for AuditLog, EventPDF, InterestSubmission, OrgContent, RushInfo alongside the existing User and RefreshToken imports
- **Files modified:** app/tests/conftest.py
- **Verification:** All 16 tests collected with no ImportError or relationship errors
- **Committed in:** `87abc31` (Task 1 commit)

**2. [Rule 1 - Bug] Fixed incorrect class name import (InterestForm → InterestSubmission)**
- **Found during:** Task 1 (Test scaffold)
- **Issue:** Initial conftest import used `InterestForm` but the actual class in interest_form.py is `InterestSubmission`
- **Fix:** Corrected import name to `InterestSubmission`
- **Files modified:** app/tests/conftest.py
- **Verification:** pytest collection succeeds without ImportError
- **Committed in:** `87abc31` (Task 1 commit)

**3. [Rule 3 - Blocking] Implemented security.py in Task 1 (not Task 2 as planned)**
- **Found during:** Task 1 (Test scaffold)
- **Issue:** conftest.py imports `hash_password` from `app.core.security` at module load time. Without security.py implemented, pytest collection fails with ImportError, making Task 1 unverifiable
- **Fix:** Implemented security.py as part of Task 1 execution; committed together with conftest.py
- **Files modified:** app/core/security.py, pyproject.toml, uv.lock
- **Verification:** pytest collection succeeds; 16 tests collected
- **Committed in:** `87abc31` (Task 1 commit)

---

**Total deviations:** 3 auto-fixed (1 blocking — model imports, 1 bug — class name, 1 blocking — task ordering)
**Impact on plan:** All auto-fixes necessary for test collection to succeed. No scope creep. Security.py implementation matches Task 2 spec exactly.

## Issues Encountered

- SQLite does not natively support `postgresql.UUID` columns, but SQLAlchemy's SQLite dialect treats unknown type names with TEXT affinity, so `create_all` succeeded without modification. The models' `UUID(as_uuid=True)` columns worked correctly in SQLite after Python-level UUID generation.

## User Setup Required

None - no external service configuration required. Tests use SQLite in-memory equivalent (`./test.db`).

## Next Phase Readiness

- `app/core/security.py` fully implemented — all 6 functions available for Plan 02-02
- `POST /v1/auth/login` and `POST /v1/auth/refresh` are production-ready with correct status codes and error messages
- 10 of 16 auth tests pass; 6 stubs (AUTH-03, AUTH-04, AUTH-05) are ready for Plan 02-02 implementation
- Test fixtures (auth_client, db_session) ready for Plan 02-02 test implementations

## Self-Check: PASSED

- FOUND: app/core/security.py
- FOUND: app/schemas/auth.py
- FOUND: app/api/v1/auth.py
- FOUND: app/tests/conftest.py
- FOUND: app/tests/test_auth.py
- FOUND: .planning/phases/02-authentication/02-01-SUMMARY.md
- FOUND commit: 87abc31 (Task 1)
- FOUND commit: 1dc583c (Task 2)
- FOUND commit: 864a879 (Task 3)
- FOUND commit: aa541d7 (docs/metadata)

---
*Phase: 02-authentication*
*Completed: 2026-03-04*
