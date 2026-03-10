import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers";

const MEMBER = { email: "member@test.com", password: "TestMember123" };
const ADMIN = { email: "admin@test.com", password: "TestAdmin123" };

test.describe("Login", () => {
  test.beforeEach(async ({ page }) => {
    // Clear auth state
    await page.goto("/login");
    await page.evaluate(() => localStorage.clear());
  });

  test("shows login form with email, password, and Sign In button", async ({
    page,
  }) => {
    await page.goto("/login");
    await expect(page.getByRole("textbox", { name: "Email" })).toBeVisible();
    await expect(page.getByRole("textbox", { name: "Password" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Sign In" })).toBeVisible();
  });

  test("redirects to /dashboard after successful member login", async ({
    page,
  }) => {
    await page.goto("/login");
    await page.getByRole("textbox", { name: "Email" }).fill(MEMBER.email);
    await page.getByRole("textbox", { name: "Password" }).fill(MEMBER.password);
    await page.getByRole("button", { name: "Sign In" }).click();
    await expect(page).toHaveURL("/dashboard");
  });

  test("shows error toast on invalid credentials", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("textbox", { name: "Email" }).fill("wrong@test.com");
    await page.getByRole("textbox", { name: "Password" }).fill("wrongpass");
    await page.getByRole("button", { name: "Sign In" }).click();
    await expect(page.getByText("Invalid email or password")).toBeVisible();
  });

  test("stores tokens in localStorage after login", async ({ page }) => {
    await page.goto("/login");
    await page.getByRole("textbox", { name: "Email" }).fill(MEMBER.email);
    await page.getByRole("textbox", { name: "Password" }).fill(MEMBER.password);
    await page.getByRole("button", { name: "Sign In" }).click();
    await page.waitForURL("/dashboard");

    const tokens = await page.evaluate(() => ({
      access: localStorage.getItem("access_token"),
      refresh: localStorage.getItem("refresh_token"),
    }));
    expect(tokens.access).toBeTruthy();
    expect(tokens.refresh).toBeTruthy();
  });

  test("already-authenticated user is redirected away from /login", async ({
    page,
  }) => {
    // Log in first
    await page.goto("/login");
    await page.getByRole("textbox", { name: "Email" }).fill(MEMBER.email);
    await page.getByRole("textbox", { name: "Password" }).fill(MEMBER.password);
    await page.getByRole("button", { name: "Sign In" }).click();
    await page.waitForURL("/dashboard");

    // Navigating back to /login should redirect to /dashboard
    await page.goto("/login");
    await expect(page).toHaveURL("/dashboard");
  });
});

test.describe("Logout", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, MEMBER.email, MEMBER.password);
  });


  test("Logout button clears tokens and redirects to /login", async ({
    page,
  }) => {
    await page.getByRole("button", { name: /logout/i }).click();
    await expect(page).toHaveURL("/login");

    const tokens = await page.evaluate(() => ({
      access: localStorage.getItem("access_token"),
      refresh: localStorage.getItem("refresh_token"),
    }));
    expect(tokens.access).toBeNull();
    expect(tokens.refresh).toBeNull();
  });
});

test.describe("Route protection", () => {
  test("unauthenticated user visiting /dashboard is redirected to /login", async ({
    page,
  }) => {
    await page.goto("/login");
    await page.evaluate(() => localStorage.clear());
    await page.goto("/dashboard");
    await expect(page).toHaveURL("/login");
  });
});
