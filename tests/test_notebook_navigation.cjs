// Real-browser regression for end -> repeated previous-entry navigation.
const fs = require('node:fs');
const http = require('node:http');
const assert = require('node:assert/strict');
const {chromium} = require('playwright');
(async () => {
  const template = fs.readFileSync(process.env.NOTEBOOK_TEMPLATE || 'index.html', 'utf8');
  const html = template.replace('__REVISION__', 'navigation-test')
    .replace('<!-- NOTEBOOK -->', fs.readFileSync('notebook.html', 'utf8'));
  const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', req.url === '/revision' ? 'application/json' : 'text/html');
    res.end(req.url === '/revision' ? '{"revision":"navigation-test"}' : html);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  const report = [];
  try {
    browser = await chromium.launch({headless: true});
    for (const motion of ['no-preference', 'reduce']) {
      const page = await browser.newPage({reducedMotion: motion});
      await page.goto(`http://127.0.0.1:${server.address().port}`, {waitUntil: 'domcontentloaded'});
      await page.waitForFunction(() => window.mathReady);
      await page.locator('[data-scroll="end"]').click();
      await page.waitForTimeout(1800);
      const count = await page.locator('main h2, main h3').count();
      for (let step = 1; step <= 8; step++) {
        await page.locator('[data-scroll="previous"]').click();
        await page.waitForTimeout(2000);
        const target = page.locator('main h2, main h3').nth(count - 1 - step);
        const data = await target.evaluate(element => ({
          title: element.textContent, top: element.getBoundingClientRect().top,
          scrollY, height: document.documentElement.scrollHeight,
        }));
        report.push({motion, step, ...data});
      }
      for (let step = 7; step >= 1; step--) {
        await page.locator('[data-scroll="next"]').click();
        await page.waitForTimeout(1800);
        const data = await page.locator('main h2, main h3').nth(count - 1 - step)
          .evaluate(element => ({title: element.textContent, top: element.getBoundingClientRect().top}));
        report.push({motion, direction: 'next', step, ...data});
      }
      // Rapid clicks must advance from the chosen destination, not an intermediate
      // point in the smooth-scroll animation. Browser pointer events are included.
      for (let n = 0; n < 3; n++) await page.locator('[data-scroll="previous"]').click();
      await page.waitForTimeout(2000);
      report.push({motion, direction: 'rapid-previous', ...await page.locator('main h2, main h3')
        .nth(count - 5).evaluate(element => ({title: element.textContent, top: element.getBoundingClientRect().top}))});
      await page.mouse.wheel(0, 250);
      await page.waitForTimeout(700);
      const manualTop = await page.locator('main h2, main h3').nth(count - 5)
        .evaluate(element => element.getBoundingClientRect().top);
      assert(Math.abs(manualTop - 16) > 100, 'Manual scrolling must release destination tracking');
      await page.close();
    }
    console.log(JSON.stringify(report, null, 2));
    assert(report.every(row => Math.abs(row.top - 16) < 3), 'Previous must align each successive heading at 16px');
  } finally {
    if (process.env.NOTEBOOK_REPORT) fs.writeFileSync(process.env.NOTEBOOK_REPORT, JSON.stringify(report, null, 2)+'\n');
    if (browser) await browser.close();
    server.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
