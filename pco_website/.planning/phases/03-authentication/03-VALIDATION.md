---
phase: 3
slug: authentication
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — no test framework detected in project |
| **Config file** | None — Wave 0 would need to establish if adding automated tests |
| **Quick run command** | `pnpm dev` + manual browser verification |
| **Full suite command** | Manual smoke test of all AUTH-01 through AUTH-06 |
| **Estimated runtime** | ~5 minutes manual verification |

---

## Sampling Rate

- **After every task commit:** Run `pnpm dev` and manually verify behavior in browser
- **After every plan wave:** Full manual smoke test of all AUTH requirements
- **Before `/gsd:verify-work`:** All 6 AUTH requirements pass manual verification
- **Max feedback latency:** ~5 minutes

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | AUTH-01 | manual | N/A | ❌ Wave 0 gap | ⬜ pending |
| 03-01-02 | 01 | 1 | AUTH-02 | manual | N/A | ❌ Wave 0 gap | ⬜ pending |
| 03-01-03 | 01 | 1 | AUTH-03 | manual | N/A | ❌ Wave 0 gap | ⬜ pending |
| 03-02-01 | 02 | 2 | AUTH-04 | manual | N/A | ❌ Wave 0 gap | ⬜ pending |
| 03-02-02 | 02 | 2 | AUTH-05 | manual | N/A | ❌ Wave 0 gap | ⬜ pending |
| 03-02-03 | 02 | 2 | AUTH-06 | manual | N/A | ❌ Wave 0 gap | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] No automated test framework exists — manual verification only for this phase

*If future phases add Playwright or Vitest, AUTH behaviors are prime candidates for E2E and unit tests respectively.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| /login page renders with email/password fields and admin note | AUTH-01 | No test framework; browser-level DOM rendering | Navigate to /login in dev server, confirm fields and note visible |
| Login success: tokens stored in localStorage, redirect to /dashboard | AUTH-02 | Requires browser localStorage API and Next.js router | Login with valid credentials, check localStorage in DevTools, confirm redirect |
| Login failure: toast shows "Invalid email or password." | AUTH-03 | Toast rendering requires browser/jsdom | Login with wrong credentials, confirm toast message (no email-existence hint) |
| Logout: localStorage cleared, redirect to / | AUTH-04 | Requires browser localStorage and router | Click logout, check localStorage cleared in DevTools, confirm redirect to / |
| Unauthenticated /dashboard access: redirect to /login | AUTH-05 | Next.js redirect behavior requires browser navigation | Clear session, navigate directly to /dashboard, confirm redirect to /login (no content flash) |
| Non-admin /admin access: redirect to /dashboard with toast | AUTH-06 | Role-based redirect requires browser + auth state | Login as non-admin, navigate to /admin/*, confirm redirect to /dashboard with access denied message |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5 min
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
