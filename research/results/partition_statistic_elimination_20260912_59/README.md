# Partition-statistic elimination: analytic evidence

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-partition-statistic-elimination)
contains the full theorem, projection, degree ledger, recognition criterion,
and binary-label control. No new numerical run was performed for this cycle.

## Proof components reused

- A genuine matching removes every pigeon outside a largest partition class,
  leaving exactly s pigeons and s-1 holes when that class has size s.
- The existing [occupancy-freezing projection](https://kbr-.github.io/math-research/#column-freezing-map)
  maps this board to N=floor((s-1)/K)-1 holes for K=-1 modulo p. Its complete
  original-degree base certificates are unchanged.
- The [constant-collapse argument](https://kbr-.github.io/math-research/#column-statistic-elimination)
  removes the selected package level by level. Every class-column statistic is
  already constant; inputs may use only earlier coefficients of this package.
- The [design pullback](https://kbr-.github.io/math-research/#column-freezing-joint-design)
  and the audited residual PC lower bound give the degree consequence.
- Proper-normal-form orbit sums give the class-statistic recognition criterion.
  The existing input-replacement theorem supplies the required degree-safe pass.

The proof reuses the exact base-image evidence from
`../column_statistic_freezing_20260912_54/checks-01.jsonl`; that suite was not rerun.
The initial projection outline was measured in the preceding research interval.

For B classes and fixed p, N is Omega(n/B) when n/B grows. Thus B(n)D(n)=o(n)
would suffice for the degree contradiction if every source block meets the
common-package hypothesis. The notebook states the exact integer size bound.

The binary-label example is analytic: logarithmically many partial-column
indicators can distinguish all pigeons, forcing a singleton common partition.
They are still handled by the single-column normalizer, so the example is only
a limit on inferring a coarse partition from size and sharp Booleanity.

`provenance.json` identifies the reused checker, complete output, and source audit.
The timing fragment and archived session preserve actual work and checkpoint
evidence. Hashing and archival are protected local processing, not new
mathematical verification runs.
