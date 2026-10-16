#!/usr/bin/env node
// Retrieve a source the way a person's browser does: open URL, wait for the page, and save the page,
// or with --download (or --click TEXT) the file it serves. For sources that refuse scripted clients:
// curl gets a 403 or a bot wall, a browser may not.
//
// Engine: the installed Firefox by default (the user's browser), driven over WebDriver BiDi by
// tools/browser_firefox.cjs, in its own headless process on a fresh temporary profile that is deleted
// afterwards; the user's open windows and profile are never touched. --engine chromium uses the
// installed Playwright instead.
//
// Session: the browser carries the cookies the user's own Firefox holds for the site and its parent
// domains (copied from the profile's cookie store by tools/firefox_cookies.py --site), which is what
// passes a wall a bare browser meets: on 16 October 2026 ResearchGate served a challenge page to
// headless Firefox and Chromium alike, and the user's browser downloaded the file with one click.
// --cookies FILE overrides; without either, a file saved at ~/.cache/cookies-HOST.json is used.
//
// Clicks: at most one link, named by --click, among visible links and buttons, preferring one on the
// page's own site over an advertisement with the same words; no form is submitted. An ad blocker runs
// in the browser when present: uBlock Origin (~/.cache/browser-extensions/uBlock0.firefox.signed.xpi)
// in Firefox, uBlock Origin Lite (~/.cache/browser-extensions/uBOLite) in Chromium, or --extension.
//
//   node tools/browser_get.cjs URL --out FILE [--download] [--click TEXT] [--engine firefox|chromium]
//        [--cookies FILE | --no-cookies | --no-main-firefox] [--firefox-db COOKIES_SQLITE]
//        [--extension PATH | --no-extension] [--headed] [--timeout SECONDS]
//
// Prints the final URL, the HTTP status of the main response, whether the page looks like a
// challenge, and the saved file's size; exits 1 when the status is 400 or above or nothing was saved,
// 2 on a usage error or when Playwright cannot be loaded, and 3 when pacing refuses the visit.
//
// Pacing (tools/browser_pacing.cjs): visits to one outside site are at least 90 s apart and at most 10
// an hour, recorded across runs; within a visit the tool reads for a few seconds, scrolls, and moves the
// pointer to the link before clicking, as a person does. A doi.org link is resolved first by asking
// doi.org alone, so the publisher's page is opened once. On a challenge page the tool does not click.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const USAGE = 'usage: node tools/browser_get.cjs URL --out FILE [--download] [--click TEXT] '
  + '[--cookies FILE] [--no-cookies] [--extension DIR | --no-extension] [--headed] [--timeout SECONDS]';
const CHALLENGE = /captcha|verify you are human|just a moment|incapsula|access denied|temporarily unavailable/i;

function parse(argv) {
  const opt = {download: false, click: null, timeout: 60, headed: false, cookies: null, noCookies: false};
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out') opt.out = argv[++i];
    else if (a === '--download') opt.download = true;
    else if (a === '--click') opt.click = argv[++i];
    else if (a === '--cookies') opt.cookies = argv[++i];
    else if (a === '--no-cookies') opt.noCookies = true;
    else if (a === '--headed') opt.headed = true;
    else if (a === '--extension') opt.extension = argv[++i];
    else if (a === '--no-extension') opt.noExtension = true;
    else if (a === '--engine') opt.engine = argv[++i];
    else if (a === '--firefox-db') opt.firefoxDb = argv[++i];
    else if (a === '--no-main-firefox') opt.noMainFirefox = true;
    else if (a === '--timeout') opt.timeout = Number(argv[++i]);
    else if (a.startsWith('--')) return null;
    else rest.push(a);
  }
  opt.url = rest[0];
  if (rest.length !== 1 || !opt.out || !(opt.timeout > 0)) return null;
  opt.engine = opt.engine || 'firefox';
  if (!['firefox', 'chromium'].includes(opt.engine)) return null;
  return opt;
}

