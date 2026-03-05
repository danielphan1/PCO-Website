# Feature Research

**Domain:** Fraternity/org website with public marketing site + authenticated member portal + admin CMS
**Researched:** 2026-03-05
**Confidence:** HIGH (grounded in fully-defined API contract, 21-story backlog, and established org-website patterns)

---

## Feature Landscape

### Table Stakes (Users Expect These)

Features each audience assumes exists. Missing these makes the product feel broken or untrustworthy.

#### Public / Rushee Audience

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Hero section with clear CTA | First thing a rushee sees; "Join Now" and "Rush Info" above the fold signal the org is active and welcoming | LOW | Two CTAs: `/join` (interest form) and `/rush` (rush schedule) |
| Rush schedule / info page | Rushees visit solely to know when/where to rush; without this the site has no conversion value | LOW | Must handle coming-soon state gracefully when `{status:"coming_soon"}` returned by API |
| Coming-soon / unpublished fallback | Rush timing is deliberate — early or off-season publication harms recruitment strategy | LOW | Toggle via `/admin/rush` visibility; UI shows placeholder copy instead of blank page |
| Interest / "rush" form | Standard expectation on any Greek org site; replaces emailing a random member | MEDIUM | Fields: name, email, phone, year, major. 409 duplicate email must show friendly message, not a raw error |
| Org history / about page | Establishes legitimacy and chapter identity for prospective members | LOW | Driven by API `GET /v1/content/history`; content editable by admin |
| Philanthropy / values page | Rushees evaluate organizations partly on community service track record | LOW | Driven by `GET /v1/content/philanthropy` |
| Contact / leadership page | "Who do I reach out to?" is a primary visitor question | LOW | Aggregates `GET /v1/content/contacts` + `GET /v1/content/leadership` |
| Mobile-responsive layout | Rushees are on phones; a desktop-only site loses credibility instantly | MEDIUM | Mobile-first Tailwind, no horizontal scroll |
| Semantic HTML + accessible navigation | Screen readers, keyboard users, and Google indexing all require it | LOW | Focus rings, aria-labels, skip-nav |

#### Active Members

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Authenticated login | Members need a private space; no login = no portal | LOW | Email + password, JWT, no self-registration |
| Profile identity snippet | Members expect to see their own name and role upon login | LOW | `GET /v1/users/me` → display name + role badge |
| Event schedule / PDFs list | Primary reason members log in — to see weekly schedules, meeting agendas | LOW | `GET /v1/events` returns signed URLs; empty-state copy required |
| In-browser PDF viewer | Downloading to view is friction; members expect tap-to-view | MEDIUM | Embed with `<iframe>` or browser native PDF rendering via signed URL |
| PDF download button | Members may want offline copies for personal calendars | LOW | Direct link to signed URL with `download` attribute or target blank |
| Leadership contacts on dashboard | Members look up officer contacts regularly; shouldn't require navigating away | LOW | Reuse `GET /v1/content/leadership` data on dashboard |
| Token auto-refresh / session persistence | Members expect to stay logged in across tab closes; expiry surprises are confusing | MEDIUM | localStorage refresh token + silent refresh on 401 |
| Route protection / redirect on auth | Accessing `/dashboard` without login should redirect cleanly to `/login` | LOW | Next.js middleware or client-side guard |

