# Phase 1: Foundation - Research

**Researched:** 2026-03-06
**Domain:** Next.js 16 App Router, Tailwind v4, React Context auth, design system components
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**File & Project Structure**
- Shared files (lib/, components/, contexts/, types/) live at root level, next to app/ — not nested inside app/
- Components organized by type: `components/ui/` for design system primitives (ChromeCard, ChromeButton, etc.), `components/layout/` for SiteLayout
- TypeScript `@/` path alias configured in tsconfig.json: `"@/*": ["./*"]` (already present)
- Route groups in app/: `(public)`, `(auth)`, `(member)`, `(admin)` — each with its own layout.tsx for auth isolation

**Navigation Design**
- Logo: "PSI CHI OMEGA" in Cormorant Garamond, uppercase, letter-tracked — text only, no image/SVG asset
- Public nav links: Rush, History, Philanthropy, Contact — all uppercase, tracked
- Header CTAs: "Join" (ChromeButton primary → /join) and "Login" (ChromeButton secondary → /login) both present
- Mobile menu: hamburger icon toggles a full-width dropdown panel below the header; no slide-in drawer

**Chrome Aesthetic — ChromeCard**
- Metallic border: thin (1px) gradient from silver/white (top-left) fading to transparent (bottom-right)
- Glow effect: hover-only, subtle green (#228B22) box-shadow/glow — no permanent glow at rest
- Rounded corners, dark card background (#0a0a0a or #111)

**Chrome Aesthetic — ChromeButton**
- Primary variant: forest green (#228B22) fill, white text
- Secondary variant: chrome outline (silver/white border), transparent background, white text
- Hover sheen: diagonal light sweep animation — CSS-only `@keyframes` + overflow hidden

**Grain Overlay**
- Include in Phase 1 — pure CSS, no JS overhead
- Applied globally via `body::before` or `body::after` pseudo-element
- Opacity: ~3-5% — extremely subtle

**Tech Decisions (from STATE.md)**
- localStorage for JWT storage — client-only auth; no Server Component token access
- proxy.ts NOT middleware.ts — Next.js 16 rename (codemod available: `npx @next/codemod@canary middleware-to-proxy .`)
- No component library — custom components only (no shadcn/ui)
- Tailwind v4 @theme in globals.css — no tailwind.config.js; validate class renames before building

### Claude's Discretion
- Exact border-radius values for ChromeCard and ChromeButton
- Specific box-shadow spread/blur values for the hover glow
- Duration/easing of the diagonal sheen animation
- Whether grain uses SVG `feTurbulence` filter or static base64 noise image
- Exact letter-spacing and font-weight values for nav labels

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INFRA-01 | API client wrapper (`lib/api.ts`) with base URL from `NEXT_PUBLIC_API_BASE`, automatic `Authorization: Bearer` header injection, clean error handling | Singleton fetch wrapper pattern; env var setup |
| INFRA-02 | Token refresh on 401 via singleton `refreshPromise` to prevent race condition | Singleton promise pattern documented in Code Examples |
| INFRA-03 | Auth state management via React Context (`AuthContext`) with user object, tokens, loading state, login/logout actions | React Context pattern; localStorage JWT storage |
| INFRA-04 | `AuthGuard` client-side hook/component that redirects unauthenticated users to `/login` and non-admin to `/dashboard` | useRouter redirect pattern; "use client" directive |
| INFRA-05 | `proxy.ts` at project root with `auth-hint` cookie bridge for optimistic server-side redirects | Next.js 16 proxy.ts API fully documented |
| INFRA-06 | `.env.example` with `NEXT_PUBLIC_API_BASE=http://localhost:8000` | Standard Next.js env convention |
| INFRA-07 | Next.js App Router route groups: `(public)`, `(auth)`, `(member)`, `(admin)` established | Route groups + per-group layout.tsx pattern |
| THEME-01 | Brand tokens in globals.css `@theme` block: black, forest green, white | Tailwind v4 @theme syntax fully documented |
| THEME-02 | EB Garamond + Cormorant Garamond via `next/font/google` with CSS variable registration | next/font pattern documented; variable names defined |
| THEME-03 | SiteLayout with responsive header, footer, mobile hamburger (no horizontal scroll) | Mobile-first nav pattern; hamburger dropdown |
| THEME-04 | ChromeCard with thin metallic gradient border and subtle hover glow | CSS gradient border + box-shadow glow pattern |
| THEME-05 | ChromeButton primary/secondary variants; hover sheen via CSS @keyframes | CSS-only diagonal sweep animation pattern |
| THEME-06 | SectionTitle component using Cormorant Garamond | Font variable application pattern |
| THEME-07 | Divider with thin chrome gradient line + small green dot accent | CSS gradient + pseudo-element dot pattern |
| THEME-08 | Toast/alert via sonner (v2.0.7) with dark theme; success/error variants | Sonner setup with theme="dark" + richColors |
| THEME-09 | Subtle grain/noise overlay on black backgrounds (~3-5% opacity, CSS-only) | SVG feTurbulence via body::before pseudo-element |
</phase_requirements>

---

## Summary

Phase 1 establishes the entire shared infrastructure and design system for the PSI CHI OMEGA website. The project runs Next.js 16.1.6 with React 19, Tailwind v4 (already wired via @tailwindcss/postcss), and TypeScript with strict mode. The project root already has a working scaffold — this phase replaces placeholder content (Geist fonts, default colors, generic layout) with the actual brand system and adds lib/, contexts/, types/, components/ directories from scratch.

The most critical technical decisions are already locked: proxy.ts (not middleware.ts) for the auth-hint cookie bridge, localStorage for JWT tokens (making auth entirely client-side), and Tailwind v4's CSS-first @theme block (no tailwind.config.js). The main research findings confirm all locked decisions are sound and provide exact implementation patterns for each.

The Chrome Hearts / luxury-dark aesthetic is implemented entirely in CSS — metallic gradient borders, hover sheen via @keyframes, SVG-based grain overlay. No third-party animation library is needed. The only new npm packages required are: react-hook-form, zod, sonner, clsx, tailwind-merge (none installed yet).

**Primary recommendation:** Install dependencies first, establish @theme tokens and fonts, then build auth utilities, then design system components in that dependency order.

---

## Standard Stack

### Core (already installed)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| next | 16.1.6 | Framework | Project requirement |
| react | 19.2.3 | UI runtime | Project requirement |
| typescript | ^5 | Type safety | Project requirement |
| tailwindcss | ^4 | Styling | Configured via postcss |
| @tailwindcss/postcss | ^4 | Tailwind v4 integration | Required for v4 PostCSS pipeline |

### To Install
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sonner | ^2.0.7 | Toast notifications | Lightweight, opinionated, dark-theme native |
| clsx | ^2 | Conditional class names | Zero-dep, tree-shakeable |
| tailwind-merge | ^3 | Resolve Tailwind class conflicts | Required for variant-based components |
| react-hook-form | ^7 | Form state + validation | Performance-first, used in Phase 2 forms |
| zod | ^3 | Schema validation | TypeScript-first; pairs with react-hook-form |

**Installation:**
```bash
pnpm add sonner clsx tailwind-merge react-hook-form zod
```

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| sonner | react-hot-toast | sonner has dark theme built-in; hot-toast requires manual theming |
| clsx + tailwind-merge | class-variance-authority | CVA adds abstraction; clsx+twMerge is simpler for custom components |
| react-hook-form | formik | RHF is lighter and uncontrolled-first; formik is heavier |

---

## Architecture Patterns

### Project Structure (root-level, no src/)
```
pco_website/
├── app/
│   ├── (public)/          # Rush, History, Philanthropy, Contact pages
│   │   └── layout.tsx     # Public layout (no auth check)
│   ├── (auth)/            # /login page
│   │   └── layout.tsx     # Minimal layout (no SiteLayout header)
│   ├── (member)/          # /dashboard
│   │   └── layout.tsx     # AuthGuard: redirect to /login if unauthenticated
│   ├── (admin)/           # /admin/*
│   │   └── layout.tsx     # AuthGuard: redirect to /login or /dashboard
│   ├── globals.css        # @import tailwindcss + @theme tokens + grain overlay
│   ├── layout.tsx         # Root layout: fonts, SiteLayout, <Toaster />
│   └── page.tsx           # Home page (Phase 2)
├── components/
│   ├── layout/
│   │   └── SiteLayout.tsx # Header, footer, mobile nav
│   └── ui/
│       ├── ChromeCard.tsx
│       ├── ChromeButton.tsx
│       ├── SectionTitle.tsx
│       └── Divider.tsx
├── contexts/
│   └── AuthContext.tsx    # JWT state, login/logout, loading
├── lib/
│   ├── api.ts             # apiFetch() with auth + singleton refresh
│   ├── auth.ts            # Token helpers (get/set/clear from localStorage)
│   └── utils.ts           # cn() utility (clsx + twMerge)
├── types/
│   └── api.ts             # Shared TypeScript types (User, ApiError, etc.)
├── proxy.ts               # auth-hint cookie bridge (Next.js 16 naming)
├── .env.example
└── .env.local             # NEXT_PUBLIC_API_BASE=http://localhost:8000
```

### Pattern 1: Tailwind v4 @theme Tokens (CSS-first config)

**What:** Brand tokens defined as CSS variables in globals.css @theme block. No tailwind.config.js.
**When to use:** All color, font, and spacing design tokens for the brand.

```css
/* app/globals.css */
/* Source: https://tailwindcss.com/docs/theme */
@import "tailwindcss";

@theme inline {
  /* Brand colors */
  --color-black: #000000;
  --color-green: #228B22;
  --color-white: #ffffff;
  --color-card: #0a0a0a;
  --color-card-elevated: #111111;
  --color-chrome: #c0c0c0;

  /* Fonts — inline because they reference CSS vars set by next/font */
  --font-body: var(--font-eb-garamond), Georgia, serif;
  --font-heading: var(--font-cormorant-garamond), Georgia, serif;
}
```

The `@theme inline` variant is required when referencing other CSS variables (like those emitted by next/font). Without `inline`, variable resolution may fail across the DOM tree.

### Pattern 2: next/font Google Font Setup

**What:** EB Garamond and Cormorant Garamond loaded at build time, zero layout shift.
**When to use:** Root layout only — fonts cascade down to all children.

```typescript
// app/layout.tsx
// Source: https://nextjs.org/docs/app/getting-started/fonts
import { EB_Garamond, Cormorant_Garamond } from "next/font/google";

const ebGaramond = EB_Garamond({
  subsets: ["latin"],
  variable: "--font-eb-garamond",
  display: "swap",
});

const cormorantGaramond = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-cormorant-garamond",
  display: "swap",
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${ebGaramond.variable} ${cormorantGaramond.variable}`}>
      <body>{children}</body>
    </html>
  );
}
```

The CSS variable names (`--font-eb-garamond`, `--font-cormorant-garamond`) are developer-chosen — they are not auto-generated. The `.variable` className emits the CSS variable to the HTML element so `@theme inline` can reference it.

### Pattern 3: proxy.ts Auth-Hint Cookie Bridge

**What:** Next.js 16 proxy.ts reads an `auth-hint` cookie and redirects before the page renders, preventing flash of protected content.
**When to use:** Optimistic server-side redirects only. Real security lives in FastAPI.

```typescript
// proxy.ts (project root — NOT app/proxy.ts)
// Source: https://nextjs.org/docs/app/api-reference/file-conventions/proxy
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const authHint = request.cookies.get("auth-hint")?.value;
  const { pathname } = request.nextUrl;

  const isProtected = pathname.startsWith("/dashboard") || pathname.startsWith("/admin");
  const isAuthPage = pathname === "/login";

  if (isProtected && !authHint) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  if (isAuthPage && authHint) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
