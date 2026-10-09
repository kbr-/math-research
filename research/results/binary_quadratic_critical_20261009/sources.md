# Quadratic critical gap — evidence and scope

Research date: 9 October 2026. A route calibration, not a new lower bound.

- Main notebook `weighted-restriction-cube`: complete proof reread; supplies the injected coordinate algebra and weighted-kernel construction. Its source-owned near-half theorem remains attributed there.
- `entry-2026-10-09-coefficient-kernel-counts`: exact intersection invariant and preceding proposed test. Equality with actual prefix rank holds in this coordinate model, not generally.
- `entry-2026-10-08-affine-feature-kernels` and `coherent-upper-spread-raw-core-cost`: full records read to compare charged polynomial normalization with raw span geometry.
- Historical `php_codex_handoff/manuscript/chapters/07_elimination.md`, Theorems 7.6–7.7: full one-block proof reread. It is a stronger generic local transfer and is not superseded.
- Searches covered quadratic unit relations, isotropic subspaces, scalar prefix critical exponents, Gauss sums, polynomial coefficients and common alternating cores. No independent novelty claim. General quadratic-source results surfaced for comparison before the next task; they are not dependencies here.

## Exact checks

Fixed informative parameter r=3, six binary coordinates. `quadric_check.g` uses native GAP finite-field dot products, ranks and Boolean lists. All matrices for h=0,1,2 and one h=3 witness are in `quadric-checks.jsonl`. The failed first run remains in `quadric-checks-first-attempt.jsonl`: it ignored the return of non-mutating IntersectionBlist. The corrected program includes a direct API control. GAP can exit zero despite an assertion failure; saved output determined success.

`certificate_check.sing` verifies ordinary polynomial identities over F2, Boolean cofactors and degrees. `certificate-checks.txt` is the final 29-check report. `certificate-checks-initial-counter.txt` preserves a successful identity run whose counter missed three degree checks.

No random samples, floating-point ranks or installations. Full protected commands and outputs are archived with the session. All-rank validity comes from the notebook proof, not the finite checks.
