import { Page } from "@playwright/test";

const API = "http://localhost:8000";

export async function loginAs(page: Page, email: string, password: string) {
  // Use the API directly to get tokens, inject into localStorage, then navigate
  const res = await page.request.post(`${API}/v1/auth/login`, {
    data: { email, password },
  });
  const { access_token, refresh_token } = await res.json();

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
  await page.getByRole("button", { name: "Logout" }).waitFor({
    state: "visible",
    timeout: 10000,
  });
}
