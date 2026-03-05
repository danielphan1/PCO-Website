# Stack Research

**Domain:** Next.js 16 App Router frontend connecting to FastAPI REST API
**Researched:** 2026-03-05
**Confidence:** HIGH (well-established ecosystem, decisions cross-verified against Next.js 16 / React 19 constraints)

---

## Recommended Stack

### Core Technologies (Already Installed — Confirmed in package.json)

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Next.js | 16.1.6 | App Router, SSR, routing | Already installed; App Router is the current standard. Do not migrate to Pages Router. |
| React | 19.2.3 | UI rendering | Already installed; React 19 introduces `use()`, async components, and `useTransition` improvements |
| TypeScript | ^5 | Type safety | Already installed; strict mode configured in tsconfig.json |
| Tailwind CSS | ^4 | Utility-first CSS | Already installed; v4 uses `@import "tailwindcss"` syntax and CSS-native theming via `@theme` |

### Form Handling

**Recommendation: react-hook-form v7 + zod v3**

| Library | Version | Purpose | Why |
|---------|---------|---------|-----|
| react-hook-form | ^7.54 | Uncontrolled form state, validation orchestration | Minimal re-renders vs controlled forms; widely adopted; works correctly with React 19 concurrent mode; `useForm` hook is fully client-side compatible |
| zod | ^3.24 | Schema-based validation | Best-in-class TypeScript inference; `z.infer<>` makes form field types come from schema, not duplicated manually; integrates with react-hook-form via `@hookform/resolvers` |
| @hookform/resolvers | ^3.10 | Bridge between RHF and zod | Drop-in: `resolver: zodResolver(schema)` — no boilerplate |

**Why not native HTML5 validation?** Insufficient for server error injection (409 duplicate email on /join). RHF lets you call `setError("email", { message: "..." })` from API response, keeping error state co-located with form.

**Why not Formik?** Controlled inputs cause re-renders on every keystroke; Formik 2.x has unresolved React 19 compatibility warnings. RHF is the current ecosystem standard.

**Pattern for this project:**
```typescript
// Client Component only — forms require interactivity
"use client"
const schema = z.object({ email: z.string().email(), name: z.string().min(1) })
const { register, handleSubmit, setError, formState } = useForm({ resolver: zodResolver(schema) })

// On 409 from /v1/interest:
setError("email", { message: "This email is already registered." })
```

### Authentication Token Storage

**Recommendation: localStorage with client-side auth context (as specified in PROJECT.md)**

| Approach | Verdict | Rationale |
|----------|---------|-----------|
| localStorage (MVP) | USE THIS | Simplest; no cookie configuration; works immediately; PROJECT.md explicitly specifies this |
| HttpOnly cookies | Do NOT use for MVP | Requires Next.js route handler to set-cookie on login response, adds complexity; backend must return tokens in cookie header or frontend must proxy; out of scope for MVP |
| sessionStorage | Avoid | Tokens lost on tab close; worse UX than localStorage for member use |

**Critical constraint: Next.js middleware.ts cannot access localStorage.** Middleware runs in the Edge Runtime (a V8 isolate without DOM APIs). `localStorage` does not exist in that environment. This means:

- Middleware-based route protection is NOT possible with localStorage JWT storage
- Route protection must be implemented client-side via a React auth context + component-level guard
- Use `"use client"` components that check `localStorage` in `useEffect` and redirect via `router.push`

**Auth context pattern:**
```typescript
// lib/auth-context.tsx — client component context
"use client"
export function AuthProvider({ children }) {
  const [token, setToken] = useState<string | null>(null)
  useEffect(() => { setToken(localStorage.getItem("access_token")) }, [])
  // expose token, login(), logout()
}

// components/AuthGuard.tsx — wraps protected pages
"use client"
export function AuthGuard({ children, requireAdmin }) {
  const { token, user } = useAuth()
  const router = useRouter()
  useEffect(() => {
    if (!token) router.push("/login")
    if (requireAdmin && user?.role !== "admin") router.push("/dashboard")
  }, [token, user])
  if (!token) return null // or loading spinner
  return children
}
```

**Token refresh:** Call `POST /v1/auth/refresh` with the opaque refresh token when the access token is expired (check on 401 response). Store both `access_token` and `refresh_token` in localStorage.

### Data Fetching

**Recommendation: Server Components for public data; custom fetch wrapper for authenticated client-side data. No SWR or React Query for MVP.**

