import { chromium, expect, test as base } from '@playwright/test';

export const test = base.extend({
  browser: [async ({}, use) => {
    const endpoint = process.env.OELP_CDP_ENDPOINT;
    const executablePath = process.env.REPLIT_PLAYWRIGHT_CHROMIUM_EXECUTABLE;
    const browser = endpoint
      ? await chromium.connectOverCDP(endpoint)
      : executablePath
        ? await chromium.launch({ executablePath })
        : await chromium.launch();

    await use(browser);
    await browser.close();
  }, { scope: 'worker' }],
});

export { expect };
