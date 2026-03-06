---
phase: 01-foundation
plan: "03"
subsystem: ui
tags: [react, tailwind, next.js, design-system, chrome-hearts, sonner]

# Dependency graph
requires:
  - phase: 01-foundation-01
    provides: "@theme inline tokens (bg-black, text-green, text-chrome, font-heading, font-body, @keyframes sheen), grain overlay"
  - phase: 01-foundation-02
    provides: "cn() utility from lib/utils.ts, AuthContext for SiteLayout logout"
provides:
  - "ChromeCard — metallic gradient border card with hover green glow"
  - "ChromeButton — primary (green fill) and secondary (chrome outline) with diagonal sheen animation"
  - "SectionTitle — Cormorant Garamond heading component"
  - "Divider — chrome gradient line with green dot accent"
  - "SiteLayout — responsive sticky header with desktop nav, mobile hamburger dropdown panel, and footer"
  - "/dev-preview page — interactive visual QA harness for all design system components"
affects:
  - "02-public-pages"
  - "03-auth-pages"
  - "04-member-dashboard"
  - "05-admin"

# Tech tracking
tech-stack:
  added: [sonner]
  patterns:
    - "Gradient border via wrapper+inner div (not border-image — incompatible with border-radius)"
    - "Sheen animation via nested <span> clipped by overflow-hidden parent (CSS-only, no JS)"
    - "Mobile dropdown below header via conditional render — no slide-in drawer"
    - "transpilePackages for sonner in next.config.ts (ESM package resolution fix)"

key-files:
  created:
    - components/ui/ChromeCard.tsx
    - components/ui/ChromeButton.tsx
    - components/ui/SectionTitle.tsx
    - components/ui/Divider.tsx
    - components/layout/SiteLayout.tsx
    - app/dev-preview/page.tsx
  modified:
    - next.config.ts

key-decisions:
  - "Gradient border implemented as wrapper+inner div (1px padding + background-clip) because CSS border-image does not support border-radius"
  - "Sheen animation uses a nested <span> as pseudo-element substitute — Tailwind cannot target ::after with arbitrary animation values"
  - "Mobile menu renders as full-width dropdown panel below header — no slide-in drawer — per CONTEXT.md constraint"
  - "SiteLayout NOT added to root app/layout.tsx — reserved for app/(public)/layout.tsx in Phase 2"
  - "dev-preview upgraded to client component with live toast triggers during QA to interactively verify Sonner integration"
  - "transpilePackages: ['sonner'] added to next.config.ts to resolve ESM import errors in Next.js 15+ build"

patterns-established:
  - "Wrapper+inner div pattern: use for any rounded element requiring a gradient border"
  - "Group-hover sheen: apply 'group' on button, nested span with group-hover:animate-[sheen_0.6s_ease-in-out]"
  - "Chrome color tokens: use text-chrome (#c0c0c0), bg-green (#228B22), bg-card (#0a0a0a) from globals.css @theme"

requirements-completed: [THEME-03, THEME-04, THEME-05, THEME-06, THEME-07, THEME-08]

# Metrics
duration: ~45min
completed: 2026-03-06
---

# Phase 1 Plan 03: Design System Components Summary

**Five Chrome Hearts UI components (ChromeCard, ChromeButton, SectionTitle, Divider, SiteLayout) built with metallic borders, sheen animations, and responsive mobile nav — all visually QA'd on /dev-preview**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-03-06
- **Completed:** 2026-03-06
- **Tasks:** 3 (2 auto + 1 checkpoint)
- **Files modified:** 7

## Accomplishments
- Built all five design system components required by Phase 1 — ChromeCard with metallic gradient border and hover glow, ChromeButton with diagonal sheen animation in both primary/secondary variants, SectionTitle using Cormorant Garamond, Divider with chrome gradient and green dot accent
- Built SiteLayout with sticky header, desktop nav, responsive hamburger mobile menu (full-width dropdown panel), and footer
- Created /dev-preview visual QA harness — interactive toast buttons, hover tests for glow/sheen, font verification, and mobile viewport testing — all confirmed passing by human QA
- Resolved sonner ESM build issue by adding `transpilePackages` to next.config.ts (Rule 3 auto-fix)

## Task Commits

