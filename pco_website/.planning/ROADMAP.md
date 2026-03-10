# Roadmap: PSI CHI OMEGA Website Frontend

## Overview

The frontend is built layer by layer, each phase unlocking the next. Phase 1 establishes the shared foundation — API client, auth infrastructure, and design system — that every subsequent page depends on. Phase 2 builds the public marketing site as Server Components with no auth dependency. Phase 3 delivers the login page and auth lifecycle, which gates Phase 4's member dashboard. Phase 5 adds the admin CMS — the most complex mutation-heavy work, built last when auth is fully validated. Phase 6 completes accessibility, SEO, and developer onboarding.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation** - API client, auth infrastructure, design system tokens and components (completed 2026-03-06)
- [ ] **Phase 2: Public Site** - All public marketing pages (/, /rush, /join, /history, /philanthropy, /contact) as Server Components
- [x] **Phase 3: Authentication** - Login page, JWT token lifecycle, route protection, AuthGuard (completed 2026-03-09)
- [x] **Phase 4: Member Dashboard** - Protected /dashboard with profile, event PDFs, and leadership contacts (completed 2026-03-10)
- [ ] **Phase 5: Admin CMS** - Full officer self-service: events, members, rush editor, content editor
- [ ] **Phase 6: Quality + Polish** - Accessibility, SEO, env setup, README, mobile audit

## Phase Details

### Phase 1: Foundation
**Goal**: The shared infrastructure that every page, component, and feature in the project depends on exists and is correct
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04, INFRA-05, INFRA-06, INFRA-07, THEME-01, THEME-02, THEME-03, THEME-04, THEME-05, THEME-06, THEME-07, THEME-08, THEME-09
**Success Criteria** (what must be TRUE):
  1. A developer can call `apiFetch()` from any component and receive properly typed data with the Authorization header automatically injected
  2. Visiting a protected route while logged out redirects to /login without a flash of protected content
  3. ChromeCard, ChromeButton, SectionTitle, and Divider components render correctly with the black/forest-green/white brand palette on a local dev page
  4. EB Garamond body text and Cormorant Garamond headings load via next/font with no layout shift
  5. SiteLayout header shows responsive navigation that collapses to a hamburger on mobile without horizontal scroll
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md — Scaffolding: install deps, route groups, globals.css @theme tokens, next/font fonts, .env files
- [ ] 01-02-PLAN.md — Auth + API infrastructure: types, cn(), auth helpers, apiFetch() singleton refresh, AuthContext, AuthGuard, proxy.ts
- [ ] 01-03-PLAN.md — Design system: ChromeCard, ChromeButton, SectionTitle, Divider, SiteLayout, /dev-preview page

### Phase 2: Public Site
**Goal**: Prospective rushees can learn about PCO, explore rush info, and submit an interest form — all rendered as fast, SEO-optimized server pages
**Depends on**: Phase 1
**Requirements**: PUB-01, PUB-02, PUB-03, PUB-04, PUB-05, PUB-06, PUB-07, PUB-08, PUB-09, PUB-10, PUB-11, PUB-12
**Success Criteria** (what must be TRUE):
  1. The homepage hero section shows "Join Now" and "Rush Info" CTAs above the fold without scrolling on a 375px mobile viewport
  2. Visiting /rush when rush is unpublished shows the coming-soon fallback with a link to /join — not an error
  3. Submitting /join with an email already in the system shows a friendly message ("Looks like you've already signed up!"), not a raw error
  4. /history, /philanthropy, and /contact pages render content fetched from the API at build time with ISR revalidation
  5. Page source for /history includes a `<title>` tag and `<meta name="description">` (confirming Server Component SSR)
**Plans**: 4 plans

Plans:
- [ ] 02-01-PLAN.md — Foundation wiring: SiteLayout into public layout, nav href updates, Phase 2 type definitions, bounce-gentle keyframe, @hookform/resolvers install
- [ ] 02-02-PLAN.md — Homepage: full-viewport hero with CTAs, long-scroll section previews (History, Philanthropy, Leadership, Contact) with ISR fetch
- [ ] 02-03-PLAN.md — /rush and /join: two-state rush page (Server Component), interest form with react-hook-form + zod + 409 handling (client component)
- [ ] 02-04-PLAN.md — /history, /philanthropy, /contact: Server Component ISR pages, parallel fetch on contact, mailto links; QA checkpoint

