# Deterministic layouts from bounded profile exceptions

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-bounded-exception-layouts)
contains the full deterministic construction and original-degree NS/PC ledger.
If at most a chosen classes omit any pigeon and at most b pigeons are excluded
in any column, K>=a+b copies suffice after filtering the columns missing a
selected pigeon, with K=-1 modulo p. The canonical choice is
`K=p*ceil((a+b+1)/p)-1 <= a+b+p-1`.

## Matching equality checks

The same short-path matcher works whenever the two minimum degrees sum to at
least K. The new checker tests all 7,471 qualifying four-by-four graphs,
including 6,566 equality cases. Every graph mask and verified matching is saved.
A degree-sum K-1 graph has an explicit Hall-deficient subset. This is a control
on the uniform degree criterion, not a lower bound for every special layout.

The matching algorithm was unchanged. Its valid domain was proved more broadly,
and the old source was exposed behind a main guard for reuse. The earlier large
majority fixtures were not rerun.

## Complete path-exception projections

The chosen class in path column j is all pigeons except j and j+1. Both exception
bounds are two, the chosen-class intersection is empty, and an endpoint pigeon
requires one initial matching deletion. There is no additional residue prefix.
Every residual board has N=3.

| p | K | Source holes | Base images | Nonzero NS certificates |
| -: | -: | -: | -: | -: |
| 2 | 5 | 21 | 5335 | 246 |
| 3 | 5 | 21 | 5335 | 246 |
| 5 | 4 | 17 | 2925 | 197 |

All 13,595 original base images fit their original degrees, with 689 nonzero
NS certificates and explicit zero-image records. All 118 local class statistics
are verified as literal constants. Three accuracy-one blocks contain the full
respective inventories; all 118 companion and 118 field images vanish.

Saved permutations identify path labels with the base checker's physical row
and column labels. Physical row zero and column zero form the matching prefix;
the final physical row is distinguished. In path labels the prefix matches
pigeon n-1 to column n-1, and the distinguished pigeon is n.

Copy shifts are two when residual row type i equals j+1, and zero otherwise.
All 36 local allowance graphs and their actual copy permutations are checked.
Three characteristic-five graphs have minimum-degree sum exactly K=4.

The source input sums are specified by saved row lists and column indices.
The standard ENS formulas, fresh coefficient indices, and original degrees
1,3,p complete the source definitions. The first unit input is the complementary
class in the matched column; no source degree is recomputed from its image.

The existing nonconstant-cell and invalid-copy-count controls are checked on
these new maps. The latter's point satisfies only residual row equations.
No full PHP satisfying model is claimed; N=3 already excludes a degree-two
base refutation, making the image certificates nonvacuous.

## Reproduce

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_bounded_exception_layouts.cpp -o /tmp/check_bounded_exception_layouts
./compute.sh run CHECK --threads 1 --category computation --timeout 120 -- \
  /tmp/check_bounded_exception_layouts --out PATH-TO-NEW-OUTPUT.jsonl
```

The checker refuses to overwrite output. `checks-01.jsonl` preserves all graph
tests, maps, certificates, class inputs, and coefficient assignments. Compilation
and all checks passed. `provenance.json`, the timing fragment, and the archived
session preserve full sources and measured work.

The initial bounded-exception outline was measured in the preceding cycle.
Some exploratory reasoning about the next total-budget step was mixed into
this interval's coding phase; no retrospective timing split is claimed.
Final preparation also included context restoration and responding to the user's
renewed Spin publication authorization; the brief documentation follow-up was
partly mixed with that preparation.
