# Pitfalls Research

**Domain:** Next.js 16 App Router + Tailwind v4 + JWT Auth Frontend
**Researched:** 2026-03-05
**Confidence:** HIGH (all critical pitfalls verified against official Next.js 16.1.6 and Tailwind v4 docs)

---

## Critical Pitfalls

### Pitfall 1: `middleware.ts` No Longer Exists in Next.js 16 — It's `proxy.ts`

**What goes wrong:**
Developers write route protection in `middleware.ts` following v15 tutorials. Next.js 16 deprecated and renamed the Middleware convention to `proxy.ts` with the exported function renamed from `middleware()` to `proxy()`. The old file is silently ignored, so auth protection appears to work locally but routes are completely unprotected.

**Why it happens:**
All existing documentation, tutorials, and AI training data reference `middleware.ts`. The rename happened in Next.js 16.0.0. The old file does not throw an error — it simply does not run.

**How to avoid:**
- Create `proxy.ts` at the project root (same level as `app/`), not `middleware.ts`
- Export a function named `proxy`, not `middleware`
- Use the official codemod if migrating: `npx @next/codemod@canary middleware-to-proxy .`
- Verify auth is enforced: visit a protected route while logged out; if you see the page, protection is not working

```typescript
// proxy.ts (NOT middleware.ts)
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function proxy(request: NextRequest) {
  // auth logic here
}

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*'],
}
```

**Warning signs:**
- File is named `middleware.ts` or function is named `export function middleware()`
- Protected routes are accessible without a token in the browser
- No build errors or runtime warnings about the missing file

**Phase to address:** Phase 1 (Auth foundation) — get this right before building any protected routes.

---

### Pitfall 2: `proxy.ts` Cannot Read `localStorage` — JWT Auth Pattern Breaks

**What goes wrong:**
The project stores JWTs in `localStorage` for MVP simplicity. `proxy.ts` (the Next.js Proxy/Middleware) runs in the Node.js server environment (Next.js 15.5+ made Node.js runtime stable; Next.js 16 defaults to Node.js runtime). `localStorage` is a browser API and does not exist in this context. Developers attempt to read the token in `proxy.ts` and get a runtime error or `undefined`, causing all protected routes to redirect to login even when the user is authenticated.

**Why it happens:**
`localStorage`-based auth is a natural pattern for SPAs but is fundamentally incompatible with server-side route protection. Proxy/Middleware runs before the page renders, before the browser has a chance to attach the token.

**How to avoid:**
Proxy can only inspect cookies and request headers. With `localStorage`-based auth, route protection MUST happen client-side:

Option A (recommended for this project — matches the constraint): Skip proxy-level auth. Protect routes using a client-side `AuthGuard` component that reads `localStorage`, checks token validity, and redirects with `useRouter` if unauthenticated. Render a loading spinner while checking.

Option B (future): Switch to HttpOnly cookies so Proxy can read the token and redirect server-side.

For this MVP, implement a `useAuthGuard()` hook or `<ProtectedRoute>` wrapper in each protected layout:
```typescript
'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export function useAuthGuard() {
  const router = useRouter()
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) router.replace('/login')
  }, [router])
}
```

**Warning signs:**
- Code in `proxy.ts` that calls `localStorage.getItem()`
- "localStorage is not defined" runtime errors in server logs
- Redirect loop: every page redirect to login, even after logging in

**Phase to address:** Phase 1 (Auth foundation) — decide on the auth guard pattern before building protected pages.

---

### Pitfall 3: Tailwind v4 Utility Class Names Changed — Silent Visual Regressions

**What goes wrong:**
Tailwind v4 renamed several commonly used utility classes. Code that uses v3 class names compiles without errors but produces wrong visual output. Shadow, blur, border, ring, and rounded utilities all shifted one step on the scale.

**Specific renames that will affect this project:**

