# Phase 4: Member Dashboard - Research

**Researched:** 2026-03-09
**Domain:** Next.js App Router client component — data fetching with useEffect, skeleton loading states, signed URL handling, Tailwind v4 list row styling
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Dashboard Layout**
- Single column, top-to-bottom: Profile snippet → Events section → Leadership section
- Sections separated by the Divider component (chrome line + green dot) above each section heading
- No sidebar, no card grid for the outer structure — mobile-first single column

**Profile Snippet**
- Minimal inline text: name in heading font (Cormorant Garamond / SectionTitle), role in muted uppercase below
- No ChromeCard wrapper, no welcome greeting — just "BRIAN NGUYEN" and "Member" directly on the page
- Data sourced from AuthContext `user` object (already fetched on mount — no additional API call needed)

**Event PDFs Presentation**
- Table/list rows (not ChromeCards) — compact, easy to scan multiple events
- Each row shows: event title + formatted date + one "VIEW" button
- View only — no separate Download button; browser's native PDF viewer provides download
- "View" opens the signed URL in a new tab (`target="_blank"`)
- Button style: ChromeButton secondary (chrome outline) per row

**Event Empty State**
- When GET /v1/events returns an empty array: show "No upcoming events posted yet." in muted text in place of the list
- No illustration or CTA — just the message

**Signed URL Fetch Strategy**
- Fetch GET /v1/events on page load (client-side useEffect, `apiFetch<Event[]>`)
- All signed URLs available immediately when user clicks View
- No on-demand re-fetch per click

**Loading States**
- While events data is loading: 2-3 muted placeholder skeleton rows in the events section
- While leadership data is loading: 2-3 muted placeholder skeleton rows in the leadership section
- Profile renders immediately from AuthContext (no additional fetch delay)

**Error Handling**
- If GET /v1/events fails: Sonner error toast ("Failed to load events. Try refreshing.") + empty section with error message
- If GET /v1/content/leadership fails: same pattern — Sonner error toast + empty section with error message
- Non-blocking — errors in one section don't affect the other

**Leadership Contacts Section**
- Compact list rows matching the events row style
- Each row: Name | Role | email as green underlined mailto link
- API order — render in whatever order GET /v1/content/leadership returns (no frontend sorting)
- Email visible as plain text, styled forest green + underline, clickable as `mailto:`

### Claude's Discretion
- Exact skeleton row implementation (CSS animation, color)
- Row border/divider styling within events and leadership lists (thin chrome line between rows)
- Typography scale for section headings vs row content
- Exact padding and spacing values

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| MEMBER-01 | /dashboard displays profile snippet (name, role) | useAuth() returns user object with name + role — zero-cost, already fetched; SectionTitle + muted uppercase role text |
| MEMBER-02 | /dashboard event PDFs list from GET /v1/events with "View" (open signed URL) per event | apiFetch<Event[]> in useEffect; ChromeButton secondary with href={signedUrl} target="_blank"; new Event type needed in types/api.ts |
| MEMBER-03 | /dashboard shows empty state when event list is empty | Conditional render on events.length === 0 after loading completes; muted text message |
| MEMBER-04 | /dashboard T6 leadership contacts section showing name, role, and email (mailto links) | apiFetch<LeadershipContact[]> in separate useEffect; LeadershipContact type needs email field added to existing partial type |
</phase_requirements>

---

## Summary

Phase 4 is a single-file implementation phase. The entire deliverable is `app/(member)/dashboard/page.tsx` — everything else (layout, auth guard, API client, components) is already wired. The Phase 3 stub that currently lives at that path is replaced wholesale.

The dashboard has three independent data sources: `user` from `AuthContext` (synchronous after hydration, no fetch needed), `GET /v1/events` (async, fetched on mount), and `GET /v1/content/leadership` (async, fetched on mount). The two async fetches run independently so a failure in one does not block the other. Each section manages its own loading/error/data state via independent `useState` pairs.

The primary engineering decision for this phase is the skeleton row implementation. The CONTEXT.md gives Claude discretion over the exact animation and color. The project has `animate-spin` from Tailwind built-in and the `@keyframes sheen` animation defined in globals.css. A `pulse`-style skeleton (opacity cycling) fits the chrome aesthetic best and does not require a new keyframe — Tailwind v4 has `animate-pulse` built in.

