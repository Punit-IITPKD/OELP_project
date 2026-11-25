import AxeBuilder from '@axe-core/playwright';
import { expect, test } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';

const evidenceRoot = process.env.QA_ARTIFACT_DIR
  ?? path.resolve(process.cwd(), '../../generated-artifacts/phase8-qa');

const routes = [
  { path: '/', heading: 'Business overview' },
  { path: '/segments', heading: 'Segments' },
  { path: '/intelligence', heading: 'Customer intelligence' },
  { path: '/behavior', heading: 'Behavior indicators' },
  { path: '/forecasting', heading: 'Forecast workspace' },
  { path: '/upload', heading: 'Upload analysis' },
  { path: '/model-performance', heading: 'Model performance' },
  { path: '/revenue-exposure', heading: 'Revenue exposure & retention planning' },
  { path: '/trajectories', heading: 'Customer trajectory explorer' },
  { path: '/research', heading: 'Research overview' },
];

const slug = (value: string) => value.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '').toLowerCase();

for (const route of routes) {
  test(`desktop route ${route.path} renders live data without server errors`, async ({ page }) => {
    const pageErrors: string[] = [];
    const apiFailures: string[] = [];
    page.on('pageerror', (error) => pageErrors.push(error.message));
    page.on('response', (response) => {
      if (response.status() >= 500 && new URL(response.url()).pathname.startsWith('/api/')) {
        apiFailures.push(`${response.status()} ${response.url()}`);
      }
    });

    const response = await page.goto(route.path);
    expect(response?.status()).toBeLessThan(400);
    await expect(page.getByRole('heading', { name: route.heading, exact: true })).toBeVisible();
    await expect(page.getByText('API connected', { exact: true })).toBeVisible();
    await page.waitForLoadState('networkidle');
    expect(pageErrors).toEqual([]);
    expect(apiFailures).toEqual([]);

    const screenshotPath = path.join(evidenceRoot, 'screenshots', 'desktop', `${slug(route.path || 'overview')}.png`);
    await fs.mkdir(path.dirname(screenshotPath), { recursive: true });
    await page.screenshot({ path: screenshotPath, fullPage: true });
  });
}

for (const route of routes) {
  test(`small-phone route ${route.path} has no page-level horizontal overflow`, async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 800 });
    const response = await page.goto(route.path);
    expect(response?.status()).toBeLessThan(400);
    await expect(page.getByRole('heading', { name: route.heading, exact: true })).toBeVisible();
    await expect(page.getByText('API connected', { exact: true })).toBeVisible();

    const dimensions = await page.evaluate(() => ({
      viewport: window.innerWidth,
      document: document.documentElement.scrollWidth,
    }));
    expect(dimensions.document).toBeLessThanOrEqual(dimensions.viewport + 1);

    const screenshotPath = path.join(evidenceRoot, 'screenshots', 'mobile-360', `${slug(route.path || 'overview')}.png`);
    await fs.mkdir(path.dirname(screenshotPath), { recursive: true });
    await page.screenshot({ path: screenshotPath, fullPage: true });
  });
}

