# Phase 4: Storage and Finish - Research

**Researched:** 2026-03-04
**Domain:** Supabase Storage (supabase-py 2.x), FastAPI multipart uploads, PDF validation, README authoring
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Signed URLs**
- Generated at list time: GET /v1/events embeds a signed URL in every item — no separate URL endpoint
- Expiry: 1 hour (3600 seconds)
- On signed URL generation failure for one event: return `url: null` for that event; do not fail the whole request

**Upload request shape**
- POST /v1/admin/events accepts multipart/form-data with three fields: `file` (PDF binary), `title` (string), `date` (YYYY-MM-DD)
- On success: return `{id, title, date, url, created_at}` — same shape as list response
- Storage-first write order: upload to Supabase Storage first; if DB write fails, delete the file from storage and return 500

**Event list response**
- GET /v1/events sorted by event date, newest first (the `date` field, not `created_at`)
- Each item: `id`, `title`, `date`, `url` — no admin-internal fields (uploaded_by, created_at) in list
- No pagination — return all events

**Delete behavior**
- DELETE /v1/admin/events/{id}: best-effort storage deletion — attempt removal, log any storage error, always delete DB record and return 200

**README**
- Audience: future developer taking over the project
- Sections: setup instructions, environment variable reference, architecture overview, link to /docs, high-level endpoint table (method, path, auth, one-line description)
- Setup section: Docker workflow only (`docker compose up`), reference `.env.example`
- Tone: concise and practical

### Claude's Discretion
- Storage path format in Supabase (e.g., `events/{uuid}.pdf` — use existing `app/storage/paths.py`)
- Supabase-py 2.x exact method signatures for upload, signed URL, and remove (verified below)
- .env.example file contents (mirrors Settings fields with placeholder values)
- README architecture section depth (a paragraph is fine — no diagrams required)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| EVNT-01 | Authenticated user can list event PDFs via GET /api/events (title, date, url) | Supabase `create_signed_url()` verified; SQLAlchemy sort by `date` DESC; Pydantic EventResponse schema design |
| EVNT-02 | Admin can upload event PDF via POST /api/events to Supabase Storage — max 10MB, validates PDF magic bytes (%PDF), stores URL + metadata in DB | FastAPI `UploadFile` + `Form()` pattern verified; `upload()` signature confirmed; storage-first write order with rollback |
| EVNT-03 | Admin can delete event PDF via DELETE /api/events/{id} — removes from Supabase Storage and DB | Supabase `remove([path])` signature confirmed; best-effort deletion pattern documented |
| XCUT-06 | README includes setup instructions, architecture overview, environment variable reference, and link to /docs | README sections, endpoint table, .env.example pattern documented |
</phase_requirements>

---

## Summary

Phase 4 implements three event PDF endpoints (list, upload, delete) backed by Supabase Storage plus a project README. All prior-phase infrastructure is already in place: the `EventPDF` ORM model exists, stub routers are registered, `get_current_user` and `require_admin` dependencies are wired, and `supabase>=2.28.0` is already installed. The primary research risk — supabase-py 2.x method signatures — has been resolved and documented with HIGH confidence via official source inspection.

The storage integration layer goes in `app/storage/files.py` (Supabase client init + method wrappers). Business logic goes in `app/services/event_service.py`. Routers in `app/api/v1/events.py` and `app/api/v1/admin/events.py` are replaced wholesale. Schemas go in `app/schemas/event.py`. Tests in `app/tests/test_events.py` mock the Supabase client using `unittest.mock.patch` so no live Supabase connection is needed in CI.

