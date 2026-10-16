// Drive the installed Firefox over WebDriver BiDi, Firefox's own remote protocol: no driver binary,
// no Playwright build, only `firefox` on the PATH and node's WebSocket (node 20 needs the flag
// --experimental-websocket, which tools/browser_get.cjs passes by re-executing itself). Used by
// tools/browser_get.cjs, whose default engine it is (the user's choice of browser, 16 October 2026).
//
// Each run gets a fresh temporary profile: downloads go to its own folder without a dialog, PDFs are
// saved rather than shown, and uBlock Origin (the signed release for Firefox, when present) is
// installed through BiDi before the page opens.
const {spawn} = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const PREFS = {
  'browser.download.folderList': 2,
  'browser.download.useDownloadDir': true,
  'browser.download.always_ask_before_handling_new_types': false,
  'browser.download.manager.showWhenStarting': false,
  'pdfjs.disabled': true,
  'browser.shell.checkDefaultBrowser': false,
  'browser.startup.homepage_override.mstone': 'ignore',
  'datareporting.policy.dataSubmissionEnabled': false,
  'toolkit.telemetry.enabled': false,
  'app.update.auto': false,
  'app.update.enabled': false,
  'browser.aboutwelcome.enabled': false,
  'extensions.autoDisableScopes': 0,
};

function userJs(downloads) {
  const prefs = {...PREFS, 'browser.download.dir': downloads};
  return Object.entries(prefs).map(([k, v]) => `user_pref(${JSON.stringify(k)}, ${JSON.stringify(v)});`).join('\n') + '\n';
}

const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const {pause, isLocal} = require('./browser_pacing.cjs');

// Start Firefox on a temporary profile and return the BiDi WebSocket address it announces.
function launch(profile, headed, timeoutMs) {
  const args = ['--no-remote', '--profile', profile, '--remote-debugging-port', '0', 'about:blank'];
  if (!headed) args.unshift('--headless');
  const child = spawn(process.env.FIREFOX || 'firefox', args, {stdio: ['ignore', 'ignore', 'pipe']});
  return new Promise((resolve, reject) => {
    let said = '';
    const timer = setTimeout(() => reject(new Error(`Firefox announced no BiDi address in ${timeoutMs} ms`)), timeoutMs);
    child.on('error', error => { clearTimeout(timer); reject(error); });
    child.stderr.on('data', chunk => {
      said += chunk;
      const match = said.match(/WebDriver BiDi listening on (ws:\/\/\S+)/);
      if (match) { clearTimeout(timer); resolve({child, address: match[1]}); }
    });
  });
}

class Bidi {
  constructor(socket) {
    this.socket = socket;
    this.next = 1;
    this.waiting = new Map();
    this.events = [];
    socket.addEventListener('message', message => {
      const data = JSON.parse(message.data);
      if (data.id && this.waiting.has(data.id)) {
        const {resolve, reject} = this.waiting.get(data.id);
        this.waiting.delete(data.id);
        if (data.type === 'error') reject(new Error(`${data.error}: ${data.message}`));
        else resolve(data.result);
      } else if (data.type === 'event') {
        this.events.push(data);
      }
    });
  }

  static open(address) {
    return new Promise((resolve, reject) => {
      const socket = new WebSocket(`${address}/session`);
      socket.addEventListener('open', () => resolve(new Bidi(socket)));
      socket.addEventListener('error', () => reject(new Error(`cannot connect to ${address}`)));
    });
  }

  send(method, params = {}, timeoutMs = 60000) {
    const id = this.next++;
    this.socket.send(JSON.stringify({id, method, params}));
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => { this.waiting.delete(id); reject(new Error(`${method} timed out`)); }, timeoutMs);
      this.waiting.set(id, {resolve: v => { clearTimeout(timer); resolve(v); },
                            reject: e => { clearTimeout(timer); reject(e); }});
    });
  }
}

// A script's value, from BiDi's typed remote value.
function plain(remote) {
  if (!remote) return undefined;
  if (remote.type === 'array') return remote.value.map(plain);
  if (remote.type === 'object') return Object.fromEntries(remote.value.map(([k, v]) => [k, plain(v)]));
  return remote.value;
}

// The finished file in the download folder (no .part), once its size stops changing.
async function waitForDownload(dir, timeoutMs) {
  const end = Date.now() + timeoutMs;
  let last = -1;
  while (Date.now() < end) {
    const names = fs.readdirSync(dir);
    const done = names.filter(n => !n.endsWith('.part'));
    if (done.length && !names.some(n => n.endsWith('.part'))) {
      const file = path.join(dir, done[0]);
      const size = fs.statSync(file).size;
      if (size > 0 && size === last) return file;
      last = size;
    }
    await sleep(100);
  }
  return null;
}

const CANDIDATES = `(text) => Array.from(document.querySelectorAll('a, button, [role=button]'))
  .filter(e => e.textContent.includes(text) && e.getClientRects().length > 0
    && getComputedStyle(e).visibility !== 'hidden')`;

