# Phase 4: Member Dashboard - Context

**Gathered:** 2026-03-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the protected `/dashboard` page for authenticated members: a profile snippet (name, role), an event PDFs list with View button per event, an empty state when no events exist, and a T6 leadership contacts section (name, role, mailto email). No mutations — this phase is read-only, consuming three endpoints: GET /v1/users/me, GET /v1/events, GET /v1/content/leadership. Auth infrastructure is fully wired from Phase 3.

</domain>

<decisions>
## Implementation Decisions

### Dashboard Layout
- Single column, top-to-bottom: Profile snippet → Events section → Leadership section
- Sections separated by the Divider component (chrome line + green dot) above each section heading
- No sidebar, no card grid for the outer structure — mobile-first single column

### Profile Snippet
- Minimal inline text: name in heading font (Cormorant Garamond / SectionTitle), role in muted uppercase below
- No ChromeCard wrapper, no welcome greeting — just "BRIAN NGUYEN" and "Member" directly on the page
- Data sourced from AuthContext `user` object (already fetched on mount — no additional API call needed)

### Event PDFs Presentation
- Table/list rows (not ChromeCards) — compact, easy to scan multiple events
- Each row shows: event title + formatted date + one "VIEW" button
- View only — no separate Download button; browser's native PDF viewer provides download
- "View" opens the signed URL in a new tab (`target="_blank"`)
- Button style: ChromeButton secondary (chrome outline) per row

### Event Empty State
- When GET /v1/events returns an empty array: show "No upcoming events posted yet." in muted text in place of the list
- No illustration or CTA — just the message

### Signed URL Fetch Strategy
- Fetch GET /v1/events on page load (client-side useEffect, `apiFetch<Event[]>`)
- All signed URLs available immediately when user clicks View
- No on-demand re-fetch per click

### Loading States
- While events data is loading: 2-3 muted placeholder skeleton rows in the events section
- While leadership data is loading: 2-3 muted placeholder skeleton rows in the leadership section
- Profile renders immediately from AuthContext (no additional fetch delay)

### Error Handling
- If GET /v1/events fails: Sonner error toast ("Failed to load events. Try refreshing.") + empty section with error message
- If GET /v1/content/leadership fails: same pattern — Sonner error toast + empty section with error message
- Non-blocking — errors in one section don't affect the other

### Leadership Contacts Section
- Compact list rows matching the events row style
- Each row: Name | Role | email as green underlined mailto link
- API order — render in whatever order GET /v1/content/leadership returns (no frontend sorting)
- Email visible as plain text, styled forest green + underline, clickable as `mailto:`

### Claude's Discretion
- Exact skeleton row implementation (CSS animation, color)
- Row border/divider styling within events and leadership lists (thin chrome line between rows)
- Typography scale for section headings vs row content
- Exact padding and spacing values

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/(member)/layout.tsx`: SiteLayout + AuthGuard("member") already wired — Phase 4 only touches page.tsx
- `contexts/AuthContext.tsx`: `useAuth()` returns `user` (name, role) — profile snippet is zero-cost, no extra fetch
- `apiFetch<T>()`: use for GET /v1/events and GET /v1/content/leadership client-side
- `components/ui/ChromeButton`: secondary variant (chrome outline) for the "VIEW" button per event row
- `components/ui/SectionTitle`: Cormorant Garamond heading for "Events" and "Leadership" section headings
- `components/ui/Divider`: chrome line + green dot — use above each section heading
- Sonner toast (dark theme, success/error) — already configured globally; import `toast` from "sonner"

### Established Patterns
- `"use client"` directive required — page uses `useAuth()` and `useEffect` for data fetching
- `apiFetch<T>()` handles Authorization header + 401 refresh automatically
- Tailwind v4 via `@theme inline` in globals.css — use `bg-black`, `text-white`, `text-green`, `border-chrome`
- `cn()` utility in `lib/utils.ts` for conditional class merging
- No component library (shadcn not used) — all UI is custom Tailwind
- Error pattern: Sonner toast for fetch failures, established in Phase 3

### Integration Points
- `app/(member)/dashboard/page.tsx` — current placeholder; Phase 4 replaces it with full implementation
- AuthContext `user` object provides name + role — no new auth code needed
- `GET /v1/events` — returns array of event objects with signed PDF URLs; fetch on mount
- `GET /v1/content/leadership` — returns T6 officer list with name, role, email; fetch on mount
- Blocker resolved: fetch on page load (not on-demand) — Supabase signed URL TTL assumed 1+ hour

</code_context>

<specifics>
## Specific Ideas

- Events and leadership both use the same compact list row style (consistent visual language within the dashboard)
- The profile area should feel like an editorial header — large name in Cormorant Garamond, role in small tracked uppercase below, with breathing room before the first Divider
- Row separators within lists should be subtle thin lines (not heavy borders) — fits the chrome aesthetic

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 04-member-dashboard*
*Context gathered: 2026-03-09*
