// The queue folds top-level items only; its continuation keeps numbering and remains searchable.
const assert = require('node:assert/strict');
const {browserCase, main, page} = require('./browser_support.cjs');

const queue = count => '<h1>Queue fixture</h1><section id="lead-queue"><h2>Lead and bridge queue</h2><ol>' +
  Array.from({length: count}, (_, i) => `<li id="queue-${i + 1}" data-summary="AGENT-ONLY-SUMMARY">Queued item ${i + 1}` +
    (i === 0 ? ' Full description and its hypotheses.'.repeat(20) +
      ' Last clause beyond the old truncation.<ul><li>Nested sub-idea</li></ul>' : '') + '</li>').join('') + '</ol></section>';

const cases = {fold: browserCase({'*': url => ['text/html', page(queue(Number(url.searchParams.get('count') || 7)))]},
  async ({url, open}) => {
    const tab = await open();
    await tab.goto(url, {waitUntil: 'domcontentloaded'});
    assert.equal(await tab.locator('#lead-queue > ol > li').count(), 5);
    assert(await tab.locator('#queue-5').isVisible());
    assert(await tab.getByText('Nested sub-idea').isVisible());
    assert(!(await tab.locator('main').innerText()).includes('AGENT-ONLY-SUMMARY'));
    const fullText = tab.locator('#queue-1 > .queue-item-text');
    const textToggle = tab.locator('#queue-1 > .queue-text-toggle');
    assert((await fullText.textContent()).includes('Last clause beyond the old truncation.'));
    const foldedHeight = await fullText.evaluate(node => node.getBoundingClientRect().height);
    await textToggle.click();
    assert.equal(await textToggle.getAttribute('aria-expanded'), 'true');
    assert((await fullText.evaluate(node => node.getBoundingClientRect().height)) > foldedHeight);
    await textToggle.click();
    assert.equal(await textToggle.getAttribute('aria-expanded'), 'false');
    assert(await tab.locator('#queue-6').isHidden());
    assert.equal(await tab.locator('.queue-more > ol').getAttribute('start'), '6');
    const toggle = tab.locator('.queue-more > summary');
    assert.equal(await toggle.textContent(), 'Show remaining 2 items');
    await toggle.click();
    assert(await tab.locator('#queue-7').isVisible());
    await tab.waitForFunction(() => document.querySelector('.queue-more > summary').textContent === 'Hide remaining items');
    await toggle.press('Enter');
    assert(await tab.locator('#queue-6').isHidden());
    await tab.locator('#search-open').click();
    await tab.locator('#search-query').fill('Last clause beyond the old truncation.');
    await tab.locator('#search-results button').last().click();
    assert.equal(await textToggle.getAttribute('aria-expanded'), 'true', 'Search reveals a collapsed full description');
    // The existing search opens closed details before focusing a result.
    await tab.locator('#search-open').click();
    await tab.locator('#search-query').fill('Queued item 7');
    await tab.locator('#search-results button').last().click();
    assert(await tab.locator('#queue-7').isVisible());
    await tab.goto(url + '?direct=1#queue-6', {waitUntil: 'domcontentloaded'});
    assert(await tab.locator('#queue-6').isVisible(), 'A direct link must reveal its queued item');
    await tab.goto(url + '?count=5', {waitUntil: 'domcontentloaded'});
    assert.equal(await tab.locator('.queue-more').count(), 0, 'Five items need no toggle');
    assert(await tab.locator('#queue-5').isVisible());
  })};
module.exports = cases;
main(module, cases);
