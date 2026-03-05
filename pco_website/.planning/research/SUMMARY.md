# Project Research Summary

**Project:** PSI CHI OMEGA Website Frontend
**Domain:** Fraternity org website — public marketing site + authenticated member portal + admin CMS
**Researched:** 2026-03-05
**Confidence:** HIGH

## Executive Summary

PSI CHI OMEGA is a Next.js 16 App Router frontend consuming a fully-built FastAPI REST backend. The product serves three distinct audiences: prospective rushees (public marketing site), active members (JWT-gated event schedule portal), and officers (admin CMS for content and member management). The backend is complete and ships a well-defined API contract, which means all feature and architecture decisions are grounded in real endpoints — not speculation. The primary work is building a premium custom UI that connects to an already-working backend.

The recommended approach is a layered build: establish the shared foundation first (design system tokens, auth utilities, API client), then build outward to public pages, then member-protected pages, then the admin CMS. This order is dictated by hard dependency chains: every page consumes the design system, every protected page requires auth to be working, and every admin mutation requires role-based route protection. The ChromeCard/ChromeButton design system must exist before any page component can be built without rework. Auth context and the `apiFetch` wrapper must exist before any authenticated page can be tested.

The key risks are all concentrated in Phase 1 and are well-understood: Next.js 16 renamed `middleware.ts` to `proxy.ts` (a silent breaking change that leaves routes unprotected), Tailwind v4 renamed several utility classes (causing silent visual regressions), `localStorage`-based auth is incompatible with server-side route protection in proxy (requiring a client-side `AuthGuard` pattern), and concurrent 401 responses will trigger a token refresh race condition if not guarded with a singleton refresh queue. All of these are low-recovery-cost if addressed in the foundation phase, and high-recovery-cost if discovered after pages are built.

## Key Findings

### Recommended Stack

The existing scaffold already has Next.js 16.1.6, React 19.2.3, TypeScript 5, and Tailwind v4 installed. No core framework changes are needed. The gaps to fill are: form handling (react-hook-form v7 + zod v3 + @hookform/resolvers), toast notifications (sonner v1), and Tailwind class utilities (clsx + tailwind-merge via a `cn()` helper). No component library (shadcn/ui, Radix, etc.) is needed or recommended — the PCO design aesthetic requires fully custom components and importing a component library would add bundle weight without matching the Chrome Hearts-inspired visual direction.

Auth storage is locked in at localStorage per PROJECT.md. This shapes the entire architecture: Server Components cannot access the token, so all protected pages must be Client Components. Route protection via proxy.ts is only a UX hint (reads an `auth-hint` cookie set at login), not a security boundary. Real security is enforced by FastAPI on every API call.

**Core technologies:**
- Next.js 16.1.6: App Router, route groups, SSR/ISR — already installed, do not migrate to Pages Router
- React 19.2.3: Concurrent mode, async components — already installed; react-hook-form v7.54+ required for React 19 compatibility
- TypeScript 5 strict: Type safety — already configured; `types/api.ts` mirrors FastAPI Pydantic schemas
- Tailwind v4: CSS-first config via `@theme` in `globals.css` — already installed; NO `tailwind.config.js`
- react-hook-form v7 + zod v3: Form state and schema validation — install; handles 409 field-level error injection
- sonner v1: Toast notifications — install; dark theme + richColors integrates with PCO aesthetic natively
- clsx + tailwind-merge: Conditional class merging via `cn()` utility — install; standard pattern

### Expected Features

The 21-story backlog in PROJECT.md is the ground truth. Every feature maps to a concrete API endpoint. The scope is well-defined.

**Must have (table stakes — P1):**
- Design system: ChromeCard, ChromeButton, SectionTitle, Divider — consumed by every page; build first
- SiteLayout with header/footer/nav — required by all public and member pages
- JWT auth: login, localStorage token storage, route protection, auto-refresh — prerequisite for all member/admin pages
- Public site: Home (hero + CTAs), /rush (with coming-soon fallback), /join (with 409 handling), /history, /philanthropy, /contact
- Member dashboard: profile snippet, event PDF list with signed-URL viewer/download, leadership contacts
- Admin CMS: hub page, events upload/delete, member management (create/role/deactivate), rush editor + visibility toggle, content editor

