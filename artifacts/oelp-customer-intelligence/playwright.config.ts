import { defineConfig } from '@playwright/test';

const baseURL = process.env.OELP_BASE_URL ?? 'http://127.0.0.1:5000';
const chromiumPath = process.env.REPLIT_PLAYWRIGHT_CHROMIUM_EXECUTABLE;

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 60_000,
  expect: { timeout: 15_000 },
  reporter: 'list',
  outputDir: '../../generated-artifacts/phase8-qa/playwright-results',
  use: {
    baseURL,
    browserName: 'chromium',
    headless: true,
    viewport: { width: 1366, height: 768 },
    launchOptions: chromiumPath
      ? { executablePath: chromiumPath, args: ['--no-sandbox'] }
      : {},
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'bash ../../scripts/run-oelp-web.sh',
    url: baseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
