# Domain Pitfalls

**Domain:** FastAPI REST API — JWT auth, RBAC, Supabase Storage, file uploads, SMTP email, SQLAlchemy, Alembic
**Project:** PCO San Diego Backend API
**Researched:** 2026-03-03
**Confidence:** HIGH (grounded in this codebase's specific scaffold + established FastAPI/SQLAlchemy patterns)

---

## Critical Pitfalls

Mistakes that cause rewrites, security breaches, or broken production deploys.

---

### Pitfall 1: JWT Secret Has a Weak Default That Survives to Production

**What goes wrong:** The current `app/core/config.py` defines `jwt_secret: str = "change-me"`. Pydantic Settings will happily use this default if `JWT_SECRET` is absent from the environment. A developer copies `.env.example` to `.env`, forgets to set the secret, and the service starts fine. In production, the service starts with a predictable key. Anyone can forge valid JWTs.

**Why it happens:** Pydantic Settings `BaseSettings` treats all field defaults as valid. There is no startup assertion that crashes the application when a sentinel value is used. The `.env.example` may have a placeholder that looks real.

**Consequences:** Fully forged admin tokens. Any user can become admin by crafting a token with `"role": "admin"`. Complete authentication bypass.

**Prevention:**
- Remove the default entirely: `jwt_secret: str` (no default). Pydantic Settings will raise `ValidationError` at startup if `JWT_SECRET` is missing.
- Add a startup validator that rejects values shorter than 32 characters:
  ```python
  @field_validator("jwt_secret")
  @classmethod
  def secret_must_be_strong(cls, v: str) -> str:
      if len(v) < 32:
          raise ValueError("JWT_SECRET must be at least 32 characters")
      return v
  ```
- Generate the secret with `openssl rand -hex 32` and document this in the README.

**Detection:** Start the service with no `.env` file. If it starts without error, the default is being used. Check: `settings.jwt_secret == "change-me"`.

**Phase:** Auth implementation (foundation phase). Fix before writing a single line of JWT logic.

---

### Pitfall 2: Refresh Token Has No Expiry Config and Is Not Revocable

**What goes wrong:** The current config has `access_token_expire_minutes: int = 60` but no `refresh_token_expire_days` setting. Refresh tokens are typically long-lived (7-30 days). If issued without an expiry claim, `python-jose` will decode them as valid indefinitely. More critically, there is no refresh token store in the planned schema — if a user is deactivated, their existing refresh token can still mint new access tokens.

**Why it happens:** Developers implement the refresh endpoint before thinking through revocation. The token itself is self-contained (JWT), so revocation requires out-of-band state. This is easy to overlook when the focus is "make the endpoint work."

**Consequences:** A deactivated member can continue accessing the API until their refresh token naturally expires (never, if expiry was omitted). Admin revoking a user has no immediate effect.

**Prevention:**
- Store refresh tokens as opaque hashed values in a `refresh_tokens` database table with columns: `id`, `user_id`, `token_hash`, `expires_at`, `revoked_at`.
- Add `REFRESH_TOKEN_EXPIRE_DAYS` to `Settings` with a sensible default (e.g., 30).
- On `POST /v1/auth/refresh`, look up the token hash in the table before decoding the JWT. If `revoked_at IS NOT NULL` or `expires_at < NOW()`, return 401.
- On user deactivation (`PATCH /v1/admin/members/{id}/deactivate`), mark all of that user's refresh tokens as revoked in the same database transaction.
- On successful token refresh, optionally rotate: delete the old token row and issue a new one (refresh token rotation).

**Detection:** Deactivate a test user. Exchange their refresh token for a new access token. If you get 200, revocation is not working.

**Phase:** Auth implementation. The `refresh_tokens` table must be in the initial Alembic migration.

---

### Pitfall 3: python-jose Has Known Vulnerabilities; Use PyJWT Instead

**What goes wrong:** `pyproject.toml` specifies `python-jose[cryptography]>=3.3`. The `python-jose` library has had multiple CVEs (including algorithm confusion attacks) and has been largely unmaintained since 2021. Its last release was 3.3.0 in 2021. It is vulnerable to `alg: none` attacks if `algorithms` is not explicitly passed to `decode()`.

**Why it happens:** `python-jose` has historically been the FastAPI-docs-recommended library. Many tutorials still use it. The FastAPI official docs updated their recommendation to `PyJWT` but existing projects copy from older examples.

**Consequences:** If `decode()` is called without the `algorithms` parameter, an attacker sends a token with `"alg": "none"` and bypasses verification entirely. Forged tokens accepted.

**Prevention:**
- Replace `python-jose` with `PyJWT`:
  ```
  # Remove: python-jose[cryptography]>=3.3
  # Add: PyJWT>=2.8
  ```
- Always pass `algorithms=["HS256"]` explicitly to `jwt.decode()`:
  ```python
  payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
  ```
- Never pass `options={"verify_signature": False}` outside of tests.

**Detection:** Run `pip-audit` or `uv run pip-audit`. Check python-jose CVE database entries.

**Phase:** Before auth implementation. Swap the library first, then build on top of PyJWT.

---

### Pitfall 4: bcrypt Timing Attack via Early Username Lookup Failure

**What goes wrong:** A naive login implementation queries the database for the user by email first. If the user doesn't exist, it returns 401 immediately — skipping the bcrypt comparison. An attacker can distinguish "user doesn't exist" (fast response, ~1ms) from "wrong password" (slow response, ~100ms bcrypt). This leaks whether an email address is registered.

**Why it happens:** The natural control flow is "find user → if not found, 401 → verify password → if wrong, 401." The fast path on user-not-found is not obviously different from the perspective of the developer.

**Consequences:** Email enumeration. An attacker can determine which email addresses have accounts, then target them for credential stuffing or phishing.

**Prevention:**
- Always run bcrypt even when the user is not found. Use a dummy hash:
  ```python
  DUMMY_HASH = "$2b$12$..." # pre-computed bcrypt hash of a dummy password

  user = db.query(User).filter(User.email == email).first()
  candidate_hash = user.password_hash if user else DUMMY_HASH
  pwd_context.verify(plain_password, candidate_hash)
  if not user or not verified:
      raise HTTPException(status_code=401, detail="Invalid credentials")
  ```
- Return the same HTTP status and body for "no user" and "wrong password": `{"detail": "Invalid credentials"}` — never `"User not found"`.
- Add a consistent minimum response time via `asyncio.sleep()` if sub-millisecond paths are a concern (rarely needed at this scale).

**Detection:** Time 100 login requests for a nonexistent email vs. 100 for an existing email with wrong password. If p50 latency differs by >50ms, the timing attack is viable.

**Phase:** Auth implementation.

---

### Pitfall 5: SQLAlchemy Session Not Closed on Exception — Connection Pool Exhaustion

**What goes wrong:** The standard FastAPI dependency injection pattern for SQLAlchemy uses a generator:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
If this `finally` is missing, or if the session is created outside a dependency (e.g., as a module-level object or in a service directly), sessions leak. PostgreSQL has a default of 100 connections. Under load, the pool exhausts and every new request fails with `OperationalError: too many connections`.

**Why it happens:** Services that need database access sometimes receive the session directly via the dependency, but then pass it into nested function calls. If an exception is raised inside a nested call and not caught, the generator still closes the session — but if someone creates `SessionLocal()` directly inside a service function, that session never closes.

**Consequences:** Connection pool exhaustion. `psycopg.OperationalError: connection pool exhausted`. All database operations fail. Requires service restart to recover.

**Prevention:**
- Only ever create sessions via the `get_db()` dependency. Never call `SessionLocal()` directly in service code.
- Use `with` statements or context managers for any session not managed by FastAPI's dependency injection.
- Set `pool_size=5, max_overflow=10` on the engine for this low-traffic app — fail fast rather than queue indefinitely.
- Enable `pool_pre_ping=True` on the engine to detect stale connections.
- In `app/db/session.py`:
  ```python
  engine = create_engine(
      settings.database_url,
      pool_size=5,
      max_overflow=10,
      pool_pre_ping=True,
  )
  SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  ```

**Detection:** Run 200 concurrent requests to any DB-backed endpoint with a connection pool of 10. If the error rate rises sharply, sessions are leaking.

**Phase:** Database foundation (before any endpoint implementation). Establish the session pattern first and enforce it as a convention.

---

### Pitfall 6: Async Endpoint with Sync SQLAlchemy Blocks the Event Loop

**What goes wrong:** The FastAPI scaffold uses `async def` for all endpoints. The current plan uses sync SQLAlchemy (via `create_engine`, not `create_async_engine`) with psycopg3. Calling synchronous SQLAlchemy `session.query()` or `session.execute()` inside an `async def` endpoint blocks the event loop for the duration of each DB round-trip. Under concurrent load, one slow query freezes all request handling.

**Why it happens:** FastAPI allows mixing sync and async routes. Using `async def` with a sync ORM feels fine in single-user testing — the blocking happens transparently. psycopg3 supports both sync and async modes, making it easy to configure the wrong one.

**Consequences:** Concurrency collapses to ~1 effective thread. A 200ms query in an `async def` handler means no other requests can be served for 200ms.

**Prevention — Option A (recommended for this project):** Use sync SQLAlchemy with sync `def` endpoints. FastAPI runs sync endpoints in a thread pool, so blocking is safe. No `asyncio` footguns.

**Prevention — Option B:** Use `create_async_engine` with `AsyncSession` and psycopg3 async driver (`postgresql+psycopg_async://...`). Requires `await` on all DB calls. More complex but fully non-blocking.

**Recommendation:** For this project (low traffic, small team), use Option A — sync endpoints with sync SQLAlchemy. The complexity of async ORM is not justified. Change `async def` to `def` for all DB-accessing endpoints.

**Detection:** Add a 500ms sleep to a DB query and measure API response time under concurrent load. If other requests also slow by 500ms, blocking is occurring.

**Phase:** Database foundation. Decide sync vs. async before writing any service code.

---

### Pitfall 7: Alembic autogenerate Misses Column Changes Silently

**What goes wrong:** `alembic revision --autogenerate` compares the SQLAlchemy model metadata against the live database schema. It misses: (1) server-side defaults that differ from SQLAlchemy defaults, (2) CHECK constraints, (3) changes to existing indexes if not reflected in metadata, (4) column type changes between compatible types (e.g., `String(50)` → `String(100)` may be ignored). A developer runs autogenerate, sees "No changes detected," and assumes the schema is current — but the database is out of sync.

**Why it happens:** Autogenerate's scope is limited by design. It's a helper, not a complete schema differ. PostgreSQL has features (partial indexes, custom types, RLS policies) that Alembic cannot introspect.

**Consequences:** Production migrations run successfully but miss columns. Runtime errors like `psycopg.errors.UndefinedColumn` appear only when that code path is hit.

**Prevention:**
- Always review the generated migration file before committing. Do not treat `--autogenerate` as authoritative.
- Write the initial migration manually to ensure all tables, indexes, and constraints are correct. This is one migration — the cost is low.
- Add `compare_type=True` and `compare_server_default=True` to `alembic/env.py`'s `context.configure()` call to catch more differences.
- Run `alembic upgrade head` against a fresh database in CI as a smoke test.
- Never edit a migration file after it has been applied to any environment. Create a new migration instead.

**Detection:** After applying migrations, run `alembic check` (Alembic 1.9+). If it reports differences, autogenerate missed something.

**Phase:** Initial schema migration. Review every generated file before committing.

---

### Pitfall 8: Alembic Migration Conflicts from Parallel Branches

**What goes wrong:** Two developers (or two feature branches) both run `alembic revision --autogenerate` in the same sprint. Both migrations reference the same `head`. When merged, Alembic sees two heads and refuses to run `upgrade head` — or worse, applies them in an arbitrary order, corrupting schema state.

**Why it happens:** Small teams often have only one developer, so this seems irrelevant. But it happens with yourself too: creating a branch, adding a migration, switching back to main, adding another migration, then trying to merge.

**Consequences:** `alembic upgrade head` fails with `Multiple head revisions are present`. Database is in an ambiguous state. Requires manual `alembic merge heads` which may silently accept incompatible schema changes.

**Prevention:**
- For this project (solo or small team), use a linear migration strategy: only one branch creates migrations at a time.
- Prefix migration filenames with timestamps (Alembic default) to make ordering unambiguous.
- If a merge is needed: `alembic merge -m "merge heads" <rev1> <rev2>` creates a merge point, then review the result carefully.
- In CI, run `alembic heads` and fail if it returns more than one revision.

**Detection:** `alembic heads` returns multiple lines. `alembic upgrade head` fails.

**Phase:** Initial schema migration. Establish the single-head convention from the start.

---

### Pitfall 9: Supabase Storage Auth — Bucket Is Accidentally Public

**What goes wrong:** Supabase Storage buckets have a public/private toggle. A developer creates the bucket, enables "public" for easy testing (to get direct URLs without generating signed URLs), and forgets to switch it to private. Event PDFs are now downloadable by anyone with the URL pattern — no authentication required.

**Why it happens:** During development, signed URL generation adds complexity. Developers take the shortcut of public buckets to iterate faster. The bucket stays public.

**Consequences:** Event PDFs (which may contain member-sensitive info like contact lists or calendars) are publicly accessible. The authentication gate on `GET /v1/events` is bypassed entirely.

**Prevention:**
- Create the Supabase Storage bucket as **private** from day one. Never flip it to public even temporarily.
- All file access must go through the API: the API fetches from Supabase Storage using the service role key and streams the file to the client, or generates a short-lived signed URL (1-5 minutes).
- Store only the Supabase file path in the database (e.g., `events/2024-spring-schedule.pdf`), not a pre-signed URL.
- Bucket policy: only the service role can read/write. Row-level security (RLS) in Supabase should deny anon/authenticated roles from direct bucket access.

**Detection:** Upload a file via the API. Attempt to access `https://<project>.supabase.co/storage/v1/object/public/<bucket>/<path>` without any auth header. If you get the file, the bucket is public.

**Phase:** Supabase Storage integration phase. Configure bucket permissions before writing upload code.

---

### Pitfall 10: Supabase Service Role Key Exposed in Docker Environment

**What goes wrong:** The Supabase service role key (not the anon key) has full database and storage access, bypassing Row-Level Security entirely. If this key appears in: a committed `.env` file, Docker Compose environment overrides checked into git, application logs, or error responses — it's a complete Supabase project compromise.

**Why it happens:** Developers add the service key to Docker Compose for convenience during development. Docker Compose files are often committed. Environment variable values sometimes appear in log output during initialization.

**Consequences:** Anyone with the service role key can read/write/delete all data and files in the Supabase project. No RLS protections apply.

**Prevention:**
- `.env` must be in `.gitignore` (verify this is already the case).
- Add `.env.example` with placeholder values like `SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here`.
- Never log environment variables at startup. In `app/core/config.py`, mark the service key field as `exclude=True` if using model export, and override `__repr__` or `__str__` to mask it.
- In Docker Compose, use `env_file: .env` rather than embedding values in the `environment:` block.
- Consider using Docker secrets for production rather than environment variables.

**Detection:** `git log --all -- .env` to check if `.env` was ever committed. Run `docker inspect <container>` to verify env vars are loaded from file, not baked into the image.

**Phase:** Infrastructure foundation and Supabase integration. Check git history before adding credentials.

---

### Pitfall 11: File Upload Validation Bypassed via Content-Type Spoofing

**What goes wrong:** Validating a PDF upload by checking `file.content_type == "application/pdf"` is insufficient. The `Content-Type` header is sent by the client and can be set to any value. A malicious user uploads a shell script or HTML file with `Content-Type: application/pdf`. The file is stored in Supabase, and if served back without the correct `Content-Disposition: attachment` header, a browser may execute it.

**Why it happens:** `file.content_type` is the most obvious thing to check. It works for honest clients. Its insufficiency is not obvious until an attack is demonstrated.

**Consequences:** Stored XSS if HTML files are served inline. Potential for malware distribution if the API serves files without forcing download. Path traversal if filenames are used as-is.

**Prevention:**
- Read the first 4 bytes of the uploaded file and check for the PDF magic bytes: `%PDF` (`0x25 0x50 0x44 0x46`). This cannot be spoofed.
  ```python
  header = await file.read(4)
  await file.seek(0)
  if header != b"%PDF":
      raise HTTPException(status_code=422, detail="File must be a valid PDF")
  ```
- Also enforce size limit before reading content (check `content_length` header or read in chunks and abort at 10MB):
  ```python
  MAX_SIZE = 10 * 1024 * 1024  # 10MB
  contents = await file.read(MAX_SIZE + 1)
  if len(contents) > MAX_SIZE:
      raise HTTPException(status_code=413, detail="File exceeds 10MB limit")
  ```
- Generate a UUID-based storage filename: `f"{uuid4()}.pdf"`. Never use the user-provided filename as the storage path.
- When serving the file URL or signed URL, ensure `Content-Disposition: attachment; filename="..."` is set so browsers download rather than render.

**Detection:** Upload a `.html` file renamed to `.pdf` with `Content-Type: application/pdf`. If the API accepts it, validation is client-side only.

**Phase:** Events/file upload implementation.

---

### Pitfall 12: uvicorn Has No Built-in Request Size Limit — Multipart Ignored

**What goes wrong:** FastAPI/uvicorn does not enforce a global request body size limit. The 10MB PDF limit in the project requirements must be enforced in application code. Without this, an attacker can upload an arbitrarily large file, consuming memory and disk. A 4GB upload will hold a uvicorn worker thread for the full upload duration.

**Why it happens:** Web framework developers assume the reverse proxy (nginx, Caddy) enforces size limits. If the API is exposed directly (Docker without a reverse proxy), there is no upstream protection.

**Consequences:** Memory exhaustion. Denial of service. Uvicorn worker killed by OOM.

**Prevention:**
- Enforce the size limit in application code (see Pitfall 11 above — read up to `MAX_SIZE + 1` bytes and reject if exceeded).
- In production, put nginx or Caddy in front of uvicorn with `client_max_body_size 11M` (slightly above the app limit to avoid confusing errors).
- In Docker Compose, do not expose uvicorn directly on port 80/443. Expose nginx, which proxies to uvicorn.

**Detection:** Send a 50MB request body to the upload endpoint with no application-level check. Measure memory usage during upload.

**Phase:** Events/file upload implementation. Also consider in deployment/infra setup.

---

### Pitfall 13: SMTP Credentials Sent in Plaintext Logs or Error Responses

**What goes wrong:** SMTP exceptions (authentication failures, connection timeouts) often include the credential-containing connection string in their message. If `smtplib.SMTPAuthenticationError` is caught and its message is passed to an HTTPException, the SMTP password appears in the 500 response body and in application logs.

**Why it happens:** Python's `smtplib` error messages include server responses that sometimes echo back the AUTH command. Developers catch the exception and pass `str(e)` to error responses for debugging.

**Consequences:** SMTP credentials exposed in logs (often shipped to a logging service) and API responses. Credential compromise.

**Prevention:**
- Catch SMTP exceptions specifically and return a generic error:
  ```python
  except smtplib.SMTPException as e:
      logger.error("SMTP failure", exc_info=True)  # Full detail in logs only
      raise HTTPException(status_code=500, detail="Email delivery failed")
  ```
- Never include `str(e)` from network/auth exceptions in HTTP responses.
- Configure log levels to only include sensitive details at DEBUG level, disabled in production.
- Use `email_password: SecretStr` in `Settings` (Pydantic's `SecretStr` masks the value in `repr()` and logging).

**Detection:** Misconfigure SMTP credentials intentionally. Trigger an email send. Check the HTTP response body and log output for credential strings.

**Phase:** SMTP email integration.

---

### Pitfall 14: RBAC Enforced Only at the Route Level — Not in the Service Layer

**What goes wrong:** Role checking is added as a FastAPI dependency on each router: `Depends(require_admin)`. A developer later adds a new service function or a background task that calls `user_service.create_user()` directly, bypassing the router entirely. The authorization check is invisible at the service level.

**Why it happens:** FastAPI's dependency injection is route-scoped. It's the natural place to put auth. But as the codebase grows, services get called from non-route contexts (background jobs, admin scripts, tests). The route-level guard is absent in those contexts.

**Consequences:** Privilege escalation. Background tasks or CLI scripts that call service functions have full access regardless of the caller's identity.

**Prevention:**
- For this project's size, route-level dependencies are sufficient — but document the convention explicitly: "all service functions assume the caller has already been authorized."
- Pass the `current_user` object into service functions: `user_service.create_member(db, current_user, payload)`. The service can assert `current_user.role == "admin"` as a secondary check.
- Never call service functions from background tasks that mutate data without passing an explicit actor context.

**Detection:** Call a service function directly in a test without setting up auth. Verify what happens.

**Phase:** Auth/RBAC implementation. Establish the service function signature convention before writing any service.

---

### Pitfall 15: CORS allow_origins=["*"] Paired with allow_credentials=True Is Rejected by Browsers

**What goes wrong:** The current `main.py` uses `allow_credentials=True`. If `allow_origins` were ever set to `["*"]` (wildcard), the browser would reject the CORS preflight — the Fetch spec prohibits `Access-Control-Allow-Credentials: true` when `Access-Control-Allow-Origin: *`. The current code parses `cors_origins` from env, which prevents literal `*` — but the risk is in misconfigured environments.

**What is already wrong:** `allow_methods=["*"]` and `allow_headers=["*"]` are overly permissive. These should be restricted to the methods and headers the API actually uses.

**Prevention:**
- Restrict methods: `allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"]`
- Restrict headers: `allow_headers=["Authorization", "Content-Type", "Accept"]`
- Validate that `cors_origins` never contains `"*"` when `allow_credentials=True`:
  ```python
  if "*" in origins and settings.allow_credentials:
      raise RuntimeError("Cannot use wildcard origin with credentials=True")
  ```
- For production, `cors_origins` should contain only the exact production domain. Remove `localhost:3000` from production config.

**Detection:** Check browser devtools Network tab. If preflight responses include `Access-Control-Allow-Methods: *`, tighten the config.

**Phase:** Already partially in place. Fix during auth implementation when CORS behavior becomes testable.

---

### Pitfall 16: Soft-Delete Deactivation Does Not Block Active Sessions

**What goes wrong:** Deactivating a user (`PATCH /v1/admin/members/{id}/deactivate`) sets an `is_active = False` flag in the database. However, that user's existing valid access token (up to 60 minutes old) continues to be accepted. The `get_current_user` dependency decodes the JWT and may not re-query the database for the `is_active` flag — it may trust the token claims alone.

**Why it happens:** JWTs are stateless by design. Checking the database on every request adds a DB round-trip. Developers often skip this check for performance, not realizing it breaks deactivation.

**Consequences:** A deactivated member retains API access for up to `access_token_expire_minutes` (60 minutes default). Combined with token refresh, access could be indefinite.

**Prevention:**
- In `get_current_user`, always query the database to verify the user exists and `is_active == True`:
  ```python
  user = db.query(User).filter(User.id == user_id).first()
  if not user or not user.is_active:
      raise HTTPException(status_code=401, detail="Account inactive")
  ```
- Reduce `access_token_expire_minutes` to 15 minutes (not 60). Shorter access tokens limit the window.
- On deactivation, revoke all refresh tokens for that user (enforced by Pitfall 2's token store).

**Detection:** Deactivate a user. Wait 0 seconds. Make an authenticated request with their token. If 200, the active session check is missing.

**Phase:** Auth implementation. The database check must be in `get_current_user` from day one.

---

## Moderate Pitfalls

---

### Pitfall 17: Interest Form Open/Closed State Lost on Restart

**What goes wrong:** The current `app/api/v1/interest.py` stores open/closed state in a module-level `STATE` dict. Restarting the container resets it to `{"open": True}`. If an admin closes the form before a rush event, a container restart (deploy, crash) silently reopens it.

**Prevention:** Move this flag to a database table or a settings row. A single-row `app_settings` table with a `interest_form_open: bool` column is sufficient. Read it on every request (or cache with a 60-second TTL).

**Phase:** Database foundation. Create the settings table in the initial migration.

---

### Pitfall 18: Temp Password Generation Not Cryptographically Random

**What goes wrong:** When admin creates a new member, a temporary password is generated and emailed. If this uses `random.choice()` or `uuid4()` truncated to 8 chars, the entropy is insufficient. `uuid4()[:8]` has ~32 bits of entropy — brute-forceable.

**Prevention:** Use `secrets.token_urlsafe(16)` (Python stdlib) for all generated credentials. This provides 128 bits of entropy.

```python
import secrets
temp_password = secrets.token_urlsafe(16)
```

**Phase:** Member management implementation.

---

### Pitfall 19: Email Enumeration via Interest Form Duplicate Detection

**What goes wrong:** `POST /api/interest` is supposed to detect duplicate email submissions and return a different response (per the requirement: "duplicate email detection"). If the response differs between "new submission" (201) and "duplicate email" (409 or 200 with "already submitted"), an attacker can enumerate which email addresses have previously expressed interest in PCO.

**Prevention:** Return the same 200/201 response regardless of whether the email is a duplicate. Log the duplicate server-side. Do not tell the client whether the email was seen before. Optionally send the confirmation email again (safe for legitimate users who submit twice).

**Phase:** Interest form implementation.

---

### Pitfall 20: Alembic env.py Imports App Models — Circular Import Risk

**What goes wrong:** `alembic/env.py` must import SQLAlchemy model metadata to enable autogenerate. The standard pattern imports from `app.db.base` which must import all models. If models import from services, and services import from `app.core.config`, a circular import chain can cause `ImportError` during migration runs.

**Prevention:**
- `app/db/base.py` should only contain `Base = declarative_base()` and model imports — no business logic.
- Models must not import from services or core modules other than the Base.
- Alembic `env.py` imports only `Base.metadata` and `settings.database_url`.
- Test: run `alembic history` immediately after adding each model to catch import errors early.

**Phase:** Initial schema migration.

---

## Minor Pitfalls

---

### Pitfall 21: OpenAPI Docs Expose Admin Endpoints in Production

**What goes wrong:** FastAPI's default `/docs` and `/redoc` UI are enabled in all environments. They show every endpoint, including admin-only ones, with full request/response schemas. This is a reconnaissance aid for attackers.

**Prevention:** Disable docs in production:
```python
app = FastAPI(
    docs_url="/docs" if settings.env != "prod" else None,
    redoc_url="/redoc" if settings.env != "prod" else None,
)
```

**Phase:** Infrastructure/main.py configuration. Set this before the first deployment.

---

### Pitfall 22: Pydantic v2 `model_config` vs Old `class Config` Pattern

**What goes wrong:** The existing `app/core/config.py` uses the Pydantic v1 inner `class Config` syntax. Pydantic v2 (which this project uses — `pydantic>=2.7`) deprecates this in favor of `model_config = SettingsConfigDict(...)`. Mixing old and new patterns causes `PydanticUserError` warnings and in some versions, silent misconfigurations.

**Prevention:** Use `SettingsConfigDict` from `pydantic_settings`:
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
    ...
```

**Phase:** Config refactor, before any new settings fields are added.

---

### Pitfall 23: Audit Log Not Written in the Same Transaction as the Change

**What goes wrong:** The requirements include an audit log entry when roles are changed. If the audit log write is a separate database call after the role update, a crash between the two leaves an unaudited change. Conversely, if the audit write fails (disk full, constraint error), the role change may have already committed.

**Prevention:** Write the audit log row in the same database transaction as the change:
```python
db.add(user_audit_log_entry)
db.add(updated_user)
db.commit()  # Both commit atomically or both roll back
```

**Phase:** Member management implementation.

---

### Pitfall 24: PDF Filename in Database Contains Supabase Path — Breaks on Bucket Rename

**What goes wrong:** Storing the full Supabase URL (`https://<project>.supabase.co/storage/v1/...`) in the database means every record is coupled to the Supabase project URL. If the project is migrated or the bucket is renamed, all stored URLs are invalid.

**Prevention:** Store only the relative path within the bucket: `events/uuid.pdf`. Reconstruct the full URL or signed URL at query time using the current Supabase config.

**Phase:** Events/file upload implementation. Decide on storage path convention before writing the first migration.

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|----------------|------------|
| Config & Settings | Weak JWT secret default; old Pydantic v1 `class Config` syntax | Add `field_validator` to reject weak secrets; migrate to `SettingsConfigDict` |
| Database foundation | Session not closed on exception; sync blocking in async endpoints; circular imports in Alembic env.py | Use generator dependency; decide sync vs. async; keep `base.py` import-clean |
| Initial Alembic migration | Autogenerate misses constraints; migration head conflicts | Write initial migration manually; add `compare_type=True`; run `alembic check` in CI |
| Auth implementation | python-jose CVEs; no refresh token expiry; no DB check on deactivated users; timing attack on login | Swap to PyJWT first; add `refresh_tokens` table; always DB-check `is_active` |
| RBAC middleware | Route-level only check bypassed by services; deactivated user retains session | Pass `current_user` into services; shorten access token TTL |
| Member management | Weak temp password entropy; audit log not atomic | Use `secrets.token_urlsafe(16)`; write audit log in same transaction |
| Interest form | Email enumeration via duplicate detection response; in-memory state lost on restart | Return identical response for dup; move state to DB |
| Events/file upload | Content-Type spoofing; no body size limit; public Supabase bucket; full URL stored in DB | Check PDF magic bytes; read with size cap; private bucket; store relative path only |
| SMTP email | Credentials in error responses/logs; SMTP exception message leaks auth details | Catch `SMTPException` specifically; use `SecretStr` for password field |
| Deployment | OpenAPI docs exposed in production; service role key in Docker Compose | Disable docs in prod; use `env_file` in Compose |

---

## Sources

**Confidence: HIGH** — All pitfalls are grounded in:
- Direct inspection of this codebase's scaffold (`app/core/config.py`, `app/main.py`, `app/api/v1/auth.py`, `pyproject.toml`)
- Known CVEs for python-jose (unmaintained since 2021, `alg: none` bypass)
- FastAPI official documentation patterns for session management, CORS, and dependency injection
- SQLAlchemy 2.0 official session lifecycle documentation
- Alembic documentation on `compare_type`, `alembic check`, and head conflicts
- Supabase Storage RLS documentation
- Pydantic v2 migration guide (`SettingsConfigDict` replacing `class Config`)
- Python `smtplib` exception message behavior (stdlib)
- RFC 6749 / JWT RFC 7519 on token lifetimes and revocation
- OWASP: Timing attacks on authentication, email enumeration, file upload validation

---

*Pitfalls audit: 2026-03-03*
