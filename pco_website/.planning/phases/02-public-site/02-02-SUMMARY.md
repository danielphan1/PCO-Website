---
phase: 02-public-site
plan: 02
subsystem: ui
tags: [next.js, react, typescript, tailwind, isr, server-component]

# Dependency graph
requires:
  - phase: 02-01
    provides: SiteLayout, design system components (ChromeButton, ChromeCard, SectionTitle, Divider), type contracts (ContentSection, LeadershipMember, ContactInfo), bounce-gentle keyframe
provides:
  - Long-scroll homepage at app/(public)/page.tsx with hero + 4 content sections
  - Section anchor IDs (#history, #philanthropy, #leadership, #contact) for nav hash links
  - ISR fetch pattern with AbortController timeout for Server Component pages
affects: [03-authentication, 04-member-dashboard]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Server Component ISR fetch with AbortController 5s timeout and null fallback
    - Promise.all parallel fetch at page component top level
    - Photo/initials fallback pattern for leadership cards

key-files:
  created: []
  modified:
    - app/(public)/page.tsx
    - app/layout.tsx

key-decisions:
  - "Hero height: min-h-[calc(100vh-4rem)] to fill viewport minus sticky header"
  - "radial-gradient background on hero for depth without visible color"
  - "Leadership card email NOT shown on public homepage — member dashboard only"
  - "Initials fallback: first letter of each name word, max 2 chars, uppercase"
  - "AbortController 5s timeout added to fetch (deviation from plan spec — enhancement for resilience)"

patterns-established:
  - "Server Component fetch with timeout: AbortController pattern used in page.tsx fetchContent<T>()"
  - "ISR revalidate: 3600 on all public content fetches"

requirements-completed: [PUB-01, PUB-02, PUB-12]

# Metrics
duration: ~45min
completed: 2026-03-06
---

# Phase 2 Plan 02: Homepage Long-Scroll Page Summary

**Full-viewport hero with CTAs + four ISR content sections (History, Philanthropy, Leadership, Contact) built as a single Server Component page with Promise.all parallel fetch and graceful null fallbacks.**

## Performance

- **Duration:** ~45 min
- **Completed:** 2026-03-06
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Replaced placeholder page.tsx with full long-scroll homepage — hero fills viewport with heading, subtitle, values line, JOIN NOW/RUSH INFO CTAs, and animated bounce chevron
- Four content sections (History, Philanthropy, Leadership, Contact) fetched in parallel via Promise.all with ISR revalidate: 3600; each section has anchor ID for nav hash links
- Leadership cards show photo or initials fallback in responsive 1/2/3-col grid; email intentionally omitted from public view
- Added AbortController 5s timeout to fetch helper for resilience beyond plan spec

## Task Commits

1. **Task 1 + 2: Homepage hero and content sections** — `49c3bd6` (feat: Phase 2 frontend page visual)

## Files Created/Modified

- `app/(public)/page.tsx` — Full long-scroll homepage: hero, History, Philanthropy, Leadership, Contact sections
- `app/layout.tsx` — Added scroll-smooth class to html element

## Decisions Made

- Added AbortController with 5s timeout to fetchContent helper — not in plan spec but adds resilience if API hangs
- Leadership member email not rendered on homepage (public) — contact page and member dashboard only

## Deviations from Plan

### Auto-fixed Issues

**1. [Enhancement] AbortController timeout added to fetch helper**
- **Found during:** Task 2 (content section implementation)
- **Issue:** Plan spec used basic fetch with no timeout; hanging API call would stall page render
- **Fix:** Wrapped fetch in AbortController with 5s timeout via setTimeout
- **Files modified:** app/(public)/page.tsx
- **Verification:** Build passes; pattern consistent with resilience requirements
- **Committed in:** 49c3bd6

## Issues Encountered

- None

## Next Phase Readiness

- Homepage anchor IDs (#history, #philanthropy, #leadership, #contact) wired; nav links in SiteLayout point to these
- fetchContent<T>() pattern established for reuse in other public pages
- JOIN NOW → /join and RUSH INFO → /rush CTAs present; those pages needed by plan 02-03

---
*Phase: 02-public-site*
*Completed: 2026-03-06*
