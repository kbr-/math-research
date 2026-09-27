// Shared setup for the real-browser notebook tests: small generated notebooks, a local server,
// and a disk cache for the MathJax files the page loads from its CDN, so a run does not wait on
// the network. Uses the installed Playwright; no downloads beyond what the page itself loads.
const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const {chromium} = require('playwright');

const CACHE = path.join(process.env.XDG_CACHE_HOME || path.join(os.homedir(), '.cache'), 'notebook-browser-tests');

// Serve every CDN request from the disk cache, fetching and storing it on the first run.
async function cacheCdn(context) {
  fs.mkdirSync(CACHE, {recursive: true});
  await context.route('https://cdn.jsdelivr.net/**', async route => {
    const key = crypto.createHash('sha256').update(route.request().url()).digest('hex');
    const file = path.join(CACHE, key);
    if (!fs.existsSync(file)) {
      const response = await route.fetch();
      if (!response.ok()) return route.fulfill({response});
      const tmp = `${file}.${process.pid}`;
      fs.writeFileSync(tmp, JSON.stringify({type: response.headers()['content-type'] || '',
        body: (await response.body()).toString('base64')}));
      fs.renameSync(tmp, file);
    }
    const {type, body} = JSON.parse(fs.readFileSync(file, 'utf8'));
    await route.fulfill({status: 200, contentType: type, body: Buffer.from(body, 'base64'),
      headers: {'access-control-allow-origin': '*'}});
  });
}

async function launch() {
  const browser = await chromium.launch({headless: true});
  // Tests search without the typing delay and poll a live notebook quickly; the page reads these
  // overrides before its defaults.
  const newContext = browser.newContext.bind(browser);
  // Every page gets the cache, including pages opened with options.
  browser.newPage = async (options = {}) => {
    const context = await newContext(options);
    await cacheCdn(context);
    await context.addInitScript(() => { window.notebookSearchDelayMs = 0; window.notebookPollMs = 50; });
    const page = await context.newPage();
    page.on('close', () => context.close().catch(() => {}));
    return page;
  };
  return browser;
}

// A notebook page from the repository's layout and the given body.
function page(body, revision = 'browser-test') {
  const template = fs.readFileSync(process.env.NOTEBOOK_TEMPLATE || 'index.html', 'utf8');
  return template.replace('__REVISION__', revision).replace('<!-- NOTEBOOK -->', body);
}

// A generated notebook: living sections, then a research record of `entries` articles, each
// with inline and display math, a subsection, and the word "companion"; `copies` repeats the
// record under other ids. The entries listed in `long` have many paragraphs of math, and the last
// entry holds the late prose "finite-domain branch interpolation".
function notebook({entries = 60, long = [5], copies = 1} = {}) {
  const living = ['where-we-stand', 'open-statements', 'remaining-route', 'proposed-next-step']
    .map(id => `<section id="${id}"><h2>${id.replace(/-/g, ' ')}</h2>` +
      `<p>Living summary with \\(\\mathrm{AC}^0[p]\\).</p></section>`).join('\n');
  const articles = [];
  for (let copy = 0; copy < copies; copy++) for (let n = 0; n < entries; n++) {
    const prefix = copy ? `copy${copy}-entry` : 'entry';
    const paragraphs = long.includes(n) ? 40 : 2;
    // Few, simple equations: typesetting is most of a page load's cost.
    const body = Array.from({length: paragraphs}, (_, p) =>
      `<p>Paragraph ${p} of entry ${n} uses a companion \\(\\mathcal{C}_{${p}}\\) in prose long enough ` +
      'to wrap over more than one line of the narrowest layout.</p>' + (p % 5 ? '' : `\\[b_{${n}} = ${p}\\]`)).join('\n');
    const late = n === entries - 1 && copy === copies - 1 ? '<p>This closes the finite-domain branch interpolation.</p>' : '';
    articles.push(`<article class="research-entry" id="${prefix}-${n}"><h3>Entry ${n} heading title</h3>` +
      `<p class="entry-meta">Status: working.</p>${body}<h4 id="${prefix}-${n}-detail">Detail ${n}</h4>` +
      `<p>Detail ${n}.</p>${late}</article>`);
  }
  return `<h1>Generated notebook</h1><p class="intro">Intro \\(\\mathrm{AC}^0[p]\\).</p>\n${living}\n` +
    `<section id="research-record"><h2>Research record</h2>\n${articles.join('\n')}\n</section>`;
}

