# Phase 1: Foundation - Context

**Gathered:** 2026-03-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Establish the shared infrastructure every page and feature depends on: API client with auth, auth context and token lifecycle, route group structure, and the full design system (brand tokens, fonts, reusable components). No user-facing pages are built in this phase — only the building blocks.

</domain>

<decisions>
## Implementation Decisions

### File & Project Structure
- Shared files (lib/, components/, contexts/, types/) live at root level, next to app/ — not nested inside app/
- Components organized by type: `components/ui/` for design system primitives (ChromeCard, ChromeButton, etc.), `components/layout/` for SiteLayout
- TypeScript `@/` path alias configured in tsconfig.json: `"@/*": ["./*"]`
- Route groups in app/: `(public)`, `(auth)`, `(member)`, `(admin)` — each with its own layout.tsx for auth isolation

### Navigation Design
- Logo: "PSI CHI OMEGA" in Cormorant Garamond, uppercase, letter-tracked — text only, no image/SVG asset needed
- Public nav links: Rush, History, Philanthropy, Contact — all uppercase, tracked (as specified in PROJECT.md)
- Header CTAs: "Join" (ChromeButton primary → /join) and "Login" (ChromeButton secondary → /login) both present in header
- Mobile menu: hamburger icon toggles a full-width dropdown panel below the header with nav links stacked vertically; no slide-in drawer

### Chrome Aesthetic — ChromeCard
- Metallic border: thin (1px) gradient from silver/white (top-left corner) fading to transparent (bottom-right corner)
- Glow effect: hover-only, subtle green (#228B22) box-shadow/glow — no permanent glow at rest
- Rounded corners, dark card background (slightly elevated from #000, e.g. #0a0a0a or #111)

### Chrome Aesthetic — ChromeButton
- Primary variant: forest green (#228B22) fill, white text
- Secondary variant: chrome outline (silver/white border), transparent background, white text
- Hover sheen: diagonal light sweep animation — a bright highlight stripe sweeps left-to-right diagonally on hover (CSS-only, `@keyframes` + overflow hidden)

### Grain Overlay
- Include in Phase 1 — pure CSS, no JS overhead
- Applied globally via `body::before` or `body::after` pseudo-element with SVG filter or noise background-image
- Opacity: ~3-5% — extremely subtle, must not obscure text or UI elements
- Covers all black background areas uniformly

### Claude's Discretion
- Exact border-radius values for ChromeCard and ChromeButton
- Specific box-shadow spread/blur values for the hover glow
- Duration/easing of the diagonal sheen animation
- Whether grain uses an SVG `feTurbulence` filter or a static base64 noise image
- Exact letter-spacing and font-weight values for nav labels

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `app/globals.css`: @import "tailwindcss" and @theme block already present — needs brand token replacement, not a new file
- `app/layout.tsx`: Root layout exists with next/font — Geist fonts need to be replaced with EB Garamond + Cormorant Garamond
- `next.config.ts`, `tsconfig.json`, `postcss.config.mjs`: All present and configured for Next.js 16 + Tailwind v4

### Established Patterns
- No existing components, hooks, or lib utilities — Phase 1 creates all of these from scratch
- No src/ directory — all project code goes at root level next to app/
- Tailwind v4 is configured via @tailwindcss/postcss (postcss.config.mjs), NOT via a tailwind.config.js file — brand tokens go in globals.css @theme block

### Integration Points
- `app/layout.tsx` is where SiteLayout wraps the app and fonts are registered
- Route groups will be created under `app/` — each group gets a layout.tsx for its auth boundary
- `proxy.ts` (Next.js 16 naming, NOT middleware.ts) goes at project root for the auth-hint cookie bridge

</code_context>

<specifics>
## Specific Ideas

- Aesthetic reference: Chrome Hearts / "I AM MUSIC" (Playboi Carti) / Isoknock — dark, premium, metallic accents. NOT neon cyberpunk or bubbly.
- Chrome/liquid metal used ONLY as accents: thin gradient borders, button hover sheen, metallic dividers. Not full chrome panels.
- Background is pure black (#000000), not dark gray
- Font pairing: EB Garamond for body (elegant, readable), Cormorant Garamond for headings (editorial, high contrast)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-foundation*
*Context gathered: 2026-03-05*
