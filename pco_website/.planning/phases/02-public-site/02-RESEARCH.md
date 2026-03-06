# Phase 2: Public Site - Research

**Researched:** 2026-03-06
**Domain:** Next.js 16 App Router — Server Components, ISR, form validation, long-scroll homepage
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Homepage Architecture**
- Single long-scroll page: Hero → History → Philanthropy → Leadership → Contact — all sections on `/`
- Each section has an `id` anchor: `#history`, `#philanthropy`, `#leadership`, `#contact`
- Nav links for History/Philanthropy/Contact updated to `/#history`, `/#philanthropy`, `/#contact` (works from any page via hash navigation)
- Rush nav link stays `/rush` (separate page)
- Smooth scroll via CSS `scroll-behavior: smooth` on html — NO scroll snapping, free manual scroll
- Divider component (chrome line + green dot) between each section
- Standalone `/history`, `/philanthropy`, `/contact` routes still exist for direct URL access

**Hero Section**
- Content: large `PSI CHI OMEGA` heading (Cormorant Garamond), "Alpha Chapter" subtitle, "Integrity   Perseverance   Eternal Brotherhood" values line, then two CTAs side by side
- CTAs: `[ JOIN NOW ]` (ChromeButton primary → /join) and `[ RUSH INFO ]` (ChromeButton secondary → /rush)
- Background: subtle chrome/metallic gradient — very faint radial or linear gradient from black to near-black with a slight silver tint (no color, no green glow in hero)
- Height: full viewport height (100vh minus header height) — hero fills the screen on load
- Scroll indicator: subtle animated chevron at the bottom center, gently pulsing/bouncing downward

**Rush Page (/rush)**
- Two states driven by API response:
  1. **Published**: Header section (page title + short intro paragraph + "Sign Up" ChromeButton → /join) above a vertical timeline layout (date marker on left, event name/time/location/description on right)
  2. **Coming soon** (`{status:"coming_soon"}`): Centered block — title, "Rush season is coming soon. Sign up to stay in the loop." message, and a "Sign Up" ChromeButton → /join

**Interest Form (/join)**
- Form fields: Name, Email, Phone, Graduation Year, Major — single column, stacked vertically (no grid)
- Validation: react-hook-form + zod; inline errors below each field as user moves past them (no summary block)
- Success state: form is replaced in-place with confirmation — "You're on our list! We'll reach out when rush begins." + "Back to Home" ChromeButton → /
- 409 duplicate email: inline error on the email field — "Looks like you've already signed up!"
- Submit button: ChromeButton primary, full width

**Leadership Section (Homepage)**
- Shows top-6 leadership cards: photo + name + role
- Email NOT shown on public homepage
- Cards arranged in a responsive grid (2-col on tablet, 3-col on desktop, 1-col on mobile)
- Backend dependency: if `GET /v1/content/leadership` does not return photo URLs, fall back to name + role only

### Claude's Discretion
- Exact chrome gradient CSS values for the hero background (keep extremely subtle)
- Chevron scroll indicator implementation (CSS animation vs Framer Motion — keep CSS-only)
- Section padding/spacing values
- Typography scale for hero heading vs subtitle vs values line
- ISR revalidate interval for content pages (suggested: 3600s / 1 hour)
- Timeline connector styling (vertical line between events)