```

Key facts about Next.js 16 proxy.ts (source: official docs):
- Export function MUST be named `proxy` (not `middleware`)
- Runs on Node.js runtime only — Edge runtime NOT supported
- `middleware.ts` is deprecated; use codemod `npx @next/codemod@canary middleware-to-proxy .` if existing file exists
- The project has no existing middleware.ts, so no codemod needed

### Pattern 4: Singleton Token Refresh Queue

**What:** A module-level `refreshPromise` variable prevents concurrent 401 responses from triggering multiple refresh calls.
**When to use:** All authenticated API calls must go through `apiFetch`.

```typescript
// lib/api.ts
let refreshPromise: Promise<string | null> | null = null;

async function refreshTokens(): Promise<string | null> {
  const refresh = localStorage.getItem("refresh_token");
  if (!refresh) return null;
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return null;
    const data = await res.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return data.access_token;
  } catch {
    return null;
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const base = process.env.NEXT_PUBLIC_API_BASE;
  const token = localStorage.getItem("access_token");

  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  headers.set("Content-Type", "application/json");

  let res = await fetch(`${base}${path}`, { ...options, headers });

  if (res.status === 401) {
    // Singleton: if refresh already in flight, await same promise
    if (!refreshPromise) {
      refreshPromise = refreshTokens().finally(() => { refreshPromise = null; });
    }
    const newToken = await refreshPromise;
    if (!newToken) throw new Error("Session expired");

    headers.set("Authorization", `Bearer ${newToken}`);
    res = await fetch(`${base}${path}`, { ...options, headers });
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw Object.assign(new Error(error.detail ?? "API error"), { status: res.status });
  }

  return res.json() as Promise<T>;
}
```

### Pattern 5: ChromeButton Diagonal Sheen Animation

**What:** Pure CSS @keyframes diagonal highlight sweep on hover.
**When to use:** Both ChromeButton variants.

```css
/* In globals.css or component <style> */
@keyframes sheen {
  0% {
    transform: translateX(-100%) skewX(-20deg);
  }
  100% {
    transform: translateX(200%) skewX(-20deg);
  }
}

