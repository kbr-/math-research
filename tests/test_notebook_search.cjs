// Real-browser regression for notebook search: the index is built on demand and reused, searching
// never typesets, results are paged and bounded, rendered and unrendered TeX are both found, a
// result opens its passage, and the last of several fast edits wins.
const assert = require('node:assert/strict');
const {browserCase, main, page, notebook, ready, registered} = require('./browser_support.cjs');

const cases = {search: browserCase({'*': ['text/html', page(notebook())]}, async ({url, open}) => {
  const tab = await open({reducedMotion: 'reduce'});
  await tab.goto(url, {waitUntil: 'domcontentloaded'});
  await ready(tab);
  assert.equal(await tab.locator('#search-open').innerText(), 'Search notebook (/)');
  const indexBuilds = () => tab.evaluate(() => performance.getEntriesByName('notebook-search-index').length);
  assert.equal(await indexBuilds(), 0, 'No search index should be built at page load');
  await tab.locator('#search-open').click();
  assert.equal(await indexBuilds(), 0, 'Opening search with an empty query should not build an index');
  let navigated = false;
  async function query(text) {
    const before = await registered(tab);
    await tab.locator('#search-query').fill(text);
    await tab.waitForFunction(() => document.getElementById('search-status').dataset.state === 'ready');
    if (!navigated) assert.equal(await registered(tab), before, 'Searching must not typeset unseen math');
    return tab.locator('#search-results button').count();
  }
  assert(await query('\\mathcal') > 0);
  assert(await tab.locator('#search-results button').count() <= 30, 'Bound result DOM size');
  await query('companion');
  assert.equal(await indexBuilds(), 1, 'Later searches must reuse the same index');
  await tab.locator('#search-next').click();
  assert((await tab.locator('#search-status').textContent()).includes('31–'));
  await tab.locator('#search-previous').click();
  // Rendered TeX and untouched late TeX are searched through the same source index.
  assert(await query('\\mathrm{AC}^0[p]') > 0);
  assert(await query('finite-domain branch interpolation') > 0);
  await tab.locator('#search-results button').last().click();
  navigated = true;
  assert(await tab.locator('#notebook-search').isHidden());
  await tab.waitForFunction(() => {
    const box = document.querySelector('.search-hit')?.getBoundingClientRect();
    return box && box.top < innerHeight && box.bottom > 0;
  });
  await tab.keyboard.press('/');
  assert(await tab.locator('#notebook-search').isVisible());
  await tab.locator('#search-case').check();
  assert.equal(await query('FINITE-DOMAIN BRANCH INTERPOLATION'), 0);
  await tab.locator('#search-case').uncheck();
  assert(await query('FINITE-DOMAIN BRANCH INTERPOLATION') > 0);
  assert.equal(await query('<script>not-a-result</script>'), 0);
  // Fast edits cancel old work; the last query wins.
  await tab.locator('#search-query').fill('companion');
  assert.equal(await query('no-such-notebook-passage-7319'), 0);
  await tab.keyboard.press('Escape');
  assert(await tab.locator('#notebook-search').isHidden());
})};
module.exports = cases;
main(module, cases);