### Deferred Ideas (OUT OF SCOPE)
None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PUB-01 | Home page (`/`) with hero section containing "Join Now" (→ `/join`) and "Rush Info" (→ `/rush`) CTAs visible above fold without scrolling | Server Component page; hero uses `min-h-[calc(100vh-4rem)]` pattern; ChromeButton with href prop already built |
| PUB-02 | Home page section previews for History, Philanthropy, Leadership, Contact — pulled via API; graceful placeholder if API returns empty | `fetch()` with `{ next: { revalidate: 3600 } }` in Server Component; try/catch returns `null` for placeholder rendering |
| PUB-03 | `/join` interest form collecting name, email, phone, graduation year, and major fields | "use client" page; react-hook-form + `@hookform/resolvers/zod` + zod v4 schema |
| PUB-04 | `/join` client-side validation with field-level error states | `useForm` + `zodResolver`; `formState.errors.fieldName.message` rendered below each input |
| PUB-05 | `/join` submits to `POST /v1/interest`; shows success confirmation state on submit | `apiFetch<T>()` or raw `fetch`; `useState` success boolean swaps form for confirmation UI |
| PUB-06 | `/join` handles 409 duplicate email with friendly inline message | Catch block checks `error.status === 409`; call `setError("email", { message: "..." })` |
| PUB-07 | `/rush` fetches `GET /v1/rush`; shows full rush details when published | Server Component; fetch with revalidate; render timeline layout when `status === "published"` |
| PUB-08 | `/rush` shows "coming soon" fallback when API returns `{status:"coming_soon"}` | Conditional render on `data.status` — no separate route, same page component branches |
| PUB-09 | `/history` fetches `GET /v1/content/history`; renders formatted content | Server Component with ISR; prose-style content block |
| PUB-10 | `/philanthropy` fetches `GET /v1/content/philanthropy`; renders formatted content | Same pattern as PUB-09 |
| PUB-11 | `/contact` fetches `GET /v1/content/contacts` + `GET /v1/content/leadership`; email as mailto links | Two parallel fetches in one Server Component using `Promise.all`; email rendered as `<a href="mailto:...">` |
| PUB-12 | All public content pages use Next.js Server Components with ISR for SEO performance | Confirmed pattern: no `"use client"` on page files; `fetch()` with `{ next: { revalidate: 3600 } }` |
</phase_requirements>

---

## Summary

Phase 2 builds all public-facing pages for the PCO website: a single long-scroll homepage, standalone `/rush`, `/join`, `/history`, `/philanthropy`, and `/contact` routes. The stack is entirely locked from Phase 1 — Next.js 16 App Router, Tailwind v4, custom component library, react-hook-form + zod for the interest form. No new dependencies are required except `@hookform/resolvers` for the form validation bridge.

The homepage is the most complex deliverable: five content sections stacked vertically with anchor IDs, a full-viewport hero, API-driven section previews, and a leadership card grid. Server Components with ISR (`revalidate: 3600`) handle all content fetching — the `/join` page is the only "use client" page because it manages form state. The `SiteLayout` component must be wired into `app/(public)/layout.tsx` as the first task, since all other public pages depend on it.

The key integration decision made in Phase 1 is that `app/page.tsx` is currently a Next.js default scaffold page — it must be replaced with the actual PCO homepage. The `(public)` layout currently passes children through unchanged; wiring SiteLayout there is a one-line change.

**Primary recommendation:** Wire SiteLayout → build homepage sections top-to-bottom → build standalone routes in dependency order (history/philanthropy/contact share the same Server Component ISR pattern) → build /rush (two-state conditional) → build /join (only client page).

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Next.js | 16.1.6 (installed) | App Router, Server Components, ISR | Already installed; no change |
| React | 19.2.3 (installed) | UI rendering | Already installed |
| Tailwind v4 | ^4 (installed) | Styling via `@theme inline` | Established in Phase 1 |
| react-hook-form | ^7.71.2 (installed) | Form state management for `/join` | Already installed |
| zod | ^4.3.6 (installed) | Schema validation for `/join` form | Already installed |
| @hookform/resolvers | ^5.x (MUST ADD) | Bridge between RHF and zod v4 | Required; not yet in package.json |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| next/font/google | (built-in) | Cormorant Garamond + EB Garamond | Already configured in root layout |
| next/image | (built-in) | Leadership member photos with fallback | Use only if leadership API returns photo URLs |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| @hookform/resolvers | Manual validate() | More boilerplate, less ergonomic with zod; not worth it |
| CSS chevron animation | Framer Motion | Framer adds bundle weight; CSS-only is sufficient per user constraint |

**Installation (only new dependency):**
```bash
pnpm add @hookform/resolvers
```

**CRITICAL:** `@hookform/resolvers` v5.x is required for Zod v4 support. The project has `zod@^4.3.6`. Do NOT install `@hookform/resolvers` v3.x or lower — those only support Zod v3.

---

## Architecture Patterns