/* Component uses overflow-hidden + ::after pseudo-element */
```

```tsx
// components/ui/ChromeButton.tsx
// The sheen is a ::after pseudo-element on the button container
// overflow-hidden clips it; animation fires on :hover
```

### Pattern 6: cn() Utility

**What:** Combines clsx (conditional classes) and twMerge (conflict resolution) into one function.
**When to use:** Every component that accepts className prop or has conditional variants.

```typescript
// lib/utils.ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### Pattern 7: Route Group Auth Layout

**What:** Each protected route group has a layout.tsx that renders `<AuthGuard>` before children.
**When to use:** `(member)` and `(admin)` groups.

```typescript
// app/(member)/layout.tsx
"use client";
import { AuthGuard } from "@/components/layout/AuthGuard";

export default function MemberLayout({ children }: { children: React.ReactNode }) {
  return <AuthGuard requiredRole="member">{children}</AuthGuard>;
}
```

### Pattern 8: Grain Overlay (CSS-only)

**What:** Extremely subtle noise texture over the black background using SVG feTurbulence filter.
**When to use:** Applied globally via body::before pseudo-element in globals.css.

```css
/* app/globals.css */
body {
  background-color: #000000;
  color: #ffffff;
  position: relative;
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 200px 200px;
}
```

SVG feTurbulence is preferred over a base64 PNG for this project: smaller payload, no extra asset file, and scales perfectly. The `numOctaves: 3` value is the performance sweet spot per Frontend Masters research.