**Primary recommendation:** Initialize one `Client` instance in `app/storage/files.py` using `create_client(settings.supabase_url, settings.supabase_service_key)`. Wrap `upload()`, `create_signed_url()`, and `remove()` in a `StorageService` class. Inject `StorageService` into `event_service.py` functions. Keep all business logic (validation, DB writes, rollback) in the service layer, not in routers.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| supabase-py | 2.28.0 (pinned in uv.lock) | Supabase Storage client | Already installed; official SDK |
| fastapi | >=0.115 | Framework, `UploadFile`, `File`, `Form` | Project-wide |
| sqlalchemy | >=2.0 | ORM queries, `Session` | Project-wide; sync pattern established |
| pydantic v2 | >=2.7 | `EventCreate`, `EventResponse` schemas | Project-wide pattern |
| python-multipart | >=0.0.9 | Parses multipart/form-data | Already installed; required for `UploadFile` |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| unittest.mock | stdlib | Patch `StorageService` in tests | Every test — no live Supabase in CI |
| uuid | stdlib | Generate UUID-based storage filenames | `app/storage/paths.py` |
| logging | stdlib | Log storage errors on best-effort ops | Delete and signed URL failure paths |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| supabase-py | boto3 (S3-compatible) | Supabase already chosen and installed |
| Direct supabase calls in router | StorageService wrapper class | Wrapper makes mocking in tests clean |
| Pydantic `date` field for `date` param | `str` + manual parse | Pydantic handles YYYY-MM-DD parsing automatically |

**Installation:** No new packages needed. All dependencies are already in `pyproject.toml` and `uv.lock`.

---

## Architecture Patterns

### Recommended Project Structure

```
app/
├── storage/
│   ├── __init__.py
│   ├── files.py         # Supabase Client init + StorageService class (upload, sign, remove)
│   └── paths.py         # Path helpers: events/{uuid}.pdf
├── schemas/
│   └── event.py         # EventCreate, EventResponse (add here — file is currently empty)
├── services/
│   └── event_service.py # list_events, upload_event, delete_event (file is currently empty)
├── api/v1/
│   ├── events.py        # GET /v1/events — replace stub
│   └── admin/
│       └── events.py    # POST /v1/admin/events, DELETE /v1/admin/events/{id} — replace stub
└── tests/
    └── test_events.py   # All event tests; mock StorageService
```

### Pattern 1: Supabase Client Initialization (Singleton Module-Level)

**What:** Initialize once at module level in `app/storage/files.py`; import the `StorageService` instance elsewhere.
**When to use:** Always — creating one client per request is wasteful and not the supabase-py pattern.

```python
# app/storage/files.py
# Source: https://github.com/supabase/supabase-py
from supabase import Client, create_client

from app.core.config import settings

_client: Client = create_client(settings.supabase_url, settings.supabase_service_key)
BUCKET = "events"  # or pull from settings if needed

class StorageService:
    def upload(self, path: str, data: bytes, content_type: str = "application/pdf") -> None:
        _client.storage.from_(BUCKET).upload(
            path=path,
            file=data,
            file_options={"content-type": content_type, "upsert": "false"},
        )

    def create_signed_url(self, path: str, expires_in: int = 3600) -> str | None:
        try:
            result = _client.storage.from_(BUCKET).create_signed_url(path, expires_in)
            # Returns dict with key "signedURL" (camelCase) — verified from storage-py source
            return result.get("signedURL")
        except Exception:
            return None

    def remove(self, path: str) -> None:
        # remove() takes a list of paths
        _client.storage.from_(BUCKET).remove([path])


storage_service = StorageService()
```

### Pattern 2: Storage Path Helper

**What:** Centralize storage path construction in `app/storage/paths.py`.
**When to use:** Anywhere a storage path is constructed (upload and delete).

```python
# app/storage/paths.py
import uuid


def event_pdf_path(event_id: uuid.UUID) -> str:
    """Return relative storage path for an event PDF: events/{uuid}.pdf"""
    return f"events/{event_id}.pdf"
```

### Pattern 3: Multipart Form with File + Text Fields

**What:** FastAPI endpoint accepting `UploadFile` and `Form()` fields in one request.
**When to use:** POST /v1/admin/events — multipart/form-data with file, title, date.

```python
# Source: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.deps import get_db, require_admin

router = APIRouter()

@router.post("/", status_code=201)
async def upload_event(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    date: Annotated[date, Form()],  # Pydantic parses YYYY-MM-DD automatically
    db=Depends(get_db),
    current_user=Depends(require_admin),
):
    ...
```

### Pattern 4: PDF Magic Bytes Validation

**What:** Read first 4 bytes to confirm file starts with `%PDF` before accepting upload.
**When to use:** Every upload — content-type header is not trustworthy.