#### Admin Officers

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Member roster management | Officers manage active membership without dev involvement | MEDIUM | List with active/deactivated filter, create, deactivate/reactivate |
| Role assignment (T6 transfer) | Officer transitions happen every semester; must be self-service | LOW | `PATCH /admin/users/{id}/role` — dropdown or modal, confirmation step |
| PDF event upload | Officers post schedules as PDFs (Google Drive → upload pattern is familiar) | MEDIUM | Multipart form, PDF-only validation, 10MB max, error on type mismatch |
| PDF event deletion with confirmation | Accidentally deleting wrong week's schedule is costly; confirmation prevents it | LOW | Modal confirm dialog before `DELETE /admin/events/{id}` |
| Rush content editor | Rush info changes every semester; officers expect a form they can fill out | MEDIUM | Textarea/rich fields for `PUT /v1/rush`; save + preview flow |
| Rush visibility toggle | Officers need to "publish" rush info at the right time without developer help | LOW | Toggle switch wired to `PATCH /v1/rush/visibility`; status clearly labeled |
| Content editor (history, philanthropy, contacts) | Chapter copy changes over time; admins expect to own their words | MEDIUM | `PUT /v1/content/{section}` — inline edit or modal editor per section |
| Access control enforcement | Non-admin members must be blocked from admin URLs; security expectation | LOW | Redirect to `/dashboard` with "Access Denied" toast for non-admin |
| Admin hub / landing page | Officers need a clear list of what they can manage; random URL guessing is not UX | LOW | Single `/admin` page with cards linking to each sub-section |

---

### Differentiators (Competitive Advantage)

Features that elevate PCO's site above the typical static Squarespace or outdated Wix fraternity pages.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Premium dark aesthetic (Chrome Hearts / "I AM MUSIC") | Signals cultural identity and chapter taste; recruits the right demographic | MEDIUM | Black bg, forest green accents, EB Garamond body, metallic dividers — consistent across all pages |
| ChromeCard / ChromeButton design system | Unified visual language makes the site feel intentional, not assembled from components | MEDIUM | Thin metallic gradient border + subtle glow; reused everywhere |
| Coming-soon rush page (no blank/error state) | Rushees who visit off-season get a teaser, not a 404 or broken page — keeps interest high | LOW | Placeholder copy "Rush info coming soon — submit your interest now" with form CTA |
| 409 duplicate email UX on interest form | Friendly handling ("Looks like you're already on our list!") instead of raw error keeps engagement | LOW | Check response status before surfacing message |
| Admin content editing without developers | Officers can update history, philanthropy copy, and contacts without filing a ticket | MEDIUM | Unlocks operational independence — differentiates from static-site competitors |
| Signed PDF URLs (no public S3 bucket) | Event schedules stay private to members — security is a differentiator vs Google Drive links in group chats | MEDIUM | Backend handles Supabase signed URLs; frontend just renders them |
| Role hierarchy badge on profile | Members see "President", "Treasurer", etc. on their profile — signals chapter structure is real and organized | LOW | Cosmetic but meaningful for community feel |
| Subtle grain/noise overlay on black background | Depth and texture; elevates from flat-black to premium feel at near-zero cost | LOW | CSS `background-image` noise SVG or canvas; optional per PROJECT.md |

---

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem desirable but create disproportionate complexity or maintenance burden for MVP.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Self-registration / sign-up flow | Visitors assume they can create accounts | Security requirement — chapter controls membership; open sign-up means anyone joins | Admin-created accounts only; `/login` page notes "Contact your chapter president to get access" |
| Password reset / forgot password | Users expect it on every login form | Backend endpoint not yet built (v2 scope); building frontend without backend is dead code | Note on login page: "Contact admin to reset password" — honest, temporary |
| Real-time notifications / push | "Notify me when rush is posted" is a natural ask | Service workers + push API + backend webhook infrastructure is significant; overkill for MVP | Interest form confirmation email is sufficient (handled backend-side) |
| RSVP / attendance tracking | Officers want to know who's coming | Requires event model expansion, member-to-event join table, notification logic — none in current API | PDF schedules + group chat; v2 feature |
| Social media feed embeds (Instagram, Twitter) | Makes site feel "alive" | Third-party API rate limits, iframe breakage, privacy consent requirements, maintenance overhead | Static philanthropy/history content updated by admin serves same "proof of activity" purpose |
| Rich text / WYSIWYG editor for content | Officers want bold, bullet points in history text | WYSIWYG editors (Quill, TipTap) add bundle size + output HTML that must be sanitized + rendered safely | Plain textarea with `\n` → `<br>` rendering is sufficient for MVP; upgrade to TipTap in v2 |
| Alumni directory | Alumni engagement is real | Requires separate auth tier, profile model, opt-in/out privacy management | Out of scope; separate v2 initiative |
| Dues payment integration (Stripe) | Money collection is a real officer need | PCI compliance, Stripe account setup, webhook handling, reconciliation — far exceeds MVP scope | External dues platform (Splitwise, Venmo, chapter management app) |
| Dark mode toggle | Some users prefer light mode | Product aesthetic is intentionally always-dark; a toggle undermines the design direction | No toggle — always dark per PROJECT.md |
| Member profile pages with bios/photos | Roster feels more personal | Requires photo upload (storage, resize, moderation), profile edit UI, privacy considerations | Leadership contacts page covers the "faces of the chapter" need for MVP |
| Chapter GPA tracker | Academic accountability is Greek culture | FERPA implications, manual data entry burden, no API endpoints | Out of scope v2 |

