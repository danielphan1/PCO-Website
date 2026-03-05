---
phase: 4
slug: storage-and-finish
status: draft
nyquist_compliant: false
wave_0_complete: false
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
| 4-01-01 | 01 | 0 | EVNT-01,02,03 | unit | `pytest app/tests/test_events.py -x` | ❌ W0 | ⬜ pending |
| 4-01-02 | 01 | 1 | EVNT-01 | integration | `pytest app/tests/test_events.py::test_list_events_member -x` | ❌ W0 | ⬜ pending |
| 4-01-03 | 01 | 1 | EVNT-01 | integration | `pytest app/tests/test_events.py::test_list_events_unauthenticated -x` | ❌ W0 | ⬜ pending |
| 4-01-04 | 01 | 1 | EVNT-01 | integration | `pytest app/tests/test_events.py::test_list_events_url_failure_graceful -x` | ❌ W0 | ⬜ pending |
| 4-01-05 | 01 | 1 | EVNT-02 | integration | `pytest app/tests/test_events.py::test_upload_pdf_success -x` | ❌ W0 | ⬜ pending |
| 4-01-06 | 01 | 1 | EVNT-02 | integration | `pytest app/tests/test_events.py::test_upload_non_pdf_rejected -x` | ❌ W0 | ⬜ pending |
| 4-01-07 | 01 | 1 | EVNT-02 | integration | `pytest app/tests/test_events.py::test_upload_oversized_rejected -x` | ❌ W0 | ⬜ pending |
| 4-01-08 | 01 | 1 | EVNT-02 | integration | `pytest app/tests/test_events.py::test_upload_non_admin_forbidden -x` | ❌ W0 | ⬜ pending |
| 4-01-09 | 01 | 1 | EVNT-02 | unit | `pytest app/tests/test_events.py::test_upload_db_failure_triggers_storage_delete -x` | ❌ W0 | ⬜ pending |
| 4-01-10 | 01 | 1 | EVNT-03 | integration | `pytest app/tests/test_events.py::test_delete_event_success -x` | ❌ W0 | ⬜ pending |
| 4-01-11 | 01 | 1 | EVNT-03 | integration | `pytest app/tests/test_events.py::test_delete_event_storage_failure_still_succeeds -x` | ❌ W0 | ⬜ pending |
| 4-01-12 | 01 | 1 | EVNT-03 | integration | `pytest app/tests/test_events.py::test_delete_event_not_found -x` | ❌ W0 | ⬜ pending |
| 4-02-01 | 02 | 2 | XCUT-06 | manual | N/A — checked at phase gate | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/tests/test_events.py` — currently empty (1-line file); all event tests must be created here
- [ ] `app/schemas/event.py` — currently empty; `EventCreate` and `EventResponse` needed before tests run
- [ ] `app/storage/files.py` — currently empty; `StorageService` and `storage_service` singleton needed
- [ ] `app/storage/paths.py` — currently empty; `event_pdf_path()` helper needed
- [ ] `app/services/event_service.py` — currently empty; all business logic functions needed
- [ ] `README.md` — does not exist yet (XCUT-06)
- [ ] `.env.example` — does not exist yet (referenced by README setup section)

*(No framework install needed — pytest, httpx, ruff are all in dev dependencies)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| README.md exists and contains required sections (setup, env vars, architecture, /docs link, endpoint table) | XCUT-06 | Content quality check, not behavior test | Open README.md and verify each required section is present and complete |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
