# Frontend Docker Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Package the Next.js frontend into a portable Docker image with runtime-configurable backend URL.

**Architecture:** Server components switch from `NEXT_PUBLIC_API_BASE` (build-time) to `process.env.BACKEND_URL` (runtime). Client-side code in `lib/api.ts` switches to a proxy route handler at `/api/proxy/[...path]` that reads `BACKEND_URL` per-request. `next.config.ts` enables `output: "standalone"` for an optimized production image. A multi-stage Dockerfile produces a minimal runner image; `docker-compose.yml` in `pco_website/` exposes `BACKEND_URL` as an env var.

**Tech Stack:** Next.js 16, Node 20 Alpine, pnpm, Docker multi-stage build.

---

### Task 1: Enable standalone output in next.config.ts

**Files:**
- Modify: `pco_website/next.config.ts`

**Step 1: Add `output: "standalone"`**

Open `pco_website/next.config.ts`. Current content:
```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["sonner"],
};

export default nextConfig;
```

Replace with:
```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["sonner"],
  output: "standalone",
};

export default nextConfig;
```

**Step 2: Verify the build produces standalone output**

Run from `pco_website/`:
```bash
pnpm build
```
Expected: Build completes successfully and `.next/standalone/` directory exists.

```bash
ls .next/standalone/
```
Expected: `server.js`, `node_modules/`, `package.json` present.

**Step 3: Commit**
```bash
git add pco_website/next.config.ts
git commit -m "feat(frontend): enable standalone output for Docker"
```

---

### Task 2: Create proxy route handler

**Files:**
- Create: `pco_website/app/api/proxy/[...path]/route.ts`

**Step 1: Create the file**

Create `pco_website/app/api/proxy/[...path]/route.ts`:
```ts
import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000";

async function forward(
  req: NextRequest,
  params: Promise<{ path: string[] }>
): Promise<NextResponse> {
  const { path } = await params;
  const joined = path.join("/");
  const search = req.nextUrl.search;
  const url = `${BACKEND_URL}/${joined}${search}`;

  const headers = new Headers(req.headers);
  headers.delete("host");

  const isBodyless = req.method === "GET" || req.method === "HEAD";

  const upstream = await fetch(url, {
    method: req.method,
    headers,
    body: isBodyless ? undefined : req.body,
    // Required for streaming request bodies in Node.js fetch
    ...(isBodyless ? {} : { duplex: "half" as const }),
  } as RequestInit);

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: upstream.headers,
  });
}

type RouteContext = { params: Promise<{ path: string[] }> };

export const GET    = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
export const POST   = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
export const PUT    = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
export const PATCH  = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
export const DELETE = (req: NextRequest, ctx: RouteContext) => forward(req, ctx.params);
```

**Step 2: Smoke test with dev server running**

With `pnpm dev` running and the backend up:
```bash
curl http://localhost:3000/api/proxy/health
```
Expected: `{"status":"ok"}` (or similar backend health response).

**Step 3: Commit**
```bash
git add pco_website/app/api/proxy/
git commit -m "feat(frontend): add proxy route handler for runtime backend URL"
```

---

### Task 3: Update lib/api.ts to use proxy (TDD)

**Files:**
- Modify: `pco_website/tests/unit/api.test.ts`
- Modify: `pco_website/lib/api.ts`

**Step 1: Update the unit test first**

Open `pco_website/tests/unit/api.test.ts`. Make these changes:

1. Remove line 5: `vi.stubEnv("NEXT_PUBLIC_API_BASE", "http://localhost:8000");`

2. Update the URL assertion in `"sends GET with Authorization header..."` test (line 24):
   ```ts
   // Before:
   expect(url).toBe("http://localhost:8000/v1/users/me");
   // After:
   expect(url).toBe("/api/proxy/v1/users/me");
   ```

