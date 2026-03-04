# Phase 2: Authentication - Context

**Gathered:** 2026-03-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement JWT-based authentication: login, refresh, and /me endpoints; bcrypt password hashing; JWT sign/verify utilities; and `get_current_user` + `require_admin` FastAPI dependencies. No member management (create/deactivate/reactivate) — that is Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Refresh token strategy
- **Rotate on every refresh** — `POST /api/auth/refresh` issues a new refresh token and revokes the old one
- If a revoked refresh token is replayed (possible theft): return 401 silently — no escalation, no mass-revocation
- Old token is marked `revoked=True` in DB; new token row inserted before responding

### Token response shape
- Login and refresh both return the same minimal shape: `{ access_token, refresh_token, token_type: "bearer" }`
- No user info embedded in login response — frontend calls `GET /api/users/me` separately if it needs name/role

### Error messages
- Bad credentials (wrong email OR wrong password): single vague message `"Invalid email or password"` — prevents email enumeration
- Deactivated user attempting login or refresh: `"Account is deactivated"` with **403** status
- Bad/expired/missing access token: **401** status
- Non-admin hitting an admin route: **403** status

### HTTP status codes
- 401: bad credentials, expired access token, missing/invalid Bearer token
- 403: deactivated account, insufficient role (non-admin on admin routes)
- 422: request body validation failures (FastAPI default, already normalized by Phase 1 error handlers)

### Token cleanup
- No cleanup in Phase 2 — expired and revoked refresh tokens accumulate in the DB
- Scheduled cleanup deferred to v2

### Claude's Discretion
- JWT payload fields (sub, role, exp, iat — standard claims)
- Exact bcrypt cost factor (passlib default is fine)
- Whether `get_current_user` also validates `is_active` inline or delegates to a separate check
- Access token expiry: use `access_token_expire_minutes` from Settings (currently 60 min)
- Refresh token expiry: use `refresh_token_expire_days` from Settings (currently 30 days)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/core/security.py` — Empty stub explicitly waiting for Phase 2. Fill with `create_access_token`, `decode_access_token`, `hash_password`, `verify_password`. PyJWT and passlib[bcrypt] already installed.
- `app/core/deps.py` — Has `get_db()` already. Phase 1 context explicitly notes: "Phase 2 adds `get_current_user` and `require_admin` here."
- `app/core/config.py` — `Settings` has `jwt_secret`, `jwt_alg`, `access_token_expire_minutes`, `refresh_token_expire_days` all ready.
- `app/models/user.py` — `User` model complete with `is_active`, `role`, `hashed_password`. `OFFICER_ROLES` and `ALL_ROLES` constants defined.
- `app/models/refresh_token.py` — `RefreshToken` model complete: `token_hash`, `expires_at`, `revoked`, `user_id` FK.
- `app/api/v1/auth.py` — Stub router with placeholder `/login`. Replace the stub body.
- `app/schemas/auth.py` — Empty file. Add `LoginRequest`, `TokenResponse`, `RefreshRequest` schemas here.

### Established Patterns
- Synchronous SQLAlchemy (`Session` from `get_db()`) — no async
- All routes under `/v1/` prefix (already wired in `app/api/router.py`)
- Pydantic v2 schemas (`model_config`, `@field_validator`)
- Error format from Phase 1: `{"detail": "...", "status_code": N}` — use `HTTPException` with matching detail strings

### Integration Points
- `app/core/deps.py` — `get_current_user` and `require_admin` dependencies live here; all protected routers import from here
- `app/api/v1/auth.py` — Login + refresh endpoints (already registered in router)
- New file needed: `app/api/v1/users.py` — `GET /api/users/me` endpoint (not yet stubbed)
- `app/api/router.py` — May need `users` router registered (check current state)

</code_context>

<specifics>
## Specific Ideas

- Token rotation means the DB write pattern on refresh is: insert new row → mark old row revoked → return new tokens. If the DB write fails, the client keeps the old token (no partial state).
- Refresh token stored as a hash in DB (same pattern as hashed passwords) — raw token returned to client, hash stored.

</specifics>

<deferred>
## Deferred Ideas

- Refresh token cleanup / expiry purge — Phase 2 leaves expired rows in DB; scheduled cleanup is a v2 concern
- Explicit logout endpoint (invalidate refresh token) — v2 requirement (AUTH-V2-02)
- User-initiated password change — v2 requirement (AUTH-V2-01)

</deferred>

---

*Phase: 02-authentication*
*Context gathered: 2026-03-04*