### Recommended Project Structure for Phase 2
```
app/
├── (public)/
│   ├── layout.tsx          # Wire SiteLayout here (TASK 1)
│   ├── page.tsx            # Replace scaffold → homepage (long-scroll)
│   ├── rush/
│   │   └── page.tsx        # Server Component, two-state conditional
│   ├── join/
│   │   └── page.tsx        # "use client" — form with RHF + zod
│   ├── history/
│   │   └── page.tsx        # Server Component, ISR
│   ├── philanthropy/
│   │   └── page.tsx        # Server Component, ISR
│   └── contact/
│       └── page.tsx        # Server Component, ISR, parallel fetch
types/
└── api.ts                  # Add RushContent, ContentSection, LeadershipMember, ContactInfo
```

### Pattern 1: Server Component with ISR (content pages)
**What:** Page file fetches from API at build time, revalidates on a timer. No `"use client"` directive.
**When to use:** All public content pages except `/join` — history, philanthropy, contact, rush, and homepage sections.

```typescript
// Source: Next.js official docs — https://nextjs.org/docs/app/building-your-application/data-fetching/fetching-caching-and-revalidating
// app/(public)/history/page.tsx

import { SectionTitle } from "@/components/ui/SectionTitle";

interface ContentSection {
  title: string;
  body: string;
}

async function getHistory(): Promise<ContentSection | null> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/v1/content/history`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function HistoryPage() {
  const content = await getHistory();

  return (
    <section className="max-w-4xl mx-auto px-4 py-24">
      <SectionTitle>History</SectionTitle>
      {content ? (
        <div className="mt-8 text-white/80 font-body leading-relaxed">
          <p>{content.body}</p>
        </div>
      ) : (
        <p className="mt-8 text-white/40">Coming soon.</p>
      )}
    </section>
  );
}
```

### Pattern 2: Parallel Fetch in Server Component (contact page)
**What:** Two independent API calls run concurrently with `Promise.all`. Each is wrapped in try/catch independently so one failure does not block the other.
**When to use:** `/contact` needs both `GET /v1/content/contacts` and `GET /v1/content/leadership`.

```typescript
// Both fetches share the same revalidate window
const [contacts, leadership] = await Promise.all([
  fetchContacts(),   // GET /v1/content/contacts
  fetchLeadership(), // GET /v1/content/leadership
]);
```

### Pattern 3: Client Form with RHF + Zod v4
**What:** `"use client"` page uses `useForm` with `zodResolver`. Success state is stored in `useState`; on success the form is unmounted and confirmation UI mounts.
**When to use:** Only `/join` — all other pages are Server Components.

```typescript
// Source: @hookform/resolvers docs — https://github.com/react-hook-form/resolvers
// app/(public)/join/page.tsx
"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  email: z.string().email("Enter a valid email"),
  phone: z.string().min(1, "Phone is required"),
  graduation_year: z.string().min(4, "Enter your graduation year"),
  major: z.string().min(1, "Major is required"),
});

type FormData = z.infer<typeof schema>;

export default function JoinPage() {
  const [success, setSuccess] = useState(false);
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<FormData>({ resolver: zodResolver(schema) });

  const onSubmit = async (data: FormData) => {
    try {
      await apiFetch("/v1/interest", { method: "POST", body: JSON.stringify(data) });
      setSuccess(true);
    } catch (err: unknown) {
      if ((err as { status?: number }).status === 409) {
        setError("email", { message: "Looks like you've already signed up!" });
      }
    }
  };

  if (success) {
    return <SuccessConfirmation />;
  }

  return <form onSubmit={handleSubmit(onSubmit)}>{/* fields */}</form>;
}
```

### Pattern 4: Metadata Export for SEO (PUB-12 / QUAL-02)
**What:** Each public page exports a static `metadata` object. Root layout already defines a fallback.
**When to use:** Every page file in `app/(public)/`.

```typescript
// Source: Next.js docs — https://nextjs.org/docs/app/api-reference/functions/generate-metadata
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Rush | Psi Chi Omega",
  description: "Learn about rush events and how to join Psi Chi Omega.",
  openGraph: {
    title: "Rush | Psi Chi Omega",
    description: "Learn about rush events and how to join Psi Chi Omega.",
    type: "website",
  },
};
```

### Pattern 5: SiteLayout Wiring (FIRST TASK)
**What:** Replace the pass-through `app/(public)/layout.tsx` with SiteLayout wrapping.
**When to use:** Task 1 of Phase 2 — all other public pages depend on this.

```typescript
// app/(public)/layout.tsx
import { SiteLayout } from "@/components/layout/SiteLayout";

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return <SiteLayout>{children}</SiteLayout>;
}
```

Note: SiteLayout nav hrefs must be updated simultaneously — `/history`, `/philanthropy`, `/contact` become `/#history`, `/#philanthropy`, `/#contact`.

