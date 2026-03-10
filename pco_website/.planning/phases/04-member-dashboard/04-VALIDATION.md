---
phase: 4
slug: member-dashboard
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-09
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None detected — no jest.config, vitest.config, playwright.config, or __tests__ directory |
| **Config file** | none — same gap as Phase 3 |
| **Quick run command** | `pnpm build` (TypeScript type check) |
| **Full suite command** | Manual walkthrough of all MEMBER requirements |
| **Estimated runtime** | ~30 seconds (build) + manual verification |

---

## Sampling Rate

- **After every task commit:** Run `pnpm build` + manual dev server check
- **After every plan wave:** Full manual walkthrough of all four MEMBER requirements
- **Before `/gsd:verify-work`:** All MEMBER-01 through MEMBER-04 pass manual verification
- **Max feedback latency:** ~30 seconds (build) per task

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 0 | MEMBER-01, MEMBER-02, MEMBER-04 | type-check | `pnpm build` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | MEMBER-01 | manual | dev server check | ❌ W0 | ⬜ pending |
| 04-01-03 | 01 | 1 | MEMBER-02 | manual | dev server check | ❌ W0 | ⬜ pending |
| 04-01-04 | 01 | 1 | MEMBER-03 | manual | dev server check | ❌ W0 | ⬜ pending |
| 04-01-05 | 01 | 1 | MEMBER-04 | manual | dev server check | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `types/api.ts` — `Event` interface and `LeadershipContact` interface must be added before implementation

*No automated test framework — manual verification is the protocol for this phase.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| /dashboard shows name and role | MEMBER-01 | Browser rendering + auth context | Log in, visit /dashboard, verify name/role visible |
| Event list View links open signed URLs in new tab | MEMBER-02 | Browser tab behavior | Click View button, verify new tab opens with signed URL |
| Download button downloads PDF | MEMBER-02 | Browser download behavior | Click Download button, verify PDF downloads |
| Empty state message when no events | MEMBER-03 | Conditional rendering | Arrange empty events, verify empty state shows |
| Leadership section with mailto links | MEMBER-04 | Browser mailto behavior | Click email link, verify mailto: opens mail client |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