// Playwright from the local tree, NODE_PATH, or the global modules of the node that runs this script.
function loadPlaywright() {
  const places = ['playwright', path.join(path.dirname(process.execPath), '..', 'lib', 'node_modules', 'playwright')];
  for (const place of places) {
    try { return require(place); } catch (e) { /* try the next place */ }
  }
  return null;
}

// The cookies firefox_cookies.py saved (name, value, domain, path, expires), in Playwright's form.
// The site's cookies, in order: --cookies FILE; else those the user's own Firefox holds now for the site
// and its parent domains (read by tools/firefox_cookies.py from a copy of the profile's cookie store,
// so a run is signed in wherever the user is; user, 16 October 2026); else a file firefox_cookies.py
// saved earlier at ~/.cache/cookies-HOST.json.
function fromMainFirefox(host, db) {
  const {spawnSync} = require('node:child_process');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'browser-get-cookies-'));
  try {
    const out = path.join(dir, 'cookies.json');
    const args = [path.join(__dirname, 'firefox_cookies.py'), host, '--site', '--out', out, ...(db ? ['--db', db] : [])];
    const done = spawnSync('python3', args, {encoding: 'utf8'});
    return done.status === 0 && fs.existsSync(out) ? fs.readFileSync(out, 'utf8') : null;
  } finally {
    fs.rmSync(dir, {recursive: true, force: true});
  }
}

function savedCookies(opt) {
  if (opt.noCookies) return [];
  const host = new URL(opt.url).hostname;
  let text = null;
  let file = opt.cookies;
  if (file && !fs.existsSync(file)) throw new Error(`no cookie file at ${file}`);
  if (!file && !opt.noMainFirefox) {
    text = fromMainFirefox(host, opt.firefoxDb);
    if (text) file = `the main Firefox profile (${host} and parent domains)`;
  }
  if (!file) {
    file = path.join(os.homedir(), '.cache', `cookies-${host}.json`);
    if (!fs.existsSync(file)) return [];
  }
  const list = JSON.parse(text || fs.readFileSync(file, 'utf8')).map(c => ({
    name: c.name, value: String(c.value), domain: c.domain, path: c.path || '/',
    expires: c.expires > 1e11 ? Math.floor(c.expires / 1000) : (c.expires || -1)}));
  console.log(`cookies: ${list.length} from ${file}`);
  return list;
}

// Where a doi.org link leads, asked of doi.org alone (it answers with a redirect and nothing is fetched
// from the publisher), so the browser opens the publisher's page once, with its cookies.
async function resolveDoi(url) {
  let current = url;
  for (let hop = 0; hop < 3 && /(^|\.)doi\.org$/.test(new URL(current).hostname); hop++) {
    const answer = await fetch(current, {method: 'HEAD', redirect: 'manual'}).catch(() => null);
    const next = answer && answer.headers.get('location');
    if (!next) break;
    current = new URL(next, current).href;
  }
  return current;
}

// Before either engine opens the page: resolve a doi.org link, gather the cookies of the site it lands
// on, and space the visit after the last one to that site (tools/browser_pacing.cjs). Exits 2 on a bad
// cookie file and 3 when pacing refuses the visit.
async function prepare(opt) {
  opt.url = await resolveDoi(opt.url);
  let cookies;
  try { cookies = savedCookies(opt); } catch (e) { console.error(`browser_get: ${e.message}`); process.exit(2); }
  try {
    await require('./browser_pacing.cjs').beforeVisit(opt.url, line => console.log(line));
  } catch (e) {
    console.error(`browser_get: ${e.message}`);
    process.exit(3);
  }
  console.log(`opening: ${opt.url}`);
  return cookies;
}

