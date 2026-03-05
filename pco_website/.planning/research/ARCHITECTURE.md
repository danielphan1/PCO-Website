# Architecture Research

**Domain:** Next.js 16 App Router frontend consuming external FastAPI REST API with JWT auth
**Researched:** 2026-03-05
**Confidence:** HIGH (official Next.js 16.1.6 docs verified via WebFetch)

---

## Standard Architecture

### System Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                         Browser (Client)                               │
│                                                                        │
│  localStorage: { access_token, refresh_token, user }                  │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Next.js App Router                            │  │
│  │                                                                  │  │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────┐   │  │
│  │  │  (public)  │  │   (auth)    │  │ (member) │  │ (admin)  │   │  │
│  │  │  /         │  │  /login     │  │/dashboard│  │  /admin  │   │  │
│  │  │  /join     │  │             │  │          │  │  /admin/ │   │  │
│  │  │  /rush     │  │             │  │          │  │  events  │   │  │
│  │  │  /history  │  │             │  │          │  │  members │   │  │
│  │  │  /philant. │  │             │  │          │  │  rush    │   │  │
│  │  │  /contact  │  │             │  │          │  │  content │   │  │
│  │  └─────┬──────┘  └──────┬──────┘  └────┬─────┘  └────┬─────┘   │  │
│  │        │                │              │              │          │  │
│  │  ┌─────▼────────────────▼──────────────▼──────────────▼──────┐  │  │
│  │  │                    Shared Layer                            │  │  │
│  │  │  lib/api.ts (fetch wrapper)  │  lib/auth.ts (token mgmt)  │  │  │
│  │  │  contexts/AuthContext.tsx    │  hooks/useAuth.ts           │  │  │
│  │  └───────────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                         │
│                   proxy.ts (route guard)                               │
│                   (reads auth-hint cookie for redirects)               │
└──────────────────────────────┬─────────────────────────────────────────┘
                               │ HTTP/HTTPS
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (port 8000)                        │
│                                                                       │
│  POST /v1/auth/login    GET /v1/users/me    GET /v1/events            │
│  POST /v1/auth/refresh  GET /v1/content/*  GET /v1/admin/users        │
│  POST /v1/interest      GET /v1/rush       POST /v1/admin/events      │
│  PUT  /v1/rush          PUT /v1/content/*  PATCH /v1/admin/users/{id} │
└──────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Communicates With |
|-----------|----------------|-------------------|
| `proxy.ts` | Route-level redirects based on auth-hint cookie; first line of defense only | Next.js routing system |
| `lib/api.ts` | Wraps all fetch calls to FastAPI: base URL, `Authorization` header injection, 401 auto-refresh, error normalization | FastAPI, `lib/auth.ts` |
| `lib/auth.ts` | Read/write tokens from localStorage, token expiry detection, logout | `lib/api.ts`, `AuthContext` |
| `AuthContext` (`'use client'`) | Provides `user`, `isLoading`, `login()`, `logout()` to all Client Components | `lib/auth.ts`, `lib/api.ts` |
| `useAuth` hook | Thin wrapper around `AuthContext`; used in client pages/components | `AuthContext` |
| `(public)` route group | Public-facing pages; no auth required; Server Components fetch content at request time | `lib/api.ts` (server-side fetch) |
| `(auth)` route group | Login page only; redirects to `/dashboard` if already authed | `AuthContext`, `lib/api.ts` |
| `(member)` route group | Protected dashboard and events; requires `AuthContext` user present | `AuthContext`, `lib/api.ts` |
| `(admin)` route group | Admin tools; requires admin role; secondary role check in each page | `AuthContext`, `lib/api.ts` |
| `components/ui/` | Design system: `ChromeCard`, `ChromeButton`, `SectionTitle`, `Divider`, `Toast` | None (purely presentational) |
| `components/layout/` | `SiteLayout`, `Header`, `Footer`, `Nav`; wraps all route groups | `AuthContext` (for nav state) |

---

## Recommended Project Structure

```
pco_website/
├── app/
│   ├── (public)/                  # No auth required — public marketing pages
│   │   ├── layout.tsx             # SiteLayout with public nav (no member links)
│   │   ├── page.tsx               # Home / landing page
│   │   ├── join/
│   │   │   └── page.tsx           # Interest form
│   │   ├── rush/
│   │   │   └── page.tsx           # Rush info or coming-soon fallback
│   │   ├── history/
│   │   │   └── page.tsx           # Org history from API
│   │   ├── philanthropy/
│   │   │   └── page.tsx           # Philanthropy content from API
│   │   └── contact/
│   │       └── page.tsx           # Contacts + leadership
│   │
│   ├── (auth)/                    # Login only — separate layout, no nav chrome
│   │   ├── layout.tsx             # Minimal layout (centered card, no nav)
│   │   └── login/
│   │       └── page.tsx           # Login form (Client Component)
│   │
│   ├── (member)/                  # Protected — members and admins
│   │   ├── layout.tsx             # SiteLayout with member nav + auth guard
│   │   └── dashboard/
│   │       └── page.tsx           # Profile snippet + events list + T6 contacts
│   │
│   ├── (admin)/                   # Protected — admin role only
│   │   ├── layout.tsx             # SiteLayout with admin nav + role guard
│   │   ├── admin/
│   │   │   ├── page.tsx           # Admin hub
│   │   │   ├── events/
│   │   │   │   └── page.tsx       # PDF upload + list + delete
│   │   │   ├── members/
│   │   │   │   └── page.tsx       # Member management
│   │   │   ├── rush/
│   │   │   │   └── page.tsx       # Rush content editor
│   │   │   └── content/
│   │   │       └── page.tsx       # Site content editor
│   │
│   ├── layout.tsx                 # Root layout: fonts, AuthProvider, globals
│   └── globals.css                # Tailwind base styles
│
├── components/
│   ├── ui/                        # Design system (Server-safe unless interactive)
│   │   ├── ChromeCard.tsx
│   │   ├── ChromeButton.tsx       # 'use client' for hover sheen animation
│   │   ├── SectionTitle.tsx
│   │   ├── Divider.tsx
│   │   └── Toast.tsx              # 'use client' — needs state
│   ├── layout/
│   │   ├── SiteLayout.tsx         # Wraps Header + Footer + children
│   │   ├── Header.tsx             # 'use client' — reads auth state for nav
│   │   └── Footer.tsx             # Server Component — static
│   └── forms/
│       ├── LoginForm.tsx          # 'use client'
│       ├── InterestForm.tsx       # 'use client'
│       └── RichTextEditor.tsx     # 'use client' — for admin content editing
│
├── lib/
│   ├── api.ts                     # Fetch wrapper: base URL, auth header, refresh
│   ├── auth.ts                    # Token storage helpers (localStorage)
│   └── utils.ts                   # Date formatting, role checks, etc.
│
├── contexts/
│   └── AuthContext.tsx            # 'use client' — global auth state
│
├── hooks/
│   └── useAuth.ts                 # Thin wrapper: useContext(AuthContext)
│
├── types/
│   └── api.ts                     # TypeScript types mirroring FastAPI Pydantic schemas
│
├── proxy.ts                       # Route guard (renamed from middleware.ts in Next.js 16)
├── next.config.ts
├── tailwind.config.ts
└── .env.example                   # NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### Structure Rationale

- **Route groups `(public)`, `(auth)`, `(member)`, `(admin)`:** Each group gets its own `layout.tsx`, enabling completely different chrome per audience. Groups do NOT appear in URLs — `/dashboard` not `/(member)/dashboard`. The `(auth)` group uses a minimal centered layout; `(public)` uses the full site layout without member nav items.

- **`lib/api.ts` as single API gateway:** All FastAPI calls go through one file. This is where the `Authorization: Bearer` header is injected, 401 responses trigger refresh, and errors are normalized. No component reaches for `fetch()` directly.

- **`lib/auth.ts` separated from `AuthContext`:** Auth token logic (get, set, clear from localStorage) is plain functions importable anywhere. `AuthContext` is the React layer on top. This separation lets `lib/api.ts` call token helpers without needing React context.

- **`components/ui/` is design system only:** No business logic, no API calls. Pure presentational. Aim for Server Components where possible; add `'use client'` only for animation state (hover sheen, toast timers).

- **`types/api.ts` mirrors Pydantic schemas:** TypeScript interfaces match the FastAPI response shapes. Single source of truth for what the API returns. Copy from backend schemas when they change.

---

## Architectural Patterns

### Pattern 1: API Client with Auto-Refresh

**What:** A central `lib/api.ts` wraps `fetch`, injects the Bearer token automatically, and handles 401 responses by attempting a refresh before retrying the original request.

**When to use:** Every call to the FastAPI backend goes through this wrapper. Never call `fetch()` directly against the API in components.

**Trade-offs:** Single choke point catches all auth errors. Slight complexity in the interceptor logic. Worth it for DRY auth handling across 15+ API endpoints.

```typescript
// lib/auth.ts — token helpers
export const TOKEN_KEY = 'pco_access_token'
export const REFRESH_KEY = 'pco_refresh_token'

export function getAccessToken(): string | null {
  return typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null
}
export function setTokens(access: string, refresh: string) {
  localStorage.setItem(TOKEN_KEY, access)
  localStorage.setItem(REFRESH_KEY, refresh)
}
export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(REFRESH_KEY)
}
```

```typescript
// lib/api.ts — fetch wrapper with auto-refresh
const BASE = process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8000'

let isRefreshing = false
let refreshQueue: Array<() => void> = []

async function refreshAccessToken(): Promise<boolean> {
  const refresh = localStorage.getItem('pco_refresh_token')
  if (!refresh) return false
  try {
    const res = await fetch(`${BASE}/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    })
    if (!res.ok) { clearTokens(); return false }
    const { access_token, refresh_token } = await res.json()
    setTokens(access_token, refresh_token)
    return true
  } catch { clearTokens(); return false }
}

export async function apiClient<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> ?? {}),
  }

  let res = await fetch(`${BASE}${path}`, { ...options, headers })

  if (res.status === 401) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      const newToken = getAccessToken()
      headers.Authorization = `Bearer ${newToken}`
      res = await fetch(`${BASE}${path}`, { ...options, headers })
    } else {
      clearTokens()
      window.location.href = '/login'
      throw new Error('Session expired')
    }
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new Error(err.detail ?? `HTTP ${res.status}`)
  }

  return res.json() as Promise<T>
}
```

### Pattern 2: AuthContext for Client-Side State

**What:** A single `'use client'` React Context at the root layout provides `user`, `isLoading`, `login()`, `logout()` to all Client Components. Server Components do not use this context (they have no access to localStorage by design).

**When to use:** Any Client Component that needs to know who is logged in, what their role is, or needs to trigger login/logout.

**Trade-offs:** Since auth state lives in `localStorage` and React context (not cookies by default), Server Components cannot render user-specific content on the server. All protected pages that need user data must be Client Components or receive data via props from a parent Client Component. This is the accepted trade-off for localStorage-based JWT MVP.

```typescript
// contexts/AuthContext.tsx
'use client'
import { createContext, useContext, useEffect, useState } from 'react'
import { getAccessToken, setTokens, clearTokens } from '@/lib/auth'
import { apiClient } from '@/lib/api'

type User = { id: string; name: string; email: string; role: string }
type AuthCtx = {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = getAccessToken()
    if (!token) { setIsLoading(false); return }
    apiClient<User>('/v1/users/me')
      .then(setUser)
      .catch(() => clearTokens())
      .finally(() => setIsLoading(false))
  }, [])

  async function login(email: string, password: string) {
    const { access_token, refresh_token } = await apiClient<{
      access_token: string; refresh_token: string
    }>('/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    setTokens(access_token, refresh_token)
    const me = await apiClient<User>('/v1/users/me')
    setUser(me)
    // Set auth-hint cookie so proxy.ts can redirect properly
    document.cookie = `auth-hint=1; path=/; max-age=${60 * 60 * 24 * 30}`
  }

  function logout() {
    clearTokens()
    setUser(null)
    document.cookie = 'auth-hint=; path=/; max-age=0'
    window.location.href = '/login'
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
```

### Pattern 3: Proxy (formerly Middleware) for Route Guards

**What:** `proxy.ts` (the Next.js 16 rename of `middleware.ts`) runs before every route render. Because it cannot access `localStorage` (server context), it reads a lightweight `auth-hint` cookie set during login. This provides optimistic redirects only — not a security boundary.

**When to use:** Redirect unauthenticated users away from `/dashboard` and `/admin/*`. Redirect already-authenticated users away from `/login`. The real security is enforced by the FastAPI backend (Bearer token validation on every request).

**Trade-offs:** `auth-hint` cookie is not cryptographically verified in proxy — it is just a presence check. Actual data is protected by the backend's 401/403 responses. A user with an expired token but a stale cookie will be let through by proxy, but will get 401 from FastAPI and be redirected by the API client.

```typescript
// proxy.ts (Next.js 16 — renamed from middleware.ts)
import { NextRequest, NextResponse } from 'next/server'

const MEMBER_ROUTES = ['/dashboard']
const ADMIN_ROUTES = ['/admin']
const AUTH_ROUTES = ['/login']

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl
  const hasAuthHint = request.cookies.has('auth-hint')

  const isMemberRoute = MEMBER_ROUTES.some(r => pathname.startsWith(r))
  const isAdminRoute = ADMIN_ROUTES.some(r => pathname.startsWith(r))
  const isAuthRoute = AUTH_ROUTES.some(r => pathname.startsWith(r))

  // Not authed → redirect to login
  if ((isMemberRoute || isAdminRoute) && !hasAuthHint) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  // Already authed → redirect away from login
  if (isAuthRoute && hasAuthHint) {
    return NextResponse.redirect(new URL('/dashboard', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\.png$).*)'],
}
```

**Note:** Next.js 16 renamed `middleware.ts` to `proxy.ts`. The `middleware` export function becomes `proxy`. A codemod is available: `npx @next/codemod@canary middleware-to-proxy .`

### Pattern 4: Server vs Client Component Decision

**What:** In this project, auth state lives in `localStorage` (inaccessible to Server Components). Public content pages can still use Server Components to fetch from the FastAPI backend using a plain server-side `fetch()`. Protected pages must use Client Components or receive data via `AuthProvider`.

**Decision matrix:**

| Page / Component | Render Mode | Reason |
|---|---|---|
| `/` Home page | Server Component | Content is public, no auth needed, SEO benefits |
| `/rush`, `/history`, `/philanthropy`, `/contact` | Server Component | Public API data, SEO benefits, no auth |
| `/join` (Interest form) | Server Component with Client form | Page shell can be server; form interaction is client |
| `/login` | Client Component | Needs `useAuth().login()`, state for form errors |
| `/dashboard` | Client Component | Reads user from `AuthContext`; shows personal data |
| `/admin/*` pages | Client Component | Role check via `useAuth().user.role`; all mutations |
| `Header.tsx` | Client Component | Reads auth state to show/hide nav items |
| `Footer.tsx` | Server Component | Static links, no interactivity |
| `ChromeCard.tsx` | Server Component | Purely presentational, no state |
| `ChromeButton.tsx` | Client Component | Hover sheen animation requires state |
| `Toast.tsx` | Client Component | Requires `useState` for show/hide |

**Server Component fetch pattern for public pages (HIGH confidence — verified):**

```typescript
// app/(public)/history/page.tsx — Server Component
export default async function HistoryPage() {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_API_BASE}/v1/content/history`,
    { next: { revalidate: 3600 } } // Cache 1 hour
  )
  if (!res.ok) return <div>Content unavailable</div>
  const data = await res.json()
  return <HistoryContent data={data} />
}
```

### Pattern 5: Role-Based Access Control in Client Pages

**What:** After proxy allows a user into `/admin/*` (based on auth-hint cookie), the page itself checks `user.role === 'admin'` from `AuthContext`. Non-admin members who somehow navigate to `/admin` see an "Access Denied" message and are redirected to `/dashboard`. Actual mutations are blocked by FastAPI's `require_admin` dependency returning 403.

**When to use:** Every `(admin)` route group page. Also the admin layout can handle this once.

```typescript
// app/(admin)/layout.tsx — Client Component
'use client'
import { useAuth } from '@/hooks/useAuth'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !user) router.replace('/login')
    if (!isLoading && user && user.role !== 'admin') router.replace('/dashboard')
  }, [user, isLoading, router])

  if (isLoading) return <LoadingSpinner />
  if (!user || user.role !== 'admin') return null

  return <SiteLayout adminNav>{children}</SiteLayout>
}
```

---

## Data Flow

### Login Flow

```
LoginForm (Client)
    │ user submits email + password
    ▼
useAuth().login(email, password)
    │
    ▼
apiClient POST /v1/auth/login
    │ returns { access_token, refresh_token }
    ▼
setTokens() → localStorage
    │
apiClient GET /v1/users/me → setUser(user)
    │
document.cookie = 'auth-hint=1'  ← enables proxy.ts redirects
    │
router.push('/dashboard')
```

### Token Refresh Flow

```
apiClient() — any protected API call
    │ 401 response from FastAPI
    ▼
refreshAccessToken()
    │ POST /v1/auth/refresh with refresh_token from localStorage
    │ returns new { access_token, refresh_token }
    ▼
setTokens(new_access, new_refresh)  ← rotation complete
    │
Retry original request with new access_token
    │ (if refresh also fails → clearTokens() + redirect /login)
```

### Public Content Request Flow

```
Browser navigates to /history
    │
Next.js Server Component renders HistoryPage
    │
server-side fetch(`${NEXT_PUBLIC_API_BASE}/v1/content/history`)
    │ no auth header needed — public endpoint
    ▼
FastAPI returns JSON content
    │
Server Component renders HTML with content
    │ (cached up to 1hr via `next: { revalidate: 3600 }`)
    ▼
HTML streamed to browser — fast FCP, SEO-friendly
```

### Protected Data Request Flow (Dashboard)

```
Browser navigates to /dashboard
    │
proxy.ts checks auth-hint cookie → present → NextResponse.next()
    │
DashboardPage (Client Component) renders
    │
useAuth() → checks AuthContext → user already loaded from /v1/users/me on mount
    │
Component calls apiClient GET /v1/events
    │ injects Authorization: Bearer <access_token> from localStorage
    ▼
FastAPI validates JWT → returns events list
    │
Component renders events with PDF signed URLs
```

### Admin Mutation Flow

```
AdminMembersPage (Client Component)
    │ admin clicks "Deactivate Member"
    ▼
apiClient PATCH /v1/admin/users/{id}/deactivate
    │ Authorization: Bearer <admin_access_token>
    ▼
FastAPI require_admin dependency validates role
    │ success → mutation + audit log
    ▼
Response → UI updates, Toast shown
```

### State Management

```
AuthContext (global, 'use client')
    │ provides: user, isLoading, login(), logout()
    │
    ├── Header.tsx (reads user for nav links)
    ├── (member)/layout.tsx (guards route)
    ├── (admin)/layout.tsx (guards route + role)
    └── All form components (reads user info)

No Zustand / Redux needed. Scope is:
  - Auth state: AuthContext (global)
  - Form state: local useState per form
  - Server data: fetched per-component, no global cache
```

**State management verdict:** React Context is sufficient. No global state library (Zustand, Redux) needed for MVP. The state surface is small: one user object, boolean flags, two token strings in localStorage. Prop drilling depth never exceeds 2-3 levels within a page.

---

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| 0-50 users (current) | localStorage JWT is fine; Client Components for all protected pages; no caching layer needed |
| 50-500 users | Add `React.cache()` for repeated server-side fetches; consider SWR or TanStack Query for client-side data freshness |
| 500-5K users | Switch auth storage from localStorage to HttpOnly cookies (eliminates XSS risk); upgrade proxy.ts to verify JWT directly; enable Next.js ISR for public content pages |
| 5K+ users | CDN for static assets; consider edge deployment for proxy.ts; backend horizontal scaling (separate concern from frontend) |

### Scaling Priorities

1. **First bottleneck:** Public content pages making redundant API calls on every request. Fix: `next: { revalidate: N }` on server-side fetches for `/history`, `/philanthropy`, `/contact`, `/rush`.

2. **Second bottleneck:** LocalStorage JWT is synchronous and blocks hydration check. Fix: If latency becomes noticeable, migrate to HttpOnly cookie auth (breaking change to auth flow, defer to v2).

---

## Anti-Patterns

### Anti-Pattern 1: Auth Checks in Layout Components

**What people do:** Put `useAuth()` guards in `layout.tsx` and assume they run on every child route navigation.

**Why it's wrong:** Next.js App Router layouts use Partial Rendering — the layout does NOT re-render on client-side navigation between sibling routes. A user could navigate between `/admin/members` and `/admin/events` without the layout re-checking auth.

**Do this instead:** Put the guard in the layout for initial load, AND add the check in each individual page for mutations. The FastAPI backend is the authoritative guard — every API call validates the token.

### Anti-Pattern 2: Using Server Components for Protected Pages

**What people do:** Try to make `/dashboard` a Server Component to fetch user-specific data server-side.

**Why it's wrong:** `localStorage` does not exist on the server. Server Components cannot access the JWT access token. The Next.js docs confirm: localStorage is a browser-only API, requiring Client Components.

**Do this instead:** Make protected pages (`/dashboard`, `/admin/*`) Client Components that read from `AuthContext`, then call `apiClient()` from the client. Public pages (`/history`, `/rush`, etc.) remain Server Components with plain server-side fetch.

### Anti-Pattern 3: Direct fetch() in Components

**What people do:** Call `fetch(process.env.NEXT_PUBLIC_API_BASE + '/v1/events', { headers: { Authorization: ... } })` directly inside a component.

**Why it's wrong:** Auth header injection, error normalization, and 401 refresh logic get duplicated across every component. When the token refresh logic needs to change, every component needs updating.

**Do this instead:** All API calls go through `apiClient()` from `lib/api.ts`. Components never touch `fetch()` directly.

### Anti-Pattern 4: Relying on proxy.ts as the Security Boundary

**What people do:** Treat `proxy.ts` (formerly `middleware.ts`) as the definitive security guard and skip auth checks in API calls.

**Why it's wrong:** `proxy.ts` only reads the `auth-hint` cookie (a lightweight presence hint, not cryptographically verified). A user with an expired or forged cookie passes through. The Next.js docs explicitly state: proxy should only be used for optimistic checks; real security must be close to the data source.

**Do this instead:** Use proxy.ts for UX redirects (fast, before render). Use FastAPI's `get_current_user` and `require_admin` dependencies as the real enforcement. Every API call that mutates data is protected by the backend.

### Anti-Pattern 5: Admin Role Check Only in proxy.ts

**What people do:** Check `user.role === 'admin'` only in proxy.ts and not in the admin page/layout components.

**Why it's wrong:** proxy.ts reads the `auth-hint` cookie which has no role information. A member navigating directly to `/admin` would pass the proxy (cookie present) but should see "Access Denied".

**Do this instead:** Check the role in `(admin)/layout.tsx` using `useAuth().user.role`. Redirect non-admin members to `/dashboard`. FastAPI enforces it on every admin API call regardless.

---

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| FastAPI backend | `apiClient()` wrapper over `fetch()` | All calls via `lib/api.ts`; base URL from `NEXT_PUBLIC_API_BASE` |
| Supabase Storage | Indirect — backend returns signed URLs; frontend just renders `<a href={signedUrl}>` | Frontend never calls Supabase directly; signed URLs expire in 1 hour |
| Google Fonts | `next/font/google` in `app/layout.tsx` | EB Garamond (body) + one editorial heading font; loaded at build time |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Server Components ↔ FastAPI | `fetch()` directly, no auth header | Public endpoints only; SSR fetch with `next: { revalidate }` |
| Client Components ↔ FastAPI | `apiClient()` from `lib/api.ts` | Auto-injects Bearer token; handles 401 refresh |
| `proxy.ts` ↔ AuthContext | `auth-hint` cookie (written by login, cleared by logout) | Cookie is hint only, not JWT; proxy cannot read localStorage |
| `AuthContext` ↔ `lib/api.ts` | `lib/auth.ts` functions (no React imports) | `lib/api.ts` calls `getAccessToken()`, `setTokens()` — pure functions |
| `(admin)/layout.tsx` ↔ `useAuth` | React Context | Layout checks `user.role === 'admin'`; redirects members |

---

## Build Order Implications

Components depend on each other in this sequence. Build in this order to avoid blocking:

1. **`types/api.ts`** — TypeScript interfaces for all API responses. Zero dependencies. Everything else imports from here.

2. **`lib/auth.ts`** — Token helpers (get/set/clear from localStorage). No React dependency. `lib/api.ts` and `AuthContext` both need this.

3. **`lib/api.ts`** — Fetch wrapper with auth injection. Depends on `lib/auth.ts` and `types/api.ts`. All pages depend on this.

4. **`contexts/AuthContext.tsx`** — Auth state. Depends on `lib/api.ts`, `lib/auth.ts`. Protected layouts and forms depend on this.

5. **`components/ui/`** — Design system components. No API dependency. Needed by all pages.

6. **`components/layout/SiteLayout.tsx`** — Depends on `AuthContext` (for nav state) and `components/ui/`. All route group layouts depend on this.

7. **`proxy.ts`** — Route guard. No external dependencies — reads cookies only. Set up once, rarely changes.

8. **`(public)` pages** — Server Components. Depend on `lib/api.ts` (server-side fetch), `components/ui/`, `components/layout/`. Can be built independently after steps 1-6.

9. **`(auth)/login`** — Depends on `AuthContext`, `components/ui/`, `lib/api.ts`. Needed before member/admin pages can be tested.

10. **`(member)/dashboard`** — Depends on `AuthContext`, `lib/api.ts`, `components/ui/`. Core member feature.

11. **`(admin)/*` pages** — Depend on `AuthContext`, `lib/api.ts`, `components/forms/`. Build after member dashboard is stable.

---

## Sources

- Next.js 16.1.6 Official Docs — Route Groups: https://nextjs.org/docs/app/api-reference/file-conventions/route-groups (verified 2026-02-27, version 16.1.6)
- Next.js 16.1.6 Official Docs — Authentication Guide: https://nextjs.org/docs/app/guides/authentication (verified 2026-02-27, version 16.1.6)
- Next.js 16.1.6 Official Docs — Server and Client Components: https://nextjs.org/docs/app/getting-started/server-and-client-components (verified 2026-02-27, version 16.1.6)
- Next.js 16.1.6 Official Docs — Proxy (formerly Middleware): https://nextjs.org/docs/app/api-reference/file-conventions/proxy (verified 2026-02-27, version 16.1.6)
- PCO Backend Architecture: `.planning/codebase/ARCHITECTURE.md`
- PCO Project Context: `.planning/PROJECT.md`

---

**Critical version note:** Next.js 16 renamed `middleware.ts` → `proxy.ts` and the export function from `middleware` → `proxy`. This is a breaking change from Next.js 15 and earlier. The project scaffold may still have `middleware.ts` — migrate with `npx @next/codemod@canary middleware-to-proxy .` or create `proxy.ts` directly.

---
*Architecture research for: PSI CHI OMEGA Website Frontend*
*Researched: 2026-03-05*
