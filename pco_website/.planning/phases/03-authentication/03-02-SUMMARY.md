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
  - All 6 AUTH requirements verified end-to-end via manual + Playwright QA

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
    - app/(member)/layout.tsx
    - app/(admin)/layout.tsx
    - app/(public)/page.tsx

key-decisions:
  - "loading=false set only in .finally() — never in happy path — prevents AuthGuard from seeing user=null during fetch"
  - "access-denied signal via ?access_denied=1 query param rather than separate state — survives router.replace across component boundaries"
  - "Logout uses onClick only on ChromeButton (no href) — passing href would 404 on /logout route"
  - "Brief flash of unauthenticated header on first render is expected and acceptable — no suppressHydrationWarning added"
  - "SiteLayout hides nav links and hamburger when user is authenticated — prevents duplicate chrome inside protected layouts"

patterns-established:
  - "Auth state conditional rendering: user ? <authenticated /> : <unauthenticated /> (no loading branch in header — spinner only in AuthGuard)"
  - "Access-denied toast pattern: redirect with ?access_denied=1 + read searchParams on destination + router.replace to clean URL"

requirements-completed: [AUTH-04, AUTH-05, AUTH-06]

# Metrics
duration: ~30min (two sessions)
completed: 2026-03-09
---

# Phase 3 Plan 02: Auth Lifecycle Summary

**AuthContext hydrates from /v1/users/me on mount, AuthGuard shows FullPageSpinner while loading, SiteLayout header is conditionally authenticated, and all 6 AUTH requirements verified via manual + Playwright QA**

## Performance

- **Duration:** ~30 min (across two sessions)
- **Started:** 2026-03-09T23:21:51Z
- **Completed:** 2026-03-09T23:30:00Z
- **Tasks:** 3 of 3 complete
- **Files modified:** 7

## Accomplishments

- AuthContext now calls `apiFetch('/v1/users/me')` when token present, hydrating real user state; stale tokens cleared on 401
- AuthGuard replaced null-render with FullPageSpinner — eliminates flash of protected content during auth resolution
- SiteLayout desktop and mobile headers conditionally show Dashboard + Logout vs Join + Login based on auth state; hides nav when authenticated inside protected layouts
- Dashboard stub created with access-denied toast fired from `?access_denied=1` query param
- All 6 AUTH requirements passed manual and Playwright QA verification

## Task Commits

Each task was committed atomically:

1. **Task 1: AuthContext hydration + AuthGuard spinner + access-denied signal** - `86235aa` (feat)
2. **Task 2: SiteLayout conditional header + dashboard stub** - `9137e09` (feat)
3. **Task 3: QA — full auth lifecycle manual verification (+ QA fixes)** - committed with summary

**Plan metadata:** `7c6fec8` (docs: complete auth lifecycle plan)

## Files Created/Modified

- `contexts/AuthContext.tsx` - Replaced stub useEffect with apiFetch('/v1/users/me') call; loading=false in .finally() only
- `components/layout/AuthGuard.tsx` - Added FullPageSpinner on loading=true; updated access-denied redirect to include ?access_denied=1
- `components/layout/SiteLayout.tsx` - Added useAuth + useRouter; conditional desktop + mobile header auth state; hides nav when user is authenticated
- `app/(member)/dashboard/page.tsx` - Minimal dashboard stub; reads ?access_denied=1 and fires sonner toast.error
- `app/(member)/layout.tsx` - Added SiteLayout wrapper (QA fix)
- `app/(admin)/layout.tsx` - Added SiteLayout wrapper (QA fix)
- `app/(public)/page.tsx` - Fixed getInitials null crash and missing key prop on leadership cards (QA fix)

## Decisions Made

- `loading=false` set exclusively in `.finally()` — if set in happy path, AuthGuard could see `user=null` before `setUser` runs and incorrectly redirect to /login
- Access-denied signal passed as `?access_denied=1` query param — survives the router.replace and is cleaned up by a follow-up `replace("/dashboard")`
- Logout button uses onClick handler only (no href prop on ChromeButton) — passing `href="/logout"` would 404
- SiteLayout hides nav links and hamburger when user is authenticated — prevents duplicate navigation chrome inside member/admin layouts

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Added SiteLayout wrapper to member and admin route group layouts**
- **Found during:** Task 3 (QA verification)
- **Issue:** `(member)/layout.tsx` and `(admin)/layout.tsx` were missing SiteLayout wrapping, so the site header did not render inside protected routes
- **Fix:** Wrapped children with SiteLayout in both layouts; SiteLayout updated to hide nav links and hamburger when user is authenticated to prevent double navigation
- **Files modified:** `app/(member)/layout.tsx`, `app/(admin)/layout.tsx`, `components/layout/SiteLayout.tsx`
- **Verification:** Dashboard page shows correct header; auth-conditional nav visible on protected routes
- **Committed in:** Task 3 QA commit

**2. [Rule 1 - Bug] Fixed getInitials crash on null name in public homepage**
- **Found during:** Task 3 (QA verification)
- **Issue:** `getInitials(null)` threw a runtime crash on the homepage leadership section when a leader's name was null
- **Fix:** Added null guard in getInitials helper; added missing `key` prop on leadership card list render
- **Files modified:** `app/(public)/page.tsx`
- **Verification:** Homepage renders without crash; React key warning resolved
- **Committed in:** Task 3 QA commit

---

**Total deviations:** 2 auto-fixed (1 missing critical, 1 bug)
**Impact on plan:** Both fixes were necessary for correctness. No scope creep.

## Issues Encountered

- First session hit a rate limit before QA checkpoint — plan was paused mid-execution and resumed in a second agent session
- QA revealed SiteLayout was not wrapped in protected route layouts — caught and fixed before plan marked complete

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Full auth lifecycle is wired and verified end-to-end (AUTH-01 through AUTH-06 complete)
- Phase 4 (member dashboard) can build on the dashboard stub at `app/(member)/dashboard/page.tsx` — AuthGuard already wraps the member route group
- Phase 5 (admin portal) can build on admin routes — AuthGuard with `requiredRole="admin"` already in place
- Blocker to confirm before Phase 4: signed URL TTL with backend owner (affects whether to fetch on page load or on click)

---
*Phase: 03-authentication*
*Completed: 2026-03-09*
