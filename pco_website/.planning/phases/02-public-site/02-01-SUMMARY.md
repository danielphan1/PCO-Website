---
phase: 02-public-site
plan: 01
subsystem: ui
tags: [next.js, react, typescript, tailwind, hookform, zod]

requires:
  - phase: 01-foundation
    provides: SiteLayout component, ChromeButton, globals.css sheen keyframe, TypeScript base types

provides:
  - SiteLayout wired into app/(public)/layout.tsx for all public routes
  - NAV_LINKS for History/Philanthropy/Contact updated to anchor hrefs (/#history, /#philanthropy, /#contact)
  - Phase 2 TypeScript contracts: LeadershipMember, RushEvent, RushContent, ContentSection, ContactInfo
  - bounce-gentle CSS keyframe for hero scroll indicator
  - "@hookform/resolvers v5.2.2 installed (Zod v4 compatible)"
  - app/(public)/page.tsx placeholder owning / route (scaffold app/page.tsx deleted)

affects:
  - 02-02-PLAN (homepage sections — imports types, uses bounce-gentle, renders via public layout)
  - 02-03-PLAN (join form — imports @hookform/resolvers, uses ContactInfo/RushContent types)
  - 02-04-PLAN (rush page — imports RushContent, RushEvent types)

tech-stack:
  added:
    - "@hookform/resolvers@5.2.2"
  patterns:
    - Public route group (app/(public)/) uses SiteLayout wrapper — no header/footer duplication in individual pages
    - Anchor-based single-page navigation (/#section) for homepage sections accessible from any public route

key-files:
  created:
    - app/(public)/page.tsx
    - .planning/phases/02-public-site/02-01-SUMMARY.md
  modified:
    - app/(public)/layout.tsx
    - components/layout/SiteLayout.tsx
    - types/api.ts
    - app/globals.css
    - package.json
    - pnpm-lock.yaml

key-decisions:
  - "Public layout wraps SiteLayout at the route-group level — individual public pages stay lean with no layout boilerplate"
  - "History/Philanthropy/Contact nav links use anchor hrefs (/#section) so they work from any public page, not just /"
  - "app/page.tsx deleted — (public) route group captures / without URL change; placeholder page in (public)/ prevents 404"

patterns-established:
  - "Route group layout pattern: app/(public)/layout.tsx is the single place to change public chrome"
  - "Type-first pattern: types/api.ts is the canonical source for all backend contracts — plans import, never redefine"

requirements-completed:
  - PUB-12

duration: 15min
completed: 2026-03-06
---

# Phase 2 Plan 01: Foundation Wiring Summary

**SiteLayout wired into public route group, Phase 2 TypeScript contracts added to types/api.ts, @hookform/resolvers v5.2.2 installed, scaffold page deleted and placeholder homepage created**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-03-06T10:15:46Z
- **Completed:** 2026-03-06T10:30:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- SiteLayout now wraps all routes under `app/(public)/` — header and footer appear on every public page without per-page boilerplate
- NAV_LINKS for History, Philanthropy, and Contact updated to anchor hrefs so they navigate within the homepage from any public route
- Five Phase 2 type interfaces exported from `types/api.ts` — plans 02, 03, and 04 can import without defining their own contracts
- `bounce-gentle` keyframe added to `globals.css` for the hero scroll indicator chevron
- `@hookform/resolvers` v5.2.2 installed (compatible with react-hook-form v7 and Zod v4)
- `app/page.tsx` (Next.js scaffold) deleted; placeholder at `app/(public)/page.tsx` owns the `/` route cleanly

## Task Commits

1. **Task 1: Install @hookform/resolvers and wire SiteLayout into public layout** - `a6d1455` (feat)
2. **Task 2: Add Phase 2 type definitions, keyframe, and delete scaffold page** - `0575fa5` (feat)

## Files Created/Modified

- `app/(public)/layout.tsx` — now imports and renders SiteLayout wrapping children
- `components/layout/SiteLayout.tsx` — NAV_LINKS history/philanthropy/contact changed to anchor hrefs
- `types/api.ts` — exports LeadershipMember, RushEvent, RushContent, ContentSection, ContactInfo
- `app/globals.css` — bounce-gentle keyframe added after existing sheen keyframe
- `app/(public)/page.tsx` — minimal placeholder (`return <div />`) created
- `app/page.tsx` — deleted (was conflicting scaffold; (public) route group now owns /)
- `package.json` / `pnpm-lock.yaml` — @hookform/resolvers v5.2.2 added

## Decisions Made

- Public layout wraps SiteLayout at the route-group level (not root layout) — keeps admin/auth routes independent of public chrome
- Anchor hrefs (/#section) chosen over separate page routes for history/philanthropy/contact — they are sections of the homepage, not separate pages
- `app/page.tsx` deleted rather than kept empty — having both would cause a route conflict; the (public) placeholder is the cleaner solution

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

- `pnpm` not on PATH; resolved by using `corepack pnpm` which is available on this system

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plans 02-02 (homepage), 02-03 (join form), and 02-04 (rush page) can now execute in parallel
- All type contracts available from `types/api.ts`
- Public layout chrome is active — any page rendered under `app/(public)/` will have the header and footer
- `@hookform/resolvers` ready for the join form validation (Plan 02-03)

---
*Phase: 02-public-site*
*Completed: 2026-03-06*
