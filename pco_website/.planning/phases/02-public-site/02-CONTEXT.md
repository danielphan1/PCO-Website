# Phase 2: Public Site - Context

**Gathered:** 2026-03-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Build all public-facing pages for prospective rushees: the homepage (long-scroll single page), /rush, /join, and standalone /history, /philanthropy, /contact routes. Pages are Server Components with ISR. No auth dependency. SiteLayout gets wired into app/(public)/layout.tsx in this phase.

</domain>

<decisions>
## Implementation Decisions

### Homepage Architecture
- Single long-scroll page: Hero → History → Philanthropy → Leadership → Contact — all sections on `/`
- Each section has an `id` anchor: `#history`, `#philanthropy`, `#leadership`, `#contact`
- Nav links for History/Philanthropy/Contact updated to `/#history`, `/#philanthropy`, `/#contact` (works from any page via hash navigation)
- Rush nav link stays `/rush` (separate page)
- Smooth scroll via CSS `scroll-behavior: smooth` on html — NO scroll snapping, free manual scroll
- Divider component (chrome line + green dot) between each section
- Standalone `/history`, `/philanthropy`, `/contact` routes still exist for direct URL access

### Hero Section
- Content: large `PSI CHI OMEGA` heading (Cormorant Garamond), "Alpha Chapter" subtitle, "Integrity   Perseverance   Eternal Brotherhood" values line, then two CTAs side by side
- CTAs: `[ JOIN NOW ]` (ChromeButton primary → /join) and `[ RUSH INFO ]` (ChromeButton secondary → /rush)
- Background: subtle chrome/metallic gradient — very faint radial or linear gradient from black to near-black with a slight silver tint (no color, no green glow in hero)
- Height: full viewport height (100vh minus header height) — hero fills the screen on load
- Scroll indicator: subtle animated chevron at the bottom center, gently pulsing/bouncing downward

### Rush Page (/rush)
- Two states driven by API response:
  1. **Published**: Header section (page title + short intro paragraph + "Sign Up" ChromeButton → /join) above a vertical timeline layout (date marker on left, event name/time/location/description on right)
  2. **Coming soon** (`{status:"coming_soon"}`): Centered block — title, "Rush season is coming soon. Sign up to stay in the loop." message, and a "Sign Up" ChromeButton → /join

### Interest Form (/join)
- Form fields: Name, Email, Phone, Graduation Year, Major — single column, stacked vertically (no grid)
- Validation: react-hook-form + zod; inline errors below each field as user moves past them (no summary block)
- Success state: form is replaced in-place with confirmation — "You're on our list! We'll reach out when rush begins." + "Back to Home" ChromeButton → /
- 409 duplicate email: inline error on the email field — "Looks like you've already signed up!"
- Submit button: ChromeButton primary, full width

### Home Section Previews — Leadership
- Leadership section on homepage shows T6 leadership cards: photo + name + role
- Email NOT shown on public homepage (email shown in member dashboard only)
- Cards arranged in a responsive grid (2-col on tablet, 3-col on desktop, 1-col on mobile)
- **Backend dependency**: Confirm whether `GET /v1/content/leadership` returns photo URLs before building — if not, fall back to name + role only

### Claude's Discretion
- Exact chrome gradient CSS values for the hero background (keep extremely subtle)
- Chevron scroll indicator implementation (CSS animation vs Framer Motion — keep CSS-only)
- Section padding/spacing values
- Typography scale for hero heading vs subtitle vs values line
- ISR revalidate interval for content pages (suggested: 3600s / 1 hour)
- Timeline connector styling (vertical line between events)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `components/ui/ChromeCard` — wrapper+inner div pattern, metallic border, hover glow; use for leadership cards and content sections
- `components/ui/ChromeButton` — accepts `href` prop (renders as `<a>`); primary (green) and secondary (chrome outline) variants; ready for all CTAs
- `components/ui/SectionTitle` — editorial heading font; use as section headings throughout homepage
- `components/ui/Divider` — chrome line + green dot; use between homepage sections
- `components/layout/SiteLayout` — full nav with Join/Login CTAs; hamburger mobile menu; needs nav href updates (`/history` → `/#history`, etc.) in this phase
- `lib/api.ts` — `apiFetch<T>()` for client components; Server Components should use `fetch()` directly with `{ next: { revalidate: N } }`
- `app/globals.css` — grain overlay already applied globally via `body::before`; `@keyframes sheen` defined

### Established Patterns
- No component library (shadcn not used) — all UI is custom Tailwind
- Tailwind v4 via `@theme inline` in globals.css — no tailwind.config.js; use `bg-black`, `text-green`, `border-chrome` etc.
- `cn()` utility in `lib/utils.ts` for conditional class merging
- Server Components: `fetch()` with `{ next: { revalidate: 3600 } }` for ISR
- TypeScript strict; `@/` alias maps to project root

### Integration Points
- `app/(public)/layout.tsx` — currently a pass-through; wire `SiteLayout` here in Phase 2
- `app/layout.tsx` — root layout; SiteLayout deliberately NOT added here (auth/member/admin routes don't use it)
- `types/api.ts` — needs new interfaces: `RushContent`, `ContentSection`, `LeadershipMember`, `ContactInfo`
- SiteLayout nav hrefs: update `/history`, `/philanthropy`, `/contact` to `/#history`, `/#philanthropy`, `/#contact`

</code_context>

<specifics>
## Specific Ideas

- Hero values line exact text: "Integrity   Perseverance   Eternal Brotherhood" (spaced with wide gaps, not bullet-separated)
- Hero subtitle: "Alpha Chapter" — not "San Diego Chapter"
- Long-scroll homepage inspired by premium brand landing pages — sections flow continuously, no jarring scroll snap
- Chrome gradient in hero: very faint — should add depth, not be noticeable as a color choice
- Leadership photo fallback: if no photo URL returned by backend, render initials in a circle (name-based) rather than a broken image

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 02-public-site*
*Context gathered: 2026-03-06*
