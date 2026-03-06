# Phase 3: Authentication - Research

**Researched:** 2026-03-06
**Domain:** Next.js App Router auth lifecycle — LoginForm, AuthContext hydration, AuthGuard spinner, access-denied signaling, SiteLayout conditional header
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Login Page Layout**
- ChromeCard centered horizontally and vertically on a full-height black page
- (auth)/layout.tsx is already minimal (no SiteLayout header) — blank canvas
- Inside the card: "PSI CHI OMEGA" in Cormorant Garamond (SectionTitle) → Divider component (chrome line + green dot) → Email field → Password field → Submit button → admin note
- Card width: narrow/medium, single column — no grid

**Login Page Error State**
- Sonner toast notification for invalid credentials: "Invalid email or password."
- Toast fires on failed POST /v1/auth/login — no inline field errors for auth failures
- Generic message — no hint about whether email exists (no enumeration)

**Login Page Admin Note**
- Small muted text below the submit button
- Text: "Accounts are created by admins. Contact your chapter officer to get access."
- Unobtrusive — same visual weight as form helper text

**AuthContext Hydration**
- On mount, if a token exists in localStorage: fetch GET /v1/users/me to populate the user object
- On 401: trigger the existing singleton refresh flow → retry once → on failure, clearTokens and setUser(null)
- On no token: setUser(null) immediately
- Only setUser(data) when the fetch succeeds — user object is never a stub

**Loading State (AuthGuard)**
- While AuthContext is resolving (loading=true): show a centered full-page spinner on a black background
- AuthGuard currently renders null while loading — Phase 3 replaces null with the spinner component
- Prevents flash of protected content AND provides visible feedback during the /v1/users/me fetch

**Already-Authenticated Redirect**
- If an authenticated user navigates to /login: redirect to /dashboard
- LoginForm checks auth state on mount; if user is set, router.replace('/dashboard')

