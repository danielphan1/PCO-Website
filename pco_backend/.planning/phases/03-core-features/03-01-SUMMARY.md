---
phase: 03-core-features
plan: 01
subsystem: api
tags: [fastapi, sqlalchemy, smtp, aiosmtplib, pydantic, audit-log, background-tasks]

# Dependency graph
requires:
  - phase: 02-authentication
    provides: require_admin dep, User model with role/is_active, RefreshToken model with revoked field
provides:
  - email_service.py with send_welcome_email and send_interest_confirmation (async SMTP, log-and-swallow)
  - user_service.py with all 5 member CRUD functions and atomic AuditLog writes
  - GET/POST/PATCH /{id}/role/deactivate/reactivate endpoints at /v1/admin/users
  - Settings.frontend_url field for email template URLs
  - MemberCreate and MemberRoleUpdate pydantic schemas with role validation via Literal
affects:
  - 03-02-interest-forms (uses send_interest_confirmation from email_service)
  - any future admin-facing features that use require_admin or user_service patterns

# Tech tracking
tech-stack:
  added:
    - aiosmtplib (async SMTP sending)
    - pydantic[email] / email-validator==2.3.0 / dnspython==2.8.0 (EmailStr validation)
  patterns:
    - Service layer pattern: router calls service functions, service owns DB transactions + audit writes
    - TDD RED/GREEN: stub tests first, implement to green
    - BackgroundTasks for non-blocking email (HTTP response returned before SMTP attempt)
    - Log-and-swallow pattern for SMTP errors (logger.error, no re-raise)
    - Atomic AuditLog: flush user first, add audit log, single db.commit()
    - Temp password: generated in service, returned via tuple to caller, never in HTTP body

key-files:
  created:
    - app/services/email_service.py
    - app/services/user_service.py (was empty stub)
    - app/tests/test_members.py
    - app/tests/test_email.py
  modified:
    - app/core/config.py (added frontend_url field)
    - app/schemas/user.py (added MemberCreate, MemberRoleUpdate)
    - app/api/v1/admin/users.py (replaced 3-stub router with 5-endpoint implementation)
    - pyproject.toml / uv.lock (added pydantic[email] dependency)

key-decisions:
  - "pydantic[email] / email-validator added to support EmailStr in MemberCreate schema"
  - "Literal type alias for ALL_ROLES used in schemas for Pydantic validation (role validated at schema layer, not service layer)"
  - "deactivate_member uses bulk UPDATE (synchronize_session=fetch) to revoke all refresh tokens atomically in same commit"
  - "Test login uses JSON body (email/password) not OAuth2 form — matches actual login endpoint contract"

patterns-established:
  - "Service layer: all DB mutations live in user_service.py, routers are thin wrappers"
  - "AuditLog written in same db.commit() as the mutation it describes"
  - "BackgroundTasks.add_task for fire-and-forget email — never await inline"
  - "SMTP errors: always catch Exception, log with logger.error, never re-raise"

requirements-completed: [MEMB-01, MEMB-02, MEMB-03, MEMB-04, MEMB-05, XCUT-04]

# Metrics
duration: 6min
completed: 2026-03-04
---

# Phase 3 Plan 01: Member Management Summary

**Five admin-only member CRUD endpoints with async SMTP welcome email (BackgroundTasks), atomic AuditLog writes, and refresh token revocation on deactivation**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-04T21:41:14Z
- **Completed:** 2026-03-04T21:46:54Z
- **Tasks:** 3
- **Files modified:** 8 (4 created, 4 modified)

## Accomplishments

- Delivered all 5 MEMB endpoints: GET list (filterable), POST create, PATCH role/deactivate/reactivate
- Email service with async SMTP via aiosmtplib — swallows failures, never blocks HTTP response
- Temp password generated with secrets.choice (12-char alphanumeric), returned only in welcome email, never in HTTP response body
- AuditLog written atomically with every mutating operation (created/role_updated/deactivated/reactivated)
- Deactivation revokes all active refresh tokens via bulk UPDATE in same commit (MEMB-04)
- Full test suite: 35 passed, 1 skipped — zero regressions against 25-test Phase 2 baseline