### Pattern 6: Hero Full-Viewport Height
**What:** Hero section fills viewport minus header (64px / 4rem).
**When to use:** Homepage hero only.

```typescript
// The header is h-16 (4rem = 64px). Use calc to subtract.
<section className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center relative">
```

### Pattern 7: Leadership Photo Fallback
**What:** Render initials in a circle when no photo URL is returned.
**When to use:** Leadership card component, homepage section.

```typescript
// If member.photo_url exists: <img src={member.photo_url} />
// Else: <div className="w-16 h-16 rounded-full bg-card-elevated flex items-center justify-center text-white/60 font-heading text-xl">{initials}</div>
const initials = member.name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase();
```

### Anti-Patterns to Avoid
- **`"use client"` on content pages:** Adding `"use client"` to history/philanthropy/contact/rush pages defeats ISR and SSR. Only `/join` is a client component.
- **Using `apiFetch()` in Server Components:** `apiFetch()` reads localStorage for tokens and is client-only. Server Components use raw `fetch()` with `{ next: { revalidate: N } }`.
- **Putting SiteLayout in root layout:** `app/layout.tsx` wraps auth/member/admin routes too. SiteLayout belongs only in `app/(public)/layout.tsx`.
- **Hash links in `<Link href>` for same-page sections:** Next.js `<Link>` can handle `/#section` from other pages, but plain `<a href="#section">` works fine for in-page navigation within the homepage scroll.
- **Importing from `"zod/v4"`:** The project uses `zod@^4.3.6` which exports from `"zod"` directly. Use `import { z } from "zod"` — not `"zod/v4"`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Form validation | Custom validation logic | react-hook-form + zodResolver + zod | Already installed; handles touched/dirty state, async errors, `setError()` for server errors |
| Gradient border on cards | CSS `border-image` | ChromeCard (wrapper+inner div pattern) | `border-image` incompatible with `border-radius` — already solved in Phase 1 |
| Toast notifications | Custom toast state | sonner (already installed) | Already wired in root layout with dark theme |
| Class merging | String concatenation | `cn()` from `lib/utils.ts` | Already established pattern; handles conditional classes safely |
| Responsive nav | Custom hamburger logic | SiteLayout (already built) | Mobile nav with hamburger is complete — just wire it |

**Key insight:** Phase 1 built the entire UI toolkit. Phase 2 is composition, not construction. Every interactive element, button variant, card, divider, and layout wrapper already exists.

---

## Common Pitfalls

### Pitfall 1: `@hookform/resolvers` Not Installed
**What goes wrong:** `import { zodResolver } from "@hookform/resolvers/zod"` throws module-not-found at runtime.
**Why it happens:** `react-hook-form` and `zod` are installed but `@hookform/resolvers` is a separate package. It is NOT in the current `package.json`.
**How to avoid:** First action in the join page task: `pnpm add @hookform/resolvers`. Verify with `pnpm list @hookform/resolvers`.
**Warning signs:** Build error "Cannot find module '@hookform/resolvers/zod'".

### Pitfall 2: SiteLayout in Root Layout
**What goes wrong:** SiteLayout header/footer wraps login, dashboard, and admin pages.
**Why it happens:** Temptation to add SiteLayout globally for convenience.
**How to avoid:** SiteLayout goes ONLY in `app/(public)/layout.tsx`. This is a locked decision from Phase 1 STATE.md.
**Warning signs:** Login page renders with public site header/footer.

