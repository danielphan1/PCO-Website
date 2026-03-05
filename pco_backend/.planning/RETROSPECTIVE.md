# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.0 — MVP

**Shipped:** 2026-03-05
**Phases:** 4 | **Plans:** 11 | **Timeline:** 2 days (2026-03-03 → 2026-03-05)

### What Was Built
- Full JWT authentication: bcrypt login, refresh token rotation with replay prevention, RBAC deps (get_current_user + require_admin)
- Admin member management: CRUD with audit logging, atomic refresh token revocation on deactivation, non-blocking SMTP emails
- Three content domains: interest form (dup detection), rush info (publish/hide), org content (5 endpoints incl. leadership from users table)
- Supabase Storage integration for event PDFs: lazy client init, 10MB limit, PDF magic byte validation
- 68 automated pytest tests, all passing; ruff zero violations; full Docker + PostgreSQL setup

### What Worked
- Strict dependency-first phase ordering (Foundation → Auth → Features → Storage) eliminated integration surprises — no phase had to reach back to fix a prior phase
- Wave-based test scaffolding (Wave 0 stubs before implementation) made RED→GREEN cycles predictable and fast
- BackgroundTasks pattern for SMTP was clean: HTTP response not blocked, failures log-and-swallow, no test complexity
- Lazy Supabase client init pattern elegantly solved the test isolation problem without mocking at the module level

### What Was Inefficient
- Phase 2 VERIFICATION.md was missing (VALIDATION.md existed but is a different artifact) — discovered at milestone completion rather than during phase execution; retroactive reconstruction was straightforward but could have been caught earlier
- Phase 1 ROADMAP.md checkboxes and REQUIREMENTS.md checkboxes had doc-only inconsistencies that accumulated; a post-phase doc cleanup step would prevent audit noise
- STATE.md progress percentage stuck at 8% throughout despite all phases completing — STATE.md updates not keeping pace with execution

### Patterns Established
- bcrypt direct (not passlib) for password hashing — passlib 1.7.4 + bcrypt 5.0.0 is broken upstream
- `_dummy_verify()` pattern: always run bcrypt.checkpw even when user not found to prevent timing-based user enumeration
- Refresh token rotation: insert new row BEFORE revoking old in single commit — client retains old token if DB fails mid-way
- SHA-256 for refresh token storage (not bcrypt): 256-bit token entropy makes brute-force pre-image infeasible
- Lazy client init pattern: `_get_client()` method on service classes avoids import-time failures when credentials are empty in test env
- Route ordering in FastAPI: static paths (`/leadership`) must be defined before parameterized paths (`/{section}`) to prevent path capture

### Key Lessons
1. **VERIFICATION.md vs VALIDATION.md are distinct artifacts** — VALIDATION.md is the pre-execution Nyquist strategy; VERIFICATION.md is the post-execution results report. Both must exist for audit to pass.
2. **Import-time initialization is a test anti-pattern** — any service that calls external APIs at import time will break test collection; lazy init via `_get_client()` is the correct pattern.
3. **UUID handling requires explicit conversion in SQLAlchemy** — JWT `sub` claim returns strings; `UUID(as_uuid=True)` columns require `uuid.UUID` objects; always convert explicitly.
4. **Startup environment validation should be eager** — SUPABASE_URL validation at startup (like jwt_secret) prevents silent 500s on first storage operation in production.
5. **GSD dependency-first phasing works well for backends** — phases that deliver complete vertical slices with tests are easier to verify and build upon than horizontal layers.

### Cost Observations
- Model: sonnet (balanced profile throughout)
- Sessions: ~5 sessions across 2 days
- Notable: 11 plans in 2 days at ~4-6 min/plan suggests the plan quality was high — little back-and-forth or rework per plan

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | ~5 | 4 | Initial baseline — dependency-first ordering, Wave 0 test scaffolding |

### Cumulative Quality

| Milestone | Tests | Zero-Dep Additions |
|-----------|-------|--------------------|
| v1.0 | 68 passing | bcrypt (direct), PyJWT, aiosmtplib, supabase-py, pydantic[email] |

### Top Lessons (Verified Across Milestones)

1. Distinguish VERIFICATION.md from VALIDATION.md — different lifecycle, different content
2. Lazy init for external service clients prevents import-time test failures
