---
phase: 01-foundation
plan: "01"
subsystem: infra
tags: [tailwind-v4, next-font, sonner, clsx, tailwind-merge, react-hook-form, zod, route-groups, brand-tokens, grain-overlay]

# Dependency graph
requires: []
provides:
  - "Tailwind v4 @theme inline brand tokens (black, green, white, card, chrome colors; font-body, font-heading)"
  - "EB Garamond (body) + Cormorant Garamond (headings) registered via next/font with CSS variables"
  - "Route group directory structure: (public), (auth), (member), (admin) with layout shells"
  - "Grain overlay applied globally at 4% opacity with pointer-events: none"
  - "sheen @keyframes for ChromeButton (plan 01-03)"
  - ".env.example template with NEXT_PUBLIC_API_BASE"
  - "sonner, clsx, tailwind-merge, react-hook-form, zod dependencies installed"
affects: [01-02, 01-03, all subsequent phases]

# Tech tracking
tech-stack:
  added:
    - sonner 2.0.7 (toast notifications)
    - clsx 2.1.1 (conditional classnames)
    - tailwind-merge 3.5.0 (Tailwind class deduplication)
    - react-hook-form 7.71.2 (form management)
    - zod 4.3.6 (schema validation)
  patterns:
    - "Tailwind v4 @theme inline in globals.css — no tailwind.config.js"
    - "next/font with CSS variable registration on <html> element"
    - "Route groups in app/ for auth boundary isolation"
    - "Grain overlay via body::before pseudo-element, pointer-events: none"

key-files:
  created:
    - app/(public)/layout.tsx
    - app/(auth)/layout.tsx
    - app/(member)/layout.tsx
    - app/(admin)/layout.tsx
    - .env.example
  modified:
    - app/globals.css
    - app/layout.tsx
    - package.json
    - .gitignore

key-decisions:
  - "Used @theme inline (not plain @theme) so font values referencing CSS vars (var(--font-eb-garamond)) resolve correctly"
  - "Cormorant Garamond requires explicit weight array ['300','400','500','600','700'] — not a variable font"
  - "Updated .gitignore to add !.env.example exception so the template file can be committed"
  - "Route group layouts are minimal shells — AuthGuard deferred to plan 01-02 when it exists"

patterns-established:
  - "Brand tokens: all colors and font stacks defined in globals.css @theme inline block"
  - "Font registration: next/font constructors in layout.tsx, variables applied to <html> className"
  - "Route groups: one layout.tsx per group, auth enforcement added when AuthGuard exists"

requirements-completed: [INFRA-06, INFRA-07, THEME-01, THEME-02, THEME-08, THEME-09]

# Metrics
duration: 1min
completed: 2026-03-06
---

# Phase 1 Plan 01: Foundation Scaffolding Summary

**Tailwind v4 brand token system with EB Garamond / Cormorant Garamond fonts, grain overlay, and route group skeleton — zero TypeScript errors on pnpm build**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-06T08:32:58Z
- **Completed:** 2026-03-06T08:37:44Z
- **Tasks:** 3
- **Files modified:** 8

## Accomplishments

- Installed sonner, clsx, tailwind-merge, react-hook-form, and zod; created .env.example template
- Created four route group layout shells: (public), (auth), (member), (admin)
- Replaced Geist-based globals.css with @theme inline brand tokens, grain overlay, and sheen @keyframes; replaced Geist fonts with EB Garamond + Cormorant Garamond via next/font

## Task Commits

Each task was committed atomically:

1. **Task 1: Install dependencies and configure env files** - `93f2673` (chore)
2. **Task 2: Establish route group directory structure** - `9943cb6` (feat)
3. **Task 3: Replace globals.css and update root layout** - `987da89` (feat)

## Files Created/Modified

- `app/globals.css` - Tailwind @theme inline brand colors, font-body/font-heading tokens, grain overlay (body::before), sheen @keyframes
- `app/layout.tsx` - EB Garamond + Cormorant Garamond next/font registration, Toaster from sonner, CSS variable className on <html>
- `app/(public)/layout.tsx` - Public marketing pages shell
- `app/(auth)/layout.tsx` - Minimal login layout, no SiteLayout header
- `app/(member)/layout.tsx` - Member area shell (AuthGuard deferred to 01-02)
- `app/(admin)/layout.tsx` - Admin area shell (AuthGuard deferred to 01-02)
- `.env.example` - NEXT_PUBLIC_API_BASE=http://localhost:8000 template
- `package.json` - Added five production dependencies
- `.gitignore` - Added !.env.example exception

## Decisions Made

- Used `@theme inline` instead of plain `@theme` so that font values referencing CSS variables (`var(--font-eb-garamond)`) resolve at build time rather than silently failing.
- Cormorant Garamond is not a variable font — explicit weight array `["300","400","500","600","700"]` required in the next/font constructor.
- Added `!.env.example` exception to `.gitignore` (was previously `.env*` catch-all) so the template can be committed for developer onboarding.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Updated .gitignore to allow .env.example to be committed**
- **Found during:** Task 1 (install dependencies and create env files)
- **Issue:** .gitignore had `.env*` catch-all which prevented committing .env.example template
- **Fix:** Added `!.env.example` exception line after `.env*` in .gitignore
- **Files modified:** .gitignore
- **Verification:** git add .env.example succeeded after the change
- **Committed in:** 93f2673 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (Rule 2 - missing critical: .env.example template must be committable)
**Impact on plan:** Minimal. .gitignore correction is necessary for developer onboarding. No scope creep.

## Issues Encountered

None — build passed on first attempt.

## User Setup Required

None - no external service configuration required. `.env.local` was created automatically with `NEXT_PUBLIC_API_BASE=http://localhost:8000`. Update this value if your backend runs on a different port.

## Next Phase Readiness

- Token system, font stack, and route group skeleton ready for 01-02 (auth utilities + AuthGuard) and 01-03 (design system components)
- CSS variables `--font-eb-garamond` and `--font-cormorant-garamond` are live on `<html>`; `font-body` and `font-heading` Tailwind utilities are available
- Route group layouts are shells — 01-02 will add AuthGuard to (member) and (admin) layouts once it exists

---

*Phase: 01-foundation*
*Completed: 2026-03-06*