**Access Denied Experience**
- Non-admin user hitting /admin/* → AuthGuard redirects to /dashboard
- A Sonner toast fires on the dashboard after redirect: "Access denied. Admin privileges required."
- Implementation mechanism (URL param vs sessionStorage flag) is Claude's discretion
- Dashboard stays visually unchanged — toast is the only indicator

**Logout Placement**
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

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AUTH-01 | /login page with email and password fields; note that accounts are admin-created | LoginForm client component: ChromeCard layout, custom Tailwind inputs, admin note text |
| AUTH-02 | Login submits to POST /v1/auth/login; on success stores tokens in localStorage and redirects to /dashboard | apiFetch<AuthTokens> + AuthContext.login() call; already wired — LoginForm calls it then router.push('/dashboard') |
| AUTH-03 | Invalid credentials show generic "Invalid email or password" with no email enumeration | Sonner toast(error, ...) on catch; backend 401 shape confirmed in apiFetch error path |
| AUTH-04 | Logout clears localStorage tokens and redirects to /login | AuthContext.logout() already implemented; SiteLayout LOGOUT button calls logout() + router.replace('/') — decisions say redirect to / |
| AUTH-05 | Protected routes (/dashboard, /admin/*) redirect unauthenticated users to /login | AuthGuard already does this; Phase 3 adds spinner while loading=true so UX is complete |
| AUTH-06 | Admin routes (/admin/*) redirect authenticated non-admin users to /dashboard with "Access Denied" | AuthGuard already redirects; Phase 3 adds signal mechanism + dashboard toast |
</phase_requirements>

---

## Summary

Phase 3 is an integration and completion phase, not a greenfield build. The auth infrastructure (AuthContext, AuthGuard, lib/auth.ts, lib/api.ts, route group layouts) was fully scaffolded in Phase 1. The two gaps remaining are: (1) the /login page UI does not exist yet, and (2) several auth lifecycle behaviors are stubbed with TODOs (AuthContext's useEffect does not call /v1/users/me, AuthGuard renders null during loading instead of a spinner, SiteLayout header is hardcoded with Join/Login regardless of auth state, and the access-denied redirect has no downstream signal to the dashboard).

The codebase audit confirms no third-party form library is in use for this phase — the CONTEXT.md explicitly rules out shadcn, and the existing Phase 2 join form used react-hook-form + zod. The login form is simpler (two fields, no complex validation beyond required/format) and can be implemented with controlled React state directly. Using a form library for two fields would add unnecessary dependency weight.

The access-denied signal is Claude's discretion. Research points to URL query param (`?access_denied=1`) as the most straightforward approach: no state management overhead, survives hard navigation, easy to strip from URL after reading, and works with `router.replace('/dashboard?access_denied=1')` which is already in the AuthGuard redirect path.

**Primary recommendation:** Implement in two task files matching the planned split: (1) LoginForm client component + (auth)/login/page.tsx, and (2) AuthContext hydration + AuthGuard spinner + SiteLayout header + access-denied signal. Use URL param `?access_denied=1` for the access denied signal.

---

## Standard Stack

### Core (already installed — no new packages needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| next | 15.x | App Router, useRouter, Link | Project foundation |
| react | 19.x | useState, useEffect, client components | Project foundation |
| sonner | latest | Toast notifications | Already configured in root layout, dark theme |
| tailwindcss | v4 | @theme tokens for styling | Project foundation, no config file |

### Supporting (already installed)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @/lib/auth | local | getAccessToken, clearTokens, setTokens | All token storage operations |
| @/lib/api | local | apiFetch<T> with auth + refresh | All authenticated API calls |
| @/contexts/AuthContext | local | useAuth(), AuthProvider | All auth state reads and mutations |

**No new packages required for Phase 3.** All dependencies are installed and operational.

---

## Architecture Patterns

### File Creation Map

```
app/
└── (auth)/
    └── login/
        └── page.tsx            ← CREATE: renders <LoginForm />, no layout changes needed

components/
└── auth/
    └── LoginForm.tsx           ← CREATE: "use client", controlled form, apiFetch login

contexts/
└── AuthContext.tsx             ← MODIFY: useEffect — add /v1/users/me fetch when token present

components/layout/
├── AuthGuard.tsx               ← MODIFY: replace null return with <FullPageSpinner /> while loading
└── SiteLayout.tsx              ← MODIFY: add useAuth(), conditional header based on user state
```

### Pattern 1: AuthContext useEffect Hydration

**What:** On client mount, if access token exists, call GET /v1/users/me to populate `user`. If 401, the existing apiFetch singleton refresh handles retry; if still fails, clearTokens + setUser(null). Set loading=false in finally block.

**When to use:** The hydration runs exactly once on mount via `useEffect([], [])`. The `loading` state must stay `true` until this resolves — AuthGuard depends on `loading` to know when to render children vs spinner vs redirect.

**Current state (lib/AuthContext.tsx lines 26-38):**
```typescript
// EXISTING STUB — Phase 3 replaces the else branch
useEffect(() => {
  const token = getAccessToken();
  if (!token) {
    setLoading(false);
  } else {
    // Token present — Phase 3 will refine this
    setLoading(false);  // ← REPLACE with apiFetch('/v1/users/me') call
  }
}, []);
```

**Phase 3 target pattern:**
```typescript
// Source: project codebase (lib/api.ts, contexts/AuthContext.tsx)
useEffect(() => {
  const token = getAccessToken();
  if (!token) {
    setLoading(false);
    return;
  }
  apiFetch<User>("/v1/users/me")
    .then((data) => setUser(data))
    .catch(() => {
      // 401 with exhausted refresh, or network error — clear stale tokens
      clearTokens();
      document.cookie = "auth-hint=; path=/; max-age=0; samesite=lax";
      setUser(null);
    })
    .finally(() => setLoading(false));
}, []);
```

**Key detail:** apiFetch already handles the 401 → refresh → retry cycle. The catch block here only fires if refresh itself fails (returns null token), which apiFetch converts to a thrown Error with status 401. No manual refresh logic needed in AuthContext.

### Pattern 2: AuthGuard Spinner

**What:** Replace `if (loading) return null` with a full-page spinner component. The spinner must be visually on-brand — a simple rotating ring, not a library spinner.

**Current state (AuthGuard.tsx line 31):**
```typescript
if (loading) return null;  // ← REPLACE with spinner
```

**Phase 3 target:**
```typescript
// Source: project codebase (components/layout/AuthGuard.tsx)
if (loading) return (
  <div className="fixed inset-0 bg-black flex items-center justify-center">
    <div className="w-8 h-8 rounded-full border border-chrome-light/30 border-t-chrome-light animate-spin" />
  </div>
);
```

The spinner uses:
- `fixed inset-0 bg-black` — covers the full viewport, matches the auth background
- `border border-chrome-light/30 border-t-chrome-light` — chrome ring aesthetic (dim base, bright top segment)
- `animate-spin` — Tailwind built-in, 1s linear infinite, no custom keyframe needed

**Discretion note:** Can be extracted to a standalone `FullPageSpinner` component if the planner prefers reusability (Phase 4 dashboard will also need a loading state). Recommend extracting.

### Pattern 3: LoginForm Client Component

**What:** A controlled React form with email and password fields. On submit, POST /v1/auth/login via apiFetch, call AuthContext.login() on success, toast error on failure.

**Key behaviors:**
1. On mount: if `user` is already set, `router.replace('/dashboard')` immediately
2. Submit handler: set `isSubmitting=true`, call apiFetch, on success call `login(tokens, user)` then `router.push('/dashboard')`, on error call `toast.error('Invalid email or password.')`
3. No inline field-level errors for auth failure — toast only
4. Disable submit button while `isSubmitting=true`

**API call shape:**
```typescript
// Source: lib/api.ts — apiFetch is the project standard
// POST /v1/auth/login expected request body (inferred from backend contract)
const data = await apiFetch<{ access_token: string; refresh_token: string; user: User }>(
  "/v1/auth/login",
  {
    method: "POST",
    body: JSON.stringify({ email, password }),
  }
);
```

**CAUTION:** The API response shape for POST /v1/auth/login is not directly confirmed in the codebase — only `AuthTokens` type (`access_token`, `refresh_token`) is defined. The `login()` function in AuthContext accepts `(tokens: AuthTokens, user: User)` as separate arguments. Verify with backend whether `/v1/auth/login` returns `{ access_token, refresh_token, user }` as a combined object or tokens and user separately. The LoginForm will need to destructure accordingly.

### Pattern 4: Access Denied Signal (URL Param)

**What:** When AuthGuard redirects a non-admin to /dashboard, pass `?access_denied=1` in the URL. The dashboard page reads this param on mount, fires the toast, then strips the param from the URL (router.replace without the param).

**Why URL param over sessionStorage:**
- Survives hard navigation without JS storage access
- No cleanup race condition (sessionStorage read before clear is fine but adds cognitive overhead)
- Idiomatic with Next.js searchParams — no extra browser API
- Easy to strip: `router.replace('/dashboard')` after reading

**AuthGuard change:**
```typescript
// Source: project codebase (components/layout/AuthGuard.tsx)
// Current:
if (requiredRole === "admin" && user.role !== "admin") {
  router.replace("/dashboard");
}
// Phase 3:
if (requiredRole === "admin" && user.role !== "admin") {
  router.replace("/dashboard?access_denied=1");
}
```

**Dashboard reading the param (Phase 3 task 2 creates the dashboard stub or adds to existing):**
```typescript
// "use client" component on /dashboard
const searchParams = useSearchParams();
useEffect(() => {
  if (searchParams.get("access_denied") === "1") {
    toast.error("Access denied. Admin privileges required.");
    router.replace("/dashboard");  // strip param
  }
}, [searchParams, router]);
```

**Note:** The /dashboard page does not yet exist (Phase 4 builds it). Phase 3 must create a minimal dashboard stub with this access-denied toast logic so AUTH-06 is verifiable.

### Pattern 5: SiteLayout Conditional Header

**What:** SiteLayout is a client component ("use client" already present). Add `useAuth()` and conditionally render Desktop CTAs and Mobile menu auth section based on `user` state.

**Current state (SiteLayout.tsx lines 71-78):**
```typescript
<div className="hidden md:flex items-center gap-3">
  <ChromeButton href="/join" variant="primary">Join</ChromeButton>
  <ChromeButton href="/login" variant="secondary">Login</ChromeButton>
</div>
```

**Phase 3 target:**
```typescript
// Source: project codebase (components/layout/SiteLayout.tsx)
const { user, logout } = useAuth();

// Desktop CTAs — conditional
{user ? (
  <div className="hidden md:flex items-center gap-3">
    <Link href="/dashboard" className="text-xs tracking-[0.15em] uppercase text-white/70 hover:text-white transition-colors duration-200">
      Dashboard
    </Link>
    <ChromeButton variant="secondary" onClick={() => { logout(); router.replace('/'); }}>
      Logout
    </ChromeButton>
  </div>
) : (
  <div className="hidden md:flex items-center gap-3">
    <ChromeButton href="/join" variant="primary">Join</ChromeButton>
    <ChromeButton href="/login" variant="secondary">Login</ChromeButton>
  </div>
)}
```

**SiteLayout must import useRouter** since logout calls `router.replace('/')`. SiteLayout currently does not use `useRouter` — this is the only new import needed.

**Mobile menu** needs the same conditional: replace the Join/Login ChromeButtons with Dashboard link + Logout button when authenticated.

### Anti-Patterns to Avoid

- **Trusting the token without validation:** The Phase 1 stub set `loading=false` without calling `/v1/users/me`. Phase 3 must validate the token to populate `user` — never treat a token's presence as proof of a valid session.
- **Setting user to a stub object:** CONTEXT.md is explicit: "user object is never a stub." Only call `setUser(data)` on successful /v1/users/me fetch.
- **Throwing on 401 in the hydration catch:** apiFetch handles refresh internally. Don't re-implement refresh logic in AuthContext's catch block — just clear tokens and setUser(null).
- **Using localStorage for access-denied flag:** URL param is simpler and doesn't require cleanup timing coordination.
- **Calling `router.push` instead of `router.replace` for auth redirects:** Protected route redirects should use `replace` so the protected URL is not in browser history.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Token storage | Custom cookie/session logic | lib/auth.ts (getAccessToken, setTokens, clearTokens) | Already handles SSR guard, localStorage keys defined |
| Token refresh on 401 | Manual retry loop | apiFetch<T> in lib/api.ts | Singleton refreshPromise already prevents race conditions |
| Auth state | Component-level useState | useAuth() from AuthContext | Single source of truth; AuthGuard and SiteLayout both depend on it |
| Toast notifications | Alert divs, inline error text | sonner toast() | Already configured with dark theme in root layout |
| Spinner animation | CSS keyframes, animation library | Tailwind animate-spin | Built-in, no extra setup |

---

## Common Pitfalls

### Pitfall 1: Race Between AuthContext Loading and AuthGuard Render

**What goes wrong:** If loading=false is set before the /v1/users/me fetch resolves, AuthGuard sees `user=null` while `loading=false` and immediately redirects to /login — even though the user is authenticated.

**Why it happens:** The stub code in Phase 1 set `loading=false` synchronously in both branches. Phase 3 must keep `loading=true` until the fetch's `.finally()` block runs.

**How to avoid:** Set `loading=false` only in `.finally()`, never in the try or happy path.

**Warning signs:** User with valid localStorage tokens gets kicked to /login on every hard refresh.

### Pitfall 2: SiteLayout Hydration Mismatch

**What goes wrong:** SiteLayout is rendered server-side with `user=null` (AuthContext can only hydrate client-side from localStorage). If JSX differs between server render and client render, React throws a hydration error.

**Why it happens:** `user` is always null on server render; client render shows the authenticated state after hydration. Any conditional that changes DOM structure (not just classNames) will mismatch.

**How to avoid:** Render the logged-out header state on both server and initial client render. After hydration, React updates the DOM. Since SiteLayout is `"use client"`, this is not a strict SSR concern — but `loading=true` initially means `user=null` briefly, so the unauthenticated view will flash before switching to authenticated. This is acceptable (and fast), but do not add suppressHydrationWarning or any hack.

**Warning signs:** "Hydration failed because the initial UI does not match" console error.

### Pitfall 3: Sonner Import Path

**What goes wrong:** Importing from `sonner` without the `transpilePackages` config causes ESM resolution errors in Next.js 15+.

**Why it happens:** Already solved in Phase 1 (`transpilePackages: ["sonner"]` in next.config.ts). Don't remove it.

**How to avoid:** Import `toast` from `"sonner"` directly. The config is in place.

```typescript
import { toast } from "sonner";
// then:
toast.error("Invalid email or password.");
```

### Pitfall 4: ChromeButton href vs onClick for Logout

**What goes wrong:** ChromeButton renders an `<a>` tag when `href` is provided. Logout must be an `onClick` handler, not a link, because it runs async logic (clearTokens, setUser, router.replace).

**Why it happens:** ChromeButton's `if (href)` branch returns `<a href={href}>`. If you accidentally pass `href="/logout"` (which doesn't exist), it will navigate to a 404.

**How to avoid:** Pass no `href` to the Logout ChromeButton. Use `onClick` only.

### Pitfall 5: Dashboard Stub Must Exist for AUTH-06 Verification

**What goes wrong:** The /dashboard page doesn't exist yet (Phase 4 builds it). AUTH-06 requires verifying the access-denied toast fires on the dashboard after AuthGuard redirect. If there's no dashboard page, the redirect goes to a 404.

**Why it happens:** Phase ordering — authentication is Phase 3, dashboard content is Phase 4.

**How to avoid:** Phase 3 Task 2 must create a minimal `app/(member)/dashboard/page.tsx` stub (just a "use client" page that reads `?access_denied=1` and fires the toast). Phase 4 will expand this stub into the full dashboard.

---

## Code Examples

### Login Form Skeleton

```typescript
// Source: project conventions (contexts/AuthContext.tsx, lib/api.ts)
// app/(auth)/login/page.tsx — thin wrapper
import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-black flex items-center justify-center px-4">
      <LoginForm />
    </div>
  );
}
```

```typescript
// components/auth/LoginForm.tsx
"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuth } from "@/contexts/AuthContext";
import { apiFetch } from "@/lib/api";
import { ChromeCard } from "@/components/ui/ChromeCard";
import { ChromeButton } from "@/components/ui/ChromeButton";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { Divider } from "@/components/ui/Divider";
import type { AuthTokens, User } from "@/types/api";

export function LoginForm() {
  const { user, login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Already-authenticated redirect
  useEffect(() => {
    if (user) router.replace("/dashboard");
  }, [user, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      // Adjust destructuring based on actual API response shape
      const data = await apiFetch<AuthTokens & { user: User }>("/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      login({ access_token: data.access_token, refresh_token: data.refresh_token }, data.user);
      router.push("/dashboard");
    } catch {
      toast.error("Invalid email or password.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="w-full max-w-sm">
      <ChromeCard>
        {/* card contents */}
      </ChromeCard>
    </div>
  );
}
```

### FullPageSpinner Component

```typescript
// Source: project Tailwind @theme tokens (globals.css)
// components/ui/FullPageSpinner.tsx — recommended reusable extraction
export function FullPageSpinner() {
  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center">
      <div
        className="w-8 h-8 rounded-full border border-chrome-light/30 border-t-chrome-light animate-spin"
        role="status"
        aria-label="Loading"
      />
    </div>
  );
}
```

### AuthContext useEffect Hydration

```typescript
// Source: project codebase (contexts/AuthContext.tsx, lib/api.ts)
useEffect(() => {
  const token = getAccessToken();
  if (!token) {
    setLoading(false);
    return;
  }
  apiFetch<User>("/v1/users/me")
    .then((data) => setUser(data))
    .catch(() => {
      clearTokens();
      document.cookie = "auth-hint=; path=/; max-age=0; samesite=lax";
      setUser(null);
    })
    .finally(() => setLoading(false));
}, []);
```

### Dashboard Stub (Minimal — for AUTH-06)

```typescript
// Source: project conventions (contexts/AuthContext.tsx, Next.js useSearchParams)
// app/(member)/dashboard/page.tsx — Phase 3 stub; Phase 4 expands
"use client";