| v3 class (broken in v4) | v4 class (correct) | Impact |
|--------------------------|-------------------|--------|
| `shadow-sm` | `shadow-xs` | Subtle shadows look wrong |
| `shadow` (bare) | `shadow-sm` | Default shadow one step heavier |
| `blur-sm` | `blur-xs` | Blur values off |
| `rounded-sm` | `rounded-xs` | Border radius too large |
| `outline-none` | `outline-hidden` | Focus outlines invisible |
| `ring` (3px) | `ring-3` | Ring width changed to 1px default |
| `bg-opacity-50` | `bg-black/50` | Opacity modifier syntax |
| `border` (implicit gray) | `border border-gray-200` | Borders invisible (now `currentColor`) |

**Why it happens:**
Tailwind v4 reorganized the scale to be more consistent. Every developer who follows v3 tutorials or copies old code will hit these. The AI code generation tools produce v3 class names by default.

**How to avoid:**
- At project start, document the v4 class mapping in a team reference
- The existing `globals.css` uses `@import "tailwindcss"` (v4 syntax) — confirm all utility usage matches v4 names
- Run `npx @tailwindcss/upgrade` if migrating any existing CSS
- For borders: always specify explicit color (`border border-white/20`) rather than relying on defaults
- For rings: always specify `ring-3` rather than bare `ring`

**Warning signs:**
- `border` or `divide-` utilities appear invisible
- Shadows/blurs look subtly wrong
- `outline-none` on focus elements actually hides outlines (accessibility issue!)
- Ring on focused elements is 1px instead of 3px

**Phase to address:** Phase 1 (Design system setup) — establish Tailwind v4 patterns before building any components.

---

### Pitfall 4: `tailwind.config.js` Does Not Exist in v4 — Config Goes in `globals.css`

**What goes wrong:**
Developers add custom colors, fonts, or spacing in a `tailwind.config.js` file as they would in v3. In v4, this file is completely ignored. Custom tokens are silently unavailable. The forest green brand color (`#228B22`) and EB Garamond font are not applied despite the config file existing.

**Why it happens:**
Tailwind v4 adopts a CSS-first configuration model. All theme customization happens in the main CSS file using `@theme` blocks, not a JavaScript config file.

**How to avoid:**
Define all project tokens in `globals.css` using the `@theme inline` block (already started by the scaffold):

```css
/* globals.css */
@import "tailwindcss";

@theme inline {
  /* Brand colors */
  --color-brand-green: #228B22;
  --color-brand-black: #000000;
  --color-brand-white: #FFFFFF;

  /* Fonts — after next/font variables are applied to <html> */
  --font-body: var(--font-eb-garamond);
  --font-heading: var(--font-editorial);
}
```

Then use as `text-brand-green`, `bg-brand-black`, `font-body`, etc.

Custom utilities use `@utility` (not `@layer utilities`):
```css
@utility chrome-border {
  border: 1px solid;
  border-image: linear-gradient(to right, #888, #fff, #888) 1;
}
```

**Warning signs:**
- `tailwind.config.js` or `tailwind.config.ts` file exists in the project root
- Custom color classes return no output in browser devtools
- Purge/content configuration in a JS file (not needed in v4 — it auto-detects)

**Phase to address:** Phase 1 (Design system setup) — establish token definitions before building any components.

---

### Pitfall 5: Token Refresh Race Condition Causes Auth Loops

**What goes wrong:**
When a user's 60-minute access token expires, multiple concurrent API requests all detect the 401 simultaneously and each fires `POST /v1/auth/refresh`. The FastAPI backend uses token rotation — each refresh call consumes and revokes the current refresh token. The first call succeeds; all subsequent calls receive 401 (token already revoked). The user sees an auth error or infinite redirect despite having a valid session.

**Why it happens:**
No refresh de-duplication logic. Each request independently detects a 401 and triggers a refresh. This is the canonical race condition in token rotation auth systems.

**How to avoid:**
Implement a singleton refresh queue in the API client:

