# Testing Patterns

**Analysis Date:** 2026-03-03

## Test Framework

**Runner:**
- Framework not yet configured; no `pytest.ini` or `setup.cfg` found
- Gitignore includes `.pytest_cache/`, indicating pytest is intended: `.gitignore`
- No test runner configured in `pyproject.toml`

**Assertion Library:**
- Not yet selected; no test dependencies in `pyproject.toml`

**Run Commands:**
Not yet configured. Future commands (inferred):
```bash
pytest                    # Run all tests
pytest -v                 # Run tests with verbose output
pytest --cov              # Run tests with coverage
```

## Test File Organization

**Location:**
- Co-located in `app/tests/` directory
- Test files placed in separate `tests/` subdirectory within `app/`

**Naming:**
- Convention: `test_<feature>.py`
- Examples: `test_auth.py`, `test_events.py`, `test_interest.py`
- Files exist but are currently empty

**Structure:**
```
app/
├── tests/
│   ├── __init__.py          # Package marker
│   ├── conftest.py          # Pytest configuration (empty)
│   ├── test_auth.py         # Auth endpoint tests (empty)
│   ├── test_events.py       # Events endpoint tests (empty)
│   └── test_interest.py     # Interest form tests (empty)
```

## Test Structure

**Suite Organization:**
Not yet implemented. Files exist but contain no test code:
- `app/tests/conftest.py` - Empty, intended for fixtures
- `app/tests/test_auth.py` - Empty, no tests
- `app/tests/test_events.py` - Empty, no tests
- `app/tests/test_interest.py` - Empty, no tests

**Patterns:**
When tests are added, inferred patterns from similar FastAPI projects:
- Setup fixtures in `conftest.py` for TestClient and database
- Use pytest decorators for parametrization and marking
- Teardown via fixture cleanup functions

## Mocking

**Framework:** Not yet selected

**Patterns:**
Not yet established. Likely candidates when implemented:
- `unittest.mock` for standard Python mocking
- `pytest-mock` for pytest integration
- `fastapi.testclient.TestClient` for endpoint testing

**What to Mock (guidance for future tests):**
- Database session/connections
- External API calls (authentication, file storage)
- State mutations (interest form open/closed status in `app/api/v1/interest.py`)

**What NOT to Mock (guidance for future tests):**
- Route handlers (test integration)
- Configuration loading (use test .env)
- FastAPI dependency injection (use TestClient)

## Fixtures and Factories

**Test Data:**
Not yet implemented. Expected structure when added:
- Database fixtures in `conftest.py`
- Example user/event factory functions
- Request body fixtures for endpoint testing

**Location:**
- Global fixtures: `app/tests/conftest.py`
- Module-specific fixtures: Top of each `test_*.py` file
- Shared factories: `app/tests/factories/` (directory structure to create)

## Coverage

**Requirements:** Not enforced; no coverage configuration in `pyproject.toml`

**View Coverage:**
When configured:
```bash
pytest --cov=app              # Generate coverage report
pytest --cov=app --cov-report=html  # Generate HTML report
```

## Test Types

**Unit Tests:**
- Scope: Individual endpoint handlers
- Approach: Test route functions with mocked dependencies
- Files: `app/tests/test_*.py`

**Integration Tests:**
- Scope: Full request-response cycle with database
- Approach: Use `TestClient` from `fastapi.testclient`
- Not yet structured; may combine with unit tests initially

**E2E Tests:**
- Framework: Not used yet
- Future consideration: Playwright or Cypress for frontend-backend integration

## Database Testing

**Setup Pattern (future):**
FastAPI projects typically use:
- Fixture for test database URL (in-memory SQLite or test PostgreSQL)
- Session override: `app.dependency_overrides[get_db]`
- Cleanup: Rollback or drop tables after each test

**Example structure (when implemented):**
```python
# conftest.py pattern
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    # Setup test database
    # yield for test
    # Teardown
    pass

@pytest.fixture
def client(test_db):
    from app.main import app
    return TestClient(app)
```

## Common Patterns

**Async Testing:**
FastAPI endpoints are synchronous (see `app/api/v1/` route handlers), except:
- `async def upload_pdf()` in `app/api/v1/admin/events.py`
- TestClient handles async automatically; no special test setup needed

**Error Testing:**
Not yet implemented. When added:
- Mock database failures
- Test validation on missing/invalid parameters
- Verify error response status codes

## Current State

**Status:** Early MVP phase
- Test files created but empty
- No dependencies configured for testing in `pyproject.toml`
- No conftest configuration yet
- No test mocking or fixtures yet
- Coverage not enforced

**Next Steps (recommended):**
1. Add pytest to `pyproject.toml` dev dependencies
2. Configure `conftest.py` with TestClient and database fixtures
3. Add parametrized tests for each endpoint in `test_auth.py`, `test_events.py`, `test_interest.py`
4. Use `pytest-cov` for coverage reporting
5. Configure GitHub Actions (or similar CI) to run tests

---

*Testing analysis: 2026-03-03*
