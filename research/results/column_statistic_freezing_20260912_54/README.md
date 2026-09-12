# Affine freezing of column occupancies

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-column-statistic-freezing)
contains the full projection, original-degree image proofs, statistic-package
elimination theorem, joint-design corollary, and precise remaining scope.

## Construction and theorem scope

Choose K>=1 with K=-1 modulo p. After a matching restriction of r=n mod K rows
and holes, let N=floor(n/K)-1. The remaining source board consists of K copies
of the residual (N+1)-by-N board, K zero columns, and one distinguished row.
The latter uses `q_j=1-sum_i y_ij` in every column copy.

Every original column occupancy becomes a literal zero or one. Copied row
equations have old row images; the distinguished row image is `-K*sum(old rows)`.
Boolean and column-collision images have explicit degree-two certificates.
No same-row exclusions are assumed or verified.

Any finite ENS package whose inputs are polynomials in original column sums and
its earlier coefficient variables can then be removed by constant coefficient
assignments. NS/PC refutation degree is unchanged, independently of family count,
accuracies, or levels. K=p-1 keeps a linear-size residual board for fixed p.
An eligible package may also be removed while other transformed blocks remain.
Arbitrary label-sensitive families are outside the complete-elimination claim.

## Reproduce

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_column_statistic_freezing.cpp -o /tmp/check_column_statistic_freezing
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_column_statistic_freezing --out PATH-TO-NEW-OUTPUT.jsonl
```

The saved session is `column_statistic_freezing_20260912_54`, with `checks-01.jsonl`
in this directory. Output is not overwritten. No random choices are used.

## Complete image checks

All four cases have residual N=3:

| p | K | Source holes | Matching prefix | Base images | Nonzero NS certificates |
| -: | -: | -: | -: | -: | -: |
| 2 | 1 | 4 | 0 | 65 | 50 |
| 3 | 2 | 9 | 1 | 505 | 99 |
| 5 | 4 | 17 | 1 | 2925 | 197 |
| 2 | 3 | 13 | 1 | 1379 | 148 |

Total: 4,874 original base images, with 494 nonzero NS certificates and explicit
zero-image records for the rest. Column collisions use one copy of each unordered
pigeon pair. Every image is checked within its original degree, and all 43 source
column sums are verified as literal constants. Each record includes the complete
affine cell map, old axiom list, and certificate references.

The residual degree-two checks are nonvacuous: the audited PC lower bound already
rules out a degree-two refutation at N=3. No full PHP satisfying model is claimed.

## ENS package and scope controls

Each case also checks four blocks across levels 1,1,2,3, with earlier-coefficient
dependence. Their input polynomials are described in formal variables Z0,Z1 for
two actual source column sums, followed by their fresh coefficients. The two sums'
images were separately verified as zero and one. Their independence as linear
source expressions preserves the formal source degree accounting.

All 32 companion images and 48 coefficient-field images vanish exactly. Five
blocks have all-zero input tuples, hence product image one; all their companions
still vanish. Nonzero field inverses, including values outside {0,1}, are exercised.

The residual-cell polynomial coordinates and these formal ENS coordinates are
labeled separately. The output preserves every source input, product, companion,
field equation, coefficient assignment, and constant image for the package.

Controls record an individual cell that remains a variable, and an invalid copy
count giving a nonzero constant dummy-row image on a model of all degree-one
residual axioms. They are scope checks, not claims that single-cell ENS blocks
cannot be normalized by other methods.

Compilation and all checks succeeded. The kernel optimization identified in the
preceding cycle was tested and committed separately; its work is included in this
session's timing. The projection's initial outline was measured in the preceding
cycle. `provenance.json`, `timing.html`, and the archived session retain exact
sources, full output, and actual intervals.