// The default engine: the installed Firefox, driven over WebDriver BiDi (tools/browser_firefox.cjs).
async function mainFirefox(opt) {
  if (typeof WebSocket === 'undefined') {
    // Node 20 has its WebSocket client behind a flag: run again with it.
    const {spawnSync} = require('node:child_process');
    const again = spawnSync(process.execPath, ['--experimental-websocket', '--no-warnings', __filename,
      ...process.argv.slice(2)], {stdio: 'inherit'});
    process.exit(again.status === null ? 1 : again.status);
  }
  const cookies = await prepare(opt);
  const {firefoxGet} = require('./browser_firefox.cjs');
  const result = await firefoxGet(opt, cookies, blocker(opt), pickTarget, isChallenge,
    (line, error) => (error ? console.error : console.log)(line));
  console.log(`final URL: ${result.finalUrl}`);
  console.log(`status: ${result.status}`);
  console.log(`challenge page: ${result.challenge ? 'yes' : 'no'}`);
  console.log(`saved: ${result.saved} bytes to ${opt.out}`);
  process.exit(result.status >= 400 || result.saved === 0 ? 1 : 0);
}

async function main() {
  const opt = parse(process.argv.slice(2));
  if (!opt) { console.error(USAGE); process.exit(2); }
  if (opt.engine === 'firefox') return mainFirefox(opt);
  const playwright = loadPlaywright();
  if (!playwright) { console.error('browser_get: Playwright cannot be loaded (local, NODE_PATH or global).'); process.exit(2); }
  const cookies = await prepare(opt);
  const extension = blocker(opt);
  let browser = null;
  let context;
  let profile = null;
  if (extension) {
    // An extension needs a persistent profile and the full Chromium build, which runs it headless too.
    profile = fs.mkdtempSync(path.join(os.tmpdir(), 'browser-get-'));
    context = await playwright.chromium.launchPersistentContext(profile, {channel: 'chromium',
      headless: !opt.headed, acceptDownloads: true, locale: 'en-US',
      args: [`--disable-extensions-except=${extension}`, `--load-extension=${extension}`]});
    const worker = context.serviceWorkers()[0]
      || await context.waitForEvent('serviceworker', {timeout: 10000}).catch(() => null);
    console.log(`ad blocker: ${worker ? 'loaded' : 'NOT running'} from ${extension}`);
  } else {
    browser = await playwright.chromium.launch({headless: !opt.headed});
    context = await browser.newContext({acceptDownloads: true, locale: 'en-US'});
    console.log('ad blocker: none');
  }
  if (cookies.length) await context.addCookies(cookies);
  const page = context.pages()[0] || await context.newPage();
  const ms = opt.timeout * 1000;
  let status = 0;
  let saved = 0;
  let challenge = false;
  try {
    const response = await page.goto(opt.url, {waitUntil: 'domcontentloaded', timeout: ms});
    status = response ? response.status() : 0;
    await page.waitForLoadState('networkidle', {timeout: Math.min(ms, 15000)}).catch(() => {});
    challenge = isChallenge(await page.title(), await page.content());
    fs.mkdirSync(path.dirname(path.resolve(opt.out)), {recursive: true});
    if (opt.download || opt.click) {
      // A file arrives as a download, or as a PDF the browser opens in its viewer: take whichever comes.
      const download = page.waitForEvent('download', {timeout: ms}).then(d => ({download: d}));
      const pdf = context.waitForEvent('response', {timeout: ms,
        predicate: r => /application\/pdf/i.test(r.headers()['content-type'] || '')}).then(r => ({pdf: r}));
      download.catch(() => {});
      pdf.catch(() => {});
      if (opt.click) {
        // As in the Firefox engine: read a few seconds, scroll, rest the pointer on the link, then click.
        const {pause, isLocal} = require('./browser_pacing.cjs');
        await pause(page.url(), 2500, 6000);
        for (let step = 0; step < 3; step++) {
          await page.mouse.wheel(0, 120 + Math.floor(Math.random() * 200));
          await pause(page.url(), 400, 1200);
        }
        const target = await clickTarget(page, opt.click);
        console.log(`clicking: ${target.describe}`);
        const local = isLocal(new URL(page.url()).hostname);
        await target.locator.hover({timeout: ms});
        await pause(page.url(), 150, 600);
        await target.locator.click({timeout: ms, delay: local ? 0 : 70 + Math.floor(Math.random() * 90)});
      }
      const got = await Promise.any([download, pdf]);
      if (got.download) await got.download.saveAs(opt.out);
      // The viewer's response body is its own wrapper page: fetch the file again in the same session.
      else fs.writeFileSync(opt.out, await (await context.request.get(got.pdf.url())).body());
    } else {
      fs.writeFileSync(opt.out, await page.content());
    }
    saved = fs.existsSync(opt.out) ? fs.statSync(opt.out).size : 0;
  } catch (e) {
    console.error(`browser_get: ${e.message.split('\n')[0]}`);
  } finally {
    console.log(`final URL: ${page.url()}`);
    console.log(`status: ${status}`);
    console.log(`challenge page: ${challenge ? 'yes' : 'no'}`);
    console.log(`saved: ${saved} bytes to ${opt.out}`);
    await (browser || context).close();
    if (profile) fs.rmSync(profile, {recursive: true, force: true});
  }
  process.exit(status >= 400 || saved === 0 ? 1 : 0);
}