1. **Task 1: Build primitive UI components** - `2fb426e` (feat)
2. **Task 2: Build SiteLayout with responsive header and dev-preview page** - `e1b41b4` (feat)
3. **Task 3: Visual QA checkpoint — dev-preview upgrades and sonner fix** - `b55584f` (feat)

## Files Created/Modified
- `components/ui/ChromeCard.tsx` — Metallic gradient border card, hover green glow via box-shadow
- `components/ui/ChromeButton.tsx` — Primary (green fill) and secondary (chrome outline), diagonal sheen span animation
- `components/ui/SectionTitle.tsx` — Heading component using font-heading (Cormorant Garamond)
- `components/ui/Divider.tsx` — Chrome gradient line via inline style, green dot accent centered with absolute span
- `components/layout/SiteLayout.tsx` — Sticky header, desktop nav, mobile hamburger with full-width dropdown panel, footer
- `app/dev-preview/page.tsx` — Visual QA harness with interactive toast buttons, upgraded to client component
- `next.config.ts` — Added transpilePackages: ["sonner"] for ESM resolution

## Decisions Made
- Gradient border: wrapper+inner div technique (1px padding, gradient background, dark inner bg) — CSS `border-image` does not support `border-radius`
- Sheen animation: nested `<span>` with `group-hover:animate-[sheen_0.6s]` — Tailwind cannot target `::after` with arbitrary animation values
- Mobile menu: full-width dropdown panel below header — matches CONTEXT.md constraint (no slide-in drawer)
- SiteLayout not wired into root `app/layout.tsx` — deferred to `app/(public)/layout.tsx` in Phase 2
- dev-preview converted to `"use client"` during QA to enable live Sonner toast testing

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added transpilePackages to next.config.ts for Sonner ESM resolution**
- **Found during:** Task 3 (QA verification / dev-preview testing)
- **Issue:** Sonner is an ESM-only package; Next.js build threw module resolution errors without explicit transpilation
- **Fix:** Added `transpilePackages: ["sonner"]` to `next.config.ts`
- **Files modified:** `next.config.ts`
- **Verification:** `pnpm build` exits 0 with /dev-preview compiled as static route
- **Committed in:** `b55584f` (Task 3 / QA commit)

**2. [Rule 1 - Enhancement] Upgraded dev-preview toast section from console instructions to live buttons**
- **Found during:** Task 3 (QA verification)
- **Issue:** Original page had a static code block instructing user to manually import sonner in DevTools console — not a true interactive test
- **Fix:** Converted page to `"use client"`, imported `toast` from `sonner`, replaced code block with interactive ChromeButton triggers for success and error toasts
- **Files modified:** `app/dev-preview/page.tsx`
- **Committed in:** `b55584f` (Task 3 / QA commit)

---

**Total deviations:** 2 auto-fixed (1 blocking dependency fix, 1 bug/enhancement)
**Impact on plan:** Both fixes necessary for build correctness and proper QA coverage. No scope creep.

## Issues Encountered
- Sonner ESM import failed at build time — resolved with `transpilePackages` in next.config.ts (standard Next.js pattern for ESM packages)

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- All five design system components are complete, exported, and visually QA'd
- SiteLayout is ready for `app/(public)/layout.tsx` in Phase 2
- ChromeCard, ChromeButton, SectionTitle, Divider ready for use in all public and protected pages
- `pnpm build` exits 0; /dev-preview compiles as static route
- Phase 1 success criteria fully met: fonts confirmed loading, mobile hamburger confirmed, no horizontal scroll at 375px

---
*Phase: 01-foundation*
*Completed: 2026-03-06*

## Self-Check: PASSED

- FOUND: components/ui/ChromeCard.tsx
- FOUND: components/ui/ChromeButton.tsx
- FOUND: components/ui/SectionTitle.tsx
- FOUND: components/ui/Divider.tsx
- FOUND: components/layout/SiteLayout.tsx
- FOUND: app/dev-preview/page.tsx
- FOUND: .planning/phases/01-foundation/01-03-SUMMARY.md
- FOUND: commit 2fb426e (Task 1)
- FOUND: commit e1b41b4 (Task 2)
- FOUND: commit b55584f (Task 3 / QA)
- Build: pnpm build exits 0, /dev-preview compiles as static route
