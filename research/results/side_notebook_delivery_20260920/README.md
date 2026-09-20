# Side-notebook delivery acceptance — 20 September 2026

Three measured implementation checkpoints are recorded in the main notebook:
identity/source resolution, selected workflows, and delivery/acceptance. The
owning plan is `research/notes/SIDE_BRANCHES_PLAN.md`; the usage guide is
`tools/SIDE_NOTEBOOKS.md`. No real side research was started and nothing was pushed.

Commands (all substantive runs used compute.sh and the named timing sessions):

- `python3 -m unittest discover -s tools/tests`: 176 tests passed before the final
  additional interrupted-setup control; the targeted side workflow then passed
  25 tests (177 tests in the resulting complete inventory).
- `python3 -m unittest discover -s tests -p 'test*pages.py'`: nine tests passed.
- `node tests/test_side_notebooks.cjs`: headless Chromium 153, live and static
  project-prefix routes, 1,000 entries each in two temporary side notebooks.
- `node tests/test_notebook_navigation.cjs`: existing real-browser navigation
  regression passed, including reduced-motion and rapid previous navigation.
- Static builder and `tests/test_pages_client.js`: minimal site and update client
  passed; all registered context budgets and append-only checks passed.

`browser-before-batching.json` and `browser.json` retain the complete browser
measurements. The latter preserves the final live/static run. All-notebook search
fell from 8,665–8,715 ms to 225–260 ms after replacing per-entry timer yields with
8 ms batches. Current-notebook search was 289–309 ms in the final run; DOM-ready
was 365–401 ms. Each all-notebook query fetched exactly two other sources; startup
and current-only search fetched none. These are fixture measurements, not general
performance guarantees. MathJax was asynchronous (zero/three registered items at
the early sample); the independent navigation regression exercised actual rendering.

Complete test output, including repaired test-fixture failures, is retained in the
session archive. A static-server fixture initially failed to serve its root;
fixing that test harness preceded the passing browser runs. An attempt to rename
an uncreated report exposed that compute.sh does not forward arbitrary environment
variables; JSON reports were recovered exactly from retained successful run logs.
Temporary repositories, side records, site output and browser profiles are not
part of the public artifact. Shared package files/environments were not modified.