**Primary recommendation:** Implement the entire dashboard in one `page.tsx` file using three inline sections (profile, events, leadership). Keep skeleton rows as inline JSX fragments (no extracted component) since they are used in only two places and have identical markup.

---

## Standard Stack

### Core (already installed — no new packages needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| next | 16.1.6 | App Router, useRouter, Link | Project foundation |
| react | 19.2.3 | useState, useEffect, client components | Project foundation |
| sonner | 2.0.7 | Error toast notifications | Already configured globally, dark theme |
| tailwindcss | v4 | @theme tokens, animate-pulse for skeletons | Project foundation |

### Supporting (project-local)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @/contexts/AuthContext | local | useAuth() — user.name, user.role | Profile snippet, zero fetch cost |
| @/lib/api (apiFetch) | local | GET /v1/events, GET /v1/content/leadership | Both async data fetches |
| @/components/ui/ChromeButton | local | secondary variant for VIEW button per event row | Event list action |
| @/components/ui/SectionTitle | local | "Events" and "Leadership" section headings | Section labels |
| @/components/ui/Divider | local | chrome line + green dot above each section heading | Section separators |
| @/types/api | local | Event type (new), LeadershipContact with email (needs update) | Type safety for API responses |

**No new packages required for Phase 4.**

**Installation:**
```bash
# Nothing to install — all dependencies exist
```

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Inline skeleton JSX | Extracted SkeletonRow component | Component extraction only worthwhile if 3+ usages; 2 usages here makes inline simpler |
| Parallel useEffect fetches | Promise.all in single useEffect | Parallel gives independent error states per section (required by CONTEXT.md); Promise.all couples them |
| animate-pulse for skeletons | Custom CSS animation | animate-pulse is Tailwind built-in, on-brand fade effect, zero setup |

---

## Architecture Patterns

### Recommended File Changes

```
app/
└── (member)/
    └── dashboard/
        └── page.tsx        ← REPLACE stub with full implementation (single file delivery)

types/
└── api.ts                  ← ADD Event interface + update LeadershipMember to include email
```

No new directories. No new components. No new layout files.

### Pattern 1: Independent Section State

**What:** Each async section (events, leadership) owns its own `useState` triple: data array, loading boolean, error boolean. These are declared at the top of the page component and fetched in separate `useEffect` calls.

**When to use:** Required by CONTEXT.md — errors in one section must not affect the other.

```typescript
// Source: project conventions (AuthContext, apiFetch patterns established Phase 1-3)
"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";
import type { Event, LeadershipContact } from "@/types/api";

export default function DashboardPage() {
  const { user } = useAuth();

  // Events section state
  const [events, setEvents] = useState<Event[]>([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [eventsError, setEventsError] = useState(false);

  // Leadership section state
  const [leaders, setLeaders] = useState<LeadershipContact[]>([]);
  const [leadersLoading, setLeadersLoading] = useState(true);
  const [leadersError, setLeadersError] = useState(false);

  useEffect(() => {
    apiFetch<Event[]>("/v1/events")
      .then(setEvents)
      .catch(() => {
        setEventsError(true);
        toast.error("Failed to load events. Try refreshing.");
      })
      .finally(() => setEventsLoading(false));
  }, []);

  useEffect(() => {
    apiFetch<LeadershipContact[]>("/v1/content/leadership")
      .then(setLeaders)
      .catch(() => {
        setLeadersError(true);
        toast.error("Failed to load leadership contacts. Try refreshing.");
      })
      .finally(() => setLeadersLoading(false));
  }, []);

  // ... render
}
```

### Pattern 2: Skeleton Rows

**What:** While loading is true, render 2-3 placeholder rows with the same height and layout as real rows. Use `animate-pulse` on a muted background bar.

**When to use:** Both events and leadership sections while their respective `loading` state is `true`.