```typescript
// lib/api.ts
let refreshPromise: Promise<string> | null = null

async function refreshAccessToken(): Promise<string> {
  if (refreshPromise) return refreshPromise  // share in-flight refresh

  refreshPromise = (async () => {
    const refresh = localStorage.getItem('refresh_token')
    const res = await fetch(`${API_BASE}/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    })
    if (!res.ok) {
      // refresh failed — force logout
      localStorage.clear()
      window.location.href = '/login'
      throw new Error('Session expired')
    }
    const data = await res.json()
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    return data.access_token
  })()

  try {
    return await refreshPromise
  } finally {
    refreshPromise = null
  }
}
```

**Warning signs:**
- Users get logged out even though they were recently active
- Console shows multiple simultaneous calls to `/v1/auth/refresh`
- 401 errors appearing immediately after a successful login

**Phase to address:** Phase 1 (Auth foundation) — implement this in the API client wrapper before any data-fetching components.

---

### Pitfall 6: `"use client"` Propagation Kills Server Component Benefits

**What goes wrong:**
A developer adds `"use client"` to a layout or high-level wrapper component (e.g., the root `AuthProvider`, the `SiteLayout`, or a nav component with a mobile menu toggle). Because `"use client"` marks a **module boundary**, every component imported by that file becomes a Client Component, including ones that could have been Server Components with direct API data fetching. The entire subtree loses server rendering benefits. This is especially problematic in Next.js App Router where layouts fetching data server-side is the intended pattern.

**Why it happens:**
Developers treat `"use client"` like a component attribute rather than a module boundary. A single interactive element (hamburger menu) at the top of the tree forces the entire layout to be a client bundle.

**How to avoid:**
- Keep `"use client"` as **deep in the tree as possible** — on individual interactive leaf components only
- For layouts with one interactive element (e.g., nav with mobile toggle): split the interactive part into its own `NavMobileToggle.tsx` with `"use client"`, keep the rest of `SiteLayout` as a Server Component
- Use the "children as slot" pattern to pass Server Component children into Client Component wrappers:

```typescript
// SiteLayout.tsx — Server Component, no "use client"
import NavMobileToggle from './NavMobileToggle'  // has "use client"

export default function SiteLayout({ children }) {
  return (
    <div>
      <nav>
        <NavMobileToggle />  {/* only this is client */}
      </nav>
      <main>{children}</main>  {/* stays server-rendered */}
    </div>
  )
}
```

**Warning signs:**
- `"use client"` appears in `layout.tsx`, `SiteLayout.tsx`, or any component file that imports many others
- Bundle size warnings in `next build` output
- Server-fetched data being re-fetched on the client

**Phase to address:** Phase 2 (Layout and navigation) — establish the correct component boundary pattern before building the full layout.

---

### Pitfall 7: Hydration Errors from Auth State Rendered During SSR

**What goes wrong:**
A Client Component reads `localStorage.getItem('access_token')` at render time to determine whether to show a "Login" or "Dashboard" link in the nav, or to show a user's name. On the server (SSR), `localStorage` is undefined and the component renders the unauthenticated state. On the client, it renders the authenticated state. React detects the mismatch and throws a hydration error, breaking the entire page.

**Why it happens:**
Auth state derived from `localStorage` is inherently client-only. Any component that renders differently based on auth state will cause a server/client mismatch if it renders during SSR.

**How to avoid:**
Use `useEffect` to read auth state only after mount, never at render time:

```typescript
'use client'
const [isAuthed, setIsAuthed] = useState(false)

useEffect(() => {
  setIsAuthed(!!localStorage.getItem('access_token'))
}, [])

