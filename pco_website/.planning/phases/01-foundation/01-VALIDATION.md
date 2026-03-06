---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-06
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None installed yet — Wave 0 creates dev-preview page |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `pnpm build` |
| **Full suite command** | `pnpm build` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pnpm build`
- **After every plan wave:** Run `pnpm build` + manual visual review of `/dev-preview` page
- **Before `/gsd:verify-work`:** Full suite must be green + all 5 success criteria verified manually
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | INFRA-06 | smoke | `test -f .env.example && grep -q NEXT_PUBLIC_API_BASE .env.example` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | INFRA-07 | smoke | `ls app/\(public\)/layout.tsx app/\(auth\)/layout.tsx app/\(member\)/layout.tsx app/\(admin\)/layout.tsx` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | THEME-01, THEME-02 | build | `pnpm build` | ❌ W0 | ⬜ pending |
| 1-02-01 | 02 | 2 | INFRA-01 | type-check | `npx tsc --noEmit` | ❌ W0 | ⬜ pending |
| 1-02-02 | 02 | 2 | INFRA-02 | manual | Manual: open two concurrent fetches, verify one refresh call in Network tab | N/A | ⬜ pending |
| 1-02-03 | 02 | 2 | INFRA-03 | manual | Manual: login flow in browser, verify localStorage + state | N/A | ⬜ pending |
| 1-02-04 | 02 | 2 | INFRA-04 | manual | Manual: visit /dashboard without token, verify redirect to /login | N/A | ⬜ pending |
| 1-02-05 | 02 | 2 | INFRA-05 | manual | Manual: clear cookies, visit /dashboard, verify redirect before render | N/A | ⬜ pending |
| 1-03-01 | 03 | 3 | THEME-03 | manual | Manual: resize to 375px, verify hamburger appears and dropdown works | N/A | ⬜ pending |
| 1-03-02 | 03 | 3 | THEME-04 | manual | Manual: render on /dev-preview, inspect CSS gradient border + hover glow | N/A | ⬜ pending |
| 1-03-03 | 03 | 3 | THEME-05 | manual | Manual: hover primary + secondary ChromeButton, verify diagonal sweep | N/A | ⬜ pending |
| 1-03-04 | 03 | 3 | THEME-06 | manual | Manual: inspect computed font-family in DevTools for SectionTitle | N/A | ⬜ pending |
| 1-03-05 | 03 | 3 | THEME-07 | manual | Manual: visual inspection of Divider chrome gradient + green dot | N/A | ⬜ pending |
| 1-03-06 | 03 | 3 | THEME-08 | manual | Manual: trigger toast.success() and toast.error() in browser | N/A | ⬜ pending |
| 1-03-07 | 03 | 3 | THEME-09 | manual | Manual: verify grain overlay visible but not obscuring text at 4% opacity | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `app/dev-preview/page.tsx` — dev-only page rendering all design system components for manual visual testing (primary test harness for Phase 1 — created in plan 01-03)
- [ ] Confirm `pnpm build` runs successfully after scaffolding (plan 01-01 gate)
- [ ] `pnpm test` script wired in package.json if needed (currently absent — not required for Phase 1)

*Note: This project has no automated test framework. Wave 0 creates the dev-preview page as the manual test harness. TypeScript type checking (`pnpm build`) serves as the automated gate.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Singleton refresh prevents race condition | INFRA-02 | Requires concurrent browser requests; no unit test framework | Open Network tab, trigger two concurrent authenticated requests that both 401, verify only one refresh call occurs |
| AuthContext login/logout state | INFRA-03 | localStorage + React state; requires browser runtime | Login via UI, verify localStorage has tokens and React DevTools shows user object; logout, verify cleared |
| AuthGuard redirect (no flash) | INFRA-04 | Requires browser navigation to verify no flash of protected content | Visit /dashboard without auth-hint cookie; verify immediate redirect with no page flash |
| proxy.ts server-side redirect | INFRA-05 | Requires actual server request to proxy before client hydration | Clear browser cookies, navigate to /dashboard, verify redirect in Network tab (302 before HTML) |
| Font loading (no CLS) | THEME-02 | Visual/performance metric; requires Lighthouse or browser | Load page, verify fonts render without layout shift; check Network tab for font preload hints |
| Mobile hamburger menu | THEME-03 | Responsive behavior; requires viewport resize | Resize to 375px width, verify hamburger icon appears, click to verify dropdown panel (full-width, not drawer) |
| ChromeCard gradient border + glow | THEME-04 | Visual CSS; no automated visual regression | Open /dev-preview, inspect CSS on ChromeCard — verify gradient border visible, hover triggers green glow |
| ChromeButton sheen animation | THEME-05 | CSS animation; no automated visual regression | Hover both primary and secondary ChromeButton, verify diagonal light sweep fires once on hover |
| SectionTitle heading font | THEME-06 | Font rendering; requires DevTools inspection | Inspect SectionTitle in DevTools → Computed → font-family must show Cormorant Garamond |
| Divider chrome gradient + dot | THEME-07 | Visual CSS; no automated visual regression | Visual inspection on /dev-preview — chrome gradient line with small green dot centered |
| Sonner toast dark theme | THEME-08 | Toast rendering; requires browser trigger | Call toast.success("Test") and toast.error("Test") from console; verify dark background with richColors |
| Grain overlay subtle | THEME-09 | Visual; requires human judgment at 4% opacity | Screenshot at 4% opacity; texture should be barely perceptible, not obscuring text or UI |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