---

## Feature Dependencies

```
[Interest Form (/join)]
    └──requires──> [Toast/Alert component] (success + error feedback)
    └──requires──> [409 duplicate-email handler] (graceful UX, not raw error)

[Rush Info Page (/rush)]
    └──requires──> [Coming-soon fallback UI] (API returns {status:"coming_soon"})
    └──enhances──> [Interest Form CTA] (coming-soon page should link to /join)

[Member Dashboard]
    └──requires──> [JWT Auth + Route Protection]
    └──requires──> [Token refresh logic] (60min access token expiry)
    └──requires──> [PDF viewer/download] (core dashboard value)

[PDF Viewer]
    └──requires──> [Signed URL from /v1/events] (backend handles URL generation)
    └──note──> Browser native PDF rendering via <iframe src={signedUrl}> — no library needed

[Admin Hub]
    └──requires──> [Role-based route guard] (admin role check)
    └──branches──> [Events Manager]
                    └──requires──> [PDF upload (multipart form)]
                    └──requires──> [Delete confirmation modal]
    └──branches──> [Members Manager]
                    └──requires──> [Active/deactivated filter toggle]
                    └──requires──> [Create member modal]
                    └──requires──> [Role assignment dropdown/modal]
    └──branches──> [Rush Editor]
                    └──requires──> [Rush visibility toggle]
    └──branches──> [Content Editor]
                    └──requires──> [Per-section save + feedback]

[Design System (ChromeCard, ChromeButton, SectionTitle, Divider)]
    └──required by──> ALL page components (build first, consume everywhere)

[SiteLayout (header/footer/nav)]
    └──required by──> ALL public pages
    └──enhances──> [Auth state awareness] (nav shows Login vs Dashboard link)
```

### Dependency Notes

- **Auth before dashboard:** JWT storage, route protection, and token refresh must be working before any member-only page can be built or tested.
- **Design system before pages:** ChromeCard, ChromeButton, SectionTitle are consumed by every page. Building them first eliminates rework.
- **PDF viewer is browser-native:** No library dependency — `<iframe src={signedUrl}>` or `window.open(signedUrl)` covers both view and download. Signed URL expiry (Supabase default: 60s–1hr) must be considered — fetch URL fresh on demand, not cached.
- **Interest form 409 handling is not optional:** A raw 409 displayed to a rushee ("Conflict") is a broken experience. The handler is low-complexity but must be explicitly implemented.
- **Rush coming-soon is not a fallback — it is a primary state:** The API will frequently return `{status:"coming_soon"}` between rush seasons. The UI for this state must be designed first-class, not as an afterthought.
- **Content editor sections are independent:** History, philanthropy, and contacts are separate `PUT /v1/content/{section}` calls. They can be built and shipped independently.

---

## MVP Definition

### Launch With (v1)

The backlog as defined in PROJECT.md is well-scoped for v1. All items below correspond directly to existing API endpoints.

