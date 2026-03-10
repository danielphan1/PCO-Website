import { Page } from "@playwright/test";

const API = "http://localhost:8000";

export async function loginAs(page: Page, email: string, password: string) {
  // Bypass the UI login form: get tokens directly from the backend API (no proxy),
  // inject them into localStorage, then navigate to /dashboard.
  //
  // We poll for the Logout button, which only appears once AuthContext has finished
  // fetching /v1/users/me via the proxy and set user in state. Under parallel
  // worker load the proxy can be slow; retrying the whole navigation on failure
  // (rather than just increasing the timeout) keeps each individual attempt short
  // and recovers from transient proxy errors.
  const res = await page.request.post(`${API}/v1/auth/login`, {
    data: { email, password },
  });
  const { access_token, refresh_token } = await res.json();

  for (let attempt = 1; attempt <= 3; attempt++) {
    await page.goto("/");
    await page.evaluate(
      ({ at, rt }) => {
        localStorage.setItem("access_token", at);
        localStorage.setItem("refresh_token", rt);
        document.cookie = "auth-hint=1; path=/; samesite=lax";
      },
      { at: access_token, rt: refresh_token }
    );

    await page.goto("/dashboard");

    try {
      await page.getByRole("button", { name: "Logout" }).waitFor({
        state: "visible",
        timeout: 12000,
      });
      return; // success
    } catch {
      if (attempt === 3) throw new Error("loginAs: Logout button never appeared after 3 attempts");
      // Re-inject tokens and retry — proxy may have been temporarily overloaded
    }
  }
}