### Pitfall 3: `app/page.tsx` Not Replaced
**What goes wrong:** The root `/` route still shows the Next.js default scaffold page.
**Why it happens:** `app/page.tsx` exists but is NOT inside `(public)/` — it's at the root. The long-scroll homepage must replace this file entirely.
**How to avoid:** The homepage lives at `app/(public)/page.tsx` (if the route group layout applies) OR at `app/page.tsx`. Verify: does `app/(public)/layout.tsx` wrap `app/page.tsx` or does the page need to move into the `(public)` group?
**Resolution:** In Next.js App Router, route groups (parentheses folders) do NOT change the URL. `app/(public)/page.tsx` maps to `/` — the same as `app/page.tsx`. The existing `app/page.tsx` at root must be DELETED or REPLACED; a new `app/(public)/page.tsx` handles the homepage within the public layout. Both cannot coexist for the same route.

### Pitfall 4: Server Components Accessing localStorage
**What goes wrong:** Calling `getAccessToken()` or `apiFetch()` in a Server Component throws "localStorage is not defined".
**Why it happens:** `lib/api.ts` uses `apiFetch()` which reads localStorage — only available in browser.
**How to avoid:** Server Components for public pages use raw `fetch()` directly. No authorization header needed for public API endpoints.

### Pitfall 5: ISR Not Working in Development
**What goes wrong:** `{ next: { revalidate: 3600 } }` appears to have no effect — data always looks fresh.
**Why it happens:** Next.js caching and ISR behave differently in `next dev` vs production build. In dev, each request re-fetches.
**How to avoid:** Don't debug ISR behavior in dev mode. Run `next build && next start` to test revalidation. This is expected behavior.

### Pitfall 6: Hash Navigation From Other Pages
**What goes wrong:** Clicking `/#history` from `/rush` scrolls to top but doesn't reach the section.
**Why it happens:** Browser navigates to `/`, then JavaScript loads, but scroll happens before React hydration.
**How to avoid:** CSS `scroll-behavior: smooth` on the `html` element is the locked decision. For most use cases this is sufficient. The browser handles hash on initial load natively. No JavaScript scroll logic required.

### Pitfall 7: Zod v4 Type Inference Pattern
**What goes wrong:** TypeScript errors when using `z.infer<typeof schema>` with custom generic wrappers.
**Why it happens:** Zod v4 changed type inference compared to v3. Generic wrapper functions that accept `ZodType` as a parameter hit incompatibility.
**How to avoid:** Always use `type FormData = z.infer<typeof schema>` directly on the schema constant — never through a generic wrapper. This pattern is confirmed working with `@hookform/resolvers@5.x` + `zod@4.x`.

---

## Code Examples

### Complete Interest Form Field Pattern
```typescript
// Source: react-hook-form docs — https://react-hook-form.com/docs/useform
// Inline error pattern — render below input when field is touched + invalid
<div className="flex flex-col gap-1.5">
  <label htmlFor="email" className="text-sm tracking-widest uppercase text-white/60">
    Email
  </label>
  <input
    id="email"
    type="email"
    {...register("email")}
    className="bg-card border border-white/10 rounded px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-chrome transition-colors"
    aria-describedby={errors.email ? "email-error" : undefined}
    aria-invalid={!!errors.email}
  />
  {errors.email && (
    <p id="email-error" className="text-xs text-red-400">
      {errors.email.message}
    </p>
  )}
</div>
```

### Rush Page Two-State Pattern
```typescript
// app/(public)/rush/page.tsx
interface RushEvent {
  id: string;
  name: string;
  date: string;
  time: string;
  location: string;
  description: string;
}

interface RushContent {
  status: "published" | "coming_soon";
  title?: string;
  intro?: string;
  events?: RushEvent[];
}

async function getRush(): Promise<RushContent | null> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/v1/rush`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

export default async function RushPage() {
  const data = await getRush();

  if (!data || data.status === "coming_soon") {
    return <RushComingSoon />;
  }

  return <RushPublished data={data} />;
}
```

### Leadership Card with Photo Fallback
```typescript
// Leadership card — initials fallback when photo_url absent
function LeadershipCard({ member }: { member: LeadershipMember }) {
  const initials = member.name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <ChromeCard>
      <div className="flex flex-col items-center gap-3 text-center">
        {member.photo_url ? (
          <img
            src={member.photo_url}
            alt={member.name}
            className="w-16 h-16 rounded-full object-cover"
          />
        ) : (
          <div className="w-16 h-16 rounded-full bg-card-elevated border border-white/10 flex items-center justify-center font-heading text-xl text-white/60">
            {initials}
          </div>
        )}
        <div>
          <p className="text-white font-medium">{member.name}</p>
          <p className="text-white/50 text-sm mt-0.5">{member.role}</p>
        </div>
      </div>
    </ChromeCard>
  );
}
```

### Chevron Scroll Indicator (CSS-only, per user constraint)
```typescript
// CSS keyframes in globals.css (add alongside existing @keyframes sheen):
// @keyframes bounce-gentle {
//   0%, 100% { transform: translateY(0); opacity: 1; }
//   50% { transform: translateY(6px); opacity: 0.6; }
// }

