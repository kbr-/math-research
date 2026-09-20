# Deferred-layout navigation regression — 20 September 2026

UI-only checkpoint; no notebook mathematics or source entries were changed.
Baseline template: `9a9df2ba587efb7a5dab467e67896c393d99e207:index.html`.
Notebook SHA-256: `392e07ffb6fa5b51102d820169356cde1dd412ed7327cf47d949f6df79aee78d`.

The old correction compared the target's current document coordinate with its
cached coordinate and ran on main-element resize. That misses viewport movement
without coordinate change, and math movement without total-height change.
A second click also cleared the navigation destination on pointerdown and chose
its next target from the unfinished smooth-scroll position.

The fix checks actual scroll position at `scrollend`, signals navigation after
individual math blocks finish, and settles the previous chosen destination before
processing another navigation click. Pointer/touch events on navigation controls
keep that destination; manual scrolling and interactions elsewhere release it.
It still uses binary heading lookup and never measures the entire record per frame.

## Actual evidence

- `chromium-before.json` / `chromium-after.json`: headless Chromium 153.0.8010.12,
  normal and reduced motion; end, eight previous clicks, seven next clicks,
  three rapid previous clicks, and manual-wheel release. The old rapid case
  missed the intended heading by about 4,462 px. All 32 fixed landings were
  within one pixel of the intended 16 px offset.
- `firefox-before-after.json`: installed Firefox 153.0, headless, isolated temporary
  profile, native WebDriver BiDi mouse actions. Six settled previous clicks and
  three rapid clicks after jumping to the end. The original settled offsets
  included -206 px, -1,014 px and -105 px instead of +16 px. All seven fixed
  landings were within half a pixel of +16 px.
- `final-browser-check.json`: full rendering/search regression with the responsive
  search-button checks. Search is asserted not to start math work before result
  navigation; after selecting a result, ordinary viewport math may finish while
  another query runs. That overlap is not search-triggered global rendering.
- Deterministic client tests cover final viewport drift with unchanged target
  coordinates, math moving a heading without total-height change, and manual
  scrolling releasing the lock.

Early 1.2-second Chromium samples sometimes caught an unfinished animation; they
were not treated as evidence of a persistent final offset. The retained navigation
reports allow animations to settle. Firefox still reproduced the reported problem.

The search button uses 75% opacity below 1084 px. Its shortcut hint appears for a
fine, hover-capable pointer (a desktop heuristic) or observed keyboard use; touch
screens otherwise show the shorter label. Browsers do not expose a reliable
physical-keyboard presence query. Tests cover narrow desktop and touch mobile,
including keyboard use on a touch device and repeated touch navigation.

## Reproduce without installing dependencies

Run with the workspace resource controls active and the existing Playwright/
Chromium installation. The Firefox evidence helper uses the installed Firefox
binary and the WebSocket implementation already bundled with Playwright.

```sh
./compute.sh --timeout 150 -- node tests/test_notebook_navigation.cjs
./compute.sh --timeout 180 -- node tests/test_notebook_browser.cjs
git show 9a9df2ba587efb7a5dab467e67896c393d99e207:index.html > /tmp/notebook-navigation-before.html
./compute.sh --timeout 150 -- env NOTEBOOK_TEMPLATE=/tmp/notebook-navigation-before.html node tests/test_notebook_navigation.cjs
./compute.sh --timeout 100 -- env NOTEBOOK_REPORT=/tmp/firefox-navigation-new.json node research/results/notebook_navigation_20260920/firefox-check.cjs
```

The baseline Chromium regression is expected to fail. The Firefox helper compares
that baseline file with the current template. It serves only temporary local pages,
uses a fresh profile, and shuts down its own Firefox process. No user's browser
profile is touched. Firefox's connection method is documented by
[Mozilla](https://developer.mozilla.org/en-US/docs/Web/WebDriver/How_to/Create_BiDi_connection).