```python
MAX_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB

async def validate_pdf_upload(file: UploadFile) -> bytes:
    """Read file, validate size and PDF magic bytes. Returns raw bytes."""
    data = await file.read()

    if len(data) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 10 MB limit.",
        )

    if not data[:4] == b"%PDF":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File is not a valid PDF (missing %PDF header).",
        )

    return data
```

### Pattern 5: Storage-First Write with Rollback

**What:** Upload to Supabase first, then write DB. On DB failure, delete from storage.
**When to use:** Upload endpoint — prevents orphaned files.

```python
def upload_event(db: Session, title: str, event_date: date, data: bytes, uploader_id: uuid.UUID) -> EventPDF:
    event_id = uuid.uuid4()
    path = event_pdf_path(event_id)

    # 1. Upload to storage first
    storage_service.upload(path, data)

    # 2. Write DB record — rollback storage on failure
    try:
        event = EventPDF(
            id=event_id,
            title=title,
            date=event_date,
            storage_path=path,
            uploaded_by=uploader_id,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    except Exception:
        # Best-effort cleanup
        try:
            storage_service.remove(path)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail="Failed to save event record.")
```

### Pattern 6: Best-Effort Delete

**What:** Attempt storage removal, log errors, always delete DB record.
**When to use:** DELETE /v1/admin/events/{id}

```python
import logging

logger = logging.getLogger(__name__)

def delete_event(db: Session, event_id: uuid.UUID) -> None:
    event = db.query(EventPDF).filter(EventPDF.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found.")

    try:
        storage_service.remove(event.storage_path)
    except Exception as exc:
        logger.warning("Storage removal failed for %s: %s", event.storage_path, exc)

    db.delete(event)
    db.commit()
```

### Pattern 7: Signed URL at List Time

**What:** Generate signed URLs for all events during GET /v1/events, return `url: null` on failure.
**When to use:** GET /v1/events — no separate URL endpoint needed.

```python
def list_events(db: Session) -> list[dict]:
    events = (
        db.query(EventPDF)
        .order_by(EventPDF.date.desc())
        .all()
    )
    result = []
    for event in events:
        url = storage_service.create_signed_url(event.storage_path, expires_in=3600)
        result.append({
            "id": str(event.id),
            "title": event.title,
            "date": str(event.date),
            "url": url,  # None if signing failed
        })
    return result
```

### Pydantic Schemas (Pydantic v2 pattern)

```python
# app/schemas/event.py
import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):
    title: str
    date: date  # parsed from YYYY-MM-DD string in Form()


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    date: date
    url: str | None  # None when signed URL generation failed
```

### Anti-Patterns to Avoid

- **Generating signed URLs at delete time:** The signed URL expiry does not need to match any delete lifecycle — sign only at list time.
- **Storing full URLs in the DB:** `storage_path` holds relative path only (`events/{uuid}.pdf`). Signed URLs are ephemeral and must be regenerated. This was decided in Phase 1.
- **Failing the whole list on one bad URL:** If one `create_signed_url` call fails, return `url: null` for that item; other items must still appear.
- **Using `async def` for DB operations:** The project uses synchronous SQLAlchemy. Upload endpoint reads the file (`await file.read()`) in an `async def`, then calls sync service functions — this is correct. Do not introduce async SQLAlchemy.
- **Storing `uploaded_by` in EventResponse:** The list response exposes only `id`, `title`, `date`, `url`. Internal fields stay server-side.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Supabase Storage client | Custom HTTP client with auth headers | `supabase.create_client()` + `storage.from_()` | Handles auth, retries, API versioning |
| PDF content type detection | Parse MIME type from Content-Type header | Read first 4 bytes for `%PDF` magic | Content-Type header is client-controlled and untrustworthy |
| UUID filename generation | Sequential IDs or hash of content | `uuid.uuid4()` at service layer | Avoids collisions, matches EventPDF.id |
| Multipart parsing | Manual `request.body()` parsing | FastAPI `UploadFile` + `Form()` | python-multipart already installed; handles streaming |
| Signed URL expiry management | Cache signed URLs in DB | Regenerate on every list request | URLs expire in 1 hour; fresh generation is the design |

