# PSI CHI OMEGA — Website Frontend (MVP v1.0)

## What This Is

The public-facing and member-portal website for the San Diego chapter of PSI CHI OMEGA (PCO), a fraternity organization. Built on Next.js 16 App Router, it connects to a fully-operational FastAPI backend. The frontend serves three distinct audiences: prospective rushees (public), active members (protected dashboard), and the T6 admin team (management tools).

## Core Value

Active members can access their event schedule and leadership contacts, while admins can manage membership, rush info, and content — all without involving a developer.

## Requirements

### Validated

<!-- Backend API is complete and tested. These capabilities exist and are ready to consume. -->

- ✓ POST /v1/auth/login — JWT access + refresh token auth — existing
- ✓ POST /v1/auth/refresh — token rotation — existing
- ✓ GET /v1/users/me — authenticated user profile — existing
- ✓ GET /v1/content/history — org history content — existing
- ✓ GET /v1/content/philanthropy — philanthropy content — existing
- ✓ GET /v1/content/contacts — contact info — existing
- ✓ GET /v1/content/leadership — T6 leadership data — existing
- ✓ GET /v1/rush — rush info (may return {status:"coming_soon"}) — existing
- ✓ POST /v1/interest — interest form submission (409 on duplicate email) — existing
- ✓ GET /v1/events — signed PDF download URLs for members — existing
- ✓ GET /v1/admin/users — member list — existing
- ✓ POST /v1/admin/users — create member account — existing
- ✓ PATCH /v1/admin/users/{id}/role — role transfer — existing
- ✓ PATCH /v1/admin/users/{id}/deactivate — deactivate member — existing
- ✓ PATCH /v1/admin/users/{id}/reactivate — reactivate member — existing
- ✓ POST /v1/admin/events — PDF upload (multipart, PDF only, 10MB max) — existing
- ✓ DELETE /v1/admin/events/{id} — remove event PDF — existing
- ✓ PUT /v1/rush — update rush info — existing
- ✓ PATCH /v1/rush/visibility — toggle rush visibility — existing
- ✓ PUT /v1/content/{section} — edit history/philanthropy/contacts — existing
- ✓ Role-based access control (member, admin, officer roles) — existing
- ✓ Supabase Storage for PDF files with signed URLs — existing

### Active

<!-- Frontend MVP — everything below needs to be built -->

**Public Pages:**
- [ ] Home/landing page with hero, "Join Now" + "Rush Info" CTAs above fold, and section previews
- [ ] /join interest form (name, email, phone, year, major; 409 duplicate handling)
- [ ] /rush page with coming-soon fallback when rush is unpublished
- [ ] /history page pulling from API
- [ ] /philanthropy page pulling from API
- [ ] /contact page with contacts + leadership

**Auth:**
- [ ] /login page (no self-registration; note about admin account creation)
- [ ] JWT token storage via localStorage (MVP simplicity)
- [ ] Route protection: unauthenticated → /login; non-admin on /admin → /dashboard with "Access Denied"
- [ ] Token refresh on expiry

**Member Dashboard:**
- [ ] /dashboard profile snippet (name, role)
- [ ] Event PDFs list with view/download buttons; empty state
- [ ] T6 leadership contacts section on dashboard

**Admin:**
- [ ] /admin hub page
- [ ] /admin/events — upload PDF + list + delete with confirmation
- [ ] /admin/members — list (active/deactivated filter) + create + role change + deactivate/reactivate
- [ ] /admin/rush — edit rush content + toggle visibility
- [ ] /admin/content — edit history/philanthropy/contacts

**Theme & Components:**
- [ ] SiteLayout (header/footer, responsive nav, tracking/uppercase nav labels)
- [ ] ChromeCard (thin metallic gradient border, subtle glow)
- [ ] ChromeButton (primary forest green; secondary chrome outline; hover sheen)
- [ ] SectionTitle (editorial heading font)
- [ ] Divider (thin chrome line + green dot)
- [ ] Toast/Alert (success/error)
- [ ] Brand: Black bg (#000000), Forest Green (#228B22) CTAs/accents, White (#FFFFFF) text
- [ ] Typography: EB Garamond (body), one editorial heading font (Google Fonts)

**Quality & Polish:**
- [ ] Mobile-first responsive layout (no horizontal scroll)
- [ ] SEO: page titles, meta descriptions, OpenGraph tags
- [ ] Accessibility: semantic HTML, aria labels, focus rings (subtle green)
- [ ] .env.example with NEXT_PUBLIC_API_BASE
- [ ] README with pnpm install, pnpm dev, env var instructions

### Out of Scope

- Password reset / forgot password flow — v2 (backend endpoint not yet built)
- Member profile pages with bios and photos — v2
- Event RSVP system — v2
- Alumni directory — v2
- Push notifications — v2
- Analytics dashboard — v2
- Dark mode toggle — always dark, no toggle needed
- Social media feed embeds — v2
- Chapter GPA tracker — v2
- Dues payment integration — v2
- Mobile app — web-first
- OAuth / social login — email/password only for v1

## Context

- Monorepo: backend at `../pco_backend/`, frontend at `./` (pco_website)
- Backend fully tested (8 test files, UAT passed); frontend is create-next-app scaffold
- Stack: Next.js 16.1.6, React 19, TypeScript strict, Tailwind CSS v4, pnpm 10
- API base URL from `NEXT_PUBLIC_API_BASE` env var (default: http://localhost:8000)
- Backend auth: JWT access tokens (60min) + opaque refresh tokens (30 days)
- Roles: member, admin, president, vp, treasurer, secretary, historian (officer roles can see admin tools if role == "admin"; backend enforces this)
- Aesthetic direction: Chrome Hearts / "I AM MUSIC" (Playboi Carti) / Isoknock — dark, premium, metallic accents, forest green highlights; NOT neon cyberpunk or bubbly UI
- Chrome/liquid metal used ONLY as accents: thin gradient borders, button hover sheen, metallic dividers
- Optional: extremely subtle grain/noise overlay on black background

## Constraints

- **Tech Stack**: Next.js App Router (already scaffolded) — no migration to Pages Router
- **Package Manager**: pnpm (lockfile committed, workspace config present)
- **API**: All data from FastAPI backend at `NEXT_PUBLIC_API_BASE` — no direct DB access from frontend
- **Auth Storage**: localStorage for MVP (simplest working approach)
- **Fonts**: Google Fonts via `next/font` only (EB Garamond body + one editorial heading)
- **Tailwind**: v4 already configured — use it for all styling
- **PDF files**: Read-only on frontend (signed URLs from backend); upload via multipart form
- **Timeline**: 5 sprints × 2 weeks = ~10 weeks; 2–3 developers
- **Maintainability**: Future CS members will contribute — keep structure clear, avoid clever abstractions

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| localStorage for JWT | Simplest MVP auth storage; avoids HttpOnly cookie complexity | — Pending |
| Next.js App Router route groups | Clean separation of (public), (auth), (member), (admin) without URL segments | — Pending |
| No self-registration | Security requirement — only admin-created accounts | — Pending |
| Tailwind v4 (already installed) | Don't switch CSS frameworks mid-project | — Pending |
| API client wrapper | Centralize base URL + Authorization header + error handling | — Pending |
| Soft-delete for members | Deactivation preserves audit trail; backend enforces | — Pending |

---
*Last updated: 2026-03-05 after initialization*
