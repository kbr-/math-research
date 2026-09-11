# Target annihilators and matching restrictions — 11 September 2026

Full statements and proofs are in [the notebook](../../../notebook.html), entry
`entry-2026-09-11-target-annihilators`, indexed in
[the continued-research claim index](../../CLAIM_INDEX.md).
This record covers target-weighted batching, matching-weight affine rigidity,
and a favorable spread embedding removed by one global matching restriction.
It does not establish coverage of arbitrary Frege simulations.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic research/tools/check_target_annihilators.cpp -o research/tmp/check_target_annihilators
./compute.sh --threads 1 research/tmp/check_target_annihilators --out research/tmp/annihilator-recheck.jsonl
```

The checker requires a new output path and refuses to overwrite an existing file.
The compiler was GCC 11.4.0 on Ubuntu. All work used exact compiled finite-field
arithmetic and the shared 14-CPU, 10-GB combined-memory controls. No packages were
installed.

## Outputs and execution history

[checks-03.jsonl](checks-03.jsonl) is the complete final output, 1,052,733 bytes.
It includes 4,589 sparse basis rows, full monomial and embedding maps, 162 spread
inputs, 37 normalization results, and all 160 pair ranks.
[summary.json](summary.json) gives the compact case ledger and exact file hashes.

Earlier outputs are preserved:

- `checks-01.jsonl` contains only the header from the failed first matrix run.
  That run exposed an off-by-one error: multiplication read affine coefficient
  `f[i]` instead of `f[i+1]`, confusing the constant and variable slots.
- `checks-02.jsonl` is the successful corrected PHP/subset/overlap suite.
- `checks-03.jsonl` adds the explicit spread-family checks; the complete expanded
  suite also passed.

The initial compilation failed because three indentation warnings were treated
as errors. They were corrected before the first execution. Both the compiler
failure and the matrix failure are preserved in the measured command logs;
neither is presented as a failed mathematical theorem.

## Ordinary PHP computation

The four cases have p = 2, 3, 5, 7, n = p+5, m = n+1, matching weight
M = x_(0,0), and PC ceiling c = 2. They lie on the upper endpoint of the proved
matching-annihilator range. The kernel dimensions are 16, 18, 22, 26, respectively,
exactly 2m.

The implementation first takes the degree-nonincreasing normal form for the
Boolean and column-exclusion axioms. Constants and variables remain; squares
reduce to variables, and products of different rows in one column vanish.
Products of two different cells in the same row remain.

It spans the normalized row equations and their products by every variable.
The resulting echelon basis has an affine part of dimension exactly m, equal
to the independent original row span. This verifies PC closure at degree two:
only affine predecessors can be multiplied while keeping ordinary degree at
most two, and every variable multiple of this affine span is already present.
Thus the calculation represents the actual normalized C2 space, not only an
NS span assumed to be PC-closed.

Multiplication by M sends the affine basis into this quotient space. Exact
Gaussian elimination computes its image rank. The explicit matching-annihilator
generators map to zero and have dimension equal to the full kernel, proving the
reported finite equality. A same-row collision M*x_(0,1) is checked outside C2,
so inadvertently adding the stronger functional encoding would fail the check.

## Additional mathematical checks

- For N = p+2, the p-subset incidence matrix has rank N-1 and constant-vector
  kernel. This checks the coefficient comparison used in the nonfunctional-row
  restriction argument.
- Thirteen ordinary coefficient identities verify the target-weighted overlap
  formula for every nonzero alpha over p = 2, 3, 5, 7. Their error terms remain
  nonzero, including the explicit witness at (x,y,z) = (alpha,1,1).
- Four spread families use two copies of the finite field K, with extension
  degree 3 for p=2 and degree 2 otherwise. The moduli are recorded and checked
  irreducible by the no-root criterion for degrees two and three. Each pair of
  graph spaces is checked disjoint, and each designated input becomes identically
  one under the same matching (0,0). The general full-rank construction is proved
  in the notebook; these smaller direct sums check its geometry and indexing.

The universal batching and rigidity results remain working mathematical proofs,
not formally verified theorems. The matrix cases are actual small ordinary-PHP
instances; the overlap and spread tests are supporting algebraic constructions.

## Schema

Every output line is a JSON object. Case records specify the field and coordinate
system for subsequent rows:

- `php_case` supplies n,m, ranks, variable counts, and the monomial map. Variables
  are numbered by `row*n+column`, with zero-based rows and columns.
- Monomial `[-1,-1]` is one, `[v,-1]` is variable v, and `[v,w]` is a product.
  The monomial array index is the matrix column.
- `basis_row` stores a normalized pivot and sparse `[column,coefficient]` cells.
  Spaces `normalized_C2` and `target_image` use the monomial map.
  `affine_annihilator` uses column 0 for one and column v+1 for variable v.
- `subset_case` supplies the width for the following `subset_incidence` basis.
- `overlap_identity` polynomials use terms `[coefficient,[x_power,y_power,z_power]]`.
- `spread_case` records the field modulus in increasing coefficient order, its
  two-copy dimension, and the embedding from abstract coordinates to PHP variables.
  Alpha is encoded by its base-p digits. `spread_input` records every graph-basis
  vector; `spread_normalization` and `spread_pair` record every computed check.

All coefficients are reduced modulo p. Sparse bases are complete, not truncated
previews. The implementation guards against more than 256 board variables,
20,000 matrix columns, or 5,000,000 stored sparse entries per basis. Prime values
are at most seven, keeping coefficient arithmetic inside ordinary integers.

## Provenance and timing

The checker source SHA-256 is
`191903ad9d9951be9717c56d7278ea0f63b965609b98543a1f8c4d5d8af41629`.
The final output SHA-256 is
`8dba98c542d66b7af88a2e0796880b75f53d7ca2706345657c74cdf9152e6131`.
The summary preserves hashes of earlier outputs and the historical chapter inputs.

Targeted sources were Chapter 8's nested quotient replay and Chapter 9's spread
and affine-rigidity proofs. Razborov, *Lower bounds for the polynomial calculus*,
Computational Complexity 7 (1998), printed pp. 296–297, Definition 2.4 and
Theorem 3.1, was checked for the all-m>n quantifier. The already imported source
hash is `a733438feeda422d58c004b2331b742380d11d84e587990a2fd240466ecda47f`.
The paper and its full text are not bundled here; see the source audit.

[timing.html](timing.html) is embedded in the notebook, and the
[session archive](../../provenance/session-records/boundary_overlap_20260911_02/)
preserves the command evidence. The interval includes the user-requested claim
index and leaner verification guidance in its preparation phase. No routine site
build or broad notebook-rendering audit was performed for this research entry.
