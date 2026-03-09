---
phase: 03-authentication
plan: 02
subsystem: auth
tags: [jwt, react, next.js, sonner, AuthContext, AuthGuard, SiteLayout]

# Dependency graph
requires:
  - phase: 03-01
    provides: AuthContext stub, AuthGuard, LoginForm, FullPageSpinner, lib/api.ts with apiFetch

provides:
  - AuthContext hydrates user from GET /v1/users/me on mount; clears stale tokens on 401
  - AuthGuard renders FullPageSpinner while loading=true (no null flash)
  - AuthGuard redirects non-admin to /dashboard?access_denied=1
  - SiteLayout conditional header: Dashboard + Logout when authenticated; Join + Login when logged out
  - Dashboard stub at app/(member)/dashboard/page.tsx with access-denied toast

affects: [04-member-dashboard, 05-admin-portal]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Auth hydration: apiFetch /v1/users/me in useEffect with .finally() for loading=false"
    - "Conditional header: user ? authenticated-view : unauthenticated-view"
    - "Access-denied signal: router.replace with ?access_denied=1 query param + sonner toast on destination"

key-files:
  created:
    - app/(member)/dashboard/page.tsx
  modified:
    - contexts/AuthContext.tsx
    - components/layout/AuthGuard.tsx
    - components/layout/SiteLayout.tsx

key-decisions:
  - "loading=false set only in .finally() — never in happy path — prevents AuthGuard from seeing user=null during fetch"
  - "access-denied signal via ?access_denied=1 query param rather than separate state — survives router.replace across component boundaries"
  - "Logout uses onClick only on ChromeButton (no href) — passing href would 404 on /logout route"
  - "Brief flash of unauthenticated header on first render is expected and acceptable — no suppressHydrationWarning added"

patterns-established:
  - "Auth state conditional rendering: user ? <authenticated /> : <unauthenticated /> (no loading branch in header — spinner only in AuthGuard)"
  - "Access-denied toast pattern: redirect with ?access_denied=1 + read searchParams on destination + router.replace to clean URL"

requirements-completed: [AUTH-04, AUTH-05, AUTH-06]

# Metrics
duration: 12min
completed: 2026-03-09
---

# Phase 3 Plan 02: Auth Lifecycle Summary

**AuthContext hydrates from /v1/users/me on mount, AuthGuard shows FullPageSpinner while loading, SiteLayout header is conditionally authenticated, and dashboard stub handles access-denied redirect with sonner toast**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-09T23:21:51Z
- **Completed:** 2026-03-09T23:33:00Z
- **Tasks:** 2 of 3 complete (Task 3 is checkpoint:human-verify — awaiting QA)
- **Files modified:** 4

## Accomplishments

- AuthContext now calls apiFetch('/v1/users/me') when token present, hydrating real user state; stale tokens cleared on 401
- AuthGuard replaced null-render with FullPageSpinner — eliminates flash of protected content during auth resolution
- SiteLayout desktop and mobile headers conditionally show Dashboard + Logout vs Join + Login based on auth state
- Dashboard stub created with access-denied toast fired from ?access_denied=1 query param

## Task Commits

Each task was committed atomically:

1. **Task 1: AuthContext hydration + AuthGuard spinner + access-denied signal** - `86235aa` (feat)
2. **Task 2: SiteLayout conditional header + dashboard stub** - `9137e09` (feat)

**Plan metadata:** (awaiting QA checkpoint completion)

## Files Created/Modified

- `contexts/AuthContext.tsx` - Replaced stub useEffect with apiFetch('/v1/users/me') call; loading=false in .finally() only
- `components/layout/AuthGuard.tsx` - Added FullPageSpinner on loading=true; updated access-denied redirect to include ?access_denied=1
- `components/layout/SiteLayout.tsx` - Added useAuth + useRouter; conditional desktop + mobile header auth state
- `app/(member)/dashboard/page.tsx` - Minimal dashboard stub; reads ?access_denied=1 and fires sonner toast.error

## Decisions Made

- loading=false set exclusively in .finally() — if set in happy path, AuthGuard could see user=null before setUser runs and incorrectly redirect to /login
- Access-denied signal passed as ?access_denied=1 query param — survives the router.replace and is cleaned up by a follow-up replace("/dashboard")
- Logout button uses onClick handler only (no href prop on ChromeButton) — passing href="/logout" would 404

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Full auth lifecycle is wired end-to-end; Task 3 (QA checkpoint) is the only remaining step
- After QA approval, AUTH-04/05/06 are fully delivered
- Phase 4 (member dashboard) can build on the dashboard stub at app/(member)/dashboard/page.tsx

---
*Phase: 03-authentication*
*Completed: 2026-03-09*