// Initial render matches server (unauthenticated state)
// useEffect fires client-side and updates to correct state
```

Or use `suppressHydrationWarning` on the specific element if the mismatch is cosmetic and acceptable.

**Warning signs:**
- "Hydration failed because the server rendered HTML didn't match the client" errors in the browser console
- Flickering between unauthenticated and authenticated UI states on page load
- Any call to `localStorage`, `window`, or `document` at the module top level or directly in the component body (outside `useEffect`)

**Phase to address:** Phase 1 (Auth) and Phase 2 (Layout) — establish the auth state reading pattern before building nav.

---

### Pitfall 8: `next/font` with Multiple Fonts — Wrong Integration with Tailwind v4

**What goes wrong:**
Developers load EB Garamond and the editorial heading font with `next/font/google` and apply them via `className` directly on elements rather than exposing them as CSS variables. In Tailwind v4, font utilities (`font-body`, `font-heading`) only work when the CSS variables are registered in `@theme`. If the font is applied only via `.className` on the `<html>` or `<body>` tag, Tailwind utility classes cannot reference them.

**Why it happens:**
The `next/font` API has two modes: `.className` (applies font directly) and `.variable` (exposes as a CSS custom property). Only `.variable` integrates with Tailwind's utility system.

**How to avoid:**
Always use `variable` option for fonts that need Tailwind utility classes:

```typescript
// app/layout.tsx
import { EB_Garamond, Playfair_Display } from 'next/font/google'

const ebGaramond = EB_Garamond({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-body',        // exposes CSS var
})

const playfair = Playfair_Display({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-heading',     // exposes CSS var
})

// Apply both variables to <html>
<html className={`${ebGaramond.variable} ${playfair.variable}`}>
```

```css
/* globals.css */
@theme inline {
  --font-body: var(--font-body);        /* maps Tailwind token to CSS var */
  --font-heading: var(--font-heading);
}
```

Then `font-body` and `font-heading` work as Tailwind utility classes anywhere.

**Warning signs:**
- Fonts render correctly in root layout but `font-body` class on child components has no effect
- Fonts applied via `.className` on `<html>` but `@theme` has no `--font-*` references
- Non-variable (fixed-weight) Google Fonts that should be variable — check Google Fonts for "Variable" badge

**Phase to address:** Phase 1 (Design system) — establish font token setup before building any components.

---

### Pitfall 9: Multipart Form Upload — Content-Type Header Must Not Be Set Manually

**What goes wrong:**
When uploading a PDF to `POST /v1/admin/events` using `FormData`, developers manually set `Content-Type: multipart/form-data` in the fetch request headers. This causes the upload to fail because the `Content-Type` header must include a `boundary` parameter automatically generated by the browser/fetch. Setting it manually omits the boundary and the FastAPI backend cannot parse the multipart body.

**Why it happens:**
Developers follow the mental model of "set Content-Type for every request." For JSON requests this is correct. For multipart form data it breaks the request.

**How to avoid:**
Never set `Content-Type` when sending `FormData`. Let the browser set it automatically:

```typescript
// WRONG — causes 422 Unprocessable Entity from FastAPI
const res = await fetch(`${API_BASE}/v1/admin/events`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'multipart/form-data',  // REMOVE THIS LINE
  },
  body: formData,
})

