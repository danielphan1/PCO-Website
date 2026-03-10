import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  globalSetup: "./tests/e2e/global-setup.ts",
  fullyParallel: true,
  retries: 0,
  reporter: "list",
  // Raise per-test timeout to 60 s. The default 30 s is too tight when the
  // Next.js dev server compiles the proxy route handler on first request
  // (cold-start). Subsequent runs are fast (~200 ms); this budget covers
  // the first-run compilation without masking real hangs.
  timeout: 60000,
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
  webServer: {
    command: "pnpm dev",
    url: "http://localhost:3000",
    reuseExistingServer: true,
  },
});
