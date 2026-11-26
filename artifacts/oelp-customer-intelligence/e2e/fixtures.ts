import { chromium, expect, test as base } from '@playwright/test';

export const test = base.extend({
  browser: [async ({}, use) => {
    const endpoint = process.env.OELP_CDP_ENDPOINT;
    const browser = endpoint
      ? await chromium.connectOverCDP(endpoint)
      : await chromium.launch();

    await use(browser);
    await browser.close();
  }, { scope: 'worker' }],
});

export { expect };
