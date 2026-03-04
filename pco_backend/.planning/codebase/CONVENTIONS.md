# Coding Conventions

**Analysis Date:** 2026-03-03

## Naming Patterns

**Files:**
- Lowercase with underscores: `auth.py`, `public.py`, `user_service.py`
- API route files match endpoint domain: `events.py`, `interest.py`, `auth.py`
- Model files singular: `user.py`, `role.py`, `event_pdf.py`
- Test files prefixed with `test_`: `test_auth.py`, `test_events.py`, `test_interest.py`

**Functions:**
- Lowercase with underscores (snake_case): `get_public_info()`, `submit_interest()`, `update_role()`
- API route handlers: `login()`, `status()`, `create_user()`, `list_events()`
- No type hints on simple functions yet; partial usage in parameters (`file: UploadFile`, `user_id: int`)

**Variables:**
- Lowercase with underscores: `jwt_secret`, `app_name`, `cors_origins`
- Module-level state uppercase: `STATE` (see `app/api/v1/interest.py`)
- Dictionary keys typically lowercase or snake_case in payloads

**Types:**
- Pydantic `BaseSettings` for configuration (see `app/core/config.py`)
- Generic `dict` used for request/response payloads (not yet Pydantic models)
- No TypeVar or generic type patterns observed

## Code Style

**Formatting:**
- Ruff configured with 100-character line limit (`.tool.ruff` in `pyproject.toml`)
- Line length: 100 characters

**Linting:**
- Ruff is primary linter/formatter (configured in `pyproject.toml`)
- No additional linting tools (flake8, pylint, mypy) configured
- Gitignore includes ruff cache directory: `.gitignore` lists `ruff_cache/`

## Import Organization

**Order:**
1. Standard library imports (not yet organized, minimal usage)
2. Third-party framework imports: `fastapi`, `pydantic`, `sqlalchemy`
3. Local application imports: `from app.xxx`

**Patterns Observed:**
- Relative imports avoided; always use absolute imports: `from app.api.router import router`
- Router imports explicit in aggregation files: `from app.api.v1 import public, interest, events, auth`
- Single import per line in aggregation modules (see `app/api/router.py`)

**Path Aliases:**
- No aliases configured; all imports use full `app.` prefix paths

## Error Handling

**Patterns:**
- No explicit error handling observed in current codebase
- No try/except blocks in implemented endpoints
- TODO comments indicate future error validation: `"# MVP stub; later: verify password, return JWT"` (see `app/api/v1/auth.py`)
- FastAPI dependency injection used for security/validation (structure in place, not yet implemented)

## Logging

**Framework:** Not implemented
- No logging imports detected
- `app/core/logging.py` file exists but is empty
- Console-based logging implied for future use

## Comments

**When to Comment:**
- MVP-focused inline comments explaining stubs: `# MVP stub; later: validate PDF, save to storage`
- TODO markers for incomplete features: `"TODO"` returns in `app/api/v1/public.py`
- Comments above MVP features document defer strategy: `# MVP: return list; later: DB entries`

**JSDoc/TSDoc:**
- No docstrings or JSDoc patterns observed
- Python project with no docstring documentation

## Function Design

**Size:** Functions are minimal (3-10 lines average)

**Parameters:**
- Accepts generic `dict` or specific types from FastAPI (`UploadFile`, `File`)
- Path parameters explicitly typed: `user_id: int`, `event_id: int`

**Return Values:**
- Consistent dictionary returns: `{"created": True, "user": payload}`
- Status responses: `{"ok": True}`, `{"received": True}`
- Passthrough patterns: `{"uploaded": True, "filename": file.filename}`

## Module Design

**Exports:**
- Each API module defines and exports single `router` object
- Pattern: `router = APIRouter()` followed by route decorators
- Central aggregation in `app/api/router.py` includes all routers

**Barrel Files:**
- Not used; each module imports what it needs directly
- Exception: `app/core/config.py` defines `settings = Settings()` for singleton export

## Async Patterns

**Usage:**
- Limited async: `async def upload_pdf()` in `app/api/v1/admin/events.py`
- Mostly synchronous endpoints
- FastAPI async support in place for file uploads, not required elsewhere yet

---

*Convention analysis: 2026-03-03*
