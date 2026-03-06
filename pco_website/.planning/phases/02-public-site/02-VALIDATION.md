---
phase: 2
slug: public-site
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None detected — Wave 0 decides: install vitest OR rely on build + manual QA |
| **Config file** | None — Wave 0 installs if test framework chosen |
| **Quick run command** | `pnpm build` (TypeScript gate after each task) |
| **Full suite command** | `pnpm test` (after Wave 0 setup) OR `pnpm build && pnpm start` (smoke) |
| **Estimated runtime** | ~30s (build) / ~10s (unit tests if installed) |

---

## Sampling Rate

- **After every task commit:** Run `pnpm build` (catches TypeScript errors and missing imports)
- **After every plan wave:** Run `pnpm test` (unit tests) OR visual QA in dev server
- **Before `/gsd:verify-work`:** Full suite green + `pnpm build` clean
- **Max feedback latency:** ~30 seconds (build) / ~10 seconds (unit tests)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 1 | PUB-01 | smoke | `pnpm build` | ❌ W0 | ⬜ pending |
| 2-01-02 | 01 | 1 | PUB-02 | unit | `vitest run src/__tests__/homepage.test.tsx` | ❌ W0 | ⬜ pending |
| 2-02-01 | 02 | 2 | PUB-03 | unit | `vitest run src/__tests__/join.test.tsx` | ❌ W0 | ⬜ pending |
| 2-02-02 | 02 | 2 | PUB-04 | unit | `vitest run src/__tests__/join.test.tsx` | ❌ W0 | ⬜ pending |
| 2-02-03 | 02 | 2 | PUB-05 | unit | `vitest run src/__tests__/join.test.tsx` | ❌ W0 | ⬜ pending |
| 2-02-04 | 02 | 2 | PUB-06 | unit | `vitest run src/__tests__/join.test.tsx` | ❌ W0 | ⬜ pending |
| 2-02-05 | 02 | 2 | PUB-07 | unit | `vitest run src/__tests__/rush.test.tsx` | ❌ W0 | ⬜ pending |
| 2-02-06 | 02 | 2 | PUB-08 | unit | `vitest run src/__tests__/rush.test.tsx` | ❌ W0 | ⬜ pending |
| 2-03-01 | 03 | 3 | PUB-09 | unit | `vitest run src/__tests__/content.test.tsx` | ❌ W0 | ⬜ pending |
| 2-03-02 | 03 | 3 | PUB-10 | unit | `vitest run src/__tests__/content.test.tsx` | ❌ W0 | ⬜ pending |
| 2-03-03 | 03 | 3 | PUB-11 | unit | `vitest run src/__tests__/content.test.tsx` | ❌ W0 | ⬜ pending |
| 2-03-04 | 03 | 3 | PUB-12 | static | `grep -r "use client" app/\(public\)/{history,philanthropy,contact,rush}` | manual | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

**Decision required at execution time:** Install vitest OR use build + manual QA only.

**Option A — Install unit tests (recommended for form logic coverage):**
- [ ] `pnpm add -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/user-event @hookform/resolvers`
- [ ] `vitest.config.ts` — test runner configuration
- [ ] `src/__tests__/join.test.tsx` — stubs for PUB-03, PUB-04, PUB-05, PUB-06
- [ ] `src/__tests__/rush.test.tsx` — stubs for PUB-07, PUB-08
- [ ] `src/__tests__/content.test.tsx` — stubs for PUB-09, PUB-10, PUB-11
- [ ] `src/__tests__/homepage.test.tsx` — stubs for PUB-02

**Option B — Build + manual QA (pragmatic for small project):**
- [ ] `pnpm add @hookform/resolvers` — only new runtime dependency
- All verification via `pnpm build` (TypeScript) + visual browser QA

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Hero CTAs visible above fold on 375px viewport | PUB-01 | Viewport rendering — no DOM measurement in jsdom | Open Chrome DevTools, set to 375px, verify both buttons visible without scroll |
| /rush coming-soon fallback shows | PUB-08 | Requires API mock returning `{status:"coming_soon"}` | Test with mock API or manually set backend to unpublished state |
| 409 duplicate email inline error | PUB-06 | Requires API returning 409 status | Test with existing email or mock API |
| SSR title/meta tags in page source | PUB-12 adjacent | Requires viewing raw HTML source, not rendered DOM | `curl http://localhost:3000/history \| grep "<title>"` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
