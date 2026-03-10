import { test, expect } from "@playwright/test";
import { loginAs } from "./helpers";

const MEMBER = { email: "member@test.com", password: "TestMember123" };

test.describe("Member Dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await loginAs(page, MEMBER.email, MEMBER.password);
  });

  test("shows member name (uppercased) and role in profile section", async ({
    page,
  }) => {
    await expect(page.locator("h1")).toContainText("TEST MEMBER");
    await expect(page.locator("p").filter({ hasText: /^member$/i }).first()).toBeVisible();
  });

  test("shows Events section heading", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "Events" })
    ).toBeVisible();
  });

  test("shows T6 Leadership section heading", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "T6 Leadership" })
    ).toBeVisible();
  });

  test("events load and show View button or empty state", async ({ page }) => {
    // Wait for skeleton to resolve
    await page.waitForTimeout(2000);

    const viewButton = page.getByRole("button", { name: "View" });
    const emptyState = page.getByText("No upcoming events posted yet.");

    const hasEvents = await viewButton.count() > 0;
    if (hasEvents) {
      await expect(viewButton.first()).toBeVisible();
    } else {
      await expect(emptyState).toBeVisible();
    }
  });

  test("View button has target=_blank (opens in new tab)", async ({ page }) => {
    await page.waitForTimeout(2000);

    // ChromeButton with href renders as an anchor — check target attribute
    const viewLink = page.locator('a[target="_blank"]').first();
    if ((await viewLink.count()) === 0) {
      test.skip();
      return;
    }
    await expect(viewLink).toHaveAttribute("rel", "noopener noreferrer");
  });

  test("leadership contacts load with mailto links", async ({ page }) => {
    await page.waitForTimeout(2000);

    const mailtoLinks = page.locator('a[href^="mailto:"]');
    const emptyState = page.getByText("No leadership contacts posted yet.");

    const hasLeaders = (await mailtoLinks.count()) > 0;
    if (hasLeaders) {
      await expect(mailtoLinks.first()).toBeVisible();
    } else {
      await expect(emptyState).toBeVisible();
    }
  });

  test("leadership mailto links have correct href format", async ({ page }) => {
    await page.waitForTimeout(2000);

    const mailtoLinks = page.locator('a[href^="mailto:"]');
    if ((await mailtoLinks.count()) === 0) return;

    const href = await mailtoLinks.first().getAttribute("href");
    expect(href).toMatch(/^mailto:.+@.+/);
  });

  test("events and leadership load independently (no cascade failure)", async ({
    page,
  }) => {
    await page.waitForTimeout(2000);
    // Both sections should have resolved — no error messages visible
    await expect(
      page.getByText("Could not load events. Please refresh the page.")
    ).not.toBeVisible();
    await expect(
      page.getByText("Could not load leadership contacts. Please refresh the page.")
    ).not.toBeVisible();
  });
});
