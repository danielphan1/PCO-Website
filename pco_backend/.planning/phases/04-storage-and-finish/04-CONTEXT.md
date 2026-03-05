# Phase 4: Storage and Finish - Context

**Gathered:** 2026-03-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement Supabase Storage integration for event PDFs: list (authenticated), upload (admin), and
delete (admin). Write the project README. No new auth logic, no new DB models — EventPDF model and
stubs already exist from prior phases.

</domain>

<decisions>
## Implementation Decisions

### Signed URLs
- Signed URLs generated **at list time**: GET /v1/events returns each event with a pre-generated
  signed URL embedded in the response — no separate URL endpoint needed
- Expiry: **1 hour** — fresh URLs are generated on every list request anyway
- If Supabase signed URL generation fails for one event: return `url: null` for that event; do not
  fail the whole request or omit the event — frontend can show an "unavailable" state

### Upload request shape
- POST /v1/admin/events accepts **multipart/form-data** with three fields: `file` (PDF binary),
  `title` (string), `date` (YYYY-MM-DD)
- On success: return the **full event record with signed URL** — `{id, title, date, url, created_at}`
  (same shape as list response)
- **Storage-first write order**: upload to Supabase Storage first; if DB write fails, delete the
  file from storage and return 500 — no orphaned files, no DB records pointing to missing files

### Event list response
- GET /v1/events sorted by **event date, newest first** (the `date` field, not `created_at`)
- Each item includes: `id`, `title`, `date`, `url` — no admin-internal fields (uploaded_by,
  created_at) exposed to authenticated members
- No pagination — return all events (v1 scope)

### Delete behavior
- DELETE /v1/admin/events/{id}: **best-effort storage deletion** — attempt to remove from Supabase
  Storage, log any storage error, then always delete the DB record and return 200
  (admin intent is honored even if the file was already manually removed from storage)

### README
- **Audience**: future developer taking over the project
- **Sections** (per XCUT-06): setup instructions, environment variable reference, architecture
  overview, link to /docs
- **Also include**: high-level endpoint table (method, path, auth required, one-line description)
- **Setup section**: Docker workflow only (`docker compose up`) — reference a `.env.example` file
  for environment variables
- Tone: concise and practical, not a tutorial

### Claude's Discretion
- Storage path format in Supabase (e.g., `events/{uuid}.pdf` — use existing `app/storage/paths.py`)
- Supabase-py 2.x exact method signatures for upload, signed URL, and remove (researcher must verify)
- .env.example file contents (mirrors Settings fields with placeholder values)
- README architecture section depth (a paragraph is fine — no diagrams required)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/models/event_pdf.py` — `EventPDF` model complete: `id`, `title`, `date`, `storage_path`,
  `uploaded_by`, `created_at`. Ready to use — no model changes needed.
- `app/schemas/event.py` — Empty stub. Add `EventCreate`, `EventResponse` schemas here.
- `app/services/event_service.py` — Empty stub. `StorageService` wrapper and event CRUD logic go here.
- `app/storage/files.py`, `app/storage/paths.py` — Empty stubs. Storage client init and path
  helpers (e.g., `events/{uuid}.pdf`) go here.
- `app/api/v1/events.py` — Stub router returning `{"events": []}`. Replace with real list endpoint.
- `app/api/v1/admin/events.py` — Stub router with upload/delete placeholders. Replace with real logic.
- `app/tests/test_events.py` — Empty. All event endpoint tests go here.
- `app/core/deps.py` — `get_current_user` and `require_admin` already wired and ready.
- `app/core/config.py` — `Settings` already has `supabase_url` and `supabase_service_key`.

### Established Patterns
- Synchronous SQLAlchemy (`Session` from `get_db()`) — all service calls are sync
- Pydantic v2 schemas in `app/schemas/` — `model_config`, `@field_validator`
- Error format: `HTTPException(status_code=N, detail="...")` normalized by global handler
- 401 for bad/missing token, 403 for role failures — same as prior phases
- Service layer owns business logic; router calls service; service owns DB + storage interaction

### Integration Points
- `app/api/router.py` — `events` and `admin_events` routers already registered; no changes needed
- `app/storage/` package — initialize supabase-py client here; `app/storage/files.py` wraps upload,
  signed URL generation, and remove operations
- `supabase_url` + `supabase_service_key` from `settings` feed into the Supabase client init

### Known Risk
- **supabase-py 2.x method signatures are MEDIUM confidence** — researcher must verify current
  `upload()`, `create_signed_url()`, and `remove()` parameter formats against SDK changelog before
  implementing `StorageService`

</code_context>

<specifics>
## Specific Ideas

- `storage_path` stores relative path only (e.g., `events/{uuid}.pdf`) — decided in Phase 1.
  Supabase Storage bucket is **private**; signed URLs are the only valid access mechanism.
- Signed URL expiry of 1 hour aligns with the fact that a fresh signed URL is generated every time
  the member loads the event list — no expectation of bookmarkable links.
- Upload response returns same shape as list items so frontend can optimistically prepend the new
  event without re-fetching the list.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-storage-and-finish*
*Context gathered: 2026-03-04*