import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

export default function DashboardPage() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (searchParams.get("access_denied") === "1") {
      toast.error("Access denied. Admin privileges required.");
      router.replace("/dashboard");
    }
  }, [searchParams, router]);

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <p className="text-white/40 font-body tracking-widest uppercase text-sm">
        Dashboard — coming in Phase 4
      </p>
    </div>
  );
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| middleware.ts | proxy.ts | Next.js 16 rename | Already handled in Phase 1 — do not create middleware.ts |
| JWT in httpOnly cookies | localStorage for MVP | Project decision (Init) | auth-hint cookie is optimistic hint only; real auth in FastAPI |
| Form library (react-hook-form) | Controlled state for simple forms | Project-specific | Login has 2 fields — no form library needed |

**Deprecated/outdated:**
- `middleware.ts` naming: project uses `proxy.ts` per Next.js 16 convention. Already in place.
- `router.push` for protected redirects: use `router.replace` so the protected URL is not in history.

---

## Open Questions

1. **POST /v1/auth/login response shape**
   - What we know: AuthContext.login() accepts `(tokens: AuthTokens, user: User)` separately
   - What's unclear: Does the backend return `{ access_token, refresh_token, user }` as one object, or tokens and user in separate fields at the root level? AuthTokens type only has `access_token` and `refresh_token`.
   - Recommendation: Check with backend owner or inspect API docs before writing the LoginForm submit handler. If the response is `{ access_token, refresh_token }` only (no user), then the LoginForm would need to call GET /v1/users/me after login — but that would duplicate the AuthContext hydration. Most likely the login endpoint returns the user object inline. Assume combined response and adjust if needed.