- [ ] Public site: Home, /rush (with coming-soon state), /join (with 409 handling), /history, /philanthropy, /contact — establishes credibility and captures rushee interest
- [ ] Auth: /login, JWT storage, route protection, token refresh — prerequisite for all member/admin features
- [ ] Member dashboard: profile snippet, event PDFs list with view/download, leadership contacts — delivers primary member value
- [ ] Admin: hub, events (upload/delete), members (list/create/role/deactivate), rush editor (content + visibility toggle), content editor — enables officer self-service
- [ ] Design system: SiteLayout, ChromeCard, ChromeButton, SectionTitle, Divider, Toast/Alert — consistency and premium feel
- [ ] Quality: Mobile-first responsive, SEO meta tags, aria labels, .env.example, README

### Add After Validation (v1.x)

- [ ] Password reset flow — add when backend `/v1/auth/forgot-password` endpoint ships; currently blocked
- [ ] WYSIWYG content editor (TipTap) — upgrade from textarea when officers request formatting; low-risk addition
- [ ] Optimistic UI on admin actions — add when officers report the save/delete interactions feel sluggish

### Future Consideration (v2+)

- [ ] Event RSVP system — add when attendance tracking becomes an operational priority
- [ ] Member profile pages (bios, photos) — add when chapter identity/recruiting value justifies storage + moderation cost
- [ ] Alumni directory — separate initiative; requires distinct auth tier and privacy model
- [ ] Push notifications / rush alerts — add when subscriber volume justifies infrastructure
- [ ] Dues payment (Stripe) — add when treasurer explicitly requests; PCI scope is significant
- [ ] Mobile app — web-first is correct for now; revisit when member engagement data supports native

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Design system (ChromeCard, ChromeButton, etc.) | HIGH | LOW | P1 |
| SiteLayout (nav, footer, responsive) | HIGH | LOW | P1 |
| JWT auth + route protection | HIGH | MEDIUM | P1 |
| Home page with CTAs | HIGH | LOW | P1 |
| /rush page with coming-soon fallback | HIGH | LOW | P1 |
| /join interest form with 409 handling | HIGH | MEDIUM | P1 |
| Member dashboard (PDFs + contacts) | HIGH | MEDIUM | P1 |
| PDF view/download (signed URL iframe) | HIGH | LOW | P1 |
| Token refresh (silent 401 handling) | HIGH | MEDIUM | P1 |
| Admin members manager | HIGH | MEDIUM | P1 |
| Admin rush editor + visibility toggle | HIGH | LOW | P1 |
| Admin events upload/delete | HIGH | MEDIUM | P1 |
| /history, /philanthropy, /contact pages | MEDIUM | LOW | P1 |
| Admin content editor (history/philanthropy/contacts) | MEDIUM | MEDIUM | P1 |
| Admin hub page | MEDIUM | LOW | P1 |
| SEO meta tags, OpenGraph | MEDIUM | LOW | P2 |
| Accessibility (aria labels, focus rings) | MEDIUM | LOW | P2 |
| Subtle grain overlay | LOW | LOW | P2 |
| .env.example + README | LOW | LOW | P2 |
| Password reset flow | HIGH | MEDIUM | P3 (blocked on backend) |
| WYSIWYG content editor | MEDIUM | MEDIUM | P3 |
| Event RSVP | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Defer — blocked or out of MVP scope

---

## Competitor Feature Analysis

Comparison against common fraternity/org website patterns (Squarespace templates, Greek Chapter Management platforms like OmegaFi, GreekTrack, and custom sites).

| Feature | Typical Squarespace/Wix site | Greek management platform (OmegaFi) | PCO Approach |
|---------|------------------------------|--------------------------------------|--------------|
| Visual identity | Generic template, hard to brand | Functional but corporate/generic | Custom Chrome Hearts-inspired dark aesthetic — intentional and distinctive |
| Member login | Often absent or Google Workspace SSO | Full portal with dues, RSVP, directory | JWT-gated dashboard with events + contacts; scoped and fast |
| Rush info | Static page, manually updated HTML | Manual update or separate rush module | API-driven with admin toggle; coming-soon state built-in |
| Interest form | Google Forms embed (jarring UX break) | Built-in CRM-style form | Native `/join` form with duplicate detection; no iframe |
| Event schedules | Facebook group or group chat | Calendar integration or spreadsheet upload | PDF upload/view — matches how chapters actually produce schedules |
| Admin tools | Login to Squarespace editor | Full platform UI | Scoped to exactly what officers need; no bloat |
| Content editing | Drag-and-drop page editor | Limited template fields | Section-by-section API-backed editing; simpler than a full CMS |
| PDF documents | Google Drive links in posts | File attachments on events | Signed Supabase URLs — private by default, no public bucket |

