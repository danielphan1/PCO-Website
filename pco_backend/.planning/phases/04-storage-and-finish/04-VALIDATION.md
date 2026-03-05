---
phase: 4
slug: storage-and-finish
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-04
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | `pyproject.toml` (`[tool.pytest.ini_options]`) |
| **Quick run command** | `pytest app/tests/test_events.py -x` |
| **Full suite command** | `pytest app/tests/ -x` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest app/tests/test_events.py -x`
- **After every plan wave:** Run `pytest app/tests/ -x`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 4-01-01 | 01 | 1 | EVNT-01,02,03 | unit | `pytest app/tests/test_events.py -x` | Created in Task 3 | ⬜ pending |
| 4-01-02 | 01 | 1 | EVNT-01 | integration | `pytest app/tests/test_events.py::test_list_events_member -x` | Created in Task 3 | ⬜ pending |
| 4-01-03 | 01 | 1 | EVNT-01 | integration | `pytest app/tests/test_events.py::test_list_events_unauthenticated -x` | Created in Task 3 | ⬜ pending |
| 4-01-04 | 01 | 1 | EVNT-01 | integration | `pytest app/tests/test_events.py::test_list_events_url_failure_graceful -x` | Created in Task 3 | ⬜ pending |
| 4-01-05 | 01 | 1 | EVNT-02 | integration | `pytest app/tests/test_events.py::test_upload_pdf_success -x` | Created in Task 3 | ⬜ pending |
| 4-01-06 | 01 | 1 | EVNT-02 | integration | `pytest app/tests/test_events.py::test_upload_non_pdf_rejected -x` | Created in Task 3 | ⬜ pending |
| 4-01-07 | 01 | 1 | EVNT-02 | integration | `pytest app/tests/test_events.py::test_upload_oversized_rejected -x` | Created in Task 3 | ⬜ pending |
| 4-01-08 | 01 | 1 | EVNT-02 | integration | `pytest app/tests/test_events.py::test_upload_non_admin_forbidden -x` | Created in Task 3 | ⬜ pending |
| 4-01-09 | 01 | 1 | EVNT-02 | unit | `pytest app/tests/test_events.py::test_upload_db_failure_triggers_storage_delete -x` | Created in Task 3 | ⬜ pending |
| 4-01-10 | 01 | 1 | EVNT-03 | integration | `pytest app/tests/test_events.py::test_delete_event_success -x` | Created in Task 3 | ⬜ pending |
| 4-01-11 | 01 | 1 | EVNT-03 | integration | `pytest app/tests/test_events.py::test_delete_event_storage_failure_still_succeeds -x` | Created in Task 3 | ⬜ pending |
| 4-01-12 | 01 | 1 | EVNT-03 | integration | `pytest app/tests/test_events.py::test_delete_event_not_found -x` | Created in Task 3 | ⬜ pending |
| 4-02-01 | 02 | 2 | XCUT-06 | manual | N/A — checked at phase gate | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Notes

Test infrastructure (app/tests/test_events.py) is created within Plan 04-01 Task 3 as part of Wave 1.
All tasks in Task 3 have `<automated>` verify commands. No separate Wave 0 plan is needed.

- `app/tests/test_events.py` — created in 04-01 Task 3
- `app/schemas/event.py` — created in 04-01 Task 1
- `app/storage/files.py` — created in 04-01 Task 1
- `app/storage/paths.py` — created in 04-01 Task 1
- `app/services/event_service.py` — created in 04-01 Task 2
- `README.md` — created in 04-03
- `.env.example` — created in 04-03

*(No framework install needed — pytest, httpx, ruff are all in dev dependencies)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| README.md exists and contains required sections (setup, env vars, architecture, /docs link, endpoint table) | XCUT-06 | Content quality check, not behavior test | Open README.md and verify each required section is present and complete |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify commands
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Test file creation handled within Wave 1 (Plan 04-01 Task 3)
- [x] No watch-mode flags
- [x] Feedback latency < 15s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending execution
