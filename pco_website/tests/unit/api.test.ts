import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { apiFetch } from "@/lib/api";

// Stub NEXT_PUBLIC_API_BASE
vi.stubEnv("NEXT_PUBLIC_API_BASE", "http://localhost:8000");

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
    expect(url).toBe("http://localhost:8000/v1/users/me");
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
      // First call: original request returns 401
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: "Unauthorized" }), {
          status: 401,
        })
      )
      // Second call: refresh attempt returns 401
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: "Invalid refresh" }), {
          status: 401,
        })
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
      // First call: original request 401
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: "Unauthorized" }), {
          status: 401,
        })
      )
      // Second call: refresh succeeds
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            access_token: "new_tok",
            refresh_token: "new_refresh",
          }),
          { status: 200 }
        )
      )
      // Third call: retry with new token succeeds
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ id: "u1" }), { status: 200 })
      );

    const result = await apiFetch<{ id: string }>("/v1/users/me");
    expect(result).toEqual({ id: "u1" });
    expect(localStorage.getItem("access_token")).toBe("new_tok");
  });
});
