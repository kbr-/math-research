// Real-browser acceptance for side notebooks, on the published (static) and live routes: startup
// fetches no other notebook, search spans all notebooks only on request, a result opens its side
// notebook, history returns, and a live side page offers a reload when its source changes.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');
const {spawn, execFile} = require('node:child_process');
const {promisify} = require('node:util');
const {main, notebook} = require('./browser_support.cjs');

const ENTRIES = 40;

// A repository with a small main notebook and two side notebooks, each with ENTRIES matching entries.
async function repository(root, site) {
  fs.writeFileSync(path.join(root, 'main-notebook.html'), notebook({entries: 5}).replace(
    '<section id="research-record">', () => String.raw`<section id="math-angles"><h2>Comparisons</h2>
      <p>\(P_{<a}>0\) and \[x<y>z\] and $$u<v>w$$.</p></section><section id="research-record">`));
  await promisify(execFile)('python3', ['-c', `
import sys, shutil
from pathlib import Path
root = Path(sys.argv[1]); repo = Path.cwd(); sys.path.insert(0, str(repo / 'tools'))
from branch import create, SECTIONS
for name in ['index.html', 'server.py', 'LICENSES/MIT.txt', 'CITATION.cff', 'research/context-budgets.json',
             'tools/notebooks.py', 'tools/notebook_site.py', 'tools/notebook_math.py']:
    p = root / name; p.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(repo / name, p)
(root / 'main-notebook.html').rename(root / 'notebook.html')
context = {k: '<p>Initial context.</p>' for k in SECTIONS}
context['goal'] = 'Independent test thread'
context['remaining-route'] = '<li data-route-item="side-test">Test obligation</li>'
for name in ['alpha', 'beta']:
    create(name, name.title(), context, root)
    p = root / 'research/branches' / name / 'notebook.html'
    entries = ''.join(f'<article id="{name}-{i}"><h3>Entry {i}</h3><p>\\\\(\\\\operatorname{{sideprobe}} x\\\\) '
                      f'{name} unique-target</p></article>' for i in range(${ENTRIES}))
    s = p.read_text(); n = s.rfind('</section>'); p.write_text(s[:n] + entries + s[n:])
if sys.argv[2] == 'static':
    from build_pages import build
    build(root / 'site', 'https://example.github.io/math-research/', root)
`, root, site ? 'static' : 'live']);
}

async function staticServer(root) {
  const server = http.createServer((req, res) => {
    let file = decodeURIComponent(req.url.split('?')[0]).replace(/^\/math-research\//, '');
    if (!file || file.endsWith('/')) file += 'index.html';
    const dest = path.resolve(root, 'site', file);
    if (!dest.startsWith(path.resolve(root, 'site') + path.sep)) { res.writeHead(404); res.end(); return; }
    try {
      res.setHeader('Content-Type', file.endsWith('.json') ? 'application/json' : 'text/html');
      res.end(fs.readFileSync(dest));
    } catch { res.writeHead(404); res.end(); }
  });
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  return {url: `http://127.0.0.1:${server.address().port}/math-research/`,
    close: () => { server.closeAllConnections(); server.close(); }};
}

async function liveServer(root) {
  const reserve = http.createServer();
  await new Promise(resolve => reserve.listen(0, '127.0.0.1', resolve));
  const port = reserve.address().port;
  await new Promise(resolve => reserve.close(resolve));
  const server = spawn('python3', [path.join(root, 'server.py'), '--port', String(port)], {stdio: ['ignore', 'pipe', 'pipe']});
  await new Promise((resolve, reject) => {
    server.stdout.once('data', resolve);
    server.once('exit', () => reject(new Error('Live server failed')));
  });
  return {url: `http://127.0.0.1:${port}/math-research/`, close: () => server.kill()};
}

const sideNotebooks = mode => async browser => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'side-notebook-browser-'));
  let page, server;
  const errors = [];
  try {
    await repository(root, mode === 'static');
    server = await (mode === 'static' ? staticServer(root) : liveServer(root));
    page = await browser.newPage();
    page.setDefaultTimeout(5000);
    const requests = [];
    page.on('request', request => requests.push(request.url()));
    page.on('pageerror', error => errors.push(error.message));
    const otherNotebooks = () => requests.filter(url => /notebooks\.json|notebook-source/.test(url)).length;
    await page.goto(server.url, {waitUntil: 'load'});
    await page.waitForFunction(() => window.mathReady);
    // Exercise production source() in both the live handler and the Pages builder.
    // MathJax sees the complete TeX only if HTML parsing did not consume its comparisons.
    await page.locator('#math-angles').scrollIntoViewIfNeeded();
    await page.waitForFunction(() => [...document.querySelectorAll('#math-angles mjx-container')]
      .filter(node => node.querySelector('svg')).length === 3);
    const formulas = await page.evaluate(() => [...MathJax.startup.document.math].map(item => item.math));
    for (const formula of [String.raw`P_{<a}>0`, 'x<y>z', 'u<v>w']) assert.ok(formulas.includes(formula), formula);
    assert.equal(await page.locator('#math-angles [data-mml-node="merror"]').count(), 0);
    const payload = await page.request.get(server.url + 'notebook-source.html');
    assert.equal(payload.status(), 200);
    assert.ok((await payload.text()).includes(String.raw`\(P_{&lt;a}&gt;0\)`));
    assert.equal(otherNotebooks(), 0, `${mode}: no other notebooks fetched on startup`);
    assert.equal(await page.locator('#search-scope').inputValue(), 'current');
    await page.locator('#search-open').click();
    await page.locator('#search-query').fill('sideprobe');
    await page.waitForFunction(() => document.getElementById('search-status').dataset.state === 'ready');
    assert.match(await page.locator('#search-status').textContent(), /No matching/);
    assert.equal(otherNotebooks(), 0, `${mode}: searching the current notebook fetches no other`);
    await page.locator('#search-scope').selectOption('all');
    await page.waitForFunction(() => document.getElementById('search-status').dataset.state === 'ready');
    assert.match(await page.locator('#search-status').textContent(), new RegExp(`${2 * ENTRIES} matching`));
    await page.locator('#search-results button').first().click();
    await page.waitForURL('**/branches/alpha/#alpha-0');
    assert.match(await page.locator('.thread-navigation').textContent(), /Alpha/);
    if (mode === 'live') {
      const revision = await page.request.get(server.url + 'branches/alpha/revision');
      assert.equal(revision.status(), 200);
      fs.appendFileSync(path.join(root, 'research/branches/alpha/notebook.html'), '\n<!-- live-change -->');
      // The live page offers a reload rather than reloading by itself.
      await page.locator('#update-notice').waitFor({state: 'visible', timeout: 3000});
      await Promise.all([page.waitForEvent('load'), page.locator('#update-notice').click()]);
      assert.ok((await page.content()).includes('live-change'), 'Side page reloads its changed source');
    }
    await page.setViewportSize({width: 390, height: 844});
    assert.ok(await page.locator('#search-open').isVisible());
    await page.goBack();
    assert.equal(new URL(page.url()).pathname, new URL(server.url).pathname, `${mode}: history returns`);
    assert.deepEqual(errors, []);
  } finally {
    if (page) await page.close();
    if (server) server.close();
    fs.rmSync(root, {recursive: true, force: true});
  }
};
const cases = {static: sideNotebooks('static'), live: sideNotebooks('live')};
module.exports = cases;
main(module, cases);