**Key insight:** The Supabase Storage HTTP API has many edge cases around content-type negotiation, signed URL token generation, and error signaling. The supabase-py SDK encapsulates all of this. Never bypass it with raw HTTP calls.

---

## Common Pitfalls

### Pitfall 1: Wrong Key for Signed URL Response

**What goes wrong:** Code accesses `result["signed_url"]` (snake_case) but the actual key is `"signedURL"` (camelCase).
**Why it happens:** Python convention suggests snake_case, but Supabase returns camelCase for this field.
**How to avoid:** Use `result.get("signedURL")` — verified from storage-py source code (`storage3/_sync/file_api.py`).
**Warning signs:** `KeyError` or `None` URLs on list endpoint when Supabase is reachable.

### Pitfall 2: Forgetting `await file.read()` for Large Files

**What goes wrong:** Only the first chunk is read, resulting in truncated or empty uploads.
**Why it happens:** `UploadFile` is a streaming object; `.read()` must be awaited to consume all bytes.
**How to avoid:** In `async def` upload endpoint, always `data = await file.read()` before any validation.
**Warning signs:** Files upload with zero bytes or fail PDF magic byte check despite valid PDFs.

### Pitfall 3: Orphaned Storage Files on DB Failure

**What goes wrong:** File uploaded to Supabase, then DB commit fails — file sits in storage forever with no DB record.
**Why it happens:** No rollback logic on DB exception.
**How to avoid:** Wrap DB write in try/except; call `storage_service.remove(path)` in the except block.
**Warning signs:** Storage bucket fills with files that have no corresponding `events` DB rows.

### Pitfall 4: `remove()` Takes a List, Not a String

**What goes wrong:** `storage.from_(BUCKET).remove(path)` raises a type error.
**Why it happens:** The `remove()` method signature is `remove(paths: list)` — always a list.
**How to avoid:** Always call `remove([path])` with a list, even for a single file.
**Warning signs:** `TypeError` or unexpected Supabase API errors on delete.

### Pitfall 5: SQLite UUID Compatibility in Tests

**What goes wrong:** `EventPDF.id` is `UUID(as_uuid=True)` which works in PostgreSQL but has edge cases in SQLite (used in tests).
**Why it happens:** The existing conftest uses SQLite for the test DB. UUID columns are stored as strings.
**How to avoid:** When constructing `EventPDF` in tests, pass `id=uuid.uuid4()` explicitly. Query filters using `str(event_id)` may be needed if SQLite stores as string. Follow existing patterns in conftest — other models with UUID PKs already handle this.
**Warning signs:** Test queries returning `None` for events that were just inserted.

### Pitfall 6: Supabase Client Init Fails at Import with Empty Credentials

**What goes wrong:** `create_client("", "")` raises an error during module import in tests.
**Why it happens:** `supabase_url` and `supabase_service_key` default to `""` in Settings — the client validates the URL format.
**How to avoid:** Tests must mock `StorageService` at the class/instance level (patch `app.storage.files.storage_service`) so the real client is never called. Do not let the real Supabase client be invoked in tests.
**Warning signs:** Import errors or connection errors when running the test suite without Supabase credentials.

### Pitfall 7: Sync vs Async Mismatch in Upload Endpoint

**What goes wrong:** Upload endpoint is `def` (sync) but `file.read()` requires `await`.
**Why it happens:** `UploadFile.read()` is a coroutine; it must be called from an `async def`.
**How to avoid:** The upload router function MUST be `async def`. The service layer functions it calls are sync (SQLAlchemy is sync). This is the correct pattern.
**Warning signs:** `RuntimeWarning: coroutine 'read' was never awaited`.

---

## Code Examples

### Verified: Supabase Client Init

```python
# Source: https://github.com/supabase/supabase-py (official README)
from supabase import Client, create_client

supabase: Client = create_client(supabase_url, supabase_key)
```

### Verified: Storage Upload

```python
# Source: https://supabase.com/docs/reference/python/storage-from-upload
supabase.storage.from_("bucket_name").upload(
    path="folder/subfolder/filename.pdf",
    file=bytes_data,
    file_options={"content-type": "application/pdf", "upsert": "false"},
)
```

### Verified: Signed URL (create_signed_url)

