// Real-browser regression for the scroll buttons: previous and next align each successive heading
// at the top, with and without smooth scrolling; rapid clicks advance from the chosen destination,
// not from a point mid-animation; manual scrolling releases the destination; end reaches the end.
const assert = require('node:assert/strict');
const {browserCase, main, page, notebook} = require('./browser_support.cjs');

// Short entries keep smooth-scroll animations short; the long last one lets any heading reach the top.
const base = notebook({entries: 12, long: [11]});

const navigation = motion => browserCase({'*': ['text/html', page(base)]}, async ({url, open}) => {
  const tab = await open({reducedMotion: motion});
  await tab.goto(url + '#entry-8', {waitUntil: 'domcontentloaded'});
  await tab.waitForFunction(() => window.mathReady);
  const aligned = (id, label) => tab.waitForFunction(id =>
    Math.abs(document.getElementById(id).querySelector('h3').getBoundingClientRect().top - 16) < 3, id)
    .catch(async () => assert.fail(`${motion}: ${label} did not align ${id}: ` + await tab.evaluate(id =>
      document.getElementById(id).querySelector('h3').getBoundingClientRect().top, id)));
  // Just below entry 8's heading, so previous goes to entry 7.
  await tab.evaluate(() => window.scrollBy(0, 1));
  await tab.locator('[data-scroll="previous"]').click();
  await aligned('entry-7', 'previous');
  await tab.locator('[data-scroll="previous"]').click();
  await aligned('entry-6', 'previous');
  await tab.locator('[data-scroll="next"]').click();
  await aligned('entry-7', 'next');
  for (let n = 0; n < 2; n++) await tab.locator('[data-scroll="previous"]').click();
  await aligned('entry-5', 'rapid previous');
  await tab.mouse.wheel(0, 250);
  await tab.waitForFunction(() =>
    Math.abs(document.getElementById('entry-5').querySelector('h3').getBoundingClientRect().top - 16) > 100)
    .catch(() => assert.fail('Manual scrolling must release destination tracking'));
  if (motion === 'reduce') {
    await tab.locator('[data-scroll="end"]').click();
    await tab.waitForFunction(() => Math.abs(document.documentElement.scrollHeight - innerHeight - scrollY) < 3);
  }
});
const cases = {smooth: navigation('no-preference'), reduced: navigation('reduce')};
module.exports = cases;
main(module, cases);