// Whether a page's title or opening text is a bot wall rather than the source.
function isChallenge(title, html) {
  return CHALLENGE.test(title) || CHALLENGE.test(html.slice(0, 20000));
}

// The ad blocker's unpacked directory: --extension DIR, else uBlock Origin Lite unpacked at
// ~/.cache/browser-extensions/uBOLite (the user's request of 16 October 2026: "make sure you don't click
// on an ad"); none with --no-extension or when it is not there.
function blocker(opt, home = os.homedir()) {
  if (opt.noExtension) return null;
  const store = path.join(home, '.cache', 'browser-extensions');
  if (opt.engine === 'firefox') {
    // Firefox runs the full uBlock Origin, from its signed release (an .xpi).
    const xpi = opt.extension || path.join(store, 'uBlock0.firefox.signed.xpi');
    if (fs.existsSync(xpi) && fs.statSync(xpi).isFile()) return path.resolve(xpi);
    if (opt.extension) console.error(`browser_get: no extension archive at ${xpi}; continuing without it`);
    return null;
  }
  const dir = opt.extension || path.join(store, 'uBOLite');
  if (fs.existsSync(path.join(dir, 'manifest.json'))) return path.resolve(dir);
  if (opt.extension) console.error(`browser_get: no extension manifest in ${dir}; continuing without it`);
  return null;
}

// The link or button to click: among a and button elements whose text contains TEXT, one pointing to
// the page's own site first, so that an advertisement with the same words on another site is passed by.
function pickTarget(candidates, pageHost) {
  const own = candidates.find(c => !c.href || new URL(c.href, `https://${pageHost}/`).hostname.endsWith(pageHost.replace(/^www\./, '')));
  return own ? candidates.indexOf(own) : (candidates.length ? 0 : -1);
}

async function clickTarget(page, text) {
  const locator = page.locator('a, button, [role=button]').filter({hasText: text, visible: true});
  const candidates = await locator.evaluateAll(els => els.map(e => ({href: e.getAttribute('href'), text: e.textContent.trim().slice(0, 60)})));
  const index = pickTarget(candidates, new URL(page.url()).hostname);
  if (index < 0) return {locator: page.getByText(text, {exact: false}).first(), describe: `text "${text}" (no link or button)`};
  const c = candidates[index];
  return {locator: locator.nth(index), describe: `"${c.text}" -> ${c.href || '(button)'} (${index + 1} of ${candidates.length})`};
}

if (require.main === module) main();
module.exports = {parse, savedCookies, isChallenge, blocker, pickTarget};
