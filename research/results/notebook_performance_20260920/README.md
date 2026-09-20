# Notebook rendering performance — 20 September 2026

This is a UI performance checkpoint, not mathematical research or a proof check.
The notebook source and append-only research record were not edited.

## Diagnosis and change

`ui/lazy` deferred equation output but still registered 32,691 expressions at
startup. The original navigation also measured all section headings on every
scroll frame. The baseline's longest uninterrupted browser task was 4,560 ms.

The page now disables MathJax's document-wide startup pass. An entry observer
activates paragraph/display observers near the viewport; only intersecting blocks
are passed to `typesetPromise`, one at a time, yielding between blocks. Leaving
an entry cancels its queued work. CSS `content-visibility: auto` defers off-screen
entry layout while keeping source text available to browser search and anchors.
Navigation uses a binary search rather than measuring every heading.

The source uses explicit equation tags, HTML claim anchors, and macros defined
in the MathJax configuration. Independent blocks must not acquire cross-block
TeX definitions or chronological automatic numbering without revisiting this
renderer. The full HTML is still downloaded and parsed, and visited SVG output
is retained. These costs grow with the record; this change bounds initial math
processing, not the source file size or all browser memory.

## Evidence and scope

`before.json` and `after.json` contain actual measurements from installed
Playwright 1.63.0 / headless Chromium 153.0.8010.12. The metrics count registered
MathJax items, DOM elements, geometry reads and browser long tasks. Elapsed time
includes deliberate settling waits and CDN requests; it is not a clean estimate
of time-to-interactive. These are local measurements, not Firefox measurements
or a guarantee for every machine/network.

## On-demand full-text and TeX search

`search-and-rendering.json` is the final combined run with search enabled.
Search preserves each changed block's original text before MathJax replaces it;
unvisited blocks are read directly. The first nonempty query builds a reusable
index in roughly 8 ms work slices, yielding between slices. Queries are also
chunked and debounced by 150 ms, old queries are cancelled, and only 30 matching
passages are displayed at a time. Opening the empty search panel does not index
anything. Search never asks MathJax to render; navigating to a result activates
the normal viewport renderer.

| Measurement | Current record | Tripled record |
| --- | ---: | ---: |
| First index build, including yields | 108.9 ms | 348.1 ms |
| First results, including 150 ms debounce | 268.0 ms | 524.7 ms |
| Repeat query work, including yields/results | 7.9 ms | 22.3 ms |
| Repeat results, including debounce | 158.3 ms | 172.8 ms |
| Retained JS heap increase after first search | 9,581,708 bytes | 28,493,552 bytes |
| Largest timer gap during first search (16 ms timer) | 32.8 ms | 34.9 ms |

Heap deltas use Chromium `Runtime.getHeapUsage` after forced garbage collection,
outside the latency measurement. They include result UI and search-associated
allocations, not just the index, and exclude native DOM/browser memory. Timer gaps
include scheduling/layout, not solely search work. No search in this run increased
the MathJax item count. Search tests also cover rendered TeX, late unvisited prose,
pagination, result navigation, case sensitivity, negative queries, rapid query
replacement, keyboard opening/closing and the absence of an eager index.

In the final combined run the longest startup task was 184 ms, versus 4,560 ms
in the old template; initial MathJax items were still 2 versus 32,691.

The browser regression covers top-of-page startup, inner-claim deep links,
a fresh deep-link load, an unvisited entry found by browser text search, newly
visible equations while scrolling a long proof, top/end navigation, mobile layout,
and a synthetic tripled research record. Tripling unvisited entries leaves the
startup math count at two. It checks rendered equation errors and page exceptions.
The six existing static build tests and client tests cover publication isolation,
project-relative revision URLs, update polling/reload, heading links and arrows.

Original template: Git commit `28990e77828025f6d8b653c23ea635b9c4f4d00d`.
Notebook SHA-256: `730770667d07e29c6194d6cf33fb96dbf47e6768e9358ae3553b1d85325ba054`.

## Reproduce

Requires the already installed Playwright and Chromium; these commands install
nothing. Internet access is needed for MathJax's existing CDN assets. Run from
the repository root with the usual resource controls active:

```sh
./compute.sh --timeout 150 -- node tests/test_notebook_browser.cjs
git show 28990e77828025f6d8b653c23ea635b9c4f4d00d:index.html > /tmp/notebook-before.html
./compute.sh --timeout 150 -- env NOTEBOOK_TEMPLATE=/tmp/notebook-before.html NOTEBOOK_PROFILE_ONLY=1 node tests/test_notebook_browser.cjs
./compute.sh -- python3 -m unittest discover -s tests -p test_pages.py
./compute.sh -- python3 tools/build_pages.py --out /tmp/notebook-performance-site
./compute.sh -- node tests/test_pages_client.js /tmp/notebook-performance-site/index.html
```

Set `NOTEBOOK_REPORT` to a new JSON path to retain a browser report. Do not
replace these dated measurements when testing later source revisions.

References: [MathJax lazy typesetting](https://docs.mathjax.org/en/latest/output/lazy.html),
[MathJax explicit-container typesetting](https://docs.mathjax.org/en/latest/web/typeset.html),
[CSS content visibility](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/content-visibility).
