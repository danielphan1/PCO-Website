/**
 * Playwright global setup — runs once before any test workers start.
 *
 * Purpose: warm the Next.js proxy route handler before tests run.
 *
 * In dev mode (`pnpm dev`) Next.js compiles API routes on first request
 * (on-demand compilation). The proxy handler at `/api/proxy/[...path]`
 * is not compiled until something hits it. When 4 parallel workers each
 * call `loginAs()` simultaneously, they all hit `/api/proxy/v1/users/me`
 * at once. Next.js dev serialises compilation — some requests queue, time
 * out (> 30 s), and the `AuthContext` treats them as auth failures,
 * redirecting the worker's page to `/login` before the Logout button
 * can appear.
 *
 * Solution: fire multiple concurrent requests to the proxy here, in the
 * single global-setup process, and wait for them to resolve before handing
 * control to the workers. By the time the first `beforeEach` runs the
 * route is compiled and cached.
 */

const BASE = "http://localhost:3000";
// Number of concurrent warmup requests — matches the default worker count.
const CONCURRENCY = 4;
// How long to wait for the proxy to respond (ms). Cold compilation can take ~20 s.
const WARMUP_TIMEOUT_MS = 45_000;

async function warmupRequest(): Promise<void> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), WARMUP_TIMEOUT_MS);
  try {
    await fetch(`${BASE}/api/proxy/v1/users/me`, {
      headers: { Authorization: "Bearer warmup" },
      signal: controller.signal,
    });
  } catch {
    // AbortError or connection error — the server isn't ready yet.
    // The webServer readiness check already guarantees localhost:3000 is up,
    // so an abort here means the route took too long. That's fine for warmup
    // purposes since the compilation will have at least started.
  } finally {
    clearTimeout(timer);
  }
}

export default async function globalSetup() {
  // Fire CONCURRENCY requests simultaneously to force the dev server to
  // compile the proxy route before any worker calls loginAs().
  await Promise.all(Array.from({ length: CONCURRENCY }, () => warmupRequest()));
}
