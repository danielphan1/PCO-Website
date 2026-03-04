---
phase: 01-foundation
plan: "01"
subsystem: infra
tags: [pyjwt, alembic, supabase, aiosmtplib, ruff, pytest, docker, uv]

# Dependency graph
requires: []
provides:
  - PyJWT>=2.8 installed; python-jose removed (CVE risk eliminated)
  - alembic, supabase, aiosmtplib installed as runtime deps
  - pytest + httpx + ruff installed as dev deps
  - Ruff lint (E/W/F/I) and format configured in pyproject.toml
  - pytest configured with testpaths = ["app/tests"]
  - Dockerfile uses uv sync --frozen --no-dev with uv.lock COPY
  - docker-compose.yml has pg_isready healthcheck and service_healthy condition
  - Wave 0 test scaffold: conftest.py + test_foundation.py (5 pass, 5 skip)
affects: [01-02, 01-03, all-subsequent-plans]

# Tech tracking
tech-stack:
  added: [PyJWT>=2.8, alembic>=1.18.4, aiosmtplib>=5.1.0, supabase>=2.28.0, pytest>=9.0.2, httpx>=0.28.1, ruff>=0.15.4]
  patterns:
    - uv for dependency management with locked reproducible builds
    - pytest with module-scoped TestClient fixture
    - Ruff for lint (E/W/F/I rules) and formatting (double quotes, space indent)

key-files:
  created:
    - app/tests/conftest.py
    - app/tests/test_foundation.py
  modified:
    - pyproject.toml
    - uv.lock
    - docker/Dockerfile
    - docker/docker-compose.yml
    - app/main.py
    - app/core/config.py
    - app/api/router.py
    - app/api/v1/auth.py
    - app/api/v1/events.py
    - app/api/v1/interest.py
    - app/api/v1/public.py
    - app/api/v1/admin/events.py
    - app/api/v1/admin/settings.py
    - app/api/v1/admin/users.py

key-decisions:
  - "Removed python-jose (no transitive conflict found — only direct dependency); replaced with PyJWT>=2.8"
  - "Added ruff as dev dependency (not globally installed); run via uv run ruff"
  - "Auto-fixed 5 ruff I001 import-sort violations across existing codebase as part of Ruff config activation"

patterns-established:
  - "TDD scaffold pattern: stubs with pytest.mark.skip for unimplemented features, real assertions for installed deps"
  - "Ruff auto-fix applied before commit to keep codebase clean from plan 01 forward"

requirements-completed: [INFRA-01, INFRA-02, INFRA-06, INFRA-07, XCUT-05]

# Metrics
duration: 3min
completed: 2026-03-04
---

# Phase 1 Plan 01: Foundation Setup Summary

**PyJWT replaces python-jose, alembic/supabase/aiosmtplib added, Ruff and pytest configured, Dockerfile hardened with frozen lock, docker-compose gets pg_isready healthcheck, and Wave 0 test scaffold created with 5 passing + 5 skipped stubs**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-04T05:01:37Z
- **Completed:** 2026-03-04T05:05:26Z
- **Tasks:** 2 completed
- **Files modified:** 14 modified, 2 created

## Accomplishments

- Swapped python-jose for PyJWT>=2.8 with no transitive conflict (only direct dep)
- Added alembic, supabase, aiosmtplib as runtime deps; pytest, httpx, ruff as dev deps
- Configured Ruff lint (E/W/F/I rules) + format, and pytest testpaths in pyproject.toml
- Hardened Dockerfile: `COPY pyproject.toml uv.lock /app/`, `uv sync --frozen --no-dev`, `COPY alembic`
- Added pg_isready healthcheck to docker-compose db service; api depends_on uses service_healthy
- Created Wave 0 test scaffold: conftest.py (TestClient fixture) + test_foundation.py (11 test stubs)
- All 5 executable tests pass; 5 stubs correctly skipped pending Plans 01-02 and 01-03

## Task Commits

Each task was committed atomically:

1. **Task 1: Swap deps, add Ruff/pytest config, fix Dockerfile and docker-compose** - `8a3097a` (chore)
2. **Task 2: Create Wave 0 test scaffold (conftest.py and test_foundation.py stubs)** - `290c285` (test)

**Plan metadata:** (docs commit follows)

_Note: TDD tasks produced code + test commits within each task commit_

## Files Created/Modified