// CORRECT
const res = await fetch(`${API_BASE}/v1/admin/events`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    // No Content-Type — browser sets multipart/form-data; boundary=... automatically
  },
  body: formData,
})
```

Also: the FastAPI backend validates that the file is a PDF by checking the `%PDF` magic bytes AND enforces a 10MB max. The frontend should validate file type (`file.type === 'application/pdf'`) and size (`file.size <= 10 * 1024 * 1024`) before sending to give early user feedback.

**Warning signs:**
- 422 Unprocessable Entity responses from the events upload endpoint
- FormData constructed correctly but backend cannot parse it
- Any fetch call that sets `Content-Type: multipart/form-data` manually

**Phase to address:** Phase 4 (Admin) — address before building the PDF upload UI.

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `localStorage` for JWT | Simple to implement, no cookie config | XSS risk, no server-side auth in Proxy | MVP only — v2 should migrate to HttpOnly cookies |
| Client-side route protection only | No Proxy complexity | User sees flash of protected content before redirect | Acceptable for MVP since backend enforces auth on every API call |
| No token expiry UI | Faster to build | Users get 401 errors mid-session with no explanation | Never — add a toast/redirect for 401 in the API client |
| Inline auth logic in components | Quicker to ship individual pages | Auth bugs multiply across pages | Never — centralize in `useAuthGuard` hook from day 1 |
| Adding `"use client"` to fix a component error | Error goes away immediately | Destroys server rendering for entire subtree | Only if the component is a leaf with no server-fetchable children |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| FastAPI JWT auth | Reading token from cookie in Proxy (token is in localStorage) | Client-side guard with `useEffect` + `useRouter` redirect |
| FastAPI refresh endpoint | Multiple parallel calls on 401 | Singleton `refreshPromise` in API client |
| FastAPI multipart upload | Setting `Content-Type` header manually | Omit header, let browser set boundary |
| Google Fonts via next/font | Using `.className` only, no CSS variable | Use `variable` option + `@theme` in CSS |
| Tailwind v4 custom tokens | Creating `tailwind.config.js` | Define in `@theme` block in `globals.css` |
| Supabase signed URLs (from backend) | Assuming URLs are permanent | URLs expire in 1 hour — fetch list on each page load, don't cache in state |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Making every component a Client Component | Large JS bundles, slow initial load | Keep data-fetching components as Server Components | Noticeable at any scale — 50KB+ unnecessary JS |
| Fetching auth state on every render | API calls firing in loops | Cache auth state in module-level variable or React context | Immediately, on every page navigation |
| Awaiting API calls sequentially in a Server Component | Slow page load (time = sum of all requests) | Use `Promise.all` for parallel calls | When any two independent API calls are made on the same page |
| Re-fetching events list after each PDF upload | Stale UI or unnecessary network request | Invalidate and re-fetch the list after a successful upload | Always — design the upload flow to refetch after success |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Storing JWT in `localStorage` without XSS hardening | XSS attack steals token | Use `dangerouslySetInnerHTML` never; sanitize any user-provided content rendered as HTML; use React's JSX (auto-escapes); avoid `eval()` |
| Logging JWT tokens to the browser console | Token exposed in devtools logs | Never `console.log` anything from `localStorage.getItem('access_token')` |
| Trusting role from localStorage for UI decisions | Doesn't match backend enforcement | UI-only role check is fine for UX; backend enforces on every API call — trust the 403 response |
| Exposing `NEXT_PUBLIC_API_BASE` with sensitive paths | Anyone can see API base URL | This env var is public by design; do not put secrets in `NEXT_PUBLIC_*` vars |
| Client component imports server-only code (API keys) | Secret leaked to browser bundle | All direct DB/secret access stays in Server Components; use `server-only` package to guard |
| Not handling 401 globally | Token expiry causes silent failures | Add a global 401 interceptor in the API client that clears localStorage and redirects to `/login` |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No loading state during client-side auth check | White flash or unprotected content briefly visible | Show loading spinner in `useAuthGuard` before redirect fires |
| PDF download opens in same tab | User navigates away from dashboard | Open signed URL with `window.open(url, '_blank')` or set `target="_blank"` on the link |
| Interest form shows no feedback on 409 (duplicate email) | User thinks form is broken | Show "An account with this email already exists — contact your admin" message specifically on 409 |
| Rush page shows loading spinner when `{status: "coming_soon"}` | User confused | Show "Rush info coming soon" copy immediately, no spinner |
| Admin role change without confirmation | Accidental role assignments | Require confirmation dialog for role change and deactivation actions |
| Toast messages that auto-dismiss too fast | Users miss success/error messages | Minimum 4 seconds for error toasts; 2 seconds for success toasts |

---

## "Looks Done But Isn't" Checklist

- [ ] **Route protection:** Test all protected routes while logged out — do they redirect to `/login`? Test `/admin` routes as a `member` role — do they show "Access Denied" not the admin UI?
- [ ] **Token refresh:** Let the access token expire (or artificially set a short-lived token) — does the app automatically refresh and continue, or does the user get logged out?
- [ ] **PDF upload:** Upload a non-PDF file — does the frontend validate before sending? Upload a >10MB file — does the frontend warn the user?
- [ ] **Signed URL expiry:** Event PDF links expire in 1 hour — are links fetched fresh or stale from a prior session?
- [ ] **Interest form 409:** Submit the interest form twice with the same email — does the UI show a meaningful duplicate error?
- [ ] **Mobile nav:** Test the navigation on a 375px viewport — is there a horizontal scroll? Do all nav items fit?
- [ ] **Font loading:** Check fonts loaded in the Network tab — are EB Garamond and the editorial font loaded from the same origin (self-hosted by Next.js), not from fonts.gstatic.com?
- [ ] **Tailwind borders:** Check all `border` utilities in browser devtools — are borders visible? (v4 default is `currentColor`, not `gray-200`)
- [ ] **`proxy.ts` not `middleware.ts`:** Confirm the auth-related file is named `proxy.ts` with `export function proxy()`, not `middleware.ts`

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Wrong `middleware.ts` (should be `proxy.ts`) | LOW | Rename file, rename export function, verify protection works |
| v3 utility class names in v4 | MEDIUM | Global find/replace for each renamed class; create a test page exercising all design tokens |
| Custom tokens in `tailwind.config.js` | LOW | Delete file, move all `theme.extend` values to `@theme` block in `globals.css` |
| Token refresh race condition | MEDIUM | Add singleton refresh queue to API client; clear old parallel-refresh logic |
| `"use client"` on layout component | MEDIUM | Extract interactive leaf into separate file with `"use client"`, remove directive from parent |
| Hydration error from localStorage in render | LOW | Move `localStorage` read into `useEffect`, initialize state with null/false |
| Manual `Content-Type` on multipart upload | LOW | Remove the header line from the fetch call |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| `proxy.ts` vs `middleware.ts` rename | Phase 1: Auth setup | Visit protected route while logged out; confirm redirect |
| `localStorage` inaccessible in proxy | Phase 1: Auth setup | Auth guard uses `useEffect`, not proxy |
| Tailwind v4 class renames | Phase 1: Design system | Visual regression check on all component states |
| No `tailwind.config.js` in v4 | Phase 1: Design system | Brand colors and fonts available as utility classes |
| Token refresh race condition | Phase 1: Auth/API client | Simulate concurrent 401s; confirm single refresh fires |
| `"use client"` propagation | Phase 2: Layout/Nav | Bundle analyzer — check client bundle size |
| Hydration error from auth state | Phase 1 + Phase 2 | No hydration warnings in browser console on any page |
| `next/font` + Tailwind v4 integration | Phase 1: Design system | `font-body` and `font-heading` classes work on any element |
| Multipart upload Content-Type | Phase 4: Admin | PDF upload succeeds; non-PDF and oversized files show client-side error |

---

## Sources

- Next.js 16.1.6 official docs — Proxy (formerly Middleware): https://nextjs.org/docs/app/api-reference/file-conventions/proxy (HIGH confidence — official docs, version-confirmed)
- Next.js 16.1.6 official docs — Server and Client Components: https://nextjs.org/docs/app/getting-started/server-and-client-components (HIGH confidence — official docs, version-confirmed)
- Next.js 16.1.6 official docs — Font Module: https://nextjs.org/docs/app/api-reference/components/font (HIGH confidence — official docs, version-confirmed)
- Next.js 16.1.6 official docs — Fetching Data: https://nextjs.org/docs/app/getting-started/fetching-data (HIGH confidence — official docs, version-confirmed)
- Tailwind CSS v4 Upgrade Guide: https://tailwindcss.com/docs/upgrade-guide (HIGH confidence — official docs)
- React 19 release blog — TypeScript breaking changes: https://react.dev/blog/2024/12/05/react-19 (HIGH confidence — official React blog)
- Project codebase analysis: `.planning/codebase/CONCERNS.md`, `ARCHITECTURE.md` (HIGH confidence — direct source inspection)
- FastAPI multipart behavior: verified from backend source `app/api/v1/admin/events.py` and `python-multipart` package behavior (HIGH confidence)

---

*Pitfalls research for: PSI CHI OMEGA Website Frontend (Next.js 16 App Router + Tailwind v4 + localStorage JWT)*
*Researched: 2026-03-05*
