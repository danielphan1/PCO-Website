import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
} from "@/lib/auth";

// localStorage is provided by jsdom

beforeEach(() => {
  localStorage.clear();
});

describe("setTokens", () => {
  it("stores access_token and refresh_token in localStorage", () => {
    setTokens({ access_token: "acc123", refresh_token: "ref456" });
    expect(localStorage.getItem("access_token")).toBe("acc123");
    expect(localStorage.getItem("refresh_token")).toBe("ref456");
  });
});

describe("getAccessToken", () => {
  it("returns null when nothing is stored", () => {
    expect(getAccessToken()).toBeNull();
  });

  it("returns the stored access token", () => {
    localStorage.setItem("access_token", "mytoken");
    expect(getAccessToken()).toBe("mytoken");
  });
});

describe("getRefreshToken", () => {
  it("returns null when nothing is stored", () => {
    expect(getRefreshToken()).toBeNull();
  });

  it("returns the stored refresh token", () => {
    localStorage.setItem("refresh_token", "myrefresh");
    expect(getRefreshToken()).toBe("myrefresh");
  });
});

describe("clearTokens", () => {
  it("removes both tokens from localStorage", () => {
    localStorage.setItem("access_token", "acc");
    localStorage.setItem("refresh_token", "ref");
    clearTokens();
    expect(localStorage.getItem("access_token")).toBeNull();
    expect(localStorage.getItem("refresh_token")).toBeNull();
  });

  it("is safe to call when tokens are already absent", () => {
    expect(() => clearTokens()).not.toThrow();
  });
});