// A local HTTP server; `routes` maps a path (without query) to [content type, body] or a function.
async function serve(routes) {
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://x');
    let route = routes[url.pathname] || routes['*'];
    if (typeof route === 'function') route = route(url);
    if (!route) { res.writeHead(404); res.end(); return; }
    res.setHeader('Content-Type', route[0]);
    res.end(route[1]);
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  server.url = `http://127.0.0.1:${server.address().port}/`;
  return server;
}

// Resolves once the page's math scheduler is idle and has rendered nothing for `quietMs`, which
// covers the observer callbacks that queue the next blocks.
function mathSettled(target, quietMs = 50) {
  return target.evaluate(quietMs => new Promise(resolve => {
    let timer;
    const reset = () => { clearTimeout(timer); timer = setTimeout(done, quietMs); };
    function done() {
      if (window.mathBusy) return reset();
      removeEventListener('notebook-math-rendered', reset);
      resolve();
    }
    addEventListener('notebook-math-rendered', reset);
    reset();
  }), quietMs);
}

// Once MathJax has started and the scheduler has settled.
async function ready(target) {
  await target.waitForFunction(() => window.mathReady && document.querySelector('mjx-container svg'));
  await mathSettled(target);
}

// How many equations MathJax has registered on the page.
function registered(target) {
  return target.evaluate(() => [...MathJax.startup.document.math].length);
}

// Until some rendered equation is in the viewport.
function visibleMath(target) {
  return target.waitForFunction(() => [...document.querySelectorAll('mjx-container')].some(node => {
    const box = node.getBoundingClientRect();
    return box.top < innerHeight && box.bottom > 0;
  }));
}

// A test case: given a browser, runs `body` against a server for `routes`; `open(options)` opens a
// page in its own context with short timeouts, and any page error fails the case.
function browserCase(routes, body) {
  return async browser => {
    const server = await serve({'/revision': ['application/json', '{"revision":"browser-test"}'], ...routes});
    const errors = [];
    const pages = [];
    try {
      const open = async (options = {}) => {
        const target = await browser.newPage(options);
        pages.push(target);
        target.setDefaultTimeout(5000);
        target.on('pageerror', error => errors.push(error.message));
        return target;
      };
      await body({url: server.url, open});
      if (errors.length) throw new Error(`Page errors: ${errors.join('; ')}`);
    } finally {
      await Promise.all(pages.map(target => target.close().catch(() => {})));
      server.closeAllConnections();
      server.close();
    }
  };
}

// Runs the named cases (all when none are named) concurrently in one browser, printing one JSON line
// per case with its outcome and seconds; the exit status is nonzero if any case fails.
async function runCases(cases, names = []) {
  const selected = names.length ? names : Object.keys(cases);
  const browser = await launch();
  try {
    const results = await Promise.all(selected.map(async name => {
      const start = performance.now();
      try {
        if (!cases[name]) throw new Error(`No such case: ${name}`);
        await cases[name](browser);
        return {name, ok: true, seconds: (performance.now() - start) / 1000};
      } catch (error) {
        return {name, ok: false, seconds: (performance.now() - start) / 1000, error: String(error.stack || error)};
      }
    }));
    for (const result of results) console.log(JSON.stringify(result));
    if (results.some(result => !result.ok)) process.exitCode = 1;
  } finally {
    await browser.close();
  }
}

// Runs a test file's cases when the file itself is run, so each file also works on its own.
function main(module, cases) {
  if (require.main === module) runCases(cases, process.argv.slice(2))
    .catch(error => { console.error(error); process.exitCode = 1; });
}

module.exports = {browserCase, runCases, main, launch, page, notebook, serve, ready, registered, visibleMath,
  mathSettled, cacheCdn, CACHE};