**Should have (P2 — competitive differentiators):**
- SEO meta tags and OpenGraph — credibility and discoverability
- Accessibility (aria labels, focus rings, skip-nav) — required for screen readers and keyboard users
- Subtle grain/noise overlay — premium visual texture, near-zero cost

**Defer (v2+):**
- Password reset flow — blocked until backend endpoint ships
- WYSIWYG content editor (TipTap) — plain textarea is sufficient for MVP
- Event RSVP system — requires API model expansion not in current backend
- Alumni directory, push notifications, Stripe dues — out of scope, significant scope increases
- Mobile app — web-first is correct until engagement data justifies native

**Critical feature notes:**
- Rush coming-soon state is the PRIMARY state between rush seasons, not a fallback. Design it first-class.
- 409 duplicate email on `/join` must show a friendly message ("Looks like you're already on our list!") — not a raw error. Treat 409 as a success variant (green/neutral toast).
- Signed PDF URLs expire (Supabase default ~1hr) — fetch fresh on user action, never cache in component state.
- PDF viewer: `<iframe src={signedUrl}>` is sufficient for desktop; always provide a prominent "Open PDF" / "Download" link as primary CTA since iOS Safari iframe PDF rendering is unreliable.

### Architecture Approach

The architecture cleanly separates four route groups — `(public)`, `(auth)`, `(member)`, `(admin)` — each with its own `layout.tsx` providing different chrome and protection levels. All API calls route through a single `lib/api.ts` wrapper that injects the Bearer token, handles 401 auto-refresh with a singleton refresh queue (preventing race conditions), and normalizes errors. Auth state lives in `lib/auth.ts` (plain localStorage helpers) and `contexts/AuthContext.tsx` (React Context layer). This separation allows `lib/api.ts` to call token helpers without React imports, which is required since it runs in both component and non-component contexts.

Public pages (`/history`, `/philanthropy`, `/contact`, `/rush`) should be Server Components with `next: { revalidate: 3600 }` for ISR — no auth token needed, SEO benefits, fast FCP. Protected pages (`/dashboard`, `/admin/*`) must be Client Components that read from AuthContext. The middleware convention in Next.js 16 is renamed to `proxy.ts` (from `middleware.ts`) — this file reads an `auth-hint` cookie for optimistic UX redirects only; it is not the security boundary.

**Major components (build order):**
1. `types/api.ts` — TypeScript interfaces mirroring FastAPI Pydantic schemas; zero dependencies; everything imports from here
2. `lib/auth.ts` — localStorage token get/set/clear helpers; no React dependency
3. `lib/api.ts` — fetch wrapper with Bearer injection, 401 auto-refresh with singleton refresh queue, error normalization
4. `contexts/AuthContext.tsx` — React Context providing `user`, `isLoading`, `login()`, `logout()`
5. `components/ui/` — Design system: ChromeCard, ChromeButton, SectionTitle, Divider; purely presentational; Server Components where possible
6. `components/layout/SiteLayout.tsx` — Header (Client, reads auth), Footer (Server, static)
7. `proxy.ts` — Route guard reading `auth-hint` cookie; set up once, rarely changes
8. `(public)` pages — Server Components with server-side fetch
9. `(auth)/login` — Client Component; required before any protected page can be tested
10. `(member)/dashboard` — Client Component; core member value
11. `(admin)/*` pages — Client Components with role guard in layout

### Critical Pitfalls

1. **`proxy.ts` vs `middleware.ts` rename** — Next.js 16 renamed `middleware.ts` to `proxy.ts` and the export from `middleware()` to `proxy()`. The old file is silently ignored — no error, but zero protection. Verify by visiting a protected route while logged out. Address in Phase 1 before building any protected routes.