// Component:
<div
  className="absolute bottom-8 left-1/2 -translate-x-1/2"
  style={{ animation: "bounce-gentle 2s ease-in-out infinite" }}
  aria-hidden="true"
>
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="text-white/30">
    <path d="M6 9l6 6 6-6" />
  </svg>
</div>
```

### New Type Definitions Required in `types/api.ts`
```typescript
// Add to types/api.ts

export interface LeadershipMember {
  id: string;
  name: string;
  role: string;
  photo_url?: string;
}

export interface RushEvent {
  id: string;
  name: string;
  date: string;
  time: string;
  location: string;
  description?: string;
}

export interface RushContent {
  status: "published" | "coming_soon";
  title?: string;
  intro?: string;
  events?: RushEvent[];
}

export interface ContentSection {
  title: string;
  body: string;
}

export interface ContactInfo {
  email?: string;
  phone?: string;
  address?: string;
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `getStaticProps` + `revalidate` (Pages Router) | `fetch()` + `{ next: { revalidate: N } }` in Server Components (App Router) | Next.js 13+ | No page-level ISR config needed; per-fetch caching |
| `@hookform/resolvers` v3 (Zod v3 only) | `@hookform/resolvers` v5+ (Zod v4 support) | 2025 | Must install v5+; v3 will fail with `zod@4.x` |
| Zod v3 `z.string().email()` | Same API in Zod v4 — no migration needed for basic schemas | 2025 | The schemas this project needs are simple; no breaking changes |
| `middleware.ts` | `proxy.ts` in Next.js 16 | Next.js 16 | Already handled in Phase 1 |

**Deprecated/outdated:**
- `getStaticProps`/`getServerSideProps`: Pages Router only; not applicable to this App Router project.
- `@hookform/resolvers` v3.x: Incompatible with `zod@4.x`.

---

## Open Questions

1. **Does `GET /v1/content/leadership` return `photo_url`?**
   - What we know: CONTEXT.md explicitly flags this as a backend dependency to confirm before building.
   - What's unclear: API shape unknown — backend not available to inspect.
   - Recommendation: Build the LeadershipCard with both photo and initials-fallback from the start. If `photo_url` is always absent, initials render; if present, photo renders. No rework needed.

2. **What is the exact shape of `GET /v1/rush`?**
   - What we know: Two states documented — `{status:"coming_soon"}` and published with events.
   - What's unclear: Field names for rush events (e.g., is it `date` or `start_date`?).
   - Recommendation: Define TypeScript interfaces as documented in CONTEXT.md. If field names differ, TypeScript will catch mismatches at build time. Use optional chaining on all event fields.

3. **Does `GET /v1/content/contacts` return email + other officer contacts, or just general contact info?**
   - What we know: PUB-11 says contacts page combines contacts + leadership; emails rendered as mailto links.
   - What's unclear: Whether general contacts (chapter email, etc.) come from `/contacts` and officer contacts from `/leadership`, or both from one endpoint.
   - Recommendation: Treat both as separate data sources as specified. Leadership provides individual officer contacts with email; content/contacts provides general chapter contact info.

---

## Validation Architecture

Nyquist validation is enabled (`workflow.nyquist_validation: true` in config.json).

### Test Framework

No test infrastructure exists in this project. No jest.config, vitest.config, or test files were found.

| Property | Value |
|----------|-------|
| Framework | None detected — must install in Wave 0 |
| Config file | None — see Wave 0 |
| Quick run command | `pnpm test` (after Wave 0 setup) |
| Full suite command | `pnpm test` (after Wave 0 setup) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PUB-01 | Hero renders with two CTAs above fold | smoke | `pnpm build && pnpm start` + manual | ❌ Wave 0 |
| PUB-02 | Section previews render; placeholder shown on empty | unit | `vitest run src/__tests__/homepage.test.tsx` | ❌ Wave 0 |
| PUB-03 | Join form renders all 5 fields | unit | `vitest run src/__tests__/join.test.tsx` | ❌ Wave 0 |
| PUB-04 | Zod validation: required fields, email format | unit | `vitest run src/__tests__/join.test.tsx` | ❌ Wave 0 |
| PUB-05 | Success state replaces form on 2xx | unit | `vitest run src/__tests__/join.test.tsx` | ❌ Wave 0 |
| PUB-06 | 409 shows inline email error | unit | `vitest run src/__tests__/join.test.tsx` | ❌ Wave 0 |
| PUB-07 | Rush published renders timeline | unit | `vitest run src/__tests__/rush.test.tsx` | ❌ Wave 0 |
| PUB-08 | Rush coming_soon renders fallback | unit | `vitest run src/__tests__/rush.test.tsx` | ❌ Wave 0 |
| PUB-09 | History content renders; placeholder on null | unit | `vitest run src/__tests__/content.test.tsx` | ❌ Wave 0 |
| PUB-10 | Philanthropy content renders; placeholder on null | unit | `vitest run src/__tests__/content.test.tsx` | ❌ Wave 0 |
| PUB-11 | Contact renders mailto links | unit | `vitest run src/__tests__/content.test.tsx` | ❌ Wave 0 |
| PUB-12 | No "use client" on content page files | static | `grep -r "use client" app/\(public\)/{history,philanthropy,contact,rush}` | manual |

**Note on PUB-12 verification:** Can be mechanically verified with grep — no test framework needed. Only `/join/page.tsx` should have `"use client"`.

### Sampling Rate
- **Per task commit:** `pnpm build` (catches TypeScript errors and missing imports)
- **Per wave merge:** `pnpm test` (unit tests after Wave 0 setup)
- **Phase gate:** Full suite green + `pnpm build` clean before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] Install test framework: `pnpm add -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/user-event` — if team decides to add unit tests
- [ ] `vitest.config.ts` — test runner configuration
- [ ] `src/__tests__/join.test.tsx` — covers PUB-03, PUB-04, PUB-05, PUB-06
- [ ] `src/__tests__/rush.test.tsx` — covers PUB-07, PUB-08
- [ ] `src/__tests__/content.test.tsx` — covers PUB-09, PUB-10, PUB-11

