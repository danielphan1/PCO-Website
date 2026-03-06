# Requirements: PSI CHI OMEGA Website Frontend

**Defined:** 2026-03-05
**Core Value:** Active members can access their event schedule and leadership contacts, while admins can manage membership, rush info, and content — all without involving a developer.

## v1 Requirements

### Infrastructure

- [ ] **INFRA-01**: API client wrapper (`lib/api.ts`) with base URL from `NEXT_PUBLIC_API_BASE`, automatic `Authorization: Bearer` header injection, and clean error handling
- [ ] **INFRA-02**: Token refresh on 401 via singleton `refreshPromise` to prevent race condition when concurrent requests expire simultaneously
- [ ] **INFRA-03**: Auth state management via React Context (`AuthContext`) with user object, tokens, loading state, login/logout actions
- [ ] **INFRA-04**: `AuthGuard` client-side hook/component that redirects unauthenticated users to `/login` and non-admin users on admin routes to `/dashboard`
- [ ] **INFRA-05**: `proxy.ts` (Next.js 16 naming — NOT `middleware.ts`) with `auth-hint` cookie bridge for optimistic server-side redirects
- [x] **INFRA-06**: `.env.example` with `NEXT_PUBLIC_API_BASE=http://localhost:8000`
- [x] **INFRA-07**: Next.js App Router route groups: `(public)`, `(auth)`, `(member)`, `(admin)` established

### Design System

