---
phase: 2
slug: authentication
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-04
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | `pyproject.toml` → `[tool.pytest.ini_options]` → `testpaths = ["app/tests"]` |
| **Quick run command** | `uv run pytest app/tests/test_auth.py -x -q` |
| **Full suite command** | `uv run pytest app/tests/ -x -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run pytest app/tests/test_auth.py -x -q`
- **After every plan wave:** Run `uv run pytest app/tests/ -x -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 0 | AUTH-07 | unit | `uv run pytest app/tests/test_auth.py::test_hash_password app/tests/test_auth.py::test_verify_password -x` | ❌ W0 | ⬜ pending |
| 2-01-02 | 01 | 0 | AUTH-01, AUTH-02 | integration | `uv run pytest app/tests/test_auth.py -x -q` | ❌ W0 | ⬜ pending |
| 2-01-03 | 01 | 1 | AUTH-07 | unit | `uv run pytest app/tests/test_auth.py::test_hash_password app/tests/test_auth.py::test_verify_password -x` | ❌ W0 | ⬜ pending |
| 2-01-04 | 01 | 1 | AUTH-01 | integration | `uv run pytest app/tests/test_auth.py::test_login_success app/tests/test_auth.py::test_login_wrong_password app/tests/test_auth.py::test_login_wrong_email app/tests/test_auth.py::test_login_deactivated_user -x` | ❌ W0 | ⬜ pending |
| 2-01-05 | 01 | 1 | AUTH-02 | integration | `uv run pytest app/tests/test_auth.py::test_refresh_success app/tests/test_auth.py::test_refresh_expired app/tests/test_auth.py::test_refresh_revoked app/tests/test_auth.py::test_refresh_deactivated_user -x` | ❌ W0 | ⬜ pending |
| 2-02-01 | 02 | 0 | AUTH-03, AUTH-04, AUTH-05 | integration | `uv run pytest app/tests/test_auth.py -x -q` | ❌ W0 | ⬜ pending |
| 2-02-02 | 02 | 1 | AUTH-04 | integration | `uv run pytest app/tests/test_auth.py::test_get_current_user_no_token app/tests/test_auth.py::test_get_current_user_expired_token -x` | ❌ W0 | ⬜ pending |
| 2-02-03 | 02 | 1 | AUTH-05 | integration | `uv run pytest app/tests/test_auth.py::test_require_admin_non_admin app/tests/test_auth.py::test_require_admin_admin_user -x` | ❌ W0 | ⬜ pending |
| 2-02-04 | 02 | 1 | AUTH-03 | integration | `uv run pytest app/tests/test_auth.py::test_users_me_authenticated app/tests/test_auth.py::test_users_me_unauthenticated -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/tests/test_auth.py` — all 16 test stubs (AUTH-01 through AUTH-07)
- [ ] `app/tests/conftest.py` — add DB override fixture or test DB session fixture for auth tests that need seeded user/token data

*Wave 0 must create all test stubs before any implementation begins.*

---

## Manual-Only Verifications

*All phase behaviors have automated verification.*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