## Task Commits

Each task was committed atomically:

1. **Task 1: Wave 0 test scaffold + email service + config extension** - `adf05c7` (test)
2. **Task 2: Member management — schemas, service, and router** - `e24e313` (feat)
3. **Task 3: Ruff lint pass and full suite smoke check** - `f53e906` (chore)

_Note: TDD tasks had separate RED (test) and GREEN (feat) commits_

## Files Created/Modified

- `app/services/email_service.py` - Async SMTP: send_welcome_email and send_interest_confirmation with log-and-swallow error handling
- `app/services/user_service.py` - Member CRUD service: list_members, create_member, update_member_role, deactivate_member, reactivate_member
- `app/api/v1/admin/users.py` - 5-endpoint admin router; replaced 3-stub placeholder
- `app/schemas/user.py` - Added MemberCreate (EmailStr + Literal role) and MemberRoleUpdate schemas
- `app/core/config.py` - Added frontend_url: str = "http://localhost:3000"
- `app/tests/test_members.py` - 8 integration tests covering all 5 MEMB requirements
- `app/tests/test_email.py` - 2 unit tests: BackgroundTasks.add_task called, SMTP failure swallowed
- `pyproject.toml` / `uv.lock` - Added pydantic[email] (email-validator==2.3.0, dnspython==2.8.0)

## Decisions Made

- **pydantic[email] dependency:** EmailStr requires email-validator package; added when missing import detected (Rule 3 auto-fix)
- **Literal type alias for roles:** `_AllRolesLiteral` Literal in schemas provides Pydantic 422 validation at schema layer; service layer validates too as a defense-in-depth
- **Test login format:** Test stubs used OAuth2 form data; fixed to JSON body (`email`/`password`) to match actual login endpoint contract
- **deactivate_member token revocation:** Used `db.query(RefreshToken).filter(...).update({...}, synchronize_session="fetch")` — bulk UPDATE to revoke all tokens in same commit

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Missing pydantic[email] dependency for EmailStr**
- **Found during:** Task 2 (schema implementation)
- **Issue:** `ImportError: email-validator is not installed` when EmailStr used in MemberCreate schema
- **Fix:** Ran `uv add "pydantic[email]"` — added email-validator==2.3.0 and dnspython==2.8.0
- **Files modified:** pyproject.toml, uv.lock
- **Verification:** `from pydantic import EmailStr` imports cleanly; all tests pass
- **Committed in:** e24e313 (Task 2 commit)

**2. [Rule 1 - Bug] Test login used wrong request format (form vs JSON)**
- **Found during:** Task 2 (TDD GREEN run)
- **Issue:** Tests used `data={"username": ..., "password": ...}` (OAuth2 form) but login endpoint accepts `json={"email": ..., "password": ...}` — caused 422 on all member tests
- **Fix:** Changed test helper `_admin_headers` and `_member_headers` to use `json=` with `email` field; also fixed test_email.py
- **Files modified:** app/tests/test_members.py, app/tests/test_email.py
- **Verification:** All 10 new tests pass; admin login returns 200
- **Committed in:** e24e313 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** Both fixes essential for operation. No scope creep.

## Issues Encountered

None beyond the two deviations above.

## User Setup Required

None — email service uses settings.smtp_* fields which default to empty strings. SMTP will silently fail (logged) until real SMTP credentials are configured in .env.

## Next Phase Readiness

- `send_interest_confirmation` in email_service.py is ready for Plan 02 (interest form confirmation email)
- Service layer pattern established — Plan 02 can follow the same structure for interest_service.py
- All 5 MEMB requirements completed and tested; Plan 01 fully closes the member management domain

---
*Phase: 03-core-features*
*Completed: 2026-03-04*
