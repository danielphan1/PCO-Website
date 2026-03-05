---
phase: 04-storage-and-finish
plan: 01
subsystem: api
tags: [supabase, storage, fastapi, pydantic, sqlalchemy, pytest]

requires:
  - phase: 03-core-features
    provides: auth deps (get_current_user, require_admin), EventPDF model, conftest fixtures
provides:
  - StorageService singleton with lazy Supabase client init (no import-time failure)
  - event_pdf_path() path helper for storage paths
  - EventCreate and EventResponse Pydantic v2 schemas
  - list_events, upload_event, delete_event service functions
  - GET /v1/events/ authenticated list endpoint
  - POST /v1/admin/events/ upload endpoint (multipart/form-data)
  - DELETE /v1/admin/events/{id} delete endpoint
  - 11-test suite covering all EVNT-01/02/03 behaviors (all passing)
affects: [04-02-router-wiring, README-plan]

tech-stack:
  added: []
  patterns:
    - StorageService class wrapping supabase-py with lazy init to avoid import-time failures
    - Storage-first write order with DB rollback on failure (no orphaned files)
    - Best-effort storage delete on event deletion (always honor admin intent)
    - Signed URLs generated at list time (1-hour expiry, url:null on failure)
    - Patch app.services.event_service.storage_service as single mock target for all tests

key-files:
  created:
    - app/storage/paths.py
    - app/storage/files.py
    - app/schemas/event.py
    - app/services/event_service.py
    - app/tests/test_events.py
  modified:
    - app/api/v1/events.py
    - app/api/v1/admin/events.py

key-decisions:
  - "Lazy Supabase client init in _get_client() — create_client('','') raises at import; deferred to first actual call"
  - "Bucket name 'events' hardcoded as BUCKET constant in storage/files.py (v1 simplicity)"
  - "upload_event returns tuple[EventPDF, str | None] — signed URL generated in service so router never imports storage_service directly"
  - "Router stubs replaced in Task 3 (Rule 3 deviation) — tests could not pass without real endpoint implementations"

patterns-established:
  - "StorageService lazy init: check settings.supabase_url before calling create_client"
  - "Storage rollback pattern: try DB commit, on exception remove from storage, raise HTTPException(500)"
  - "Patch target: app.services.event_service.storage_service covers all storage calls (list, upload, delete)"

requirements-completed: [EVNT-01, EVNT-02, EVNT-03]

duration: 3min
completed: 2026-03-05
---

# Phase 4 Plan 01: Storage and Event Service Summary

**Supabase StorageService with lazy init, event service with PDF validation and storage-first write, and 11-test suite with full mock coverage — all tests passing**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-05T05:42:14Z
- **Completed:** 2026-03-05T05:44:58Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- StorageService wrapper with lazy Supabase client initialization (avoids import-time failure when credentials are empty)
- Event service layer with PDF magic-byte validation (422), size validation (413), storage-first upload with DB rollback, and best-effort delete
- Full 11-test suite covering EVNT-01/02/03: unauthenticated rejection, member list, URL failure graceful handling, admin-only upload, PDF/size validation, DB failure rollback, and delete scenarios

## Task Commits

Each task was committed atomically:

1. **Task 1: Storage layer and schemas** - `d05d3fb` (feat)
2. **Task 2: Event service layer** - `f586881` (feat)
3. **Task 3: Event test suite** - `9b779fc` (feat)

## Files Created/Modified

- `app/storage/paths.py` - event_pdf_path() returning events/{uuid}.pdf
- `app/storage/files.py` - StorageService with lazy client init and storage_service singleton
- `app/schemas/event.py` - EventCreate and EventResponse Pydantic v2 schemas
- `app/services/event_service.py` - list_events, upload_event, delete_event service functions
- `app/tests/test_events.py` - 11-test suite with storage fully mocked
- `app/api/v1/events.py` - GET /v1/events/ authenticated list endpoint (replaced stub)
- `app/api/v1/admin/events.py` - POST /v1/admin/events/ and DELETE /{id} endpoints (replaced stubs)

## Decisions Made

- Lazy Supabase client init (`_get_client()` function) to prevent import-time `create_client("","")` failure in tests
- `upload_event` returns `tuple[EventPDF, str | None]` so the router never needs to call `storage_service` directly — single patch target for all tests
- Bucket name hardcoded as `BUCKET = "events"` in `files.py` for v1 simplicity

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Replaced router stubs with real endpoint implementations**
- **Found during:** Task 3 (Event test suite)
- **Issue:** Stub routers had wrong paths (`/upload` vs `/`, integer `event_id` vs UUID), missing auth deps, and no service calls — tests could not pass against stub routes
- **Fix:** Replaced `app/api/v1/events.py` and `app/api/v1/admin/events.py` with real implementations calling the service layer
- **Files modified:** app/api/v1/events.py, app/api/v1/admin/events.py
- **Verification:** All 11 event tests pass; full suite 68 passed, 1 skipped, no regressions
- **Committed in:** 9b779fc (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (blocking)
**Impact on plan:** Router replacement was required for tests to run; no scope creep — routers are described in Plan 02's objective and the plan explicitly noted stubs needed replacing.

## Issues Encountered

- Ruff import-sort violation in test_events.py (I001) — auto-fixed with `ruff check --fix`
- `python` not in PATH (Darwin shell); used `.venv/bin/python` for all verification commands

## Next Phase Readiness

- All service layer contracts (list_events, upload_event, delete_event) are implemented and tested
- Routers are fully wired; no additional router work needed in Plan 02
- Plan 02 (router wiring) is essentially already done — may just need verification pass

---
*Phase: 04-storage-and-finish*
*Completed: 2026-03-05*
