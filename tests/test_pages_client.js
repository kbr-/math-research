// Exercise the published-page client without network access or browser dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

async function check(changed) {
  const page = fs.readFileSync(process.argv[2] || '_site/index.html', 'utf8');
  const live = process.argv[3] === 'live';
  const revision = page.match(/revision !== '([a-f0-9]{64})'/)[1];
  const status = { textContent: '', dataset: {} };
  const requests = [], delays = [];
  let reloads = 0;
  const context = {
    URL,
    AbortSignal: { timeout: () => undefined },
    document: { getElementById: id => id === 'status' ? status : { addEventListener() {} } },
    location: { href: live ? 'http://localhost:8000/' : 'https://example.github.io/math-research/', reload() { reloads++; } },
    sessionStorage: { getItem: () => null, setItem() {}, removeItem() {} },
    scrollY: 0,
    scrollTo() {},
    setTimeout: (_, delay) => delays.push(delay),
    fetch: async url => {
      requests.push(String(url));
      return { ok: true, json: async () => ({ revision: changed ? 'new-revision' : revision }) };
    },
  };
  context.window = context;
  vm.createContext(context);
  for (const [, attrs, code] of page.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)) {
    if (!/\bsrc=/.test(attrs)) vm.runInContext(code, context);
  }
  context.MathJax.startup.defaultPageReady = async () => {};
  await context.MathJax.startup.pageReady();
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(new URL(requests[0]).pathname, live ? '/revision' : '/math-research/revision.json');
  assert.equal(status.textContent, live ? 'Live · watching for changes' : 'Published notebook');
  assert.equal(reloads, changed ? 1 : 0);
  if (!changed) assert.deepEqual(delays, [live ? 1000 : 30000]);
}

Promise.resolve().then(() => check(false)).then(() => check(true)).then(() => {
  process.stdout.write('Notebook client: correct update URL, ready status, polling, and update reload.\n');
}).catch(error => { console.error(error); process.exitCode = 1; });