// Open opt.url in Firefox and save the page or the downloaded file to opt.out. Returns what happened.
async function firefoxGet(opt, cookies, extension, pickTarget, isChallenge, log) {
  const ms = opt.timeout * 1000;
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'browser-get-firefox-'));
  const downloads = path.join(profile, 'downloads');
  fs.mkdirSync(downloads);
  fs.writeFileSync(path.join(profile, 'user.js'), userJs(downloads));
  const result = {finalUrl: '', status: 0, challenge: false, saved: 0};
  let child = null;
  let bidi = null;
  try {
    const started = await launch(profile, opt.headed, 30000);
    child = started.child;
    bidi = await Bidi.open(started.address);
    await bidi.send('session.new', {capabilities: {}});
    if (extension) {
      const installed = await bidi.send('webExtension.install',
        {extensionData: {type: 'archivePath', path: extension}}).catch(e => ({error: e.message}));
      log(`ad blocker: ${installed.extension ? `loaded (${installed.extension})` : `NOT running (${installed.error})`} from ${extension}`);
    } else {
      log('ad blocker: none');
    }
    for (const c of cookies) {
      await bidi.send('storage.setCookie', {cookie: {name: c.name, value: {type: 'string', value: c.value},
        domain: c.domain, path: c.path || '/'}});
    }
    await bidi.send('session.subscribe', {events: ['network.responseCompleted']});
    const tree = await bidi.send('browsingContext.getTree', {});
    const context = tree.contexts[0].context;
    await bidi.send('browsingContext.navigate', {context, url: opt.url, wait: 'complete'}, ms)
      .catch(e => log(`navigation: ${e.message.split('\n')[0]}`));
    await sleep(200);   // the main response's event can follow the navigation's reply
    const main = bidi.events.filter(e => e.method === 'network.responseCompleted' && e.params.context === context
      && e.params.navigation);
    if (main.length) result.status = main[main.length - 1].params.response.status;
    const page = await bidi.send('script.evaluate', {target: {context}, awaitPromise: false,
      expression: '[location.href, document.title, document.documentElement ? document.documentElement.outerHTML : ""]'});
    const [href, title, html] = plain(page.result);
    result.finalUrl = href;
    result.challenge = isChallenge(title || '', html || '');
    fs.mkdirSync(path.dirname(path.resolve(opt.out)), {recursive: true});
    let file = fs.readdirSync(downloads).length ? await waitForDownload(downloads, 5000) : null;
    if (!file && opt.click && !result.challenge) {
      // A person reads the page for a few seconds and scrolls before looking for the link.
      await pause(href, 2500, 6000);
      for (let step = 0; step < 3; step++) {
        await bidi.send('script.evaluate', {target: {context}, awaitPromise: false,
          expression: `window.scrollBy(0, ${120 + Math.floor(Math.random() * 200)})`});
        await pause(href, 400, 1200);
      }
      const found = await bidi.send('script.evaluate', {target: {context}, awaitPromise: false,
        expression: `(${CANDIDATES})(${JSON.stringify(opt.click)}).map(e => ({href: e.getAttribute('href'), text: e.textContent.trim().slice(0, 60)}))`});
      const candidates = plain(found.result);
      const index = pickTarget(candidates, new URL(href).hostname);
      if (index < 0) throw new Error(`no link or button with the text "${opt.click}"`);
      log(`clicking: "${candidates[index].text}" -> ${candidates[index].href || '(button)'} (${index + 1} of ${candidates.length})`);
      const element = await bidi.send('script.evaluate', {target: {context}, awaitPromise: false, resultOwnership: 'root',
        expression: `(${CANDIDATES})(${JSON.stringify(opt.click)})[${index}]`});
      await bidi.send('script.callFunction', {target: {context}, awaitPromise: false,
        functionDeclaration: 'e => e.scrollIntoView({behavior: "smooth", block: "center"})', arguments: [element.result]});
      await pause(href, 600, 1400);
      // The pointer travels to the link over a few hundred milliseconds and rests on it before the click.
      const local = isLocal(new URL(href).hostname);
      const travel = local ? 0 : 250 + Math.floor(Math.random() * 450);
      await bidi.send('input.performActions', {context, actions: [{type: 'pointer', id: 'mouse', actions: [
        {type: 'pointerMove', x: 40 + Math.floor(Math.random() * 300), y: 60 + Math.floor(Math.random() * 300), duration: 0},
        {type: 'pointerMove', x: 0, y: 0, duration: travel, origin: {type: 'element', element: {sharedId: element.result.sharedId}}},
        {type: 'pause', duration: local ? 0 : 150 + Math.floor(Math.random() * 450)},
        {type: 'pointerDown', button: 0}, {type: 'pause', duration: local ? 0 : 70 + Math.floor(Math.random() * 90)},
        {type: 'pointerUp', button: 0}]}]});
    }
    if (!file && (opt.click || opt.download)) file = await waitForDownload(downloads, ms);
    if (file) fs.copyFileSync(file, opt.out);
    else if (!opt.click && !opt.download) fs.writeFileSync(opt.out, html || '');
    result.saved = fs.existsSync(opt.out) ? fs.statSync(opt.out).size : 0;
  } catch (e) {
    log(`browser_get: ${e.message.split('\n')[0]}`, true);
  } finally {
    if (bidi) await bidi.send('browser.close', {}, 5000).catch(() => {});
    if (child && child.exitCode === null) {
      await Promise.race([new Promise(resolve => child.on('exit', resolve)), sleep(5000)]);
      if (child.exitCode === null) child.kill('SIGKILL');
    }
    fs.rmSync(profile, {recursive: true, force: true});
  }
  return result;
}

module.exports = {firefoxGet, userJs};