test('sidebar navigation, history, refresh, and deep link preserve the selected route', async ({ page }) => {
  await page.goto('/');
  await page.getByTestId('link-research').click();
  await expect(page.getByRole('heading', { name: 'Research overview', exact: true })).toBeVisible();
  await page.getByTestId('link-segments').click();
  await expect(page.getByRole('heading', { name: 'Segments', exact: true })).toBeVisible();
  await page.goBack();
  await expect(page.getByRole('heading', { name: 'Research overview', exact: true })).toBeVisible();
  await page.goForward();
  await expect(page.getByRole('heading', { name: 'Segments', exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Segments', exact: true })).toBeVisible();
});

test('customer 18102 completes the saved forecast and research workflow', async ({ page }) => {
  await page.goto('/intelligence');
  await page.getByTestId('input-customer-id').fill('18102');
  await page.getByTestId('button-search-customer').click();
  await page.getByTestId('button-open-customer-18102').waitFor();
  await page.getByTestId('button-open-customer-18102').click();

  await expect(page.getByText('Customer 18102', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Purchase probability', exact: true })).toBeVisible();
  await expect(page.getByTestId('section-customer-revenue-exposure')).toBeVisible();

  await page.getByTestId('button-load-customer-explanation').click();
  await expect(page.getByText('Why this 30-day forecast?', { exact: true })).toBeVisible();
  await page.getByTestId('button-load-customer-reliability').click();
  await expect(page.getByText('Saved group reliability', { exact: true })).toBeVisible();
});

test('research source links use existing main-branch repository paths', async ({ page }) => {
  await page.goto('/research');
  await expect(page.getByRole('heading', { name: 'Research overview', exact: true })).toBeVisible();
  await expect(page.getByText('Notebook 11', { exact: false })).toHaveCount(0);

  const sourceHrefs = await page.locator('a[href*="/blob/"]').evaluateAll((anchors) =>
    anchors.map((anchor) => (anchor as HTMLAnchorElement).href),
  );
  expect(sourceHrefs.length).toBeGreaterThan(0);
  expect(sourceHrefs.every((href) => href.includes('/blob/main/'))).toBe(true);

  const repositoryPaths = sourceHrefs.map((href) => href.split('/blob/main/')[1]);
  for (const sourcePath of repositoryPaths) {
    const exists = await fs.access(path.resolve(process.cwd(), '../../', sourcePath)).then(() => true, () => false);
    expect(exists, `Missing repository source ${sourcePath}`).toBe(true);
  }
});

test('upload preview, analysis, and export use only an in-memory synthetic CSV', async ({ page }) => {
  await page.goto('/upload');
  const csv = [
    'Order ref,Stock code,Product,Count,Bought at,Unit price,Client,Location',
    '90001,SKU-1,Widget,2,2010-01-01 09:00:00,5.00,901001,United Kingdom',
    '90002,SKU-2,Gadget,1,2010-01-20 12:00:00,7.00,901001,United Kingdom',
    '90003,SKU-3,Book,1,2010-02-01 10:00:00,8.00,901002,United Kingdom',
    '90003,SKU-3,Book,1,2010-02-01 10:00:00,8.00,901002,United Kingdom',
    'C90004,SKU-4,Return,-1,2010-02-05 10:00:00,8.00,901002,United Kingdom',
  ].join('\n');
  await page.getByTestId('input-upload-file').setInputFiles({
    name: 'synthetic-retail.csv',
    mimeType: 'text/csv',
    buffer: Buffer.from(csv),
  });
  await expect(page.getByText(/5 rows · 8 columns/)).toBeVisible();

  const mappings: Record<string, string> = {
    Invoice: 'Order ref',
    StockCode: 'Stock code',
    Description: 'Product',
    Quantity: 'Count',
    InvoiceDate: 'Bought at',
    Price: 'Unit price',
    'Customer ID': 'Client',
    Country: 'Location',
  };
  for (const [field, column] of Object.entries(mappings)) {
    await page.getByTestId(`select-map-${field}`).selectOption({ label: column });
  }
  await page.getByTestId('button-analyze-upload').click();
  await expect(page.getByText('Positive gross revenue', { exact: true })).toBeVisible();

  const download = page.waitForEvent('download');
  await page.getByRole('button', { name: /Export cleaned transactions/i }).click();
  expect((await download).suggestedFilename()).toBe('cleaned_transactions.csv');
});

test('key demonstration screens have no serious or critical WCAG violations', async ({ page }) => {
  const results: Array<{ path: string; violations: unknown[] }> = [];
  const blockers: Array<{ path: string; id: string; impact: string | null; description: string }> = [];

  for (const routePath of ['/', '/intelligence', '/research', '/upload', '/revenue-exposure']) {
    await page.goto(routePath);
    await expect(page.getByText('API connected', { exact: true })).toBeVisible();
    const result = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa'])
      .analyze();
    results.push({ path: routePath, violations: result.violations });
    for (const violation of result.violations) {
      if (violation.impact === 'critical' || violation.impact === 'serious') {
        blockers.push({
          path: routePath,
          id: violation.id,
          impact: violation.impact,
          description: violation.description,
        });
      }
    }
  }

  const reportPath = path.join(evidenceRoot, 'accessibility', 'axe-results.json');
  await fs.mkdir(path.dirname(reportPath), { recursive: true });
  await fs.writeFile(reportPath, `${JSON.stringify(results, null, 2)}\n`);
  expect(blockers).toEqual([]);
});