The full updated file:
```ts
import { describe, it, expect, beforeEach, vi } from "vitest";
import { apiFetch } from "@/lib/api";

beforeEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

describe("apiFetch — happy path", () => {
  it("sends GET with Authorization header when token is stored", async () => {
    localStorage.setItem("access_token", "tok123");

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ id: "1" }), { status: 200 })
    );

    await apiFetch("/v1/users/me");

    expect(fetchSpy).toHaveBeenCalledOnce();
    const [url, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("/api/proxy/v1/users/me");
    expect((init.headers as Headers).get("Authorization")).toBe("Bearer tok123");
  });

  it("sends request without Authorization when no token stored", async () => {
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify([]), { status: 200 })
    );

    await apiFetch("/v1/content/history");

    const [, init] = fetchSpy.mock.calls[0] as [string, RequestInit];
    expect((init.headers as Headers).get("Authorization")).toBeNull();
  });

  it("returns parsed JSON body on 200", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ section: "history", content: "text" }), {
        status: 200,
      })
    );

    const result = await apiFetch<{ section: string; content: string }>(
      "/v1/content/history"
    );
    expect(result).toEqual({ section: "history", content: "text" });
  });

  it("returns null for 204 No Content", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(null, { status: 204 })
    );

    const result = await apiFetch("/v1/something");
    expect(result).toBeNull();
  });
});

describe("apiFetch — error handling", () => {
  it("throws with status on non-ok response", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce(
      new Response(JSON.stringify({ detail: "Not found" }), { status: 404 })
    );

    await expect(apiFetch("/v1/missing")).rejects.toMatchObject({
      message: "Not found",
      status: 404,
    });
  });

  it("clears tokens and throws on 401 after failed refresh", async () => {
    localStorage.setItem("access_token", "expired");
    localStorage.setItem("refresh_token", "bad_refresh");

    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: "Unauthorized" }), { status: 401 })
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: "Invalid refresh" }), { status: 401 })
      );

    await expect(apiFetch("/v1/users/me")).rejects.toMatchObject({
      message: "Session expired",
      status: 401,
    });

    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });

  it("retries with new token after successful refresh", async () => {
    localStorage.setItem("access_token", "expired_tok");
    localStorage.setItem("refresh_token", "valid_refresh");

    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: "Unauthorized" }), { status: 401 })
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({ access_token: "new_tok", refresh_token: "new_refresh" }),
          { status: 200 }
        )
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ id: "u1" }), { status: 200 })
      );

    const result = await apiFetch<{ id: string }>("/v1/users/me");
    expect(result).toEqual({ id: "u1" });
    expect(localStorage.getItem("access_token")).toBe("new_tok");
  });
});
```

**Step 2: Run test — expect FAIL**

```bash
cd pco_website && pnpm test
```
Expected: FAIL — URL assertion `"/api/proxy/v1/users/me"` does not match `"http://localhost:8000/v1/users/me"`.

**Step 3: Update lib/api.ts**