2. **Token refresh race condition** — When multiple concurrent requests receive 401, all attempt `POST /v1/auth/refresh` simultaneously. FastAPI uses token rotation; only the first refresh succeeds; all others receive 401, logging the user out mid-session. Prevention: implement a singleton `refreshPromise` in `lib/api.ts` that shares the in-flight refresh across all waiting callers. Must be in place before any data-fetching pages are built.

3. **Tailwind v4 utility class renames** — v4 renamed `shadow` → `shadow-sm`, `shadow-sm` → `shadow-xs`, `outline-none` → `outline-hidden`, `ring` (3px) → `ring-3`, `border` (now defaults to `currentColor` not gray). Silent visual regressions — no compiler errors. Establish v4 class conventions in the design system phase before building any components. Document the mapping in a team reference.

4. **`"use client"` propagation destroys Server Component benefits** — Placing `"use client"` on a layout or high-level wrapper makes every component it imports a Client Component. The entire subtree loses server rendering. Mitigation: push `"use client"` as deep as possible; extract interactive leaf components (`NavMobileToggle`, `Toast`) into separate files; use the "children as slot" pattern to pass Server Component content into Client Component wrappers.

5. **Multipart upload: never set `Content-Type` manually** — When sending `FormData` to `POST /v1/admin/events`, manually setting `Content-Type: multipart/form-data` omits the required `boundary` parameter. FastAPI returns 422. Solution: omit the header entirely; the browser sets it correctly with the boundary. Always validate file type and size client-side before sending (PDF only, 10MB max).

## Implications for Roadmap

Based on the dependency graph in the research, the architecture's build order, and pitfall phase mapping, the following phase structure is recommended:

### Phase 1: Foundation (Design System + Auth + API Client)

**Rationale:** Every other phase depends on this. The design system is consumed by every page component. Auth context and the API client are required by every protected page and form. Getting the Tailwind v4 token setup wrong here causes rework in every subsequent component. Getting auth wrong here breaks every protected page. All of the highest-severity pitfalls must be addressed here.

**Delivers:** `types/api.ts`, `lib/auth.ts`, `lib/api.ts` with singleton refresh queue, `contexts/AuthContext.tsx`, `proxy.ts` (not `middleware.ts`), `components/ui/` design system (ChromeCard, ChromeButton, SectionTitle, Divider), Tailwind v4 `@theme` token setup with brand colors and fonts, `cn()` utility, sonner Toaster in root layout.

**Addresses:** Design system (ChromeCard, ChromeButton), authentication infrastructure

**Avoids:** proxy.ts rename pitfall, token refresh race condition, Tailwind v4 class renames, `tailwind.config.js` anti-pattern, next/font + Tailwind v4 integration pitfall, hydration errors from auth state

### Phase 2: Public Site (Marketing Pages + Login)

**Rationale:** Public pages are Server Components with no auth dependency — they can be built and deployed independently once the design system exists. Login must be built here because it is required to test any protected page in Phase 3. Rush and Join are the highest-traffic public pages and establish the recruitee conversion funnel.

**Delivers:** `(public)/` route group — Home, /rush (with coming-soon fallback designed as primary state), /join (with 409 duplicate-email handling), /history, /philanthropy, /contact. `(auth)/login` with LoginForm. SiteLayout + Header + Footer. SEO meta tags. Mobile-responsive layout.

**Addresses:** Public table stakes, CTA funnel, coming-soon rush state, 409 UX, interest form, mobile-first responsive layout

**Avoids:** `"use client"` propagation in SiteLayout (extract NavMobileToggle as leaf), hydration errors in Header auth state

### Phase 3: Member Portal (Dashboard + Protected Routes)

**Rationale:** Login is working from Phase 2. Auth guard pattern is established from Phase 1. Dashboard delivers the core member value proposition: viewing the weekly event PDF schedule. Token refresh behavior can now be fully tested with real protected API calls.

