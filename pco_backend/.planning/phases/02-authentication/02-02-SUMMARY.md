---
phase: 02-authentication
plan: "02"
subsystem: auth
tags: [fastapi, jwt, pyjwt, sqlalchemy, pydantic, rbac, oauth2]

# Dependency graph
requires:
  - phase: 02-authentication/02-01
    provides: security.py with create_access_token, decode_access_token, hash_password, verify_password, generate_refresh_token, hash_refresh_token; login and refresh endpoints

provides:
  - get_current_user FastAPI dependency — validates Bearer JWT, returns active User (401 on bad/expired token, 403 on deactivated account)
  - require_admin FastAPI dependency — gates admin-only routes, raises 403 for non-admin role
  - GET /v1/users/me endpoint — returns authenticated user profile (id, email, full_name, role, is_active)
  - UserResponse Pydantic schema
  - require_admin applied to all /v1/admin/users/* stub routes
  - All 16 auth tests passing (AUTH-01 through AUTH-07)

affects: [phase-03-content, phase-04-storage, any phase with protected routes]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "OAuth2PasswordBearer with tokenUrl=/v1/auth/login for Swagger UI compatibility"
    - "UUID string from JWT sub claim parsed to uuid.UUID before SQLAlchemy filter"
    - "Shared _credentials_exception singleton for 401 responses (avoids leaking reason)"
    - "require_admin chains via Depends(get_current_user) — admin gate always validates token first"

key-files:
  created:
    - app/core/deps.py (expanded — get_current_user and require_admin added)
    - app/api/v1/users.py
    - app/schemas/user.py
  modified:
    - app/api/router.py (users router registered at /v1/users)
    - app/api/v1/admin/users.py (require_admin applied to all stub routes)
    - app/tests/test_auth.py (6 stubs filled in for AUTH-03, AUTH-04, AUTH-05)

key-decisions:
  - "oauth2_scheme tokenUrl set to /v1/auth/login — matches actual login route, enables Swagger Authorize button"
  - "UUID str-to-uuid.UUID conversion in get_current_user — SQLAlchemy UUID(as_uuid=True) requires uuid.UUID object, not raw string from JWT sub claim"
  - "require_admin stub routes in admin/users.py use phase-3-stub bodies — Phase 3 replaces stubs with real DB queries"

patterns-established:
  - "Protected endpoint pattern: Annotated[User, Depends(get_current_user)] in function signature"
  - "Admin endpoint pattern: Annotated[User, Depends(require_admin)] in function signature"
  - "UserResponse.model_config = from_attributes=True for ORM model serialization"

requirements-completed: [AUTH-03, AUTH-04, AUTH-05]

# Metrics
duration: 4min
completed: 2026-03-04
---

# Phase 2 Plan 02: Authentication Dependencies and /users/me Summary

**FastAPI OAuth2 dependency layer with JWT validation, RBAC gating, and a /users/me endpoint — all 16 auth tests passing**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-04T10:25:15Z
- **Completed:** 2026-03-04T10:29:23Z
- **Tasks:** 2 of 2 automated (Task 3 is human-verify checkpoint)
- **Files modified:** 6

## Accomplishments

- get_current_user dependency in deps.py validates Bearer JWT via PyJWT, resolves the User from DB, raises 401 on bad/expired/missing token, raises 403 on deactivated account
- require_admin dependency chains off get_current_user and raises 403 with "Admin access required" for non-admin roles
- GET /v1/users/me endpoint returns authenticated user's id, email, full_name, role, is_active
- require_admin applied to all /v1/admin/users/* stub routes — Phase 3 will replace stub bodies
- All 16 auth tests pass: 10 from Plan 02-01 + 6 new stubs (AUTH-03, AUTH-04, AUTH-05)
- Full test suite green: 25 passed, 1 skipped

## Task Commits

Each task was committed atomically:

1. **Task 1: deps.py — add get_current_user and require_admin** - `c6b9415` (feat)
2. **Task 2: users.py endpoint + router.py wiring + complete all test stubs** - `c0d83b4` (feat)

_Note: TDD tasks — RED phase confirmed with pre-existing stub failures, GREEN phase reached on first implementation pass after UUID bug fix._

## Files Created/Modified

- `app/core/deps.py` — Expanded with OAuth2PasswordBearer, get_current_user, require_admin; preserved get_db unchanged
- `app/api/v1/users.py` — New file: GET /me endpoint using get_current_user dependency
- `app/schemas/user.py` — New file: UserResponse Pydantic schema with from_attributes=True
- `app/api/router.py` — Added users router import and include_router at /v1/users prefix
- `app/api/v1/admin/users.py` — Updated all stub routes to require require_admin; added GET / list stub for test coverage
- `app/tests/test_auth.py` — Removed unused pytest import; filled in 6 stubs for AUTH-03, AUTH-04, AUTH-05

## Decisions Made

- oauth2_scheme tokenUrl set to `/v1/auth/login` — matches actual login route, enables Swagger Authorize button to work correctly
- UUID string-to-object conversion added in get_current_user — JWT sub claim is a string, but SQLAlchemy's `UUID(as_uuid=True)` column type requires a `uuid.UUID` object; ValueError on invalid UUID is caught and mapped to 401
- Admin stub routes now include GET / (list_users) — required for test_require_admin_* tests to exercise the gate

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] UUID str to uuid.UUID conversion in get_current_user**
- **Found during:** Task 2 (running test suite after implementation)
- **Issue:** JWT `sub` claim is stored/returned as a string (e.g., `"5770a830-077d-4c8f-a695-125fd93cbe2f"`). SQLAlchemy's `UUID(as_uuid=True)` column type requires a `uuid.UUID` object for filter comparison; passing a raw string caused `AttributeError: 'str' object has no attribute 'hex'`
- **Fix:** Added `uuid.UUID(user_id_str)` conversion in get_current_user try/except block; `ValueError` from malformed UUIDs is caught alongside `jwt.InvalidTokenError` and mapped to 401
- **Files modified:** `app/core/deps.py`
- **Verification:** All 3 affected tests (test_users_me_authenticated, test_require_admin_non_admin, test_require_admin_admin_user) now pass
- **Committed in:** `c0d83b4` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug)
**Impact on plan:** Fix essential for correctness in both SQLite test environment and PostgreSQL production (UUID column type strict in both). No scope creep.

## Issues Encountered

- ruff import sorting: plan's code snippet had `from typing import Annotated, Generator` before `import jwt` — ruff I001 requires stdlib imports before third-party. Auto-fixed with `ruff check --fix` and `ruff format`.
- ruff line length: plan's test code used single-line `.post(...)` calls exceeding 100-char limit. Reformatted to multi-line style consistent with existing tests.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Full authentication system complete: login, refresh rotation, get_current_user, require_admin, /users/me
- Any route in Phase 3 that needs auth simply adds `Depends(get_current_user)` or `Depends(require_admin)`
- Admin stub bodies (list_users, create_user, update_role) are ready for Phase 3 real implementation
- Checkpoint: Task 3 requires human end-to-end verification via Swagger UI before Phase 2 is marked complete

## Task 3: Live E2E Verification — PASSED (2026-03-04)

All 6 checks passed against running Docker stack:

| Check | Result |
|-------|--------|
| Login → 200 + tokens | PASS |
| GET /users/me (admin token) → 200 + correct email | PASS |
| Refresh token → 200 + new tokens | PASS |
| Replay old refresh token → 401 | PASS |
| Non-admin hits /admin/users/ → 403 | PASS |
| Unauthenticated /users/me → 401 | PASS |

### Bugs Found During Bring-Up (committed c577b29)

1. **ORM mapper failure** — `User` had a forward `EventPDF` relationship; `app/db/base.py` (which registers all models) was never imported by the app. Fixed: import in `session.py`; remove `uploaded_events` from `User`.
2. **Migration seed type mismatch** — `bindparams(id=str(uuid))` fails on UUID columns. Fixed: use `gen_random_uuid()` / `now()` in SQL.
3. **Docker DB URL** — default `localhost:5432` unreachable inside container. Fixed: `DATABASE_URL=...@db:5432/...` in `.env`.

## Self-Check: PASSED

- FOUND: app/core/deps.py
- FOUND: app/api/v1/users.py
- FOUND: app/schemas/user.py
- FOUND: .planning/phases/02-authentication/02-02-SUMMARY.md
- FOUND commit: c6b9415 (feat(02-02): add get_current_user and require_admin to deps.py)
- FOUND commit: c0d83b4 (feat(02-02): wire users/me endpoint, admin RBAC, and complete auth tests)

---
*Phase: 02-authentication*
*Completed: 2026-03-04*
