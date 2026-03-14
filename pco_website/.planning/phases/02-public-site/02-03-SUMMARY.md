---
phase: 02-public-site
plan: 03
subsystem: ui
tags: [next.js, react, typescript, tailwind, isr, server-component]

# Dependency graph
requires:
  - phase: 02-01
    provides: SiteLayout, ChromeButton, SectionTitle, RushContent type, apiFetch (client-only)
provides:
  - /rush page with two-state conditional (coming_soon / published timeline)
  - /join interest form page with RHF + zod + 409 inline error handling
affects: [03-authentication]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Two-state Server Component conditional render based on API status field
    - Vertical timeline layout with absolute connector line and dot markers

key-files:
  created:
    - app/(public)/rush/page.tsx
  modified: []

key-decisions:
  - "/rush uses same AbortController timeout pattern as homepage fetch"
  - "/join page was never created — work was paused before Task 2"

patterns-established:
  - "Vertical timeline: absolute left line + green dot marker per event row"

requirements-completed: [PUB-03, PUB-04, PUB-05, PUB-06, PUB-07, PUB-08]

# Metrics
duration: ~45min
completed: 2026-03-06
---

# Phase 2 Plan 03: /rush and /join Pages Summary

**/rush Server Component with coming_soon fallback and published event timeline; /join interest form with RHF + zod validation, success state, and 409 inline email error.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-03-06
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Built /rush as a Server Component with ISR revalidate: 3600 — renders coming-soon block (Sign Up CTA → /join) or published event timeline based on API `status` field; timeline uses vertical connector line with green dot markers per event
- Built /join as "use client" interest form: 5 fields (Name, Email, Phone, Graduation Year, Major) with zodResolver validation showing inline field errors on touch; success state replaces form in-place
- 409 duplicate email response maps to inline error on email field: "Looks like you've already signed up!" — not a toast or page-level error

## Task Commits

1. **Task 1: /rush two-state page** — `49c3bd6` (feat: Phase 2 frontend page visual)
2. **Task 2: /join interest form** — committed after paused work resumed

## Files Created/Modified

- `app/(public)/rush/page.tsx` — Two-state rush page (coming_soon / published timeline); Server Component with ISR
- `app/(public)/join/page.tsx` — Interest form; "use client", RHF + zod, POST /v1/interest, success state, 409 handling

## Decisions Made

- AbortController 5s timeout used in getRush() fetch, consistent with homepage pattern
- apiFetch used for POST /v1/interest (public endpoint — no token sent, Authorization header omitted when getAccessToken() returns null)
- metadata export omitted from join/page.tsx since "use client" and metadata cannot coexist; SEO deferred to Phase 6

## Deviations from Plan

None — implemented as specified.

## Issues Encountered

- @hookform/resolvers was listed in package.json but not installed in node_modules; ran `pnpm install` to resolve before build

## Next Phase Readiness

- /rush and /join fully functional; JOIN NOW and RUSH INFO CTAs from homepage both resolve
- Interest form submissions land in backend /v1/interest; admin can view via GET /v1/interest

---
*Phase: 02-public-site*
*Completed (partial): 2026-03-06*
