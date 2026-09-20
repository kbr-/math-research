// Optional real-browser regression/profile: requires the user's installed Playwright
// and Chromium. Run through compute.sh; no downloads or dependency installation.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const {chromium} = require('playwright');

(async () => {
  const template = fs.readFileSync(process.env.NOTEBOOK_TEMPLATE || 'index.html', 'utf8');
  const notebook = fs.readFileSync('notebook.html', 'utf8');
  const html = template.replace('__REVISION__', 'browser-test').replace('<!-- NOTEBOOK -->', notebook);
  const recordEnd = notebook.lastIndexOf('</section>');
  const articles = notebook.slice(notebook.indexOf('<article '), recordEnd);
  const extraArticles = [1, 2].map(n => articles.replace(/\bid="([^"]+)"/g, `id="growth-${n}-$1"`)).join('');
  const growingNotebook = notebook.slice(0, recordEnd) + extraArticles + notebook.slice(recordEnd);
  const growingHtml = template.replace('__REVISION__', 'browser-test').replace('<!-- NOTEBOOK -->', growingNotebook);
  const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', req.url === '/revision' ? 'application/json' : 'text/html');
    res.end(req.url === '/revision' ? '{"revision":"browser-test"}' : req.url.includes('growth=1') ? growingHtml : html);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  let browser;
  const report = {browser: '', samples: [], errors: []};
  try {
    browser = await chromium.launch({headless: true});
    report.browser = browser.version();
    const page = await browser.newPage({reducedMotion: 'reduce'});
    page.on('pageerror', error => report.errors.push(error.message));
    await page.addInitScript(() => {
      window.longTasks = [];
      new PerformanceObserver(list => longTasks.push(...list.getEntries().map(e => e.duration)))
        .observe({type: 'longtask', buffered: true});
      window.rectReads = 0;
      const original = Element.prototype.getBoundingClientRect;
      Element.prototype.getBoundingClientRect = function () { rectReads++; return original.call(this); };
    });
    const url = `http://127.0.0.1:${server.address().port}/`;
    async function sample(stage) {
      const data = await page.evaluate(() => ({
        elapsedMs: performance.now(), registeredMath: [...MathJax.startup.document.math].length,
        nodes: document.querySelectorAll('*').length, rectReads,
        mathErrors: document.querySelectorAll('[data-mml-node="merror"]').length,
        longestTaskMs: Math.max(0, ...longTasks), blockingMs: longTasks.reduce((a, b) => a + b, 0),
      }));
      report.samples.push({stage, ...data});
      assert.equal(data.mathErrors, 0, 'Visited math must typeset without errors');
      return data;
    }
    async function ready() {
      await page.waitForFunction(() => window.mathReady);
      await page.waitForFunction(() => document.querySelector('mjx-container svg'));
      await page.waitForTimeout(1000);
    }
    async function visibleMath() {
      await page.waitForFunction(() => [...document.querySelectorAll('mjx-container')].some(node => {
        const box = node.getBoundingClientRect();
        return box.top < innerHeight && box.bottom > 0;
      }));
    }
    const cdp = await page.context().newCDPSession(page);
    async function checkSearch(label) {
      assert.equal(await page.evaluate(() => performance.getEntriesByName('notebook-search-index').length), 0,
        'No search index should be built at page load');
      await page.locator('#search-open').click();
      assert.equal(await page.evaluate(() => performance.getEntriesByName('notebook-search-index').length), 0,
        'Opening search with an empty query should not build an index');
      await cdp.send('HeapProfiler.collectGarbage');
      const beforeHeap = (await cdp.send('Runtime.getHeapUsage')).usedSize;
      let navigated = false;
      async function query(text, stage) {
        await page.evaluate(text => {
          const input = document.getElementById('search-query');
          window.searchProbe = {start: performance.now(), last: performance.now(), worstGap: 0,
            mathBefore: [...MathJax.startup.document.math].length};
          window.searchHeartbeat = setInterval(() => {
            const now = performance.now();
            searchProbe.worstGap = Math.max(searchProbe.worstGap, now - searchProbe.last);
            searchProbe.last = now;
          }, 16);
          input.value = text;
          input.dispatchEvent(new Event('input', {bubbles: true}));
        }, text);
        await page.waitForFunction(() => document.getElementById('search-status').dataset.state === 'ready');
        await page.waitForTimeout(50);
        const measurement = await page.evaluate(() => {
          clearInterval(searchHeartbeat);
          const measure = performance.getEntriesByName('notebook-search-query').at(-1);
          return {
            indexMs: performance.getEntriesByName('notebook-search-index').at(-1)?.duration,
            queryMs: measure.duration,
            resultsAfterMs: measure.startTime + measure.duration - searchProbe.start,
            longestHeartbeatGapMs: searchProbe.worstGap,
            mathBefore: searchProbe.mathBefore, mathAfter: [...MathJax.startup.document.math].length,
            status: document.getElementById('search-status').textContent,
          };
        });
        // After choosing a result, nearby math may still be finishing independently
        // of a subsequent query. Assert isolation before that navigation begins.
        if (!navigated) assert.equal(measurement.mathAfter, measurement.mathBefore,
          'Searching must not typeset unseen math');
        report.samples.push({stage: `${label}-${stage}`, ...measurement});
        return measurement;
      }
      const first = await query('\\mathcal', 'first-search');
      assert(!first.status.startsWith('No matching'));
      assert(await page.locator('#search-results button').count() <= 30, 'Bound result DOM size');
      await cdp.send('HeapProfiler.collectGarbage');
      report.samples.push({stage: `${label}-search-memory`, heapBeforeBytes: beforeHeap,
        heapAfterBytes: (await cdp.send('Runtime.getHeapUsage')).usedSize});
      await query('companion', 'repeat-search');
      assert.equal(await page.evaluate(() => performance.getEntriesByName('notebook-search-index').length), 1,
        'Later searches must reuse the same index');
      await page.locator('#search-next').click();
      assert((await page.locator('#search-status').textContent()).includes('31–'));
      await page.locator('#search-previous').click();
      // Search already rendered TeX and untouched late TeX through the same source index.
      await query('\\mathrm{AC}^0[p]', 'rendered-tex');
      assert(await page.locator('#search-results button').count() > 0);
      await query('finite-domain branch interpolation', 'late-prose');
      assert(await page.locator('#search-results button').count() > 0);
      await page.locator('#search-results button').last().click();
      navigated = true;
      assert(await page.locator('#notebook-search').isHidden());
      await page.waitForFunction(() => {
        const hit = document.querySelector('.search-hit');
        const box = hit?.getBoundingClientRect();
        return box && box.top < innerHeight && box.bottom > 0;
      });
      await page.keyboard.press('/');
      assert(await page.locator('#notebook-search').isVisible());
      await page.locator('#search-case').check();
      await query('FINITE-DOMAIN BRANCH INTERPOLATION', 'case-sensitive-negative');
      assert.equal(await page.locator('#search-results button').count(), 0);
      await page.locator('#search-case').uncheck();
      await query('FINITE-DOMAIN BRANCH INTERPOLATION', 'case-insensitive');
      assert(await page.locator('#search-results button').count() > 0);
      await query('<script>not-a-result</script>', 'negative');
      assert.equal(await page.locator('#search-results button').count(), 0);
      // Fast edits cancel old work; the last query wins.
      await page.locator('#search-query').fill('companion');
      await page.locator('#search-query').fill('no-such-notebook-passage-7319');
      await page.waitForFunction(() => document.getElementById('search-status').dataset.state === 'ready');
      assert.equal(await page.locator('#search-results button').count(), 0);
      await page.keyboard.press('Escape');
      assert(await page.locator('#notebook-search').isHidden());
    }
    await page.goto(url, {waitUntil: 'domcontentloaded'});
    await ready();
    const initial = await sample('top');
    if (process.env.NOTEBOOK_PROFILE_ONLY) {
      await page.evaluate(() => { location.hash = [...document.querySelectorAll('.research-entry')].at(-1).id; });
      await page.waitForTimeout(2000);
      await sample('end');
      console.log(JSON.stringify(report, null, 2));
      return;
    }
    assert.equal(await page.locator('#search-open').innerText(), 'Search notebook (/)');
    await checkSearch('current');
    await page.goto(url + '?aftersearch=1', {waitUntil: 'domcontentloaded'});
    await ready();
    assert(initial.registeredMath < 100, 'Startup must not register the whole research record');
    const last = await page.locator('.research-entry').last().getAttribute('id');
    const deep = await page.locator('.research-entry').last().locator('h4[id]').first().getAttribute('id');
    await page.evaluate(id => { location.hash = id; }, deep);
    await visibleMath();
    await page.waitForTimeout(1000);
    const afterJump = await sample('deep-link');
    assert(afterJump.registeredMath < 300, 'Jumping to the end must not process earlier entries');
    assert(await page.locator(`#${last} mjx-container`).count() > 0);
    assert.equal(await page.locator('.research-entry').nth(30).locator('mjx-container').count(), 0,
      'Unvisited middle entries must remain unprocessed');
    const findText = (await page.locator('.research-entry').nth(30).locator('h3').textContent()).trim();
    assert(await page.evaluate(text => window.find(text, false, false, true), findText),
      `Browser text search must find an unvisited entry: ${JSON.stringify(findText)}`);
    await visibleMath();
    // Use a long older proof to exercise more than one viewport of math.
    await page.evaluate(() => { location.hash = 'entry-2026-09-11-mp-composition'; });
    await visibleMath();
    await page.waitForTimeout(1000);
    const beforeScroll = await sample('long-entry');
    await page.mouse.wheel(0, 800);
    await page.waitForTimeout(1000);
    await visibleMath();
    assert((await sample('scrolled')).registeredMath > beforeScroll.registeredMath,
      'Scrolling must render newly visible blocks');
    // Actual browser history and deep-link startup, including layout containment.
    await page.goBack();
    await page.waitForTimeout(500);
    await page.goto(url + '?direct=1#' + deep, {waitUntil: 'domcontentloaded'});
    await ready();
    await visibleMath();
    const direct = await sample('direct-deep-link');
    assert(direct.registeredMath < 300);
    const targetTop = await page.locator(`#${deep}`).evaluate(node => node.getBoundingClientRect().top);
    assert(Math.abs(targetTop) < 150, `Deep link moved out of view: ${targetTop}`);
    await page.locator('[data-scroll="top"]').click();
    await page.waitForFunction(() => scrollY < 2);
    await page.locator('[data-scroll="end"]').click();
    await page.waitForTimeout(1000);
    assert(await page.evaluate(() => Math.abs(document.documentElement.scrollHeight - innerHeight - scrollY) < 3),
      'End navigation must follow deferred layout');
    // Mobile layout uses the same viewport scheduler.
    await page.setViewportSize({width: 390, height: 844});
    await page.goto(url, {waitUntil: 'domcontentloaded'});
    await ready();
    assert((await sample('mobile-top')).registeredMath < 100);
    assert.equal(await page.locator('#search-open').evaluate(node => getComputedStyle(node).opacity), '0.75');
    assert.equal(await page.locator('#search-open').innerText(), 'Search notebook (/)',
      'A narrow desktop window keeps the keyboard hint');
    assert.equal(await page.locator('mjx-merror').count(), 0);
    const touchPage = await browser.newPage({isMobile: true, hasTouch: true,
      viewport: {width: 390, height: 844}});
    touchPage.on('pageerror', error => report.errors.push(error.message));
    await touchPage.goto(url, {waitUntil: 'domcontentloaded'});
    assert.equal(await touchPage.locator('#search-open').innerText(), 'Search notebook');
    assert.equal(await touchPage.locator('#search-open').evaluate(node => getComputedStyle(node).opacity), '0.75');
    await touchPage.keyboard.press('/');
    assert(await touchPage.locator('#notebook-search').isVisible());
    assert.equal(await touchPage.locator('#search-open').innerText(), 'Search notebook (/)',
      'Using a keyboard on a touch device reveals the shortcut');
    await touchPage.keyboard.press('Escape');
    await touchPage.waitForFunction(() => window.mathReady);
    await touchPage.evaluate(() => window.scrollTo(0, 100));
    await touchPage.locator('[data-scroll="end"]').tap();
    await touchPage.waitForTimeout(2000);
    const touchHeadingCount = await touchPage.locator('main h2, main h3').count();
    for (let n = 0; n < 3; n++) await touchPage.locator('[data-scroll="previous"]').tap();
    await touchPage.waitForTimeout(2000);
    const touchTop = await touchPage.locator('main h2, main h3').nth(touchHeadingCount - 4)
      .evaluate(node => node.getBoundingClientRect().top);
    assert(Math.abs(touchTop - 16) < 3, `Repeated touch navigation lost its target: ${touchTop}`);
    await touchPage.close();
    await page.setViewportSize({width: 1280, height: 720});
    await page.goto(url + '?growth=1', {waitUntil: 'domcontentloaded'});
    await ready();
    const growing = await sample('triple-record-top');
    assert.equal(growing.registeredMath, initial.registeredMath,
      'Tripling the unvisited record must not add startup MathJax work');
    await checkSearch('triple');
    assert.deepEqual(report.errors, []);
    console.log(JSON.stringify(report, null, 2));
  } finally {
    if (process.env.NOTEBOOK_REPORT) fs.writeFileSync(process.env.NOTEBOOK_REPORT, JSON.stringify(report, null, 2)+'\n');
    if (browser) await browser.close();
    server.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
