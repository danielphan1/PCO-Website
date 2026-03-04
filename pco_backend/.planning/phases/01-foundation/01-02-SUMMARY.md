---
plan: 01-02
phase: 01-foundation
status: complete
commit: 6d82b30
---

# Plan 01-02 Summary: Config, ORM Models, DB Session

## What Was Built

**Task 1 — Settings hardening + ORM models + session factory:**

- `app/core/config.py`: Pydantic v2 `BaseSettings` with `model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)`, `jwt_secret` has no default (required), `field_validator` enforces ≥32 chars
- New fields: `app_version`, `refresh_token_expire_days`, `supabase_url`, `supabase_service_key`, `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`
- `app/db/base_class.py`: `DeclarativeBase` subclass `Base`
- `app/db/base.py`: Imports all 7 models so `Base.metadata` is fully populated
- 7 ORM models (SQLAlchemy 2.0 `Mapped`/`mapped_column` style):
  - `app/models/user.py`: `users` — id, email, hashed_password, role, is_active, timestamps
  - `app/models/refresh_token.py`: `refresh_tokens` — token, user_id FK, expires_at, revoked
  - `app/models/interest_form.py`: `interest_submissions` — contact fields, metadata as `extra_data` (SA reserved attr)
  - `app/models/event_pdf.py`: `events` — title, file_url, supabase_path, timestamps
  - `app/models/rush_info.py`: `rush_info` — content JSON, active flag
  - `app/models/org_content.py`: `org_content` — key/value content store
  - `app/models/audit_log.py`: `audit_log` — action, user_id FK, target_type, target_id, timestamp
- `app/db/session.py`: `create_engine` with `pool_pre_ping=True`, `SessionLocal`
- `app/core/deps.py`: `get_db()` generator dependency

**Task 2 — Alembic wiring + initial migration:**

- `alembic/env.py`: Imports `Base` from `app.db.base`, sets `target_metadata = Base.metadata`
- `alembic/versions/001_initial_schema.py`: Creates all 7 tables, FK constraints, indexes

## Key Decisions

- `metadata` column renamed to `extra_data` attribute with `name="metadata"` — SQLAlchemy reserves `.metadata` on mapped classes
- `role` field uses string column (not Enum type) for portability
- `pool_pre_ping=True` on engine for connection health in production

## Test Results

```
9 passed, 1 skipped (test_migration requires RUN_MIGRATION_TEST=1)
```

`test_orm_models` PASSED — all 7 models import with correct `__tablename__`
`test_settings_validation` PASSED — short secret raises ValidationError

## Self-Check: PASSED

## key-files.created

- app/core/config.py
- app/db/base_class.py
- app/db/base.py
- app/db/session.py
- app/core/deps.py
- app/models/user.py
- app/models/refresh_token.py
- app/models/interest_form.py
- app/models/event_pdf.py
- app/models/rush_info.py
- app/models/org_content.py
- app/models/audit_log.py
- alembic/versions/001_initial_schema.py