### Anti-Patterns to Avoid

- **Placing brand tokens in `:root` instead of `@theme`:** `:root` variables do NOT generate Tailwind utility classes. Only `@theme` variables create utilities like `bg-green` or `font-heading`.
- **Using `@theme` (not `inline`) for font variables:** When the value references another CSS variable (e.g., `var(--font-eb-garamond)`), use `@theme inline` to ensure correct resolution.
- **Calling `apiFetch` from Server Components:** tokens live in localStorage, which is client-only. All authenticated fetches must be in Client Components or API route handlers.
- **Named export `middleware` in proxy.ts:** The exported function must be named `proxy`. Naming it `middleware` will still work (Next.js provides backward compat) but is deprecated.
- **Importing `sonner`'s `<Toaster>` in a Client Component boundary without "use client":** `<Toaster>` itself is safe in Server Components (layout.tsx) but `toast()` calls must come from Client Components.
- **Cormorant Garamond without explicit weight array:** Unlike variable fonts, Cormorant Garamond requires explicit `weight` values. Omitting them will only load the default weight.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Conditional class merging | Custom string concat | `clsx` + `tailwind-merge` | Tailwind conflict resolution (e.g., `p-2` vs `p-4`) is non-trivial |
| Toast notifications | Custom toast state | `sonner` | Position management, animation, stacking, accessibility (aria-live) |
| Form validation | Manual onChange state | `react-hook-form` + `zod` | Uncontrolled performance, error state management, schema inference |
| Font loading | Manual `<link>` tags | `next/font/google` | Built-in subsetting, preload, zero layout shift, no FOUT |

