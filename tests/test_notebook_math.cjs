// Real-browser regression: bare and wrapped TeX get small math containers, code and distant math
// stay untouched, search keeps raw TeX, and display math stays inside the notebook on a phone.
const assert = require('node:assert/strict');
const {browserCase, main, page, ready} = require('./browser_support.cjs');

const fixture = String.raw`
  <section id="fixture-overview"><h2>Math blocks</h2><p>Overview.</p></section>
  <section id="research-record">
    <article id="bare-math"><h3>Bare and wrapped math</h3>
      <p id="wrapped-math">Wrapped \(x+1\).</p>
      \[x^2+1\]
      <div id="nested-bare">\[y^2+1\]</div>
      <p>Inline text next:</p> Bare \(z^2+1\).
      <pre id="literal-math">\[leave this example alone\]</pre>
      $$w^2+1$$
    </article>
    <article id="wide-math"><h3>Wide display math</h3>
      \[x_1+x_2+x_3+x_4+x_5+x_6+x_7+x_8+x_9+x_{10}+x_{11}+x_{12}+x_{13}+x_{14}+x_{15}+x_{16}\tag{W}\]
      \[y_1+y_2+y_3+y_4+y_5+y_6+y_7+y_8+y_9+y_{10}+y_{11}+y_{12}+y_{13}+y_{14}+y_{15}+y_{16}\]
    </article>
    <article id="distant-math" style="margin-top:100000px"><h3>Distant math</h3>
      \[\text{unvisited-orphan-probe}+q^2\]
    </article>
  </section>`;

const cases = {layout: browserCase({'*': ['text/html', page(fixture)]}, async ({url, open}) => {
  const desktop = await open({reducedMotion: 'reduce'});
  await desktop.goto(url, {waitUntil: 'domcontentloaded'});
  await ready(desktop);
  assert.equal(await desktop.locator('#bare-math mjx-container').count(), 5);
  assert.equal(await desktop.locator('#bare-math .math-fragment').count(), 4);
  assert.equal(await desktop.locator('#literal-math .math-fragment, #literal-math mjx-container').count(), 0);
  assert.equal(await desktop.locator('#distant-math mjx-container').count(), 0);
  const rendered = await desktop.locator('mjx-container').count();
  await desktop.locator('#search-open').click();
  await desktop.locator('#search-query').fill('unvisited-orphan-probe');
  await desktop.waitForFunction(() => document.getElementById('search-status').dataset.state === 'ready');
  assert.equal(await desktop.locator('#search-results button').count(), 1);
  assert.equal(await desktop.locator('mjx-container').count(), rendered,
    'Searching bare TeX must not typeset an unvisited article');
  await desktop.locator('#search-results button').click();
  await desktop.waitForFunction(() => document.querySelector('#distant-math mjx-container'));
  assert.equal(await desktop.locator('[data-mml-node="merror"]').count(), 0);

  // MathJax gives a tagged display equation an inline min-width of its full width, which
  // overrode max-width and widened the whole page on a phone.
  const phone = await open({isMobile: true, hasTouch: true, viewport: {width: 390, height: 844}});
  await phone.goto(url + '#wide-math', {waitUntil: 'domcontentloaded'});
  await phone.waitForFunction(() => window.mathReady &&
    [...document.querySelectorAll('#wide-math mjx-container')].filter(node => node.querySelector('svg')).length === 2);
  const width = await phone.evaluate(() => {
    const main = document.querySelector('main').getBoundingClientRect();
    return {page: document.documentElement.scrollWidth, screen: innerWidth,
      outside: [...document.querySelectorAll('#wide-math mjx-container')]
        .filter(node => node.getBoundingClientRect().right > main.right + 1).length};
  });
  assert.equal(width.outside, 0, 'Display math must stay inside the notebook on a phone');
  assert(width.page <= width.screen, `Wide math widened the page: ${JSON.stringify(width)}`);
})};
module.exports = cases;
main(module, cases);
