---
phase: 03-core-features
plan: "03"
subsystem: api
tags: [fastapi, sqlalchemy, pydantic, content, leadership]

# Dependency graph
requires:
  - phase: 03-core-features/03-01
    provides: admin user management endpoints and member model
  - phase: 03-core-features/03-02
    provides: rush info endpoints and OrgContent/RushInfo models
provides:
  - Public GET /v1/content/{history,philanthropy,contacts} endpoints with empty-row safety
  - Admin PUT /v1/content/{section} upsert with Literal section validation (422 on invalid)
  - Public GET /v1/content/leadership returning active officer-role users
  - ContentUpdate, ContentResponse, LeadershipEntry pydantic schemas
  - Content router registered at /v1/content in app/api/router.py
affects:
  - phase-4 (any frontend or Phase 4 feature that reads org content)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Route ordering: GET /leadership defined before GET /{section} to prevent FastAPI capturing 'leadership' as path param"
    - "Empty-row safety: OrgContent GET returns content='' when no DB row exists"
    - "Literal path param for PUT /{section} gives automatic 422 on invalid section values"
    - "Inline router logic (no separate service file) for simple CRUD domains"

key-files:
  created:
    - app/schemas/content.py
    - app/api/v1/content.py
    - app/tests/test_content.py
  modified:
    - app/api/router.py

key-decisions:
  - "GET /leadership defined first in router to avoid FastAPI matching 'leadership' as /{section} path param"
  - "PUT /{section} uses Literal['history', 'philanthropy', 'contacts'] as path type for automatic 422 validation"
  - "auth login in tests uses JSON body {email, password} not OAuth2 form data — matches actual login endpoint contract"

patterns-established:
  - "Route ordering: fixed routes before parameterized routes in FastAPI APIRouter"
  - "Empty-row fallback: always return default response shape instead of 404 for optional content rows"

requirements-completed: [CONT-01, CONT-02, CONT-03, CONT-04, CONT-05]

# Metrics
duration: 3min
completed: 2026-03-04
---

# Phase 3 Plan 03: Content Endpoints Summary

**Five public/admin org content endpoints with empty-row safety and Literal-validated section path parameters, completing Phase 3**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-04T21:55:09Z
- **Completed:** 2026-03-04T21:58:10Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- Implemented GET /v1/content/{history,philanthropy,contacts} (public, returns empty string when no DB row)
- Implemented PUT /v1/content/{section} (admin only, upserts content, returns 422 for invalid section)
- Implemented GET /v1/content/leadership (public, returns active users with OFFICER_ROLES)
- Registered content router at /v1/content in app/api/router.py
- 57 tests green (9 new content tests + 48 prior Phase 1-3 tests)

## Task Commits

Each task was committed atomically:

1. **Task 1: Wave 0 test scaffold — test_content.py** - `6989d55` (test)
2. **Task 2: Content schemas, router, and router wiring** - `bc2ff62` (feat)
3. **Task 3: Final ruff pass and full Phase 3 suite validation** - `c607308` (chore)

_Note: TDD tasks — test scaffold committed as RED, implementation as GREEN_

## Files Created/Modified

- `app/schemas/content.py` - ContentUpdate, ContentResponse, LeadershipEntry pydantic schemas
- `app/api/v1/content.py` - 3 endpoints: GET /leadership, GET /{section}, PUT /{section}
- `app/api/router.py` - Added content router registration at /v1/content
- `app/tests/test_content.py` - 9 integration tests covering CONT-01 through CONT-05

## Decisions Made

- GET /leadership is defined first in the router to prevent FastAPI from matching "leadership" as the `{section}` path parameter (FastAPI routes match in declaration order)
- PUT /{section} uses `Literal["history", "philanthropy", "contacts"]` as path param type — FastAPI/Pydantic automatically returns 422 for any value not in the Literal set
- Test auth helpers use JSON body `{"email": ..., "password": ...}` not OAuth2 form data — this matches the actual `/v1/auth/login` endpoint contract used throughout the project

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed test auth helpers using wrong login format**
- **Found during:** Task 2 (GREEN phase — running tests after implementation)
- **Issue:** Plan's conftest snippet showed `data={"username": ...}` (OAuth2 form style), but actual login endpoint uses JSON body `{"email": ..., "password": ...}`
- **Fix:** Changed `get_admin_token` and `get_member_token` helpers in test_content.py to use `json={"email": ..., "password": ...}`
- **Files modified:** app/tests/test_content.py
- **Verification:** 9/9 tests pass after fix
- **Committed in:** bc2ff62 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Fix required for tests to pass; no scope creep; existing login contract honored.

## Issues Encountered

- FastAPI 422 on login with form data: plan's conftest snippet used `data={"username": ...}` (OAuth2 style) but the project's login endpoint accepts JSON body — fixed by matching the actual endpoint contract used in all other test files.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 3 complete: all 5 success criteria (SC1-SC5) verified via 57 passing tests
- Phase 4 (media/storage) can begin — OrgContent, User, and all other models are stable
- Content endpoints ready for frontend integration

## Self-Check: PASSED

All files verified present. All task commits verified in git log.

---
*Phase: 03-core-features*
*Completed: 2026-03-04*