**Key insight:** The "don't hand-roll" items here are specifically the invisible complexity ones — toast stacking, font flash prevention, and Tailwind class conflict resolution all have edge cases that are time-consuming to discover and fix.

---

## Common Pitfalls

### Pitfall 1: @theme vs @theme inline for Font References
**What goes wrong:** `@theme { --font-body: var(--font-eb-garamond); }` silently fails — Tailwind uses an unresolved CSS variable reference, fonts don't load in utilities.
**Why it happens:** Standard `@theme` resolves variable values at definition scope, not at usage scope. `next/font` attaches its CSS variable to the `<html>` element, which is a different scope.
**How to avoid:** Always use `@theme inline` when the value is `var(--something-else)`.
**Warning signs:** Font utility classes exist but apply `font-family: var(--font-eb-garamond)` which resolves to empty string in component CSS.

### Pitfall 2: Race Condition on Token Refresh
**What goes wrong:** Two concurrent API calls both get 401, both call `refreshTokens()`, second refresh invalidates the first refresh token, all requests fail, user is logged out.
**Why it happens:** Without the singleton `refreshPromise`, each 401 independently kicks off a refresh cycle.
**How to avoid:** Module-level `let refreshPromise: Promise<...> | null = null` pattern — all concurrent 401s await the same promise.
**Warning signs:** Intermittent logouts when navigating quickly between pages that trigger multiple API calls.

### Pitfall 3: Cormorant Garamond Weight Not Loading
**What goes wrong:** Headings render in the wrong weight or fall back to system serif.
**Why it happens:** Cormorant Garamond is not a variable font — specific weight values must be requested explicitly.
**How to avoid:** Pass `weight: ["300", "400", "500", "600", "700"]` to the font constructor.
**Warning signs:** Heading appears in weight 400 regardless of CSS font-weight value.

### Pitfall 4: Grain Overlay Blocking Clicks
**What goes wrong:** Interactive elements below the grain overlay become unclickable.
**Why it happens:** `body::before` with `position: fixed` and `z-index: 9999` sits over everything including buttons.
**How to avoid:** Always add `pointer-events: none` to the grain pseudo-element.
**Warning signs:** Buttons visually present but don't respond to clicks.

### Pitfall 5: `localStorage` Access in Server Components
**What goes wrong:** Build-time error "localStorage is not defined" or hydration mismatch.
**Why it happens:** Server Components run in Node.js — no browser globals.
**How to avoid:** Auth utilities in `lib/auth.ts` must only be called from Client Components (files with `"use client"`) or inside `useEffect`. AuthContext itself must be a Client Component.
**Warning signs:** Build fails or "ReferenceError: localStorage is not defined" at runtime.