**Delivers:** `(member)/dashboard` — profile snippet (name + role badge), event PDF list with signed-URL iframe viewer and download link, empty state copy, leadership contacts section. Route protection via `(member)/layout.tsx` with AuthGuard. iOS Safari fallback: "Open PDF" link as primary CTA alongside iframe.

**Addresses:** Member table stakes (login, profile, events, contacts), token auto-refresh, route protection, PDF viewer/download, signed URL freshness (fetch on page load, not cached)

**Avoids:** Signed URL expiry trap (fetch list fresh on each page load), PDF download opening in same tab (use `target="_blank"`)

### Phase 4: Admin CMS (Officer Self-Service)

**Rationale:** Admin pages are the most complex (most mutations, most forms, most confirmation dialogs) and have the hardest dependency: they require auth to work (Phase 1) AND the member portal to be stable (Phase 3 validates auth end-to-end). Admin role guard pattern extends directly from the member AuthGuard. Content editor sections are independent and can be built/shipped in any order.

**Delivers:** `(admin)/` route group — admin hub page, events manager (PDF upload with multipart FormData + delete with confirmation modal), members manager (list with active/deactivated filter, create modal, role assignment, deactivate/reactivate), rush editor (content form + visibility toggle with optimistic UI), content editor (history, philanthropy, contacts per-section save). Admin role guard in `(admin)/layout.tsx`.

**Addresses:** All admin P1 features, role-based route protection, admin access control enforcement, multipart upload with correct FormData handling

**Avoids:** Multipart Content-Type manual-set pitfall, admin role check only in proxy (must be in layout), confirmation dialogs for destructive actions

### Phase 5: Polish + Quality

**Rationale:** Polish and quality items are independent of feature completion but add significant perceived quality and long-term maintainability. Accessibility and SEO can be validated only after pages are structurally complete.

**Delivers:** Accessibility audit (aria labels, focus rings, skip-nav, `outline-hidden` per Tailwind v4), OpenGraph meta tags, subtle grain/noise overlay, `.env.example`, README, "looks done but isn't" checklist verification (route protection smoke test, token refresh simulation, PDF upload edge cases, 409 interest form, mobile viewport test).

**Addresses:** P2 features, accessibility, SEO discoverability, developer onboarding

### Phase Ordering Rationale

- Foundation before everything: `types/api.ts` → `lib/auth.ts` → `lib/api.ts` → `AuthContext` is a hard dependency chain. No page can be built or tested without it.
- Design system before pages: ChromeCard and ChromeButton are consumed by every page. Building them first eliminates rework when visual language is established.
- Public before protected: Public pages have no auth dependency, deliver recruiter-facing value immediately, and allow login to be the last public-page item — which bridges directly into protected page testing.
- Member before admin: Dashboard validates the full auth lifecycle (login → token use → 401 → refresh → retry) in a low-mutation context before admin adds complex mutations.
- Polish last: Quality items are additive and do not block feature delivery, but a final audit pass is more efficient than piecemeal quality fixes throughout.

### Research Flags

Phases with standard, well-documented patterns (research-phase can be skipped):
- **Phase 1 (Foundation):** All patterns are fully specified in research — exact code for `lib/api.ts`, `lib/auth.ts`, `AuthContext`, `proxy.ts`, and Tailwind v4 `@theme` setup are documented in detail. No additional research needed.
- **Phase 2 (Public Site):** Server Component + ISR fetch pattern is standard Next.js 16. Interest form 409 handling and rush coming-soon patterns are specified. No additional research needed.
- **Phase 3 (Member Portal):** Dashboard auth pattern and PDF viewer pattern are fully specified. Signed URL behavior documented. No additional research needed.