```typescript
// Source: Tailwind v4 built-in animate-pulse + project @theme tokens
function SkeletonRow() {
  return (
    <div className="flex items-center justify-between py-4 border-b border-chrome/10">
      <div className="flex flex-col gap-2">
        <div className="h-4 w-48 bg-white/10 rounded animate-pulse" />
        <div className="h-3 w-24 bg-white/5 rounded animate-pulse" />
      </div>
      <div className="h-8 w-16 bg-white/10 rounded animate-pulse" />
    </div>
  );
}
```

**Note on discretion:** The exact widths (w-48, w-24) and opacity values (white/10, white/5) are Claude's discretion per CONTEXT.md. These values fit the chrome aesthetic — dim, not distracting.

### Pattern 3: Event Row

**What:** A horizontal row showing event title + formatted date on the left, ChromeButton secondary "VIEW" on the right. Rows separated by thin border-b.

**When to use:** For each item in `events` array.

```typescript
// Source: project conventions (ChromeButton.tsx — secondary variant with href)
function EventRow({ event }: { event: Event }) {
  const formattedDate = new Date(event.date).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });

  return (
    <div className="flex items-center justify-between py-4 border-b border-chrome/10 last:border-b-0">
      <div>
        <p className="font-body text-white text-sm">{event.title}</p>
        <p className="font-body text-white/40 text-xs tracking-wider mt-0.5">{formattedDate}</p>
      </div>
      <ChromeButton
        variant="secondary"
        href={event.signed_url}
        // ChromeButton renders <a> when href provided — target="_blank" via anchor
      >
        View
      </ChromeButton>
    </div>
  );
}
```

**Important:** ChromeButton's `href` prop renders an `<a>` tag. To open in a new tab, the component would need a `target` prop added, OR the implementation uses a plain `<a>` styled to match ChromeButton secondary. See Pitfall 2 below.

### Pattern 4: Leadership Row

**What:** A horizontal row showing name + role on the left, mailto email link on the right. Same row style as events for visual consistency.

```typescript
// Source: project @theme tokens — text-green for accent color
function LeaderRow({ leader }: { leader: LeadershipContact }) {
  return (
    <div className="flex items-center justify-between py-4 border-b border-chrome/10 last:border-b-0">
      <div>
        <p className="font-body text-white text-sm">{leader.name}</p>
        <p className="font-body text-white/40 text-xs tracking-wider uppercase mt-0.5">{leader.role}</p>
      </div>
      <a
        href={`mailto:${leader.email}`}
        className="font-body text-green underline text-sm hover:text-green/80 transition-colors"
      >
        {leader.email}
      </a>
    </div>
  );
}
```

### Pattern 5: Profile Snippet

**What:** Name in SectionTitle (large Cormorant Garamond), role in small muted uppercase below. No wrapper component, no fetch needed.

```typescript
// Source: components/ui/SectionTitle.tsx — font-heading, text-3xl, font-light
// Source: contexts/AuthContext.tsx — user.name, user.role
<div className="pt-8 pb-6">
  <SectionTitle as="h1">{user?.name?.toUpperCase()}</SectionTitle>
  <p className="font-body text-white/40 text-xs tracking-[0.2em] uppercase mt-2">
    {user?.role}
  </p>
</div>
```

**Key:** `user` may briefly be null if AuthContext hasn't hydrated yet, but `AuthGuard` in the layout ensures the page only renders when `loading=false` and `user` is set. Nullish access (`user?.name`) is a safety guard only.

### Anti-Patterns to Avoid

- **Fetching /v1/users/me inside dashboard/page.tsx:** AuthContext already does this on mount. Reading `user` from `useAuth()` is zero-cost. Adding a second fetch is redundant and wasteful.
- **Single useEffect for both fetches:** Coupling events and leadership fetches in one `useEffect` with `Promise.all` means one error aborts both. CONTEXT.md requires non-blocking independent sections.
- **ChromeCard wrapper around sections:** CONTEXT.md explicitly says no ChromeCard wrapper for the outer structure. Sections are directly on the black page background.
- **Sorting leadership array:** CONTEXT.md says render in API order. No `sort()` call.
- **Re-fetching signed URLs on each View click:** All signed URLs are fetched on page load per CONTEXT.md. The ChromeButton (or anchor) opens the already-fetched URL directly.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Auth token injection | Manual Authorization header | apiFetch<T> in lib/api.ts | Already handles Bearer injection + 401 refresh singleton |
| Loading animation | Custom CSS keyframes | Tailwind animate-pulse | Built-in, already available with Tailwind v4 — no globals.css addition needed |
| Toast notifications | Alert divs or inline error messages | sonner toast.error() | Already configured globally; correct dark theme |
| Auth state + user data | Separate fetch or useState | useAuth() from AuthContext | /v1/users/me already called on mount; user object populated |
| Date formatting | Manual string slicing | Date constructor + toLocaleDateString | Handles timezone edge cases correctly |