| Pattern | When to Use | Why |
|---------|-------------|-----|
| `async` Server Component + native `fetch` | Public pages: /history, /philanthropy, /contact, /rush | No auth token needed; server-side fetch improves initial load time and SEO; Tailwind renders correctly |
| Client component + `fetch` in `useEffect` | Authenticated pages: /dashboard, /admin/* | JWT is in localStorage (inaccessible on server); must be client-side; `useEffect` fetch is simple and appropriate for this app scale |
| SWR / React Query | NOT for MVP | Adds dependency weight; this app has low data mutation complexity; the member-facing data (events list) does not need real-time polling; introduce in v2 if needed |

**Custom API client (required pattern):**
```typescript
// lib/api.ts
const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000"

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  })
  if (res.status === 401) {
    // attempt token refresh, then retry once
  }
  return res
}
```

**Server Component fetch (public data):**
```typescript
// app/history/page.tsx — no "use client"
export default async function HistoryPage() {
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/v1/content/history`, {
    next: { revalidate: 3600 } // ISR: revalidate every hour
  })
  const data = await res.json()
  return <HistoryContent data={data} />
}
```

### File Upload (PDF to FastAPI)

**Recommendation: Native `fetch` with `FormData` — no library needed**

The backend accepts `POST /v1/admin/events` as `multipart/form-data` with a PDF file (10MB max, PDF only). The native Fetch API handles this correctly. Do NOT set `Content-Type` header manually when using FormData — the browser sets it with the correct boundary automatically.

```typescript
// Pattern for PDF upload
async function uploadEvent(file: File) {
  const formData = new FormData()
  formData.append("file", file)
  const token = localStorage.getItem("access_token")
  const res = await fetch(`${BASE}/v1/admin/events`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    // DO NOT set Content-Type — FormData sets it with boundary
    body: formData,
  })
  return res
}
```

**Client-side validation before upload:**
```typescript
// Validate before hitting API (saves bandwidth, gives instant feedback)
if (file.type !== "application/pdf") setError("File must be a PDF")
if (file.size > 10 * 1024 * 1024) setError("File must be under 10MB")
```

**No library needed.** Libraries like `react-dropzone` add drag-and-drop UX but are optional for MVP. A plain `<input type="file" accept=".pdf">` is sufficient and maintainable.

### Toast / Notification

**Recommendation: sonner v1**

| Library | Version | Verdict | Reason |
|---------|---------|---------|--------|
| sonner | ^1.7 | USE THIS | Lightweight (~4KB); opinionated beautiful defaults; Tailwind v4 compatible; built by shadcn (same author as shadcn/ui); works with React 19; no global provider side effects; simple API: `toast.success("Saved!")` |
| react-hot-toast | ^2 | Acceptable alternative | Solid library but lacks the visual polish and Tailwind theming flexibility of sonner |
| react-toastify | ^10 | Avoid | Heavier; requires importing CSS that can conflict with Tailwind v4's reset; more config overhead |

**Installation and setup:**
```typescript
// app/layout.tsx — add once at root
import { Toaster } from "sonner"
// inside <body>:
<Toaster position="bottom-right" theme="dark" richColors />

// Usage anywhere in a Client Component:
import { toast } from "sonner"
toast.success("Member created successfully.")
toast.error("Failed to upload PDF.")
```

**Why sonner fits this project:** The dark theme + richColors produces green/red toasts that integrate naturally with the black/forest-green aesthetic. No custom CSS needed.

### Font Loading

**Recommendation: next/font/google — already configured, needs font replacement**

The scaffold currently loads `Geist` and `Geist_Mono`. PROJECT.md requires:
- Body: EB Garamond (Google Fonts serif)
- Editorial heading: one additional Google Fonts choice

**Recommended editorial heading font:** `Cormorant Garamond` (high-fashion, editorial, premium feel — aligns with Chrome Hearts / "I AM MUSIC" direction) or `Playfair Display` (heavier serifs, dramatic). Both are available on Google Fonts.

**Pattern:**
```typescript
// app/layout.tsx
import { EB_Garamond, Cormorant_Garamond } from "next/font/google"

const ebGaramond = EB_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  variable: "--font-body",
  display: "swap",
})

const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["300", "400", "600", "700"],
  style: ["normal", "italic"],
  variable: "--font-heading",
  display: "swap",
})

// In <body className>:
className={`${ebGaramond.variable} ${cormorant.variable}`}
```

**In Tailwind v4 globals.css:**
```css
@theme inline {
  --font-body: var(--font-body);       /* maps to CSS var from next/font */
  --font-heading: var(--font-heading);
}
```

**Why next/font only:** Self-hosts fonts, eliminates render-blocking Google Fonts `<link>` requests, prevents layout shift (CLS), and works correctly with App Router's streaming. Never use `<link rel="stylesheet">` for Google Fonts in Next.js — it breaks LCP scores.

### Route Protection

**Recommendation: Client-side AuthGuard components (NOT Next.js middleware.ts)**

Because JWT tokens are stored in localStorage, and middleware runs in Edge Runtime (no DOM APIs), route protection must be fully client-side.

**Architecture:**
```
app/
  (public)/          # No protection — Server Components
    page.tsx
    rush/page.tsx
    history/page.tsx
    philanthropy/page.tsx
    contact/page.tsx
    join/page.tsx
  (auth)/            # Auth pages — redirect to /dashboard if already logged in
    login/page.tsx
  (member)/          # Protected — redirect to /login if no token
    dashboard/page.tsx
  (admin)/           # Protected + role check — redirect to /dashboard if not admin
    admin/
      page.tsx
      events/page.tsx
      members/page.tsx
      rush/page.tsx
      content/page.tsx
