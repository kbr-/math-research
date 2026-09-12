# A rank-two design and its logarithmic collision attack

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-low-covariance-collision-prototype)
contains the complete construction, query proof, degree accounting, and scope.

Over F2, a one-collision mean vector can be corrected to a quadratic
functional-PHP design by B=u*v^T+v*u^T of rank two. The verified chessboard
extension theorem extends these prescribed moments through R when N>=2R-1.
Partial-matching lifts and row/column permutations preserve rank two.

However, every supported first-moment vector is a one-hot assignment with
one doubled column and all other columns singly occupied. A deterministic
linear-query tree finds its collision in at most

    ceil(log2 n) + 2*ceil(log2(n+1)) - 1

queries. The column exclusion gives a conflict at the leaf. The attack applies
to every higher-degree extension and every distribution supported on these
first moments, independently of its covariance. Low rank alone supplies no
pseudo-solution guarantee.

## Reproduction

No dependencies were installed. The exact C++17 checker uses one thread.
From the repository root, use a fresh output path if replaying:

~~~bash
./compute.sh run nonuniform_low_covariance_20260912_79 --threads 1 \
  --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_low_covariance_collision.cpp \
  -o /tmp/check_low_covariance_collision_79
./compute.sh run nonuniform_low_covariance_20260912_79 --threads 1 -- \
  /tmp/check_low_covariance_collision_79 --out NEW_OUTPUT.jsonl
~~~

The original run wrote collision-checks.jsonl. It contains:

- Full quadratic moment matrices for N=3,4,6,8, with 160,385,1435,3825
  normalization-compatible moment/symmetry checks, respectively. All pass;
  each covariance has rank two. The zero-covariance control fails one column
  exclusion in each case.
- Every collision-column and unordered row-pair combination for n=3,4,6,8,12,16:
  18,40,126,288,936,2176 cases, totaling 3584. Other rows use a canonical
  bijection to the remaining columns; other bijections are not separately
  enumerated. They do not affect any query answer in this algorithm.
- The complete mean destination vector, every query polynomial in structured
  form, its answer, and the final two rows and column. Maximum observed heights
  are 5,6,8,9,11,12, within the proved bounds 5,7,8,10,11,13.

All indices are zero-based. Variable (i,j) has index i*n+j. A_rows stores each
matrix row as a binary string; mu is encoded by mean_destinations. The vectors
u and v are stored by support, so B and A can also be reconstructed exactly.
A column_defect_sum query is sum over its listed columns of
(1+sum_i X_ij); a column_row_sum query is the sum of its listed row variables
in the indicated column. Arithmetic is over F2. The leaf's product value zero
uses the column axiom, not a numerical assertion about an uncomputed extension.

The general extension statement and all-degree attack are analytic; no
higher-degree design was computed here. The checker makes no random choices.
All compile/run commands succeeded and their complete output is archived.
provenance.json pins the source, output, and prior dependency evidence.

## Measurement and process

Initial preparation includes the preceding checkpoint, compaction restoration,
and the separately committed user-requested missing-paper rule. Brief planning
of the finite check occurred during the mathematics phase; implementation and
its detailed design were marked as coding. No times were retrospectively split.
One notebook-patch invocation failed at JavaScript parsing before changing files;
the corrected invocation succeeded. This was an editing failure, not a failed
mathematical check.

Testing the first moments avoided an unnecessary extension-field covariance
attack or sampling of higher-degree fillings. The existing bounded-test workflow
was sufficient; no additional framework rule was warranted.