**Key insight:** Phase 4 has zero new infrastructure. The entire phase is composition of already-built pieces into one page file.

---

## Common Pitfalls

### Pitfall 1: ChromeButton Cannot Set target="_blank" for View Button

**What goes wrong:** ChromeButton renders `<a href={href}>` when `href` is passed, but has no `target` prop in its interface. Calling `window.open()` on click is not how anchors work semantically.

**Why it happens:** ChromeButton was designed for navigation links (Join, Login) that open in the same tab. The View requirement explicitly needs `target="_blank"`.

**How to avoid:** Two options — (A) add `target` and `rel` props to ChromeButton, or (B) use a plain `<a>` element styled to match the secondary ChromeButton appearance directly in the event row. Option A is cleaner and reusable; Option B avoids touching a shared component. Planner should pick one approach and commit to it.

**Warning signs:** Clicking View opens the PDF in the same tab, replacing the dashboard.

### Pitfall 2: LeadershipMember Type Missing email Field

**What goes wrong:** `types/api.ts` defines `LeadershipMember` with `id`, `name`, `role`, and optional `photo_url` — no `email` field. Phase 4 needs email for mailto links.

**Why it happens:** The existing `LeadershipMember` type was created for the public-facing `/contact` and `/leadership` pages where email may not be displayed. The `/v1/content/leadership` endpoint used by Phase 4 (member dashboard) presumably returns email for authenticated users.

**How to avoid:** Add a new `LeadershipContact` type to `types/api.ts` that extends or duplicates `LeadershipMember` with an `email: string` field. Do not modify `LeadershipMember` if public pages don't expose email — keep the types separate.

**Warning signs:** TypeScript error on `leader.email` access; the field renders as `undefined`.

### Pitfall 3: Event Type Does Not Exist Yet

**What goes wrong:** `types/api.ts` has no `Event` interface for the GET /v1/events response. Writing `apiFetch<Event[]>` without the type defined will either cause a TS error or use the global DOM `Event` type (a silent collision).

**Why it happens:** Phase 1-3 did not need events — the type was never created.

**How to avoid:** Define an `Event` interface in `types/api.ts` before or as part of the page implementation. Minimal shape:

```typescript
// types/api.ts addition
export interface Event {
  id: string;
  title: string;
  date: string;           // ISO date string from backend
  signed_url: string;     // Supabase signed URL for PDF
}
```

**Important caveat:** The exact field names from GET /v1/events are not confirmed — `signed_url` is the assumed field name. The backend owner should confirm. Using a wrong field name produces `undefined` silently (no TypeScript error on optional fields).

**Warning signs:** View button opens a broken URL or `undefined`; PDF does not load.

### Pitfall 4: user Can Be null Before AuthGuard Resolves

**What goes wrong:** Dashboard page renders before `user` is set, so `user.name` throws `Cannot read properties of null`.

**Why it happens:** AuthContext initializes with `user=null`. The `(member)/layout.tsx` `AuthGuard` prevents rendering children until `loading=false` and `user` is set — but during the brief loading window, the page component may technically render.

**How to avoid:** Use optional chaining (`user?.name`) for profile snippet rendering. AuthGuard handles the real protection; optional chaining is just defensive coding.

**Warning signs:** TypeError in console on hard refresh before auth resolves.

### Pitfall 5: useEffect Runs on Every Render If Dependencies Are Wrong

**What goes wrong:** If the useEffect dependency array is incorrect or omitted, the fetch runs on every render, causing infinite re-fetch loops.

**Why it happens:** Empty dependency array `[]` is correct for on-mount fetches. If `[]` is accidentally omitted, the effect runs after every state update (including the ones triggered by the fetch itself).