### Pitfall 6: proxy.ts File Location
**What goes wrong:** proxy.ts placed inside `app/` directory is treated as a route file, not the proxy.
**Why it happens:** Next.js expects proxy.ts at the project root (same level as `app/`, `package.json`).
**How to avoid:** Create `proxy.ts` at `/Users/briannguyen/Workspace/PCO-Website/pco_website/proxy.ts`.
**Warning signs:** Redirects don't fire; no proxy behavior observed in dev server logs.

### Pitfall 7: Tailwind v4 Class Renames
**What goes wrong:** Using Tailwind v3 class names that were renamed in v4.
**Why it happens:** v4 introduced class renames (e.g., `shadow-sm` → `shadow-xs` equivalents, `flex-wrap` syntax changes, `overflow-x` behavior).
**How to avoid:** Check the [Tailwind v4 upgrade guide](https://tailwindcss.com/docs/upgrade-guide) before writing components. Use `npx @tailwindcss/upgrade` for auto-migration if converting v3 code.
**Warning signs:** Styles silently not applying; wrong visual result without errors.

---

## Code Examples

### globals.css Complete Setup
```css
/* app/globals.css */
@import "tailwindcss";

@theme inline {
  /* Brand colors */
  --color-black: #000000;
  --color-green: #228B22;
  --color-white: #ffffff;
  --color-card: #0a0a0a;
  --color-card-elevated: #111111;
  --color-chrome: #c0c0c0;
  --color-chrome-light: #e8e8e8;

  /* Fonts — must be inline to reference next/font CSS vars */
  --font-body: var(--font-eb-garamond), Georgia, serif;
  --font-heading: var(--font-cormorant-garamond), "Times New Roman", serif;
}

/* Grain overlay */
body {
  background-color: #000000;
  color: #ffffff;
  font-family: var(--font-body);
}

body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  opacity: 0.04;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  background-repeat: repeat;
  background-size: 200px 200px;
}

/* Chrome sheen animation */
@keyframes sheen {
  0% { transform: translateX(-100%) skewX(-20deg); }
  100% { transform: translateX(250%) skewX(-20deg); }
}
```

### Sonner Setup in Root Layout
```typescript
// app/layout.tsx
import { Toaster } from "sonner";

// In the JSX:
// <Toaster theme="dark" richColors position="top-right" />
//
// Usage from client components:
// import { toast } from "sonner";
// toast.success("Saved!"); // renders in green
// toast.error("Something went wrong"); // renders in red
```

### AuthContext Shell
```typescript
// contexts/AuthContext.tsx
"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

interface User { id: string; name: string; email: string; role: "member" | "admin"; }
interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (tokens: { access_token: string; refresh_token: string }, user: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Hydrate from localStorage on mount
    const token = localStorage.getItem("access_token");
    // TODO: validate token / fetch /v1/users/me if needed
    setLoading(false);
  }, []);

  const login = (tokens: { access_token: string; refresh_token: string }, user: User) => {
    localStorage.setItem("access_token", tokens.access_token);
    localStorage.setItem("refresh_token", tokens.refresh_token);
    // Set auth-hint cookie so proxy.ts can read it
    document.cookie = "auth-hint=1; path=/; samesite=lax";
    setUser(user);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    document.cookie = "auth-hint=; path=/; max-age=0";
    setUser(null);
  };

  return <AuthContext.Provider value={{ user, loading, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
```

### ChromeCard Structure
```tsx
// components/ui/ChromeCard.tsx
import { cn } from "@/lib/utils";

interface ChromeCardProps {
  children: React.ReactNode;
  className?: string;
}

export function ChromeCard({ children, className }: ChromeCardProps) {
  return (
    <div className={cn(
      // Dark background slightly elevated from pure black
      "relative rounded-lg bg-card",
      // Metallic gradient border via background-clip trick
      // border-image or pseudo-element approach
      "before:absolute before:inset-0 before:rounded-[inherit] before:p-px",
      "before:bg-gradient-to-br before:from-chrome-light before:to-transparent",
      "before:-z-10",
      // Hover glow
      "transition-shadow duration-300",
      "hover:shadow-[0_0_20px_rgba(34,139,34,0.3)]",
      className
    )}>
      <div className="relative z-10 rounded-[inherit] bg-card p-6">
        {children}
      </div>
    </div>
  );
}
```

Note: The metallic border gradient on a div with rounded corners requires a wrapper + inner div technique (background-clip) because CSS `border-image` does not support `border-radius`. The `before:` pseudo-element creates the gradient "border" by being slightly larger than the inner div.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `middleware.ts` with `export function middleware()` | `proxy.ts` with `export function proxy()` | Next.js 16.0.0 | Must use new name; old file is deprecated |
| `tailwind.config.js` with `theme.extend` | `@theme` block in CSS | Tailwind v4 (2025) | No JS config file; tokens in CSS |
| `next/font` in `_document.js` | `next/font` in layout.tsx App Router | Next.js 13+ | Font loaded at layout level, not document |
| Edge runtime for middleware | Node.js runtime for proxy | Next.js 15.5.0 stable | Full Node.js APIs available in proxy |
| `@theme` standard | `@theme inline` for CSS var references | Tailwind v4 | Required when referencing other CSS variables |

**Deprecated/outdated:**
- `middleware.ts` / `export function middleware()`: Deprecated in Next.js 16. Still works but will be removed in a future version.
- `tailwind.config.js` for v4: Tailwind v4 ignores this file by default. Tokens go in `globals.css`.
- `Geist` fonts in `app/layout.tsx`: Present in the scaffold; must be replaced with EB Garamond + Cormorant Garamond.
- `--background` / `--foreground` CSS vars + dark mode media query in current globals.css: Must be removed and replaced with brand-specific tokens.

---

## Open Questions

1. **Cormorant Garamond weight for the logo**
   - What we know: Logo uses "PSI CHI OMEGA" uppercase + tracked in Cormorant Garamond
   - What's unclear: Whether weight 300 (thin/elegant) or 600 (semibold/editorial) matches the Chrome Hearts reference
   - Recommendation: Claude's discretion — implement at 300 initially; easy to adjust without API changes

2. **auth-hint cookie lifetime / HttpOnly**
   - What we know: auth-hint is set client-side via `document.cookie` (not HttpOnly); proxy.ts reads it for optimistic redirects
   - What's unclear: Whether auth-hint should expire with the session or be a persistent cookie
   - Recommendation: Set as session cookie (no `max-age`); cleared on logout via `max-age=0`

3. **AuthGuard implementation: component vs hook**
   - What we know: INFRA-04 specifies "hook/component" — both approaches are valid
   - What's unclear: Whether a HOC component or `useAuthGuard()` hook in each layout is cleaner
   - Recommendation: Component `<AuthGuard>` in route group layout.tsx — clearer intent, easier to add loading state UI

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | None installed yet |
| Config file | None — Wave 0 must create |
| Quick run command | `pnpm test` (after setup) |
| Full suite command | `pnpm test` |

Note: This project has no existing test infrastructure (confirmed by scan). Given the nature of Phase 1 — CSS design system components, CSS token configuration, and auth utilities — testing is primarily visual/manual plus TypeScript type checking as the automated gate.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INFRA-01 | apiFetch injects Authorization header | unit | `npx tsc --noEmit` (type check) | ❌ Wave 0 |
| INFRA-02 | Singleton refresh — only one refresh call for concurrent 401s | manual-only | Manual: open two concurrent fetches, verify one refresh call in Network tab | N/A |
| INFRA-03 | AuthContext login/logout state updates | manual-only | Manual: login flow in browser, verify localStorage + state | N/A |
| INFRA-04 | AuthGuard redirects unauthenticated users | manual-only | Manual: visit /dashboard without token, verify redirect to /login | N/A |
| INFRA-05 | proxy.ts redirects when no auth-hint cookie | manual-only | Manual: clear cookies, visit /dashboard, verify redirect before render | N/A |
| INFRA-06 | .env.example contains NEXT_PUBLIC_API_BASE | smoke | `test -f .env.example && grep -q NEXT_PUBLIC_API_BASE .env.example` | ❌ Wave 0 |
| INFRA-07 | Route groups exist with layout.tsx files | smoke | `ls app/(public)/layout.tsx app/(auth)/layout.tsx app/(member)/layout.tsx app/(admin)/layout.tsx` | ❌ Wave 0 |
| THEME-01 | Brand tokens in globals.css @theme block | smoke | `npx tsc --noEmit && pnpm build` | ❌ Wave 0 |
| THEME-02 | Fonts load with no layout shift | manual-only | Manual: check Network tab for font preload, Lighthouse CLS score | N/A |
| THEME-03 | SiteLayout header collapses to hamburger on mobile | manual-only | Manual: resize to 375px, verify hamburger appears, dropdown works | N/A |
| THEME-04 | ChromeCard renders gradient border + hover glow | manual-only | Manual: render on /dev-preview page, inspect CSS | N/A |
| THEME-05 | ChromeButton sheen animation fires on hover | manual-only | Manual: hover primary + secondary buttons, verify diagonal sweep | N/A |
| THEME-06 | SectionTitle uses heading font | manual-only | Manual: inspect computed font-family in DevTools | N/A |
| THEME-07 | Divider renders chrome gradient + green dot | manual-only | Manual: visual inspection on /dev-preview page | N/A |
| THEME-08 | Sonner toast shows dark theme success/error | manual-only | Manual: trigger toast.success() and toast.error() in browser | N/A |
| THEME-09 | Grain overlay visible but not obscuring text | manual-only | Manual: screenshot at 100% opacity then 4%, verify subtle texture | N/A |

### Sampling Rate
- **Per task commit:** `pnpm build` (TypeScript + Next.js compilation)
- **Per wave merge:** `pnpm build` + manual visual review of dev-preview page
- **Phase gate:** All 5 success criteria met (per phase description) + build green

### Wave 0 Gaps
- [ ] Create a `/app/dev-preview/page.tsx` dev-only page to render all design system components for manual visual testing — this is the primary "test harness" for Phase 1
- [ ] Confirm `pnpm test` script wired in package.json (currently absent)

---

## Sources

### Primary (HIGH confidence)
- [Next.js 16 official proxy.ts docs](https://nextjs.org/docs/app/api-reference/file-conventions/proxy) — full API, migration guide, cookie/header examples
- [Tailwind CSS v4 theme docs](https://tailwindcss.com/docs/theme) — @theme syntax, namespaces, inline vs standard
- [Next.js font optimization docs](https://nextjs.org/docs/app/getting-started/fonts) — next/font/google setup, CSS variable registration

### Secondary (MEDIUM confidence)
- [Google Fonts in Next.js 15 + Tailwind v4 guide](https://www.buildwithmatija.com/blog/how-to-use-custom-google-fonts-in-next-js-15-and-tailwind-v4) — verified pattern for variable naming
- [Grainy Gradients - Frontend Masters](https://frontendmasters.com/blog/grainy-gradients/) — SVG feTurbulence performance guidance
- [Sonner npm package](https://www.npmjs.com/package/sonner) — confirmed version 2.0.7

### Tertiary (LOW confidence — for validation)
- [Next.js 16 middleware rename article](https://medium.com/@amitupadhyay878/next-js-16-update-middleware-js-5a020bdf9ca7) — supplementary context; primary source is official docs
- [Token refresh race condition pattern](https://brainsandbeards.com/blog/2024-token-renewal-mutex/) — pattern confirmed by multiple sources

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — versions confirmed from package.json + npm
- Architecture: HIGH — patterns verified against official Next.js 16 and Tailwind v4 docs
- proxy.ts API: HIGH — official docs fetched directly
- Pitfalls: HIGH — sourced from official docs (font inline, Tailwind v4 renames) + known Next.js gotchas
- CSS chrome effects: MEDIUM — pattern is standard CSS, specific values (border-radius, shadow spread) are Claude's discretion

**Research date:** 2026-03-06
**Valid until:** 2026-06-06 (stable stack; Tailwind v4 and Next.js 16 unlikely to have breaking changes within 3 months)
