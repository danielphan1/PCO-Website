import { getAccessToken, getRefreshToken, setTokens, clearTokens } from "@/lib/auth";
import type { AuthTokens } from "@/types/api";

const PROXY_BASE = "/api/proxy";

// Singleton refresh promise — prevents concurrent 401s from triggering multiple refresh calls.
// If two requests both get 401, the second one awaits the same promise as the first.
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
