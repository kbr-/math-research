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
  const events = {}, buttonClicks = {};
  const buttons = ['top', 'previous', 'next', 'end'].map(name => ({
    dataset: { scroll: name }, hidden: true,
    addEventListener(event, handler) {
      assert.equal(event, 'click');
      buttonClicks[name] = handler;
    },
  }));
  const main = {};
  const navigation = { dataset: {} };
  const timers = new Map();
  let timerId = 0;
  const headingTops = [100, 500, 900];
  let resizeCallback;
  let reloads = 0;
  const context = {
    URL,
    AbortSignal: { timeout: () => undefined },
    document: {
      getElementById: id => id === 'status' ? status : { addEventListener() {} },
      querySelectorAll(selector) {
        if (selector === 'main h2, main h3') return headingTops.map((_, index) => ({
          getBoundingClientRect: () => ({ top: headingTops[index] - context.scrollY }),
        }));
        if (selector === '[data-scroll]') return buttons;
        throw new Error(`Unexpected selector: ${selector}`);
      },
      querySelector(selector) {
        if (selector === '.scroll-nav') return navigation;
        assert.equal(selector, 'main'); return main;
      },
      documentElement: { scrollHeight: 1500 },
    },
    location: { href: live ? 'http://localhost:8000/' : 'https://example.github.io/math-research/', reload() { reloads++; } },
    sessionStorage: { getItem: () => null, setItem() {}, removeItem() {} },
    scrollY: 0,
    innerHeight: 400,
    scrollTo(options) { context.scrollY = options.top; events.scroll(); },
    matchMedia: () => ({ matches: true }),
    addEventListener(event, handler) { events[event] = handler; },
    requestAnimationFrame(callback) { callback(); },
    ResizeObserver: class {
      constructor(callback) { resizeCallback = callback; }
      observe(element) { assert.equal(element, main); }
    },
    setTimeout(callback, delay) {
      delays.push(delay);
      timers.set(++timerId, { callback, delay });
      return timerId;
    },
    clearTimeout(id) { timers.delete(id); },
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
  assert.equal(navigation.dataset.active, undefined, 'Overlay starts hidden');
  events.scroll();
  assert.equal(navigation.dataset.active, '', 'Scrolling reveals the overlay');
  events.scroll();
  const hideTimers = [...timers.values()].filter(timer => timer.delay === 3500);
  assert.equal(hideTimers.length, 1, 'Further scrolling resets the idle timer');
  hideTimers[0].callback();
  assert.equal(navigation.dataset.active, undefined, 'Overlay hides after 3.5 seconds idle');
  events.scroll();
  assert.equal(navigation.dataset.active, '', 'Scrolling reveals the overlay again');

  // Check navigation against a small layout, including the distinct section/end boundaries.
  const visible = () => buttons.filter(button => !button.hidden).map(button => button.dataset.scroll);
  assert.deepEqual(visible(), ['next', 'end']);
  buttonClicks.next();
  assert.equal(context.scrollY, 84);
  assert.deepEqual(visible(), ['top', 'next', 'end']);
  buttonClicks.next();
  assert.equal(context.scrollY, 484);
  assert.deepEqual(visible(), ['top', 'previous', 'next', 'end']);
  buttonClicks.previous();
  assert.equal(context.scrollY, 84);
  buttonClicks.next();
  buttonClicks.next();
  assert.equal(context.scrollY, 884);
  assert.deepEqual(visible(), ['top', 'previous', 'end']);
  buttonClicks.end();
  assert.equal(context.scrollY, 1100);
  assert.deepEqual(visible(), ['top', 'previous']);
  context.document.documentElement.scrollHeight = 1700;
  resizeCallback();
  assert.equal(context.scrollY, 1300, 'Follow the bottom after lazy rendering expands the page');
  assert.deepEqual(visible(), ['top', 'previous']);
  events.wheel();
  context.document.documentElement.scrollHeight = 1800;
  resizeCallback();
  assert.equal(context.scrollY, 1300, 'Manual scrolling releases the destination');
  assert.deepEqual(visible(), ['top', 'previous', 'end']);
  buttonClicks.top();
  assert.equal(context.scrollY, 0);
  assert.deepEqual(visible(), ['next', 'end']);
  buttonClicks.next();
  buttonClicks.next();
  headingTops[1] += 120;
  resizeCallback();
  assert.equal(context.scrollY, 604, 'Follow the chosen heading when preceding math expands');
  events.touchstart();
  headingTops[1] += 80;
  resizeCallback();
  assert.equal(context.scrollY, 604, 'Touch scrolling releases the heading');
  buttonClicks.end();
  events.keydown({ key: 'PageUp' });
  context.document.documentElement.scrollHeight += 100;
  resizeCallback();
  assert.equal(context.scrollY, 1400, 'Keyboard scrolling releases the destination');
}

Promise.resolve().then(() => check(false)).then(() => check(true)).then(() => {
  process.stdout.write('Notebook client: update URL, ready status, polling, reload, and navigation passed.\n');
}).catch(error => { console.error(error); process.exitCode = 1; });