**How to avoid:** Both event and leadership useEffects must use `[]` as the dependency array — fetch on mount only, no re-fetch on data change.

**Warning signs:** Network tab shows continuous API requests; events/leadership state flickers.

---

## Code Examples

### types/api.ts Additions

```typescript
// Source: project types/api.ts — additions for Phase 4
// Add below existing types

export interface Event {
  id: string;
  title: string;
  date: string;           // ISO date string — format with Date constructor
  signed_url: string;     // Supabase signed URL — confirm exact field name with backend
}

// LeadershipContact is separate from LeadershipMember (public type has no email)
export interface LeadershipContact {
  id: string;
  name: string;
  role: string;
  email: string;          // Required for mailto links — confirm field name with backend
}
```

### Dashboard Page Structure (Full Skeleton)

```typescript
// Source: project conventions — all imports established in Phase 1-3
"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";
import { SectionTitle } from "@/components/ui/SectionTitle";
import { Divider } from "@/components/ui/Divider";
import { ChromeButton } from "@/components/ui/ChromeButton";
import type { Event, LeadershipContact } from "@/types/api";

// Skeleton row — used in events and leadership sections while loading
function SkeletonRow() {
  return (
    <div className="flex items-center justify-between py-4 border-b border-chrome/10">
      <div className="flex flex-col gap-2">
        <div className="h-4 w-48 bg-white/10 rounded animate-pulse" />
        <div className="h-3 w-24 bg-white/5 rounded animate-pulse" />
      </div>
      <div className="h-8 w-16 bg-white/10 rounded animate-pulse" />
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();

  const [events, setEvents] = useState<Event[]>([]);
  const [eventsLoading, setEventsLoading] = useState(true);
  const [eventsError, setEventsError] = useState(false);

  const [leaders, setLeaders] = useState<LeadershipContact[]>([]);
  const [leadersLoading, setLeadersLoading] = useState(true);
  const [leadersError, setLeadersError] = useState(false);

  useEffect(() => {
    apiFetch<Event[]>("/v1/events")
      .then(setEvents)
      .catch(() => {
        setEventsError(true);
        toast.error("Failed to load events. Try refreshing.");
      })
      .finally(() => setEventsLoading(false));
  }, []);

  useEffect(() => {
    apiFetch<LeadershipContact[]>("/v1/content/leadership")
      .then(setLeaders)
      .catch(() => {
        setLeadersError(true);
        toast.error("Failed to load leadership contacts. Try refreshing.");
      })
      .finally(() => setLeadersLoading(false));
  }, []);

  return (
    <main className="max-w-2xl mx-auto px-4 py-12">
      {/* Profile Snippet */}
      <div className="pb-8">
        <SectionTitle as="h1">{user?.name?.toUpperCase()}</SectionTitle>
        <p className="font-body text-white/40 text-xs tracking-[0.2em] uppercase mt-2">
          {user?.role}
        </p>
      </div>

      {/* Events Section */}
      <Divider className="mb-6" />
      <SectionTitle as="h2" className="text-xl mb-4">Events</SectionTitle>
      {eventsLoading ? (
        <>
          <SkeletonRow />
          <SkeletonRow />
          <SkeletonRow />
        </>
      ) : eventsError ? (
        <p className="font-body text-white/40 text-sm py-4">
          Could not load events. Please refresh the page.
        </p>
      ) : events.length === 0 ? (
        <p className="font-body text-white/40 text-sm py-4">
          No upcoming events posted yet.
        </p>
      ) : (
        <div>
          {events.map((event) => {
            const formattedDate = new Date(event.date).toLocaleDateString("en-US", {
              month: "long", day: "numeric", year: "numeric",
            });
            return (
              <div key={event.id} className="flex items-center justify-between py-4 border-b border-chrome/10 last:border-b-0">
                <div>
                  <p className="font-body text-white text-sm">{event.title}</p>
                  <p className="font-body text-white/40 text-xs tracking-wider mt-0.5">{formattedDate}</p>
                </div>
                {/* See Pitfall 1 — ChromeButton may need target prop added */}
                <a
                  href={event.signed_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="relative inline-flex items-center justify-center overflow-hidden px-4 py-2 rounded-sm text-xs font-medium tracking-widest uppercase border border-chrome text-white hover:border-chrome-light transition-colors duration-200"
                >
                  View
                </a>
              </div>
            );
          })}
        </div>
      )}

      {/* Leadership Section */}
      <Divider className="mt-10 mb-6" />
      <SectionTitle as="h2" className="text-xl mb-4">T6 Leadership</SectionTitle>
      {leadersLoading ? (
        <>
          <SkeletonRow />
          <SkeletonRow />
          <SkeletonRow />
        </>
      ) : leadersError ? (
        <p className="font-body text-white/40 text-sm py-4">
          Could not load leadership contacts. Please refresh the page.
        </p>
      ) : (
        <div>
          {leaders.map((leader) => (
            <div key={leader.id} className="flex items-center justify-between py-4 border-b border-chrome/10 last:border-b-0">
              <div>
                <p className="font-body text-white text-sm">{leader.name}</p>
                <p className="font-body text-white/40 text-xs tracking-wider uppercase mt-0.5">{leader.role}</p>
              </div>
              <a
                href={`mailto:${leader.email}`}
                className="font-body text-green underline text-sm hover:text-green/80 transition-colors"
              >
                {leader.email}
              </a>
            </div>
          ))}
        </div>
      )}
    </main>
  );
}
```

