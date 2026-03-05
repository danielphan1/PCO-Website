# Milestones

## v1.0 MVP (Shipped: 2026-03-05)

**Phases completed:** 4 phases, 11 plans
**Timeline:** 2026-03-03 — 2026-03-05 (2 days)
**Stats:** 3,029 Python LOC across 64 files | 239 files changed

**Key accomplishments:**
- Hardened FastAPI scaffold: PyJWT, 7 ORM models, Alembic migrations, Pydantic v2 Settings, Docker/PostgreSQL, global exception handlers, ruff linting
- Secure authentication: bcrypt (direct, passlib removed), timing-safe login, refresh token rotation, JWT Bearer validation with get_current_user + require_admin RBAC deps
- Member management: full admin CRUD (list/create/role/deactivate/reactivate) with audit logging, atomic refresh token revocation, non-blocking SMTP via BackgroundTasks
- Core features: interest form (dup detection + confirmation email), rush info (publish/hide toggle), org content (history, philanthropy, contacts, leadership from users table)
- Event PDF storage: Supabase Storage integration with lazy client init, 10MB limit, PDF magic byte validation, full 11-test suite
- Documentation: README with Docker setup, environment variable reference, architecture overview, API endpoint table; .env.example

**Archive:** `.planning/milestones/v1.0-ROADMAP.md`

---
