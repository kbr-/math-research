# Higher-dimensional cube witnesses for full old target freedom

The [notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-higher-row-cube-target-extension)
combines existing target-cube packing with a signed residual matching design.
Packing the multiplier edges afterward preserves all Boolean-consistent old
moments through min(D, ell-2), for polynomial one-level affine inventory and
polylogarithmic PC degree. Selector-moment extension remains open.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_cube_dual_design.cpp \
  -o /tmp/math-higher-cubes
./compute.sh run TURN --threads 1 -- \
  /tmp/math-higher-cubes --out NEW_F2_OUTPUT --prime 2 --higher-cubes
./compute.sh run TURN --threads 1 -- \
  /tmp/math-higher-cubes --out NEW_F3_OUTPUT --prime 3 --higher-cubes
~~~

Run from the repository root, with the resource controls active and fresh output
paths. Exact compiled field arithmetic and guarded integer counts are used.
The new option selects new fixtures; the historical edge-only mode remains
available. This cycle did not rerun its historical fixture suite.

## Complete output and scope

Each field file contains two fixtures:

| n, m, B | Selected axis sets | Nonzero moments | Relevant marginal rows | Bit monomials |
| --- | --- | ---: | ---: | ---: |
| 16, 17, 4 | {0,1}, {3} | 2648 | 5466 | 64 |
| 32, 33, 4 | {0,1,2}, {4} | 22832 | 44526 | 325 |

For multi-axis fixtures, read <code>axis_sets</code> and the complete vertex lists
in <code>lines</code>; the legacy <code>directions</code> field gives only each
row's first axis.
Moments use cell IDs row*n+column. Bit-polynomial terms use
[coefficient,[row*ell+axis IDs]], with repetitions representing ordinary powers.
The residual degree-two design uses three distinct labels and signed pair
weights (1,-1,1). Every unlisted moment is zero.

Every potentially nonzero marginal is recorded, including all faces of nonzero
moments and missing-row right sides of nonzero lower moments. All remaining
marginals have zero on both sides. Booleanity and collision constraints follow
from the matching normal form. The total row-equation counts are 32481169 and
4887387681; no enumeration of that zero portion is claimed.

The selected-row monomial checks include every nonempty axis set in each selected
row whose combined bit degree is at most three or four, respectively. Only the
chosen monomial has nonzero value. New target products also contain a term using
two bits in the multiplier row.

Controls delete a top moment, replace signed moments by unsigned ones over F3,
and exhibit a non-top monomial missed by a fixed cube witness. That last control
does not assert an old polynomial relation. The small boards test the dual
detector and residual budget, not the asymptotic affine-family theorem itself.

All mathematical checks passed. A preliminary compiler indentation warning was
corrected. Source/output hashes, complete command evidence, and measured timing
are retained with the checkpoint.
