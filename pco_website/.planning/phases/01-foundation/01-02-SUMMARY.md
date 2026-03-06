---
phase: 01-foundation
plan: "02"
subsystem: auth
tags: [jwt, localStorage, next.js, react-context, typescript, proxy]

# Dependency graph
requires:
  - phase: 01-foundation plan 01
    provides: Tailwind v4 config, fonts, globals.css, root layout shell, route group directories

provides:
  - types/api.ts: User, AuthTokens, ApiError shared TypeScript interfaces
  - lib/utils.ts: cn() utility for class merging
  - lib/auth.ts: localStorage token helpers (getAccessToken, getRefreshToken, setTokens, clearTokens)
  - lib/api.ts: apiFetch() with auto Bearer header + singleton refresh queue
  - contexts/AuthContext.tsx: AuthProvider, useAuth hook with login/logout
  - components/layout/AuthGuard.tsx: client-side role-based route guard
  - proxy.ts: Next.js 16 server-side optimistic redirect via auth-hint cookie

affects:
  - 01-03 (components use cn(), AuthGuard pattern)
  - Phase 2 (public pages use AuthContext)
  - Phase 3 (login page calls login() from AuthContext)
  - Phase 4 (dashboard uses apiFetch(), AuthGuard member role)
  - Phase 5 (admin uses apiFetch(), AuthGuard admin role)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Singleton refresh promise for concurrent 401 handling
    - auth-hint session cookie for server-side optimistic redirects
    - SSR guards (typeof window === "undefined") in localStorage helpers
    - Client-only AuthContext hydrated in useEffect to avoid SSR mismatch

key-files:
  created:
    - types/api.ts
    - lib/utils.ts
    - lib/auth.ts
    - lib/api.ts
    - contexts/AuthContext.tsx
    - components/layout/AuthGuard.tsx
    - proxy.ts
  modified:
    - app/layout.tsx
    - app/(member)/layout.tsx
    - app/(admin)/layout.tsx

key-decisions:
  - "Singleton refreshPromise prevents duplicate token refresh calls when concurrent requests all receive 401"
  - "auth-hint is an optimistic hint only — real authorization enforced by FastAPI; proxy redirect prevents flash of protected content"
  - "localStorage token storage confirmed — shapes auth as client-only with no Server Component token access"
  - "proxy.ts (not middleware.ts) required for Next.js 16; exports named function 'proxy'"

patterns-established:
  - "apiFetch() pattern: call from any client component; auto-injects Bearer header; handles refresh"
  - "AuthGuard pattern: wrap route group layout with requiredRole prop"
  - "AuthContext pattern: login() sets tokens + auth-hint cookie; logout() clears both"

requirements-completed:
  - INFRA-01
  - INFRA-02
  - INFRA-03
  - INFRA-04
  - INFRA-05

# Metrics
duration: 2min
completed: 2026-03-06
---

# Phase 1 Plan 02: Auth and API Infrastructure Summary

**localStorage JWT auth with singleton refresh queue, AuthContext with auth-hint cookie, and Next.js 16 proxy for server-side optimistic redirects**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-03-06T08:36:57Z
- **Completed:** 2026-03-06T08:38:40Z
- **Tasks:** 3
- **Files modified:** 10

## Accomplishments

- Complete client-side auth system: token storage, apiFetch() wrapper, AuthContext with login/logout
- Singleton refresh promise ensuring only one token refresh fires regardless of concurrent 401s
- Next.js 16 proxy.ts with auth-hint cookie logic for server-side redirect before React hydrates
- AuthGuard component wired into both (member) and (admin) route group layouts

## Task Commits

Each task was committed atomically:

1. **Task 1: Create shared types, cn() utility, and token helpers** - `63754f4` (feat)
2. **Task 2: Build apiFetch() with singleton refresh queue and AuthContext** - `619d3d1` (feat)
3. **Task 3: Create AuthGuard component, proxy.ts, and wire route group layouts** - `bd2bad7` (feat)

## Files Created/Modified

- `types/api.ts` - User, AuthTokens, ApiError TypeScript interfaces
- `lib/utils.ts` - cn() combining clsx + tailwind-merge
- `lib/auth.ts` - Token helpers: getAccessToken, getRefreshToken, setTokens, clearTokens (with SSR guards)
- `lib/api.ts` - apiFetch() with auto auth header and singleton refreshPromise
- `contexts/AuthContext.tsx` - AuthProvider, useAuth hook, login/logout with auth-hint cookie management
- `components/layout/AuthGuard.tsx` - Client-side AuthGuard accepting requiredRole prop
- `proxy.ts` - Next.js 16 proxy with auth-hint cookie redirect logic
- `app/layout.tsx` - Added AuthProvider wrapping body children
- `app/(member)/layout.tsx` - Wired AuthGuard with requiredRole="member"
- `app/(admin)/layout.tsx` - Wired AuthGuard with requiredRole="admin"

## Decisions Made

- Singleton refreshPromise: module-level variable in lib/api.ts ensures only one refresh call fires when multiple concurrent requests get 401 — subsequent callers await the same promise
- auth-hint cookie: session-scoped (no max-age), SameSite=Lax, set on login and cleared on logout — optimistic hint only, FastAPI remains the real authorization authority
- proxy.ts exports named function `proxy` (not `middleware`) as required by Next.js 16 API

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required. `NEXT_PUBLIC_API_BASE` environment variable will be needed at runtime but is referenced in lib/api.ts without blocking the build.

## Next Phase Readiness

- All auth infrastructure contracts established for Phase 3 (login page) and Phase 4/5 (dashboard/admin)
- apiFetch() ready to call any FastAPI endpoint with automatic token injection
- AuthGuard enforces role access in (member) and (admin) route groups
- Proxy provides server-side pre-redirect before React hydration for both /dashboard and /admin routes

---
*Phase: 01-foundation*
*Completed: 2026-03-06*