```python
# Source: https://supabase.com/docs/reference/python/storage-from-createsignedurl
# Returns dict: {"signedURL": "https://...", "signedUrl": "https://..."}
result = supabase.storage.from_("bucket_name").create_signed_url("folder/file.pdf", 3600)
signed_url = result.get("signedURL")  # Key is camelCase "signedURL"
```

### Verified: Storage Remove

```python
# Source: https://supabase.com/docs/reference/python/storage-from-remove
# paths must be a list
supabase.storage.from_("bucket_name").remove(["folder/file.pdf"])
```

### Verified: FastAPI Multipart with UploadFile + Form Fields

```python
# Source: https://fastapi.tiangolo.com/tutorial/request-forms-and-files/
from typing import Annotated
from fastapi import File, Form, UploadFile

@router.post("/")
async def upload_event(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    date: Annotated[date, Form()],
):
    data = await file.read()
```

### Verified: SQLAlchemy Order by Date DESC

```python
# Standard SQLAlchemy 2.0 pattern (project-wide)
events = db.query(EventPDF).order_by(EventPDF.date.desc()).all()
```

### Test Pattern: Mock StorageService

```python
# Patch the singleton storage_service instance used by event_service
from unittest.mock import MagicMock, patch

def test_list_events_with_url(auth_client):
    member_token = ...  # login as member

    mock_storage = MagicMock()
    mock_storage.create_signed_url.return_value = "https://signed.url/file.pdf"

    with patch("app.services.event_service.storage_service", mock_storage):
        resp = auth_client.get(
            "/v1/events/",
            headers={"Authorization": f"Bearer {member_token}"},
        )
    assert resp.status_code == 200
    events = resp.json()
    assert all("url" in e for e in events)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `get_public_url()` for access | `create_signed_url()` for private buckets | Supabase Storage private bucket model | Public URLs expose files without auth; signed URLs are the correct pattern for private buckets |
| `python-jose` for JWT | `PyJWT` | Phase 1 (CVE fix) | Already done — no JWT work in Phase 4 |
| Passlib + bcrypt | Direct `bcrypt` | Phase 2 | Already done |

**Deprecated/outdated in this context:**
- `get_public_url()`: Returns a permanent URL that bypasses bucket access controls. Do not use for private buckets. Use `create_signed_url()` instead.
- Storing full signed URLs in the DB: Signed URLs expire — storing them is useless. Store relative `storage_path` only (already the design).

---

## Open Questions

1. **Supabase bucket name**
   - What we know: Settings has `supabase_url` and `supabase_service_key`. No `supabase_bucket` setting exists yet.
   - What's unclear: Whether the bucket name should be hardcoded or configurable via Settings.
   - Recommendation: Hardcode `"events"` as a constant in `app/storage/files.py` for v1 simplicity. If needed, add to Settings later.

2. **Supabase client behavior with empty credentials at import**
   - What we know: `supabase_url` and `supabase_service_key` default to `""` in Settings.
   - What's unclear: Whether `create_client("", "")` raises at import time or only on first API call.
   - Recommendation: Lazy-initialize the client — only call `create_client()` when `StorageService` methods are invoked, or wrap in a function that checks credentials first. Alternatively, test suite mocks before import resolution matters.

3. **SQLite and `date` column type**
   - What we know: `EventPDF.date` is `Mapped[date]` with `Date` column type; SQLite stores dates as strings.
   - What's unclear: Whether `order_by(EventPDF.date.desc())` works correctly in SQLite for the test suite.
   - Recommendation: Verify in the first test run. SQLAlchemy handles `Date` type for SQLite correctly via Python `date` objects in most cases.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| Quick run command | `pytest app/tests/test_events.py -x` |
| Full suite command | `pytest app/tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| EVNT-01 | Authenticated member can GET /v1/events — returns list with id, title, date, url | integration | `pytest app/tests/test_events.py::test_list_events_member -x` | ❌ Wave 0 |
| EVNT-01 | Unauthenticated GET /v1/events returns 401 | integration | `pytest app/tests/test_events.py::test_list_events_unauthenticated -x` | ❌ Wave 0 |
| EVNT-01 | Signed URL failure for one event returns url: null, does not fail request | integration | `pytest app/tests/test_events.py::test_list_events_url_failure_graceful -x` | ❌ Wave 0 |
| EVNT-02 | Admin POST /v1/admin/events with valid PDF returns 201 with full EventResponse | integration | `pytest app/tests/test_events.py::test_upload_pdf_success -x` | ❌ Wave 0 |
| EVNT-02 | Non-PDF file rejected with 422 | integration | `pytest app/tests/test_events.py::test_upload_non_pdf_rejected -x` | ❌ Wave 0 |
| EVNT-02 | File over 10 MB rejected with 413 | integration | `pytest app/tests/test_events.py::test_upload_oversized_rejected -x` | ❌ Wave 0 |
| EVNT-02 | Non-admin POST /v1/admin/events returns 403 | integration | `pytest app/tests/test_events.py::test_upload_non_admin_forbidden -x` | ❌ Wave 0 |
| EVNT-02 | DB failure after storage upload triggers storage rollback | unit | `pytest app/tests/test_events.py::test_upload_db_failure_triggers_storage_delete -x` | ❌ Wave 0 |
| EVNT-03 | Admin DELETE /v1/admin/events/{id} returns 200 and removes DB record | integration | `pytest app/tests/test_events.py::test_delete_event_success -x` | ❌ Wave 0 |
| EVNT-03 | DELETE with storage failure still deletes DB record and returns 200 | integration | `pytest app/tests/test_events.py::test_delete_event_storage_failure_still_succeeds -x` | ❌ Wave 0 |
| EVNT-03 | DELETE nonexistent id returns 404 | integration | `pytest app/tests/test_events.py::test_delete_event_not_found -x` | ❌ Wave 0 |
| XCUT-06 | README.md exists and contains required sections | manual | N/A — checked at phase gate | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest app/tests/test_events.py -x`
- **Per wave merge:** `pytest app/tests/ -x`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `app/tests/test_events.py` — currently empty (1-line file); all event tests must be created here
- [ ] `app/schemas/event.py` — currently empty; `EventCreate` and `EventResponse` needed before tests run
- [ ] `app/storage/files.py` — currently empty; `StorageService` and `storage_service` singleton needed
- [ ] `app/storage/paths.py` — currently empty; `event_pdf_path()` helper needed
- [ ] `app/services/event_service.py` — currently empty; all business logic functions needed
- [ ] `README.md` — does not exist yet (XCUT-06)
- [ ] `.env.example` — does not exist yet (referenced by README setup section)

*(No framework install needed — pytest, httpx, ruff are all in dev dependencies)*

---

## Sources

### Primary (HIGH confidence)

- `https://github.com/supabase/storage-py/blob/main/storage3/_sync/file_api.py` — `create_signed_url()` return structure (`"signedURL"` key), `upload()` signature, `remove([paths])` signature verified directly from SDK source
- `https://supabase.com/docs/reference/python/storage-from-upload` — upload parameter names and `file_options` dict format
- `https://supabase.com/docs/reference/python/storage-from-createsignedurl` — `create_signed_url(path, expires_in, options)` signature
- `https://supabase.com/docs/reference/python/storage-from-remove` — `remove(paths: list)` confirmed as list parameter
- `https://fastapi.tiangolo.com/tutorial/request-forms-and-files/` — `UploadFile` + `Form()` pattern for mixed multipart

### Secondary (MEDIUM confidence)

- `https://github.com/supabase/supabase-py` — `from supabase import create_client, Client` import pattern; confirmed by multiple sources
- PyPI `supabase==2.28.0` installed and confirmed via `pip show supabase`

### Tertiary (LOW confidence)

- None — all critical claims were verified from primary or secondary sources.

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — supabase-py 2.28.0 already installed; method signatures verified from SDK source
- Architecture: HIGH — patterns follow established project conventions (sync SQLAlchemy, service layer, Pydantic v2)
- Supabase API signatures: HIGH — verified from storage-py source code, not just documentation
- Pitfalls: HIGH — pitfalls derived from actual SDK behavior and existing project patterns
- Test approach: HIGH — follows existing conftest/auth_client patterns; mocking strategy is standard pytest

**Research date:** 2026-03-04
**Valid until:** 2026-04-04 (supabase-py version pinned in uv.lock; method signatures stable)