### Phase 3: Authentication
**Goal**: Members can log in, stay logged in across browser sessions, and be redirected correctly based on their role
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06
**Success Criteria** (what must be TRUE):
  1. A member can enter their email/password, click Login, and land on /dashboard with their session persisted in localStorage
  2. Entering wrong credentials shows "Invalid email or password" — no hint about whether the email exists
  3. Clicking Logout from any page clears the session and redirects to /login
  4. Navigating directly to /dashboard while logged out redirects to /login without showing any dashboard content
  5. A logged-in non-admin navigating to /admin/* is redirected to /dashboard with an "Access Denied" message visible
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md — Login page: FullPageSpinner component, LoginForm client component (ChromeCard layout, email/password, admin note, toast error)
- [ ] 03-02-PLAN.md — Auth lifecycle: AuthContext /v1/users/me hydration, AuthGuard spinner, SiteLayout conditional header, dashboard stub + access-denied toast

### Phase 4: Member Dashboard
**Goal**: Active members can view their event schedule and find leadership contacts without involving anyone else
**Depends on**: Phase 3
**Requirements**: MEMBER-01, MEMBER-02, MEMBER-03, MEMBER-04
**Success Criteria** (what must be TRUE):
  1. A logged-in member sees their name and role displayed on /dashboard immediately after login
  2. The event PDF list shows each event with working "View" (opens signed URL in new tab) and "Download" buttons
  3. When no events are posted, the dashboard shows an empty state message instead of a blank list
  4. The T6 leadership section shows each officer's name, role, and a clickable mailto email link
**Plans**: 1 plan

Plans:
- [ ] 04-01-PLAN.md — Types contract + ChromeButton target prop + full /dashboard implementation (profile, events, leadership)

### Phase 5: Admin CMS
**Goal**: Officers can manage event PDFs, member accounts, rush info, and site content without developer involvement
**Depends on**: Phase 4
**Requirements**: ADMIN-01, ADMIN-02, ADMIN-03, ADMIN-04, ADMIN-05, ADMIN-06, ADMIN-07, ADMIN-08, ADMIN-09, ADMIN-10, ADMIN-11
**Success Criteria** (what must be TRUE):
  1. An admin can upload a PDF event (with client-side PDF type + 10MB size validation) and see it appear in the events list immediately
  2. Deleting an event or deactivating a member requires a confirmation dialog before the destructive action fires
  3. An admin can create a new member account with name, email, and role — handling duplicate email with a friendly error
  4. The rush editor saves content changes and the visibility toggle correctly publishes or hides rush info (verifiable by checking /rush as a public visitor)
  5. All four admin sections (events, members, rush, content) are reachable from the /admin hub page
**Plans**: TBD

Plans:
- [ ] 05-01: Admin hub + events manager — /admin hub page, PDF upload form (multipart, PDF-only, 10MB validation), event list, delete with confirmation
- [ ] 05-02: Members manager — list with active/deactivated filter, create member form, role change dropdown with confirmation, deactivate/reactivate with confirmation
- [ ] 05-03: Rush editor + content editor — rush form + visibility toggle, content editor for history/philanthropy/contacts

### Phase 6: Quality + Polish
**Goal**: The site is accessible, discoverable, documented, and ready for handoff to future contributors
**Depends on**: Phase 5
**Requirements**: QUAL-01, QUAL-02, QUAL-03, QUAL-04
**Success Criteria** (what must be TRUE):
  1. Every page passes a mobile viewport check at 375px with no horizontal scrolling
  2. View-source on the homepage shows OpenGraph `og:title` and `og:description` meta tags
  3. All interactive elements (buttons, links, form fields) have visible focus rings using the green accent color when tabbed to via keyboard
  4. A new developer can clone the repo, copy `.env.example` to `.env.local`, run `pnpm install && pnpm dev`, and have a working local instance using only the README instructions
**Plans**: TBD

Plans:
- [ ] 06-01: SEO + OpenGraph — unique title/description per page, og tags on homepage, semantic HTML audit
- [ ] 06-02: Accessibility + mobile — aria labels on interactive elements, focus rings (green), skip-nav, mobile viewport smoke test across all pages
- [ ] 06-03: Developer onboarding — .env.example, README (pnpm install, pnpm dev, env var docs), final smoke test checklist

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 3/3 | Complete   | 2026-03-06 |
| 2. Public Site | 0/4 | Not started | - |
| 3. Authentication | 2/2 | Complete   | 2026-03-10 |
| 4. Member Dashboard | 1/1 | Complete   | 2026-03-10 |
| 5. Admin CMS | 0/3 | Not started | - |
| 6. Quality + Polish | 0/3 | Not started | - |