**Note on View button:** The code above uses a plain `<a>` styled inline to match ChromeButton secondary. The alternative is to add `target` and `rel` props to the `ChromeButton` component. Planner should decide which approach based on whether ChromeButton needs `target` reuse in later phases (Phase 5 admin may also need external links).

### access_denied Toast (Keep from Phase 3 Stub)

The current `page.tsx` already handles `?access_denied=1`. This logic MUST be preserved when the stub is replaced:

```typescript
// Source: app/(member)/dashboard/page.tsx (Phase 3 stub — preserve this logic)
import { useRouter, useSearchParams } from "next/navigation";

const router = useRouter();
const searchParams = useSearchParams();

useEffect(() => {
  if (searchParams.get("access_denied") === "1") {
    toast.error("Access denied. Admin privileges required.");
    router.replace("/dashboard");
  }
}, [searchParams, router]);
```

This useEffect must be added to the Phase 4 page component alongside the data-fetch effects.

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| fetch() with manual auth headers | apiFetch<T>() from lib/api | Phase 1 | All API calls use apiFetch — no manual headers in components |
| shimmer/skeleton libraries | Tailwind animate-pulse | Project convention | No external skeleton library; Tailwind built-in is sufficient |
| react-hook-form for all forms | Controlled state for simple forms | Phase 3 decision | Dashboard has no forms — not relevant here |

**Deprecated/outdated:**
- Any pattern fetching `/v1/users/me` inside a page component: AuthContext already does this. Reading from `useAuth()` is the established pattern.

---

## Open Questions

1. **GET /v1/events response field names**
   - What we know: The endpoint exists and returns event data with PDF access
   - What's unclear: Exact field names (`signed_url`? `pdf_url`? `url`?), exact date field name (`date`? `event_date`?), whether pagination exists
   - Recommendation: Confirm with backend owner before writing the Event type. A mismatch in field names produces `undefined` silently — TypeScript won't catch it on optional fields.

2. **GET /v1/content/leadership email field**
   - What we know: Existing `LeadershipMember` type has no email field; public-facing pages may not expose email
   - What's unclear: Whether the member-facing endpoint includes email, or whether a different endpoint/response shape is used for authenticated member access
   - Recommendation: Confirm with backend owner whether `/v1/content/leadership` returns `email` for authenticated members, or if a different endpoint serves member-facing leadership data.

3. **ChromeButton target prop**
   - What we know: ChromeButton renders `<a>` when href is passed; current interface has no `target` prop
   - What's unclear: Whether to add `target` to ChromeButton (touches shared component) or use a styled plain `<a>` inline (keeps component untouched)
   - Recommendation: Add `target` and `rel` props to ChromeButton. Phase 5 admin will also likely need external links. The component is simple enough that adding two optional props is low risk.