```

**Route group layouts for protection:**
```typescript
// app/(member)/layout.tsx — "use client"
"use client"
export default function MemberLayout({ children }) {
  return <AuthGuard>{children}</AuthGuard>
}

// app/(admin)/layout.tsx — "use client"
"use client"
export default function AdminLayout({ children }) {
  return <AuthGuard requireAdmin>{children}</AuthGuard>
}
```

**Why not middleware.ts?** Middleware cannot read localStorage. Workaround of storing token in a cookie just for middleware reads is over-engineering for MVP. The client-side guard produces a brief flash (null render) before redirect, which is acceptable for a member portal that isn't public-facing.

**Flash mitigation:** Show a loading skeleton on null token state rather than nothing:
```typescript
if (isLoading) return <PageSkeleton />  // renders on first paint
if (!token) return null                  // then redirects
```

---

## Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| react-hook-form | ^7.54 | Form state + validation orchestration | All forms: /join interest form, /login, all admin forms |
| zod | ^3.24 | Runtime schema validation + TypeScript type inference | Required alongside react-hook-form; also validates API responses if desired |
| @hookform/resolvers | ^3.10 | Connects zod schemas to react-hook-form | Required when using zod with RHF |
| sonner | ^1.7 | Toast notifications | All user feedback: success/error states on mutations |
| clsx | ^2.1 | Conditional className merging | Component variants: `clsx("base-class", { "active-class": isActive })` |
| tailwind-merge | ^2.6 | Merge Tailwind classes without conflicts | Component libraries where props can override base classes |

**Note on clsx + tailwind-merge:** Often used together via a `cn()` utility:
```typescript
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```
This is the standard pattern from shadcn/ui, now broadly adopted. Use it in every component.

---

## Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| ESLint 9 + eslint-config-next | Linting | Already configured; run `pnpm lint` |
| TypeScript ^5 strict | Type checking | Already configured; keep `"strict": true` in tsconfig |
| pnpm 10 | Package manager | Already configured; never use npm or yarn in this project |

---

## Installation

```bash
# Form handling
pnpm add react-hook-form zod @hookform/resolvers

# Toast notifications
pnpm add sonner

