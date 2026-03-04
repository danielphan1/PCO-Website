---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-03
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (not yet installed — Wave 0 installs) |
| **Config file** | none — Wave 0 adds `[tool.pytest.ini_options]` to pyproject.toml |
| **Quick run command** | `pytest app/tests/test_foundation.py -x -q` |
| **Full suite command** | `pytest app/tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `ruff check . && ruff format --check . && pytest app/tests/test_foundation.py -x -q`
- **After every plan wave:** Run `pytest app/tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| deps-install | 01-01 | 0 | INFRA-01, INFRA-02 | smoke | `pytest app/tests/test_foundation.py::test_pyjwt_importable app/tests/test_foundation.py::test_deps_importable -x` | ❌ W0 | ⬜ pending |
| config-hardening | 01-01 | 1 | INFRA-05 | unit | `pytest app/tests/test_foundation.py::test_settings_validation -x` | ❌ W0 | ⬜ pending |
| docker-fix | 01-01 | 1 | INFRA-06 | manual | N/A — manual `docker build && docker compose up` | N/A | ⬜ pending |
| orm-models | 01-02 | 1 | INFRA-03 | unit | `pytest app/tests/test_foundation.py::test_orm_models -x` | ❌ W0 | ⬜ pending |
| alembic-migration | 01-02 | 2 | INFRA-04 | integration | `pytest app/tests/test_foundation.py::test_migration -x` | ❌ W0 | ⬜ pending |
| db-session | 01-02 | 2 | INFRA-03 | unit | `pytest app/tests/test_foundation.py::test_orm_models -x` | ❌ W0 | ⬜ pending |
| security-utils | 01-03 | 1 | INFRA-01 | smoke | `pytest app/tests/test_foundation.py::test_pyjwt_importable -x` | ❌ W0 | ⬜ pending |
| error-handlers | 01-03 | 1 | XCUT-01 | unit | `pytest app/tests/test_foundation.py::test_error_format -x` | ❌ W0 | ⬜ pending |
| cors-config | 01-03 | 1 | XCUT-03 | unit | `pytest app/tests/test_foundation.py::test_cors_headers -x` | ❌ W0 | ⬜ pending |
| openapi-config | 01-03 | 1 | XCUT-02 | smoke | `pytest app/tests/test_foundation.py::test_openapi_docs -x` | ❌ W0 | ⬜ pending |
| health-endpoint | 01-03 | 1 | INFRA-07 | smoke | `pytest app/tests/test_foundation.py::test_health_endpoint -x` | ❌ W0 | ⬜ pending |
| ruff-config | 01-01 | 0 | XCUT-05 | tool | `ruff check . && ruff format --check .` | N/A — command | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/tests/test_foundation.py` — stubs for INFRA-01 through INFRA-05, INFRA-07, XCUT-01 through XCUT-03
- [ ] `app/tests/conftest.py` — shared fixtures (TestClient, test DB session)
- [ ] `uv add --dev pytest httpx` — pytest and httpx not in pyproject.toml
- [ ] `pyproject.toml` pytest config: add `[tool.pytest.ini_options]` with `testpaths = ["app/tests"]`

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Docker build succeeds and `docker compose up` starts cleanly | INFRA-06 | Requires Docker daemon; no in-process simulation possible | Run `docker build -t pco-backend .` then `docker compose up`; verify `GET /health` returns 200 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