2. **Dashboard page existence for AUTH-06 verification**
   - What we know: app/(member)/dashboard/page.tsx does not exist yet
   - What's unclear: Whether Phase 3 should create a full stub or just the bare minimum
   - Recommendation: Create a minimal stub (shown in Code Examples above) that satisfies AUTH-06 verification without implementing MEMBER-01 through MEMBER-04 content, which belong to Phase 4.

---

## Validation Architecture

> nyquist_validation is enabled in .planning/config.json.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None detected — no jest.config, vitest.config, pytest.ini, or __tests__ directory found |
| Config file | None — Wave 0 must establish if automated tests are required |
| Quick run command | N/A |
| Full suite command | N/A |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTH-01 | /login page renders with email/password fields and admin note | manual-only | N/A — no test framework | ❌ Wave 0 gap |
| AUTH-02 | Login success: tokens stored in localStorage, redirect to /dashboard | manual-only | N/A — no test framework | ❌ Wave 0 gap |
| AUTH-03 | Login failure: toast shows "Invalid email or password." | manual-only | N/A — no test framework | ❌ Wave 0 gap |
| AUTH-04 | Logout: localStorage cleared, redirect to / | manual-only | N/A — no test framework | ❌ Wave 0 gap |
| AUTH-05 | Unauthenticated /dashboard access: redirect to /login | manual-only | N/A — no test framework | ❌ Wave 0 gap |
| AUTH-06 | Non-admin /admin access: redirect to /dashboard with toast | manual-only | N/A — no test framework | ❌ Wave 0 gap |