- [x] **THEME-01**: Brand tokens defined in `globals.css` `@theme` block: black (#000000) background, forest green (#228B22) accent, white (#FFFFFF) text
- [x] **THEME-02**: EB Garamond (body) + Cormorant Garamond (headings) via `next/font/google` with CSS variable registration for Tailwind
- [ ] **THEME-03**: `SiteLayout` component with responsive header (tracking/uppercase nav), footer, and mobile hamburger menu (no horizontal scroll)
- [ ] **THEME-04**: `ChromeCard` component with thin metallic gradient border and subtle glow on dark background
- [ ] **THEME-05**: `ChromeButton` with primary (forest green fill) and secondary (chrome outline) variants; hover sheen animation via CSS
- [ ] **THEME-06**: `SectionTitle` component using heading font (Cormorant Garamond)
- [ ] **THEME-07**: `Divider` component: thin chrome gradient line with small green dot accent
- [x] **THEME-08**: Toast/alert system via `sonner` with dark theme; success (green), error (red) variants
- [x] **THEME-09**: Optional: extremely subtle grain/noise overlay on black backgrounds (low opacity, CSS-only)

### Public Pages

- [ ] **PUB-01**: Home page (`/`) with hero section containing "Join Now" (→ `/join`) and "Rush Info" (→ `/rush`) CTAs visible above fold without scrolling
- [ ] **PUB-02**: Home page section previews for History, Philanthropy, Leadership, Contact — pulled via API; graceful placeholder if API returns empty
- [ ] **PUB-03**: `/join` interest form collecting name, email, phone, graduation year, and major fields
- [ ] **PUB-04**: `/join` client-side validation (react-hook-form + zod) with field-level error states
- [ ] **PUB-05**: `/join` submits to `POST /v1/interest`; shows success confirmation state on submit
- [ ] **PUB-06**: `/join` handles 409 duplicate email with friendly message ("Looks like you've already signed up!")
- [ ] **PUB-07**: `/rush` fetches `GET /v1/rush`; shows full rush details when published
- [ ] **PUB-08**: `/rush` shows "coming soon" fallback with CTA to `/join` when API returns `{status:"coming_soon"}`
- [ ] **PUB-09**: `/history` fetches `GET /v1/content/history`; renders formatted content
- [ ] **PUB-10**: `/philanthropy` fetches `GET /v1/content/philanthropy`; renders formatted content
- [ ] **PUB-11**: `/contact` fetches `GET /v1/content/contacts` + `GET /v1/content/leadership`; email addresses are `mailto:` links
- [ ] **PUB-12**: All public content pages use Next.js Server Components with ISR for SEO performance

### Authentication

- [ ] **AUTH-01**: `/login` page with email and password fields; note displayed that accounts are admin-created (no self-registration link)
- [ ] **AUTH-02**: Login submits to `POST /v1/auth/login`; on success stores access + refresh tokens in localStorage and redirects to `/dashboard`
- [ ] **AUTH-03**: Invalid credentials show generic error ("Invalid email or password") with no email enumeration
- [ ] **AUTH-04**: Logout clears localStorage tokens and redirects to `/login`
- [ ] **AUTH-05**: Protected routes (`/dashboard`, `/admin/*`) redirect unauthenticated users to `/login`
- [ ] **AUTH-06**: Admin routes (`/admin/*`) redirect authenticated non-admin users to `/dashboard` with "Access Denied" message

### Member Dashboard

- [ ] **MEMBER-01**: `/dashboard` displays profile snippet from `GET /v1/users/me` (name, role)
- [ ] **MEMBER-02**: `/dashboard` event PDFs list from `GET /v1/events` with "View" (open signed URL) and "Download" buttons per event
- [ ] **MEMBER-03**: `/dashboard` shows empty state ("No upcoming events posted yet") when event list is empty
- [ ] **MEMBER-04**: `/dashboard` T6 leadership contacts section showing name, role, and email (mailto links)

### Admin CMS

- [ ] **ADMIN-01**: `/admin` hub page with navigation to all admin sub-sections
- [ ] **ADMIN-02**: `/admin/events` lists uploaded PDFs (title, date) with delete button per entry
- [ ] **ADMIN-03**: `/admin/events` PDF upload form: file picker (PDF only, 10MB max client validation) + title + date; submits as multipart to `POST /v1/admin/events`
- [ ] **ADMIN-04**: `/admin/events` delete PDF shows confirmation dialog before calling `DELETE /v1/admin/events/{id}`
- [ ] **ADMIN-05**: `/admin/members` lists all members with name, email, role, and active/deactivated status; filter between active and deactivated
- [ ] **ADMIN-06**: `/admin/members` create member form: name, email, role; submits to `POST /v1/admin/users`; handles duplicate email with friendly error
- [ ] **ADMIN-07**: `/admin/members` role change dropdown per member; confirmation dialog before `PATCH /v1/admin/users/{id}/role`
- [ ] **ADMIN-08**: `/admin/members` deactivate/reactivate button per member; confirmation dialog before action
- [ ] **ADMIN-09**: `/admin/rush` form to edit rush content (dates, events, descriptions); submits to `PUT /v1/rush`
- [ ] **ADMIN-10**: `/admin/rush` visibility toggle (published / hidden); calls `PATCH /v1/rush/visibility`
- [ ] **ADMIN-11**: `/admin/content` forms to edit history, philanthropy, and contacts sections; each submits to `PUT /v1/content/{section}`

### Quality

- [ ] **QUAL-01**: All pages mobile-responsive with no horizontal scrolling; mobile-first layout breakpoints
- [ ] **QUAL-02**: SEO: unique `<title>` and `<meta name="description">` per page; OpenGraph tags on homepage
- [ ] **QUAL-03**: Accessibility: semantic HTML, aria labels on interactive elements, visible focus rings (subtle green)
- [ ] **QUAL-04**: README with `pnpm install`, `pnpm dev`, env var setup instructions

## v2 Requirements

### Auth

- **AUTH-V2-01**: Password reset / forgot password flow (backend endpoint not yet built)
- **AUTH-V2-02**: Secure HttpOnly cookie token storage instead of localStorage

### Member Features

- **MEMBER-V2-01**: Member profile pages with bios and photos
- **MEMBER-V2-02**: Event RSVP system (beyond PDF viewing)

### Admin Features

- **ADMIN-V2-01**: Upload progress indicator for PDF uploads
- **ADMIN-V2-02**: WYSIWYG rich text editor for content sections (currently plain text/textarea)

### Discoverability

- **DISC-V2-01**: Alumni directory with search
- **DISC-V2-02**: Instagram feed embed

### Platform

- **PLAT-V2-01**: Push notifications for new events
- **PLAT-V2-02**: Analytics dashboard (interest form conversion, site traffic)
- **PLAT-V2-03**: Dues payment integration (Venmo/Stripe)
- **PLAT-V2-04**: Chapter GPA tracker

## Out of Scope

| Feature | Reason |
|---------|---------|
| Self-registration | Security requirement — admin-only account creation |
| Password reset | Backend endpoint not built for v1 |
| OAuth / social login | Email/password sufficient for v1 |
| Dark mode toggle | Always-dark design — no toggle needed |
| Mobile app | Web-first; mobile-responsive web covers v1 |
| Real-time features (WebSockets) | Backend is REST-only; no WebSocket support |
| Social media embeds | v2 |
| GPA tracker | v2 |
| Dues payments | v2 |

## Traceability

Updated during roadmap creation: 2026-03-05

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1: Foundation | Pending |
| INFRA-02 | Phase 1: Foundation | Pending |
| INFRA-03 | Phase 1: Foundation | Pending |
| INFRA-04 | Phase 1: Foundation | Pending |
| INFRA-05 | Phase 1: Foundation | Pending |
| INFRA-06 | Phase 1: Foundation | Complete |
| INFRA-07 | Phase 1: Foundation | Complete |
| THEME-01 | Phase 1: Foundation | Complete |
| THEME-02 | Phase 1: Foundation | Complete |
| THEME-03 | Phase 1: Foundation | Pending |
| THEME-04 | Phase 1: Foundation | Pending |
| THEME-05 | Phase 1: Foundation | Pending |
| THEME-06 | Phase 1: Foundation | Pending |
| THEME-07 | Phase 1: Foundation | Pending |
| THEME-08 | Phase 1: Foundation | Complete |
| THEME-09 | Phase 1: Foundation | Complete |
| PUB-01 | Phase 2: Public Site | Pending |
| PUB-02 | Phase 2: Public Site | Pending |
| PUB-03 | Phase 2: Public Site | Pending |
| PUB-04 | Phase 2: Public Site | Pending |
| PUB-05 | Phase 2: Public Site | Pending |
| PUB-06 | Phase 2: Public Site | Pending |
| PUB-07 | Phase 2: Public Site | Pending |
| PUB-08 | Phase 2: Public Site | Pending |
| PUB-09 | Phase 2: Public Site | Pending |
| PUB-10 | Phase 2: Public Site | Pending |
| PUB-11 | Phase 2: Public Site | Pending |
| PUB-12 | Phase 2: Public Site | Pending |
| AUTH-01 | Phase 3: Authentication | Pending |
| AUTH-02 | Phase 3: Authentication | Pending |
| AUTH-03 | Phase 3: Authentication | Pending |
| AUTH-04 | Phase 3: Authentication | Pending |
| AUTH-05 | Phase 3: Authentication | Pending |
| AUTH-06 | Phase 3: Authentication | Pending |
| MEMBER-01 | Phase 4: Member Dashboard | Pending |
| MEMBER-02 | Phase 4: Member Dashboard | Pending |
| MEMBER-03 | Phase 4: Member Dashboard | Pending |
| MEMBER-04 | Phase 4: Member Dashboard | Pending |
| ADMIN-01 | Phase 5: Admin CMS | Pending |
| ADMIN-02 | Phase 5: Admin CMS | Pending |
| ADMIN-03 | Phase 5: Admin CMS | Pending |
| ADMIN-04 | Phase 5: Admin CMS | Pending |
| ADMIN-05 | Phase 5: Admin CMS | Pending |
| ADMIN-06 | Phase 5: Admin CMS | Pending |
| ADMIN-07 | Phase 5: Admin CMS | Pending |
| ADMIN-08 | Phase 5: Admin CMS | Pending |
| ADMIN-09 | Phase 5: Admin CMS | Pending |
| ADMIN-10 | Phase 5: Admin CMS | Pending |
| ADMIN-11 | Phase 5: Admin CMS | Pending |
| QUAL-01 | Phase 6: Quality + Polish | Pending |
| QUAL-02 | Phase 6: Quality + Polish | Pending |
| QUAL-03 | Phase 6: Quality + Polish | Pending |
| QUAL-04 | Phase 6: Quality + Polish | Pending |

**Coverage:**
- v1 requirements: 48 total
- Mapped to phases: 48
- Unmapped: 0

---
*Requirements defined: 2026-03-05*
*Last updated: 2026-03-05 — traceability updated after roadmap creation (6 phases)*
