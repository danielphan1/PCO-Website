---
phase: 3
slug: core-features
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-04
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`, `testpaths = ["app/tests"]`) |
| **Quick run command** | `uv run python -m pytest app/tests/ -x -q` |
| **Full suite command** | `uv run python -m pytest app/tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run python -m pytest app/tests/ -x -q`
- **After every plan wave:** Run `uv run python -m pytest app/tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** ~10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 0 | MEMB-01,MEMB-02,MEMB-03,MEMB-04,MEMB-05,XCUT-04 | unit | `uv run python -m pytest app/tests/test_members.py app/tests/test_email.py -x` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | XCUT-04 | unit | `uv run python -m pytest app/tests/test_email.py -x` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | MEMB-01 | integration | `uv run python -m pytest app/tests/test_members.py::test_list_members -x` | ❌ W0 | ⬜ pending |
| 03-01-04 | 01 | 1 | MEMB-02 | integration | `uv run python -m pytest app/tests/test_members.py::test_create_member -x` | ❌ W0 | ⬜ pending |
| 03-01-05 | 01 | 1 | MEMB-03 | integration | `uv run python -m pytest app/tests/test_members.py::test_update_role -x` | ❌ W0 | ⬜ pending |
| 03-01-06 | 01 | 1 | MEMB-04 | integration | `uv run python -m pytest app/tests/test_members.py::test_deactivate_member -x` | ❌ W0 | ⬜ pending |
| 03-01-07 | 01 | 1 | MEMB-05 | integration | `uv run python -m pytest app/tests/test_members.py::test_reactivate_member -x` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 0 | INTR-01,INTR-02,RUSH-01,RUSH-02,RUSH-03 | unit | `uv run python -m pytest app/tests/test_interest.py app/tests/test_rush.py -x` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 1 | INTR-01 | integration | `uv run python -m pytest app/tests/test_interest.py::test_submit_interest -x` | ❌ W0 | ⬜ pending |
| 03-02-03 | 02 | 1 | INTR-02 | integration | `uv run python -m pytest app/tests/test_interest.py::test_list_interest -x` | ❌ W0 | ⬜ pending |
| 03-02-04 | 02 | 1 | RUSH-01 | integration | `uv run python -m pytest app/tests/test_rush.py::test_get_rush -x` | ❌ W0 | ⬜ pending |
| 03-02-05 | 02 | 1 | RUSH-02 | integration | `uv run python -m pytest app/tests/test_rush.py::test_update_rush -x` | ❌ W0 | ⬜ pending |
| 03-02-06 | 02 | 1 | RUSH-03 | integration | `uv run python -m pytest app/tests/test_rush.py::test_toggle_visibility -x` | ❌ W0 | ⬜ pending |
| 03-03-01 | 03 | 0 | CONT-01,CONT-02,CONT-03,CONT-04,CONT-05 | unit | `uv run python -m pytest app/tests/test_content.py -x` | ❌ W0 | ⬜ pending |
| 03-03-02 | 03 | 1 | CONT-01 | integration | `uv run python -m pytest app/tests/test_content.py::test_get_history -x` | ❌ W0 | ⬜ pending |
| 03-03-03 | 03 | 1 | CONT-02 | integration | `uv run python -m pytest app/tests/test_content.py::test_get_philanthropy -x` | ❌ W0 | ⬜ pending |
| 03-03-04 | 03 | 1 | CONT-03 | integration | `uv run python -m pytest app/tests/test_content.py::test_get_contacts -x` | ❌ W0 | ⬜ pending |
| 03-03-05 | 03 | 1 | CONT-04 | integration | `uv run python -m pytest app/tests/test_content.py::test_get_leadership -x` | ❌ W0 | ⬜ pending |
| 03-03-06 | 03 | 1 | CONT-05 | integration | `uv run python -m pytest app/tests/test_content.py::test_update_content -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/tests/test_members.py` — stubs for MEMB-01 through MEMB-05
- [ ] `app/tests/test_interest.py` — fill currently empty file; covers INTR-01, INTR-02
- [ ] `app/tests/test_rush.py` — stubs for RUSH-01, RUSH-02, RUSH-03
- [ ] `app/tests/test_content.py` — stubs for CONT-01 through CONT-05
- [ ] `app/tests/test_email.py` — covers XCUT-04 (mock SMTP, verify BackgroundTasks.add_task called)
- [ ] `app/tests/conftest.py` — extend with `member_token`/`admin_token` helper fixtures (or inline login)

*Note: `conftest.py` already has `auth_client` fixture with admin user seeded — reuse for all admin endpoint tests.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Welcome email content includes temp password, login URL | MEMB-02 | Email delivery requires live SMTP | Send to test account; verify subject, body includes password and FRONTEND_URL |
| Interest confirmation email delivered | INTR-01 | Email delivery requires live SMTP | Submit interest form; verify acknowledgment email received |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