- `pyproject.toml` - Removed python-jose, added PyJWT/alembic/supabase/aiosmtplib, added ruff and pytest config sections
- `uv.lock` - Updated lock file with all new/removed dependencies
- `docker/Dockerfile` - COPY uv.lock, uv sync --frozen --no-dev, COPY alembic
- `docker/docker-compose.yml` - pg_isready healthcheck on db service, service_healthy condition on api
- `app/tests/conftest.py` - TestClient fixture (scope=module)
- `app/tests/test_foundation.py` - 11 Wave 0 test stubs: 5 pass, 5 skip
- `app/main.py` - Ruff import-sort auto-fix
- `app/core/config.py` - Ruff import-sort auto-fix
- `app/api/router.py` - Ruff import-sort auto-fix
- `app/api/v1/*.py` (4 files) - Ruff import-sort auto-fix
- `app/api/v1/admin/*.py` (3 files) - Ruff import-sort auto-fix

## Decisions Made

- **python-jose removal**: Confirmed no transitive conflict before removing — only direct dependency in the project, safe to remove. Replaced with PyJWT>=2.8 which avoids the alg:none vulnerability.
- **ruff as dev dep**: Added ruff to the dev dependency group since it's a tooling dependency; invoked via `uv run ruff`.
- **Auto-fix scope**: Applied ruff --fix and ruff format to the full codebase as part of activating ruff config — affected 9 files with import sorting (I001) violations. This is expected when enabling ruff for the first time.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] ruff not installed — added as dev dependency**
- **Found during:** Task 1 (after adding Ruff config to pyproject.toml)
- **Issue:** `uv run ruff check .` failed with "No such file or directory" — ruff was not in the dependency group
- **Fix:** `uv add --dev ruff` — added ruff>=0.15.4 to dev dependencies
- **Files modified:** pyproject.toml, uv.lock
- **Verification:** `uv run ruff check .` runs successfully
- **Committed in:** 8a3097a (Task 1 commit)

**2. [Rule 2 - Missing Critical] 5 ruff I001 import-sort violations in existing codebase**
- **Found during:** Task 1 (running `ruff check .` for the first time)
- **Issue:** Existing source files had unsorted imports (app/main.py, app/core/config.py, app/api/router.py, app/api/v1/admin/events.py, app/api/v1/admin/settings.py)
- **Fix:** `uv run ruff check --fix . && uv run ruff format .` — auto-fixed all violations
- **Files modified:** app/main.py, app/core/config.py, app/api/router.py, app/api/v1/admin/events.py, app/api/v1/admin/settings.py (+ reformatted 4 more files)
- **Verification:** `ruff check .` exits 0; `ruff format --check .` exits 0
- **Committed in:** 8a3097a (Task 1 commit)

**3. [Rule 2 - Missing Critical] ruff I001 violation in new test_foundation.py**
- **Found during:** Task 2 (running ruff check on new test files)
- **Issue:** `import aiosmtplib; import alembic; import supabase` — alembic should come before aiosmtplib alphabetically per isort
- **Fix:** `uv run ruff check --fix app/tests/ && uv run ruff format app/tests/` — auto-fixed
- **Files modified:** app/tests/test_foundation.py
- **Verification:** `ruff check .` and `ruff format --check .` both exit 0
- **Committed in:** 290c285 (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (1 blocking dep, 2 missing critical — import sort)
**Impact on plan:** All auto-fixes necessary for correct tooling setup and code quality. No scope creep.

## Issues Encountered

None - all verifications passed on first attempt after auto-fixes.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 01-01 complete: dependency foundation and test scaffold in place
- Plans 01-02 and 01-03 can now begin (Wave 1 plans, no dependencies between them)
- test_foundation.py stubs for Plans 01-02 and 01-03 are already in place with skip markers
- The Pydantic V2 deprecation warning (class-based Config) in app/core/config.py is a pre-existing issue — deferred to Plan 01-03 when settings are hardened

## Self-Check: PASSED

- FOUND: app/tests/conftest.py
- FOUND: app/tests/test_foundation.py
- FOUND: docker/Dockerfile
- FOUND: docker/docker-compose.yml
- FOUND: pyproject.toml
- FOUND: commit 8a3097a (Task 1)
- FOUND: commit 290c285 (Task 2)
- FOUND: uv sync --frozen in Dockerfile
- FOUND: service_healthy in docker-compose.yml
- FOUND: PyJWT in pyproject.toml
- FOUND: [tool.ruff.lint] in pyproject.toml
- FOUND: [tool.pytest.ini_options] in pyproject.toml

---
*Phase: 01-foundation*
*Completed: 2026-03-04*