**Alternative:** Given that this is a small project with no existing test infrastructure, the planner may choose to skip automated unit tests for Phase 2 and rely on `pnpm build` (TypeScript), visual QA in dev, and the `pnpm build && pnpm start` smoke test for phase gate verification. This is a pragmatic tradeoff — document the decision if made.

---

## Sources

### Primary (HIGH confidence)
- Project codebase (directly read) — all Phase 1 components, layouts, types, API client, globals.css
- Next.js official docs — ISR revalidate pattern, generateMetadata, App Router fetch caching
- react-hook-form official docs — useForm, zodResolver usage pattern

### Secondary (MEDIUM confidence)
- `@hookform/resolvers` GitHub README — Zod v4 support via v5.x; install command verified
- WebSearch cross-verified: `@hookform/resolvers@5.x` required for `zod@4.x` compatibility; multiple sources confirm

### Tertiary (LOW confidence)
- Assumed API response shapes for `/v1/rush`, `/v1/content/*`, `/v1/content/leadership` — not inspectable without running backend
- Photo URL presence in leadership API response — flagged as open question in CONTEXT.md

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — all dependencies verified against installed package.json; only `@hookform/resolvers` is new and its version requirement is confirmed
- Architecture: HIGH — patterns derived directly from existing project code and Next.js App Router documentation
- Pitfalls: HIGH — most pitfalls derived from actual project code inspection (e.g., SiteLayout location, apiFetch client-only nature, page.tsx scaffold replacement)
- API shapes: LOW — backend not inspectable; TypeScript interfaces are best-effort from CONTEXT.md descriptions

**Research date:** 2026-03-06
**Valid until:** 2026-04-06 (stable stack — Next.js 16, Tailwind v4, react-hook-form v7 all stable releases)
