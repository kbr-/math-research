// Real-browser regression for viewport-scheduled math: startup and deep links process only nearby
// entries, unvisited entries stay raw but findable, scrolling renders new blocks, top and end
// navigation follow deferred layout, and a longer record adds no startup work.
const assert = require('node:assert/strict');
const {browserCase, main, page, notebook, ready, registered, visibleMath} = require('./browser_support.cjs');

const base = notebook();
const total = base.split('\\(').length + base.split('\\[').length - 2;
const check = parts => browserCase(
  {'*': url => ['text/html', page(url.searchParams.has('growth') ? notebook({copies: 3}) : base)]},
  async ({url, open}) => {
    const tab = await open({reducedMotion: 'reduce'});
    await tab.goto(url, {waitUntil: 'domcontentloaded'});
    await ready(tab);
    const initial = await registered(tab);
    assert(initial < total / 4, `Startup must not register the whole research record: ${initial} of ${total}`);

    if (parts.includes('growth')) {
      // A three times longer record adds no startup work.
      await tab.goto(url + '?growth=1', {waitUntil: 'domcontentloaded'});
      await ready(tab);
      assert.equal(await tab.locator('.research-entry').count(), 180);
      assert.equal(await registered(tab), initial, 'Tripling the unvisited record must not add startup MathJax work');
      if (!parts.includes('links')) return;
      await tab.goto(url, {waitUntil: 'domcontentloaded'});
      await ready(tab);
    }

    // Near the end, with enough below it to scroll the target to the top.
    const late = await tab.locator('.research-entry').nth(-4).getAttribute('id');
    const deep = `${late}-detail`;
    await tab.evaluate(id => { location.hash = id; }, deep);
    await tab.waitForFunction(id => document.querySelector(`#${id} mjx-container`), late);
    assert(await registered(tab) < total / 3, 'Jumping to the end must not process earlier entries');
    assert.equal(await tab.locator('.research-entry').nth(30).locator('mjx-container').count(), 0,
      'Unvisited middle entries must remain unprocessed');
    const findText = (await tab.locator('.research-entry').nth(30).locator('h3').textContent()).trim();
    assert(await tab.evaluate(text => window.find(text, false, false, true), findText),
      `Browser text search must find an unvisited entry: ${JSON.stringify(findText)}`);

    // A long entry exercises more than one viewport of math.
    await tab.evaluate(() => { location.hash = 'entry-5'; });
    await visibleMath(tab);
    const beforeScroll = await registered(tab);
    await tab.mouse.wheel(0, 800);
    await tab.waitForFunction(before => [...MathJax.startup.document.math].length > before, beforeScroll);

    // Deep-link startup, then top and end navigation over deferred layout.
    await tab.goto(url + `?direct=1#${deep}`, {waitUntil: 'domcontentloaded'});
    await ready(tab);
    await visibleMath(tab);
    assert(await registered(tab) < total / 3);
    const top = await tab.locator(`#${deep}`).evaluate(node => node.getBoundingClientRect().top);
    assert(Math.abs(top) < 150, `Deep link moved out of view: ${top}`);
    await tab.locator('[data-scroll="top"]').click();
    await tab.waitForFunction(() => scrollY < 2);
    await tab.locator('[data-scroll="end"]').click();
    await tab.waitForFunction(() => Math.abs(document.documentElement.scrollHeight - innerHeight - scrollY) < 3);
    assert.equal(await tab.locator('[data-mml-node="merror"]').count(), 0);
  });
const cases = {links: check(['links']), growth: check(['growth'])};
module.exports = cases;
main(module, cases);