Phases that may benefit from targeted research-phase during planning:
- **Phase 4 (Admin CMS):** The rich-text content editor (even as a plain textarea) may benefit from research into how `\n` → `<br>` rendering should be handled in React — specifically whether to use `whitespace-pre-wrap` CSS or explicit conversion. Minor, but worth a targeted lookup before building the content editor. PDF upload multipart pattern is fully documented.
- **Phase 5 (Accessibility):** If WCAG compliance becomes a stated requirement, a research-phase on ARIA patterns for the specific admin modal and confirmation dialog components would be valuable. For MVP accessibility (focus rings, aria labels, skip nav), the patterns are standard and need no research.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All decisions grounded in existing package.json, PROJECT.md explicit choices, and official Next.js 16.1.6 docs. Versions confirmed against React 19 compatibility matrix. |
| Features | HIGH | Feature list derived directly from the PROJECT.md 21-story backlog and the complete API contract. Every feature maps to a specific endpoint. Domain conventions (interest form patterns, Greek org website norms) are MEDIUM but the backlog is the authoritative source. |
| Architecture | HIGH | Core patterns (route groups, Server vs Client component split, auth context, proxy.ts) verified against official Next.js 16.1.6 docs. Build order derived from explicit dependency analysis. |
| Pitfalls | HIGH | All 9 critical pitfalls are verified against official docs (Next.js 16, Tailwind v4, React 19 release blog, FastAPI source). The `proxy.ts` rename and Tailwind v4 class renames are confirmed breaking changes. |

**Overall confidence:** HIGH

### Gaps to Address

- **Signed URL TTL:** Supabase default signed URL TTL varies by configuration (60s to 1hr). The exact backend configuration is not confirmed. Recommendation: fetch URLs on demand (click action), not on page load, to be safe regardless of TTL. Validate with backend owner before Phase 3.

- **`next/font` variable naming convention:** The exact CSS variable names emitted by `next/font/google` when using the `variable` option depend on the font name (e.g., `--font-eb-garamond`). The `@theme` mapping must use the exact variable name Next.js generates. Validate in Phase 1 by inspecting the `<html>` element in devtools.

- **Rush content fields:** The rush editor content schema (which fields `PUT /v1/rush` accepts beyond a plain text/markdown body) should be confirmed against the backend API spec before building the rush editor form in Phase 4.

- **Proxy.ts in Next.js 16:** The ARCHITECTURE.md notes the rename from `middleware.ts` to `proxy.ts`. The existing scaffold may still have `middleware.ts`. Confirm and migrate in Phase 1 using the codemod: `npx @next/codemod@canary middleware-to-proxy .`

## Sources

### Primary (HIGH confidence)

- `.planning/PROJECT.md` — Explicit technology decisions, full API contract, 21-story backlog
- `.planning/codebase/ARCHITECTURE.md`, `CONCERNS.md` — Existing codebase state
- `pco_website/package.json` — Confirmed installed versions
- Next.js 16.1.6 Official Docs — Route Groups, Authentication Guide, Server and Client Components, Proxy (formerly Middleware), Font Module, Fetching Data
- Tailwind CSS v4 Upgrade Guide — Class renames, `@theme` configuration, `@utility` blocks
- React 19 release blog — TypeScript breaking changes, concurrent mode compatibility

### Secondary (MEDIUM confidence)

- Domain knowledge: Greek org website conventions (PSI chapters, IFC-affiliated fraternities, OmegaFi/GreekTrack feature sets) — informed feature prioritization and anti-feature identification
- Supabase Storage signed URL behavior — expiry patterns derived from documented behavior; exact TTL configuration is project-specific
- iOS Safari iframe PDF rendering limitation — well-established WebKit behavior, widely documented

### Tertiary (LOW confidence)

- Interest form UX patterns (409 copy, field conventions) — established lead-capture form conventions; copy choices are subjective
- Font pairing recommendation (Cormorant Garamond / Playfair Display) — aesthetic judgment based on Chrome Hearts / editorial design direction in PROJECT.md

---
*Research completed: 2026-03-05*
*Ready for roadmap: yes*