Open `pco_website/lib/api.ts`. Replace the entire file:
```ts
import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "@/lib/auth";
import type { AuthTokens } from "@/types/api";

const PROXY_BASE = "/api/proxy";

// Singleton refresh promise — prevents concurrent 401s from triggering multiple refresh calls.
let refreshPromise: Promise<string | null> | null = null;

async function refreshTokens(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  try {
    const res = await fetch(`${PROXY_BASE}/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });

    if (!res.ok) {
      clearTokens();
      return null;
    }

    const data: AuthTokens = await res.json();
    setTokens(data);
    return data.access_token;
  } catch {
    clearTokens();
    return null;
  }
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAccessToken();

  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  // Only set Content-Type for non-FormData bodies — multipart uploads set their own boundary
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  let res = await fetch(`${PROXY_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    // Singleton: if refresh already in flight, all concurrent 401s await the same promise
    if (!refreshPromise) {
      refreshPromise = refreshTokens().finally(() => {
        refreshPromise = null;
      });
    }
    const newToken = await refreshPromise;

    if (!newToken) {
      throw Object.assign(new Error("Session expired"), { status: 401 });
    }

    headers.set("Authorization", `Bearer ${newToken}`);
    res = await fetch(`${PROXY_BASE}${path}`, { ...options, headers });
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({}));
    throw Object.assign(
      new Error(error.detail ?? "API error"),
      { status: res.status }
    );
  }

  // Return null for 204 No Content responses
  if (res.status === 204) return null as T;

  return res.json() as Promise<T>;
}
```

**Step 4: Run test — expect PASS**

```bash
pnpm test
```
Expected: 14/14 tests pass.

**Step 5: Commit**
```bash
git add pco_website/lib/api.ts pco_website/tests/unit/api.test.ts
git commit -m "feat(frontend): route client-side API calls through proxy handler"
```

---

### Task 4: Update server components to use BACKEND_URL

**Files:**
- Modify: `pco_website/app/(public)/history/page.tsx`
- Modify: `pco_website/app/(public)/philanthropy/page.tsx`
- Modify: `pco_website/app/(public)/contact/page.tsx`
- Modify: `pco_website/app/(public)/rush/page.tsx`
- Modify: `pco_website/app/(public)/page.tsx`
- Modify: `pco_website/.env.local`

**Step 1: Update history/page.tsx**

Change line 12:
```ts
// Before:
const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/v1/content/history`, {
// After:
const res = await fetch(`${process.env.BACKEND_URL}/v1/content/history`, {
```

**Step 2: Update philanthropy/page.tsx**

Change line 12:
```ts
// Before:
const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/v1/content/philanthropy`, {
// After:
const res = await fetch(`${process.env.BACKEND_URL}/v1/content/philanthropy`, {
```

**Step 3: Update contact/page.tsx**

Change lines 13 and 25:
```ts
// Before:
const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/v1/content/contacts`, {
// After:
const res = await fetch(`${process.env.BACKEND_URL}/v1/content/contacts`, {

// Before:
const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE}/v1/content/leadership`, {
// After:
const res = await fetch(`${process.env.BACKEND_URL}/v1/content/leadership`, {
```

**Step 4: Update rush/page.tsx**

Change lines 13-14:
```ts
// Before:
const apiBase = process.env.NEXT_PUBLIC_API_BASE;
if (!apiBase) return null;
const res = await fetch(`${apiBase}/v1/rush`, {
// After:
const apiBase = process.env.BACKEND_URL;
if (!apiBase) return null;
const res = await fetch(`${apiBase}/v1/rush`, {
```

**Step 5: Update page.tsx (home page)**

Change lines 20-21:
```ts
// Before:
const apiBase = process.env.NEXT_PUBLIC_API_BASE;
if (!apiBase) return null;
const res = await fetch(`${apiBase}${path}`, {
// After:
const apiBase = process.env.BACKEND_URL;
if (!apiBase) return null;
const res = await fetch(`${apiBase}${path}`, {
```

**Step 6: Update .env.local**

Replace the content of `pco_website/.env.local`:
```
BACKEND_URL=http://localhost:8000
```

**Step 7: Run E2E tests to verify public pages still work**

```bash
cd pco_website && pnpm test:e2e
```
Expected: 14/15 pass, 1 skipped (same as before).

**Step 8: Commit**
```bash
git add pco_website/app/ pco_website/.env.local
git commit -m "feat(frontend): use runtime BACKEND_URL in server components"
```

---

### Task 5: Create Dockerfile

**Files:**
- Create: `pco_website/Dockerfile`
- Create: `pco_website/.dockerignore`

**Step 1: Create .dockerignore**

Create `pco_website/.dockerignore`:
```
node_modules
.next
.env.local
.env*.local
*.md
.git
.gitignore
tests
.playwright-mcp
test-results
```

**Step 2: Create Dockerfile**

Create `pco_website/Dockerfile`:
```dockerfile
# Stage 1: install dependencies
FROM node:20-alpine AS deps
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Stage 2: build
FROM node:20-alpine AS builder
RUN corepack enable && corepack prepare pnpm@latest --activate
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# Stage 3: production runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

**Step 3: Commit**
```bash
git add pco_website/Dockerfile pco_website/.dockerignore
git commit -m "feat(frontend): add multi-stage Dockerfile"
```

---

### Task 6: Create docker-compose.yml

**Files:**
- Create: `pco_website/docker-compose.yml`

**Step 1: Create docker-compose.yml**

Create `pco_website/docker-compose.yml`:
```yaml
services:
  web:
    build: .
    ports:
      - "3000:3000"
    environment:
      # Set to the reachable address of your backend from inside the container.
      # Use host.docker.internal:8000 on Mac/Windows if the backend runs on the host.
      BACKEND_URL: ${BACKEND_URL:-http://host.docker.internal:8000}
```

**Step 2: Commit**
```bash
git add pco_website/docker-compose.yml
git commit -m "feat(frontend): add docker-compose for standalone web service"
```

---

### Task 7: Build and smoke test the Docker image

**Step 1: Build the image**

```bash
cd pco_website && docker compose build
```
Expected: Build completes with all 3 stages. No errors.

**Step 2: Start the container**

```bash
docker compose up -d
```
Expected: Container starts, port 3000 is exposed.

**Step 3: Smoke test — home page loads**

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/
```
Expected: `200`

**Step 4: Smoke test — proxy route works**

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/api/proxy/health
```
Expected: `200`

**Step 5: Confirm BACKEND_URL is runtime-configurable**

Stop and restart with a different (intentionally wrong) URL to prove it's not baked in:
```bash
docker compose down
BACKEND_URL=http://nonexistent:9999 docker compose up -d
curl http://localhost:3000/api/proxy/health
```
Expected: Connection error from proxy (not a build-time 404) — proves the URL is read at runtime.

```bash
docker compose down
```

**Step 6: Run full test suite one final time**

```bash
cd pco_website && pnpm test && pnpm test:e2e
```
Expected: 14/14 unit tests pass, 14/15 E2E pass (1 skipped).

**Step 7: Final commit (if any cleanup needed)**
```bash
git add -p
git commit -m "chore(frontend): verify Docker build and runtime env"
```

---

### Update root Makefile

**Files:**
- Modify: `Makefile`

**Step 1: Add Docker targets**

Open `/Users/briannguyen/Workspace/PCO-Website/Makefile` and append:
```makefile
.PHONY: docker-build docker-up docker-down

docker-build:
	cd $(FRONTEND_DIR) && docker compose build

docker-up:
	cd $(FRONTEND_DIR) && docker compose up -d

docker-down:
	cd $(FRONTEND_DIR) && docker compose down
```

**Step 2: Commit**
```bash
git add Makefile
git commit -m "chore: add Docker targets to root Makefile"
```
