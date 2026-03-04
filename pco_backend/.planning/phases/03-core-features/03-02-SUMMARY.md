---
phase: 03-core-features
plan: 02
subsystem: api
tags: [fastapi, sqlalchemy, pydantic, background-tasks, email, interest-form, rush-info]

# Dependency graph
requires:
  - phase: 03-core-features-01
    provides: email_service.send_interest_confirmation, require_admin dep, DB session pattern
  - phase: 02-authentication
    provides: get_current_user, require_admin, JWT auth system
provides:
  - interest_service.py with submit_interest (409 dup email guard) and list_submissions
  - rush_service.py with get_rush, upsert_rush, toggle_visibility (single-row upsert pattern)
  - POST /v1/interest/ (public 201, 409 dup, 422 missing) with background confirmation email
  - GET /v1/interest/ (admin-only 200/403/401)
  - GET /v1/rush/ (public — coming_soon or full RushInfoResponse based on is_published)
  - PUT /v1/rush/ (admin-only upsert returning RushInfoResponse)
  - PATCH /v1/rush/visibility (admin-only toggle returning updated is_published)
affects:
  - any future admin dashboard or public rush page features

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Single-row upsert: query first, create if None, mutate, commit — used in rush_service
    - coming_soon guard: GET /v1/rush/ returns dict when None or not is_published (no 404)
    - BackgroundTasks.add_task for fire-and-forget confirmation email (same as Plan 01 welcome email)

key-files:
  created:
    - app/schemas/interest_form.py
    - app/schemas/rush.py
    - app/services/interest_service.py
    - app/services/rush_service.py
    - app/api/v1/rush.py
    - app/tests/test_interest.py
    - app/tests/test_rush.py
  modified:
    - app/api/v1/interest.py (replaced MVP stub with full implementation)
    - app/api/router.py (added rush router at /v1/rush)
    - app/api/v1/admin/settings.py (removed broken STATE import from removed MVP stub)

key-decisions:
  - "admin/settings.py MVP stub removed — imported STATE from old interest.py which no longer exists; replaced with empty placeholder router"
  - "toggle_visibility creates row if none exists — first toggle on empty table sets is_published=True (publish)"
  - "GET /v1/rush/ returns dict directly when unpublished — no separate schema needed for coming_soon response"

patterns-established:
  - "Single-row upsert: query RushInfo first, create RushInfo() if None, mutate fields, single commit"
  - "coming_soon guard: if rush is None or not rush.is_published: return dict — avoids 404 on public endpoint"
  - "Service layer enforces 409 via HTTPException(409) before DB insert — consistent with member service pattern"

requirements-completed: [INTR-01, INTR-02, RUSH-01, RUSH-02, RUSH-03]

# Metrics
duration: 8min
completed: 2026-03-04
---

# Phase 3 Plan 02: Interest Form and Rush Info Summary

**DB-backed interest form (POST 201/409/422, GET admin-only) and single-row rush info CRUD (GET coming_soon/published, PUT upsert, PATCH visibility toggle) with background confirmation email**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-04T21:49:37Z
- **Completed:** 2026-03-04T21:57:00Z
- **Tasks:** 3 (TDD RED + GREEN + lint)
- **Files modified:** 10 (7 created, 3 modified)

## Accomplishments

- All 5 requirements delivered: INTR-01/02 (interest form POST + GET) and RUSH-01/02/03 (rush GET/PUT/PATCH)
- Single-row upsert pattern for rush info — no duplicate rows, idempotent PUT
- GET /v1/rush/ returns `{"status": "coming_soon"}` when empty or unpublished, full data when published
- Background confirmation email queued non-blocking on every successful interest form submission
- Full suite: 48 passed, 1 skipped — zero regressions against all prior phases

## Task Commits

Each task was committed atomically:

1. **Task 1: Wave 0 test scaffolds — test_interest.py and test_rush.py** - `0283d6b` (test)
2. **Task 2: Interest form and rush info — schemas, services, routers, router wiring** - `67bb7ff` (feat)
3. **Task 3: Ruff lint pass and full suite smoke check** - `d4a5e34` (chore)

_Note: TDD tasks had separate RED (test) and GREEN (feat) commits_

## Files Created/Modified

- `app/schemas/interest_form.py` - InterestFormCreate (EmailStr) and InterestFormResponse (from_attributes)
- `app/schemas/rush.py` - RushInfoUpdate and RushInfoResponse (from_attributes)
- `app/services/interest_service.py` - submit_interest (409 on dup email), list_submissions
- `app/services/rush_service.py` - get_rush, upsert_rush, toggle_visibility (single-row upsert)
- `app/api/v1/interest.py` - Replaced MVP STATE stub; POST / (201 + background email) and GET / (require_admin)
- `app/api/v1/rush.py` - New router: GET / (coming_soon or full), PUT / (upsert), PATCH /visibility (toggle)
- `app/api/router.py` - Added `from app.api.v1 import rush` and `rush.router` at /v1/rush
- `app/api/v1/admin/settings.py` - Removed broken STATE import; now empty placeholder
- `app/tests/test_interest.py` - 6 tests covering INTR-01 and INTR-02
- `app/tests/test_rush.py` - 7 tests covering RUSH-01, RUSH-02, RUSH-03 (sequential state order)

## Decisions Made

- **admin/settings.py STATE removal:** The MVP stub imported `STATE` from the old interest.py which was an in-memory dict. Replacing interest.py with a DB-backed router removed STATE, breaking settings.py. The stub routes (`/admin/settings/interest/open|close`) are now obsolete. Replaced with empty router — Rule 1 auto-fix.
- **toggle_visibility creates row on first call:** If no rush row exists and admin toggles visibility, a new row is created with is_published=True. This is correct: toggling from False (implicit) to True = publish.
- **GET /v1/rush/ returns plain dict:** Returning `{"status": "coming_soon"}` directly avoids creating a discriminated union schema. FastAPI serializes the dict as-is when the response_model is omitted on this route.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] admin/settings.py imported STATE from removed MVP interest.py stub**
- **Found during:** Task 2 (after replacing interest.py body)
- **Issue:** `ImportError: cannot import name 'STATE' from 'app.api.v1.interest'` — app failed to start
- **Fix:** Replaced admin/settings.py with empty placeholder router (stub routes are now obsolete with DB-backed interest)
- **Files modified:** app/api/v1/admin/settings.py
- **Verification:** conftest.py imports app successfully; all 13 new tests pass
- **Committed in:** 67bb7ff (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Essential fix — app failed to start without it. No scope creep; the broken routes were MVP placeholders superseded by this plan's implementation.

## Issues Encountered

None beyond the one deviation above.

## User Setup Required

None — confirmation email uses existing smtp_* settings from .env. SMTP will silently fail (logged) until real SMTP credentials are configured.

## Next Phase Readiness

- All 5 INTR/RUSH requirements completed and tested
- Plan 02 closes the interest form and rush info domains
- Phase 3 plans remaining: events domain (03-03) and any remaining core features
- Service layer pattern consistent with Plan 01 — future plans can follow the same structure

## Self-Check: PASSED

All created files verified on disk. All task commits verified in git log:
- 0283d6b — test(03-02): RED test scaffolds
- 67bb7ff — feat(03-02): GREEN implementation
- d4a5e34 — chore(03-02): ruff lint pass

---
*Phase: 03-core-features*
*Completed: 2026-03-04*
