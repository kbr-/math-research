#!/usr/bin/env node
// Retrieve a source the way a person's browser does: open URL in Chromium (the installed Playwright),
// wait for the page, and save the page, or with --download (or --click TEXT) the file it serves.
// For sources that refuse scripted clients: curl gets a 403 or a bot wall, a browser may not. With the
// cookies tools/firefox_cookies.py saved for the host (~/.cache/cookies-HOST.json, or --cookies FILE),
// the browser carries the user's signed-in session, which is what passes a wall a bare browser meets
// (on 16 October 2026 ResearchGate served a CAPTCHA to headless and headed Chromium alike, and the
// user's own browser downloaded the file with one click). GET-style browsing only: it clicks at most
// one link, named by --click, and never submits a form.
//
//   node tools/browser_get.cjs URL --out FILE [--download] [--click TEXT] [--cookies FILE]
//                              [--no-cookies] [--headed] [--timeout SECONDS]
//
// Prints the final URL, the HTTP status of the main response, whether the page looks like a
// challenge, and the saved file's size; exits 1 when the status is 400 or above or nothing was saved,
// and 2 on a usage error or when Playwright cannot be loaded.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const USAGE = 'usage: node tools/browser_get.cjs URL --out FILE [--download] [--click TEXT] '
  + '[--cookies FILE] [--no-cookies] [--headed] [--timeout SECONDS]';
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
    else if (a === '--timeout') opt.timeout = Number(argv[++i]);
    else if (a.startsWith('--')) return null;
    else rest.push(a);
  }
  opt.url = rest[0];
  if (rest.length !== 1 || !opt.out || !(opt.timeout > 0)) return null;
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
function savedCookies(opt) {
  if (opt.noCookies) return [];
  const host = new URL(opt.url).hostname;
  const file = opt.cookies || path.join(os.homedir(), '.cache', `cookies-${host}.json`);
  if (!fs.existsSync(file)) {
    if (opt.cookies) throw new Error(`no cookie file at ${file}`);
    return [];
  }
  const list = JSON.parse(fs.readFileSync(file, 'utf8')).map(c => ({
    name: c.name, value: String(c.value), domain: c.domain, path: c.path || '/',
    expires: c.expires > 1e11 ? Math.floor(c.expires / 1000) : (c.expires || -1)}));
  console.log(`cookies: ${list.length} from ${file}`);
  return list;
}

async function main() {
  const opt = parse(process.argv.slice(2));
  if (!opt) { console.error(USAGE); process.exit(2); }
  const playwright = loadPlaywright();
  if (!playwright) { console.error('browser_get: Playwright cannot be loaded (local, NODE_PATH or global).'); process.exit(2); }
  let cookies;
  try { cookies = savedCookies(opt); } catch (e) { console.error(`browser_get: ${e.message}`); process.exit(2); }
  const browser = await playwright.chromium.launch({headless: !opt.headed});
  const context = await browser.newContext({acceptDownloads: true, locale: 'en-US'});
  if (cookies.length) await context.addCookies(cookies);
  const page = await context.newPage();
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
      const wait = page.waitForEvent('download', {timeout: ms});
      if (opt.click) await page.getByText(opt.click, {exact: false}).first().click({timeout: ms});
      await (await wait).saveAs(opt.out);
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
    await browser.close();
  }
  process.exit(status >= 400 || saved === 0 ? 1 : 0);
}

// Whether a page's title or opening text is a bot wall rather than the source.
function isChallenge(title, html) {
  return CHALLENGE.test(title) || CHALLENGE.test(html.slice(0, 20000));
}

if (require.main === module) main();
module.exports = {parse, savedCookies, isChallenge};