# Class utilities
pnpm add clsx tailwind-merge
```

No dev dependency additions needed for these — they are runtime dependencies.

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| react-hook-form | Formik | Only if team is already deeply familiar with Formik; Formik has React 19 compatibility issues as of early 2025 |
| zod | yup / joi | yup if already in codebase; zod has better TypeScript inference and is the current ecosystem standard |
| sonner | react-hot-toast | react-hot-toast is fine and has fewer dependencies; choose it if bundle size is critical (unlikely here) |
| client-side AuthGuard | Next.js middleware | Only viable if tokens are stored in cookies; incompatible with the localStorage choice |
| native fetch wrapper | SWR / React Query | Introduce SWR in v2 if event list needs real-time polling or the team grows; overkill for MVP with ~5 data types |
| next/font/google | CSS @import Google Fonts | Never; @import blocks rendering and hurts Core Web Vitals |
| native FormData | react-dropzone | Add react-dropzone in v2 if drag-and-drop PDF upload UX is requested; not needed for MVP admin tools |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Formik | React 19 compatibility warnings; controlled inputs re-render on every keystroke | react-hook-form v7 |
| react-toastify | Requires importing its own CSS which conflicts with Tailwind v4 reset; heavier bundle | sonner |
| SWR / React Query (for MVP) | Adds ~30-50KB; this app's data fetching is simple enough for useEffect + fetch; over-engineering for 2-3 devs on a 10-week timeline | Custom `apiFetch` wrapper |
| axios | Unnecessary when native fetch covers all requirements; adds bundle weight; `async/await` with fetch is equally readable in 2025 | Native fetch in `apiFetch` wrapper |
| next/headers cookies for auth | Requires server-side cookie flow incompatible with FastAPI JWT without a proxy layer | localStorage per PROJECT.md decision |
| `<link rel="stylesheet">` for Google Fonts | Blocking request; hurts LCP and CLS; eliminated by next/font | `next/font/google` imports |
| shadcn/ui component library | Adds Radix UI dependencies (~100KB+); the PCO aesthetic requires fully custom components anyway; learning shadcn's system adds overhead for future CS contributors | Hand-rolled Tailwind components |

---

## Stack Patterns by Variant

**For Server Component public pages (no auth):**
- Use `async` Server Component with `fetch()` directly
- Add `next: { revalidate: 3600 }` for ISR (content changes rarely)
- No client-side JavaScript needed for read-only content

**For Client Component authenticated pages:**
- Mark `"use client"` at top of component
- Use `useEffect` to check localStorage token
- Use custom `apiFetch` wrapper for all API calls
- Wrap with `AuthGuard` via route group layout

**For admin mutation forms:**
- react-hook-form + zod schema
- On submit: call `apiFetch`, handle success with `toast.success()`, handle errors by calling `setError()` for field-specific errors or `toast.error()` for generic failures
- Disable submit button during `formState.isSubmitting`

**For the interest form (/join) with 409 handling:**
- Same pattern; specifically map HTTP 409 → `setError("email", { message: "Email already registered." })`

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|----------------|-------|
| react-hook-form ^7.54 | React 19.2.3 | v7.50+ explicitly supports React 19's concurrent features; no issues |
| zod ^3.24 | TypeScript ^5, Node 22 | No compatibility concerns; zod 4 is in development but 3.x is stable |
| sonner ^1.7 | React 19, Next.js App Router, Tailwind v4 | Works with RSC architecture; `<Toaster>` must be in a Client Component (root layout body) |
| clsx ^2.1 | React 19, TypeScript ^5 | Tiny utility; no compatibility concerns |
| tailwind-merge ^2.6 | Tailwind v4 | v2.6+ is aware of Tailwind v4 class syntax |
| @hookform/resolvers ^3.10 | react-hook-form ^7.54, zod ^3.24 | Versions must be kept in sync; ^3.10 targets RHF v7 |

---

## Architecture Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Form handling | react-hook-form + zod | Industry standard; uncontrolled inputs; field-level error injection from API |
| Auth storage | localStorage (PROJECT.md constraint) | Simplest MVP; HttpOnly cookies require proxy complexity |
| Route protection | Client-side AuthGuard components | middleware.ts cannot access localStorage |
| Data fetching (public) | async Server Components + native fetch with ISR | Better SEO, no client JS overhead |
| Data fetching (protected) | useEffect + custom apiFetch wrapper | JWT only available client-side |
| Toast | sonner | Best fit for dark theme aesthetic, minimal config |
| Fonts | next/font/google | Performance (no render-blocking); already used in scaffold |
| File upload | Native FormData + fetch | No library needed; matches backend multipart expectation |
| CSS utilities | clsx + tailwind-merge via cn() | Standard pattern; prevents Tailwind class conflicts |

---

## Sources

- Project context: `/pco_website/.planning/PROJECT.md` — explicit decisions (localStorage auth, App Router, Tailwind v4) — HIGH confidence
- Existing codebase: `package.json`, `app/layout.tsx`, `globals.css` — confirmed current scaffold state — HIGH confidence
- Training knowledge: Next.js 16 App Router behavior (Edge Runtime, localStorage restriction), React 19 compatibility matrix for RHF, sonner/sonner-toast ecosystem dominance — MEDIUM-HIGH confidence (knowledge cutoff August 2025; Next.js 16 released ~early 2025)
- Edge Runtime limitation (no localStorage in middleware): Verified from training — Next.js middleware runs in a V8 isolate without DOM globals; this is a known, documented constraint — HIGH confidence

---

*Stack research for: PCO Website Frontend — Next.js 16 App Router + FastAPI backend*
*Researched: 2026-03-05*