**Justification for manual-only:** No test framework is installed in this project. All AUTH requirements involve browser-level behavior (localStorage, redirects, toast rendering, cookie setting) that requires either a full browser environment (Playwright/Cypress) or jsdom mocking (Jest/Vitest). Installing a test framework is out of scope for this phase. Verification is via manual smoke testing against the running dev server.

### Sampling Rate

- **Per task commit:** Manual dev server check (`pnpm dev` + browser verification)
- **Per wave merge:** Full manual smoke test of all AUTH-01 through AUTH-06
- **Phase gate:** All 6 AUTH requirements pass manual verification before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] No automated test framework exists — manual verification only for this phase
- [ ] If future phases add Playwright or Vitest, AUTH behaviors are prime candidates for E2E and unit tests respectively

---

## Sources

### Primary (HIGH confidence)

- Project codebase (direct file read) — `contexts/AuthContext.tsx`, `components/layout/AuthGuard.tsx`, `lib/auth.ts`, `lib/api.ts`, `app/layout.tsx`, `components/layout/SiteLayout.tsx`, `app/(auth)/layout.tsx`, `app/(member)/layout.tsx`, `app/(admin)/layout.tsx`, `types/api.ts`, `app/globals.css`
- Project codebase (direct file read) — `components/ui/ChromeCard.tsx`, `ChromeButton.tsx`, `Divider.tsx`, `SectionTitle.tsx`
- `.planning/phases/03-authentication/03-CONTEXT.md` — user decisions and locked choices

### Secondary (MEDIUM confidence)

- Next.js App Router docs pattern: `router.replace` for auth redirects (standard Next.js convention)
- Sonner docs: `toast.error()` API (confirmed via project usage in existing code)

### Tertiary (LOW confidence)

- POST /v1/auth/login response shape — inferred from AuthContext.login() signature and AuthTokens type; not directly confirmed from backend spec

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — entire stack is existing project code, no new dependencies
- Architecture: HIGH — patterns derived from direct codebase inspection
- Pitfalls: HIGH — specific to this codebase's known stubs and TODOs
- API response shape: LOW — inferred, not verified from backend spec

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable — no fast-moving external dependencies)