---

## Interest Form — Specific Pattern Notes

**Standard fields for Greek org interest forms (confirmed across comparable sites):**
- Full name (first + last, or combined) — required
- Email address — required; used as deduplication key
- Phone number — optional on many sites but expected for follow-up
- Graduation year / academic year (Freshman/Sophomore/Junior/Senior) — used for rush class targeting
- Major / field of study — used for org fit assessment
- Optional: "How did you hear about us?" — useful for marketing attribution but not in current API model

**409 Duplicate Handling — UX Pattern:**
- Do not surface "409 Conflict" or "Email already exists" as-is — sounds like a server error
- Preferred copy: "Looks like you're already on our list! We'll be in touch about upcoming rush events."
- Alternative copy (if they may be a current member): "This email is already registered. If you're an active member, log in instead."
- Do not clear the form on 409 — user may want to verify they used the right email
- Treat 409 as a success variant, not an error state (green/neutral toast, not red)

---

## Rush Visibility Toggle — Pattern Notes

**The coming-soon state is not an edge case — it is the default state between rush seasons.**

- API returns `{status: "coming_soon"}` when rush is unpublished
- UI must render a purposeful page, not a blank section or loading spinner
- Recommended pattern: full-page layout with org name, "Rush [Season Year] info coming soon" headline, and a CTA to `/join` (interest form)
- Admin toggle (`PATCH /v1/rush/visibility`) should show current state clearly in the admin UI: "Currently: Hidden" / "Currently: Visible" — not just an unlabeled switch
- Consider optimistic UI on toggle: flip state immediately, revert on API error with toast

---

## PDF Viewer / Download — Pattern Notes

**Browser-native is correct for MVP. No library needed.**

- Signed URLs from Supabase are standard HTTPS URLs pointing to a PDF
- `<iframe src={signedUrl} width="100%" height="600px" title="Event PDF">` renders inline in all modern browsers (Chrome, Safari, Firefox, Edge)
- For mobile: iframe PDF rendering is unreliable on iOS Safari — provide a prominent "Open PDF" / "Download" link as primary CTA, with iframe as secondary/desktop enhancement
- Download pattern: `<a href={signedUrl} download target="_blank">Download PDF</a>` — `download` attribute works for same-origin; for Supabase URLs (cross-origin) use `target="_blank"` which opens in browser's native PDF viewer
- Signed URL expiry: Supabase default signed URL TTL varies (60s to 1hr depending on config). Fetch fresh signed URL on user action (click "View"), not on page load — avoids serving expired URLs if user leaves tab open
- Empty state: "No events posted yet" with friendly copy — officers post on a weekly/semester cadence so this state will be common early in a semester

---

## Sources

- PROJECT.md — Fully-defined backlog and API contract (HIGH confidence — this is the ground truth)
- Domain knowledge: Greek org website conventions from comparable chapter sites (PSI chapters, IFC-affiliated fraternities), OmegaFi / GreekTrack platform feature sets (MEDIUM confidence — pattern analysis, not primary source)
- Supabase Storage signed URL behavior — documented behavior of cross-origin signed URLs (MEDIUM confidence — established pattern, WebSearch unavailable to verify current TTL defaults)
- iOS Safari iframe PDF rendering limitation — well-established browser compatibility issue (HIGH confidence — widely documented WebKit behavior)
- Interest form UX patterns — established form design conventions for lead capture on Greek org and event-based sites (MEDIUM confidence)

---

*Feature research for: Fraternity/org website + member portal (PSI CHI OMEGA — San Diego chapter)*
*Researched: 2026-03-05*
