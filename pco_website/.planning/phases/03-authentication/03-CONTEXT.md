# Phase 3: Authentication - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the /login page UI, complete the auth lifecycle (token validation on mount, logout, access denied feedback), and wire SiteLayout to show conditional auth state. AuthGuard, AuthContext scaffolding, and token helpers already exist from Phase 1 — Phase 3 completes their implementation and connects them to real UI.

</domain>

<decisions>
## Implementation Decisions

### Login Page Layout
- ChromeCard centered horizontally and vertically on a full-height black page
- (auth)/layout.tsx is already minimal (no SiteLayout header) — blank canvas
- Inside the card: "PSI CHI OMEGA" in Cormorant Garamond (SectionTitle) → Divider component (chrome line + green dot) → Email field → Password field → Submit button → admin note
- Card width: narrow/medium, single column — no grid

### Login Page Error State
- Sonner toast notification for invalid credentials: "Invalid email or password."
- Toast fires on failed POST /v1/auth/login — no inline field errors for auth failures
- Generic message — no hint about whether email exists (no enumeration)

### Login Page Admin Note
- Small muted text below the submit button
- Text: "Accounts are created by admins. Contact your chapter officer to get access."
- Unobtrusive — same visual weight as form helper text

### AuthContext Hydration
- On mount, if a token exists in localStorage: fetch GET /v1/users/me to populate the user object
- On 401: trigger the existing singleton refresh flow → retry once → on failure, clearTokens and setUser(null)
- On no token: setUser(null) immediately
- Only setUser(data) when the fetch succeeds — user object is never a stub

### Loading State (AuthGuard)
- While AuthContext is resolving (loading=true): show a centered full-page spinner on a black background
- AuthGuard currently renders null while loading — Phase 3 replaces null with the spinner component
- Prevents flash of protected content AND provides visible feedback during the /v1/users/me fetch

### Already-Authenticated Redirect
- If an authenticated user navigates to /login: redirect to /dashboard
- LoginForm checks auth state on mount; if user is set, router.replace('/dashboard')

### Access Denied Experience
- Non-admin user hitting /admin/* → AuthGuard redirects to /dashboard
- A Sonner toast fires on the dashboard after redirect: "Access denied. Admin privileges required."
- Implementation mechanism (URL param vs sessionStorage flag) is Claude's discretion
- Dashboard stays visually unchanged — toast is the only indicator

### Logout Placement
- Logout lives in SiteLayout header — conditional on auth state
- Logged out: [ JOIN ] [ LOGIN ] (existing behavior)
- Logged in: "Dashboard" nav link (text, routes to /dashboard) + [ LOGOUT ] ChromeButton secondary
- "Join" and "Login" are removed from the header when authenticated
- After logout: clearTokens + setUser(null) + router.replace('/')

### Claude's Discretion
- Exact spinner design (size, color, animation — keep minimal, on-brand)
- How the access-denied signal is passed from AuthGuard to dashboard (URL param, sessionStorage, etc.)
- Card padding, field spacing, input styling (consistent with Tailwind v4 @theme tokens)
- Whether "PSI CHI OMEGA" in the card uses SectionTitle component or a plain heading element

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `lib/auth.ts`: getAccessToken, getRefreshToken, setTokens, clearTokens — all ready, Phase 3 calls these directly
- `contexts/AuthContext.tsx`: AuthProvider with login/logout already wired; Phase 3 adds /v1/users/me fetch on mount to replace the TODO stub
- `components/layout/AuthGuard.tsx`: redirect logic complete; Phase 3 adds spinner rendering while loading=true
- `components/layout/SiteLayout`: Phase 3 adds conditional header rendering (Dashboard + Logout vs Join + Login) based on useAuth()
- `components/ui/ChromeCard`: metallic border wrapper — use as the login form container
- `components/ui/ChromeButton`: primary (green) for submit; secondary (chrome outline) for Logout in header
- `components/ui/Divider`: chrome line + green dot — use below the PCO logo inside the login card
- `lib/api.ts`: apiFetch<T>() with automatic Authorization header + 401/refresh handling — use for GET /v1/users/me on mount

### Established Patterns
- Sonner toast already configured (dark theme, success/error variants) — use for both login errors and access denied
- No component library (shadcn not used) — all inputs are custom Tailwind
- Tailwind v4 via @theme inline in globals.css — use bg-black, text-white, border-chrome, text-green etc.
- "use client" directive required for all components that use useAuth() or useRouter()
- auth-hint cookie: login sets it, logout clears it — already in AuthContext.login/logout

### Integration Points
- `app/(auth)/login/page.tsx` — needs to be created (LoginForm client component)
- `contexts/AuthContext.tsx` — useEffect update: add /v1/users/me fetch when token present
- `components/layout/AuthGuard.tsx` — replace null return with spinner while loading
- `components/layout/SiteLayout` — add useAuth() and conditional header rendering
- `app/layout.tsx` — AuthProvider must wrap the root layout so SiteLayout can access auth state

</code_context>

<specifics>
## Specific Ideas

- Login card mirrors the card style from the Phase 1 dev-preview — ChromeCard with metallic border and subtle hover glow
- Header auth state: "Dashboard" as a plain nav link (not a button), "LOGOUT" as ChromeButton secondary — matches the uppercase tracked nav style established in Phase 1
- The loading spinner should feel like the rest of the UI — minimal, not a spinning React logo or generic CSS spinner; a simple rotating chrome/white ring would fit the aesthetic

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-authentication*
*Context gathered: 2026-03-06*
