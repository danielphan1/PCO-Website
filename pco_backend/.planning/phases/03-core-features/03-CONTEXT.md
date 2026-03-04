# Phase 3: Core Features - Context

**Gathered:** 2026-03-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement all core feature endpoints over the working auth layer: member management (admin only),
interest form (public submit / admin list), rush info (public read / admin write), org content
(public read / admin write), and the SMTP email service that backs member creation and interest
form submission. Event PDFs are Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Email — welcome (new member)
- **Full onboarding content**: welcome message, their email, their temp password, and a login URL
- Login URL sourced from `FRONTEND_URL` env var — add to `Settings` class; works for dev and prod
- Non-blocking: sent via FastAPI `BackgroundTasks` (XCUT-04 already specified)

### Email — interest form confirmation
- **Simple acknowledgment only**: "We received your interest form and will reach out soon."
- Non-blocking: sent via FastAPI `BackgroundTasks`

### Email — failure handling
- **Log and swallow**: if the background SMTP task fails, log the error server-side only
- HTTP response is already returned; client and admin are not notified of email failure
- No `email_sent` field in responses

### Org content format
- **Plain text** for all three sections (history, philanthropy, contacts)
- `PUT /v1/content/{section}` accepts and stores raw string; no processing or validation of format
- Frontend handles any display formatting

### Leadership endpoint
- Return **name + role only** per officer: `{"full_name": "...", "role": "president"}`
- **Omit vacant roles**: if no user holds a given officer role, that role does not appear in the response
- Query: `WHERE role IN OFFICER_ROLES AND is_active = true`
- `OFFICER_ROLES` constant already defined in `app/models/user.py`

### Audit log scope
- **All member mutations** write to `audit_log`:
  - Member created (POST /admin/members)
  - Role changed (PATCH /admin/members/{id}/role)
  - Member deactivated (PATCH /admin/members/{id}/deactivate)
  - Member reactivated (PATCH /admin/members/{id}/reactivate)
- Actor is the authenticated admin (`require_admin` dependency provides the user)
- Use existing `AuditLog` model: `actor_id`, `action` (string verb), `target_id` (user UUID), `target_type` ("user")

### Claude's Discretion
- Temp password length and character set (alphanumeric, ~12 chars is reasonable)
- Welcome email subject line and exact body copy (professional tone)
- Confirmation email subject line and exact body copy
- Audit log `action` string values (e.g., "member.created", "member.role_updated", etc.)
- Whether `PUT /v1/rush` upserts a single row or errors if no row exists yet

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/core/deps.py` — `get_current_user` and `require_admin` deps ready for all protected routes
- `app/models/user.py` — `OFFICER_ROLES` and `ALL_ROLES` constants defined; use directly for leadership query and role validation
- `app/models/audit_log.py` — `AuditLog` model complete with `actor_id`, `action`, `target_id`, `target_type`, `extra_data`; `actor` relationship back to `User`
- `app/models/rush_info.py` — `RushInfo` model with `dates`, `times`, `locations`, `description`, `is_published`
- `app/models/org_content.py` — `OrgContent` model with `section` (unique string key) + `content` (Text)
- `app/models/interest_form.py` — `InterestSubmission` model with all required fields: `name`, `email`, `phone`, `year`, `major`
- `app/services/user_service.py`, `interest_service.py`, `auth_service.py` — empty stubs, ready to fill
- `app/api/v1/admin/users.py`, `app/api/v1/interest.py`, `app/api/v1/events.py` — stub routers registered

### Established Patterns
- Synchronous SQLAlchemy (`Session` from `get_db()`) — all services use sync DB calls
- Pydantic v2 schemas in `app/schemas/` — one file per domain, `model_config`, `@field_validator`
- Error format from Phase 1: `HTTPException(status_code=N, detail="...")` normalized by global handler
- 401 for auth failures, 403 for role failures (Phase 2 decisions carry forward)
- Route prefix: all routes under `/v1/` (already wired)

### Integration Points
- `app/api/v1/admin/users.py` — member management endpoints go here (already stubbed)
- `app/api/v1/interest.py` — interest form endpoints (already stubbed)
- New files needed: `app/api/v1/rush.py`, `app/api/v1/content.py` — not yet created
- `app/api/router.py` — must register rush and content routers
- New service needed: `app/services/email_service.py` — SMTP via `aiosmtplib` (already in deps per INFRA-02)
- `app/core/config.py` — add `FRONTEND_URL` to `Settings` class

</code_context>

<specifics>
## Specific Ideas

- Welcome email must include temp password clearly — admin is handing account creation off to email
- Login URL from `FRONTEND_URL` env var so the same codebase works in dev (localhost:3000) and prod
- Leadership returns only active officers (is_active=true) with officer roles — vacant roles silently omitted

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-core-features*
*Context gathered: 2026-03-04*