4. **Signed URL TTL (from STATE.md blocker)**
   - What we know: STATE.md flags "Confirm signed URL TTL with backend owner before dashboard build — affects whether to fetch on page load or on click"
   - What's decided: CONTEXT.md locks "fetch on page load" strategy with assumption of 1+ hour TTL
   - Status: The decision is locked. If TTL is shorter than a typical user session (~30 min), the View button may present expired URLs to users who stay on the page. The CONTEXT.md decision is accepted as-is for v1.

---

## Validation Architecture

> nyquist_validation is enabled in .planning/config.json.

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None detected — no jest.config, vitest.config, playwright.config, or __tests__ directory in project root |
| Config file | None — same gap as Phase 3 |
| Quick run command | N/A |
| Full suite command | N/A |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MEMBER-01 | /dashboard shows name and role from auth context | manual-only | N/A — no test framework | ❌ Wave 0 gap |
| MEMBER-02 | Event list renders with View links opening signed URLs in new tab | manual-only | N/A — browser behavior | ❌ Wave 0 gap |
| MEMBER-03 | Empty state message appears when events array is empty | manual-only | N/A — no test framework | ❌ Wave 0 gap |
| MEMBER-04 | Leadership section shows name, role, and clickable mailto links | manual-only | N/A — browser behavior | ❌ Wave 0 gap |

**Justification for manual-only:** No test framework is installed. Dashboard requirements involve browser rendering, authenticated API calls, and URL opening behavior — all require either Playwright E2E or React Testing Library + msw mocking. Installing a test framework is out of scope for this phase. Verification is via manual smoke testing against the running dev server with the backend running.

### Sampling Rate

- **Per task commit:** `pnpm build` (TypeScript type check catches type errors) + manual dev server check
- **Per wave merge:** Full manual walkthrough of all four MEMBER requirements
- **Phase gate:** All MEMBER-01 through MEMBER-04 pass manual verification before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `types/api.ts` — `Event` interface and `LeadershipContact` interface must be added before implementation (Wave 0 task)
- [ ] No automated test framework — manual verification only for this phase

*(No test files to create — manual verification is the protocol.)*

---

## Sources

### Primary (HIGH confidence)

- Project codebase (direct file read): `app/(member)/dashboard/page.tsx` (Phase 3 stub), `app/(member)/layout.tsx`, `contexts/AuthContext.tsx`, `lib/api.ts`, `lib/auth.ts`, `lib/utils.ts`
- Project codebase (direct file read): `components/ui/ChromeButton.tsx`, `Divider.tsx`, `SectionTitle.tsx`, `FullPageSpinner.tsx`, `ChromeCard.tsx`
- Project codebase (direct file read): `types/api.ts` — confirmed existing types and gaps
- Project codebase (direct file read): `app/globals.css` — confirmed @theme tokens (`text-green`, `border-chrome`, `border-chrome-light`)
- Project codebase (direct file read): `package.json` — confirmed no test framework, confirmed dependency versions
- `.planning/phases/04-member-dashboard/04-CONTEXT.md` — all locked decisions and discretion areas

### Secondary (MEDIUM confidence)

- `.planning/phases/03-authentication/03-RESEARCH.md` — established patterns for apiFetch, Sonner toast, Tailwind token usage
- `.planning/STATE.md` — accumulated decisions (localStorage for JWT, no component library, Tailwind v4 @theme inline)
- Tailwind v4 docs (via existing codebase evidence): `animate-pulse` available as built-in utility

### Tertiary (LOW confidence)

- GET /v1/events and GET /v1/content/leadership field names — inferred from context, not verified from backend spec or OpenAPI document
- Signed URL TTL — assumed 1+ hour per CONTEXT.md; not confirmed with backend

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — entire stack is existing project code verified by direct file read
- Architecture: HIGH — patterns derived from codebase inspection and established Phase 1-3 conventions
- API field names: LOW — `signed_url`, `date`, `email` are assumed; backend spec not available
- Pitfalls: HIGH — derived from direct inspection of existing code and known gaps in types/api.ts

**Research date:** 2026-03-09
**Valid until:** 2026-04-09 (stable — no external dependencies; only risk is backend API shape clarification)
