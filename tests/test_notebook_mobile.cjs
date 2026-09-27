// Real-browser regression for narrow screens: a narrow desktop window keeps the search shortcut
// hint, a touch device reveals it only once a keyboard is used, and repeated touch navigation
// lands on its target.
const assert = require('node:assert/strict');
const {browserCase, main, page, notebook, ready, registered} = require('./browser_support.cjs');

// Long last entries, so a heading near the end can scroll to the top.
const base = notebook({long: [5, 56, 57, 58, 59]});

const cases = {narrow: browserCase({'*': ['text/html', page(base)]}, async ({url, open}) => {
  const narrow = await open({reducedMotion: 'reduce', viewport: {width: 390, height: 844}});
  await narrow.goto(url, {waitUntil: 'domcontentloaded'});
  await ready(narrow);
  assert(await registered(narrow) < 60, 'Startup must not register the whole research record');
  assert.equal(await narrow.locator('#search-open').evaluate(node => getComputedStyle(node).opacity), '0.75');
  assert.equal(await narrow.locator('#search-open').innerText(), 'Search notebook (/)',
    'A narrow desktop window keeps the keyboard hint');

  const touch = await open({isMobile: true, hasTouch: true, reducedMotion: 'reduce',
    viewport: {width: 390, height: 844}});
  await touch.goto(url, {waitUntil: 'domcontentloaded'});
  assert.equal(await touch.locator('#search-open').innerText(), 'Search notebook');
  assert.equal(await touch.locator('#search-open').evaluate(node => getComputedStyle(node).opacity), '0.75');
  await touch.keyboard.press('/');
  assert(await touch.locator('#notebook-search').isVisible());
  assert.equal(await touch.locator('#search-open').innerText(), 'Search notebook (/)',
    'Using a keyboard on a touch device reveals the shortcut');
  await touch.keyboard.press('Escape');
  await touch.waitForFunction(() => window.mathReady);
  await touch.evaluate(() => window.scrollTo(0, 100));
  await touch.locator('[data-scroll="end"]').tap();
  await touch.waitForFunction(() => Math.abs(document.documentElement.scrollHeight - innerHeight - scrollY) < 3);
  const target = (await touch.locator('main h2, main h3').count()) - 4;
  for (let n = 0; n < 3; n++) await touch.locator('[data-scroll="previous"]').tap();
  const top = () => touch.evaluate(index =>
    document.querySelectorAll('main h2, main h3')[index].getBoundingClientRect().top, target);
  await touch.waitForFunction(index => Math.abs(
    document.querySelectorAll('main h2, main h3')[index].getBoundingClientRect().top - 16) < 3, target)
    .catch(async () => assert.fail(`Repeated touch navigation lost its target: ${await top()}`));
})};
module.exports = cases;
main(module, cases);
