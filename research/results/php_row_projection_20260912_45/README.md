# Global row projection and pivot-independent normal forms

The complete statements and proofs are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-php-row-projection).
The affine row quotient appeared earlier in the spread analysis; this cycle
applies it to full proof/family preprocessing, with exact degree and support rules.

## Main result and scope

Choose one pivot cell per row and replace it by one minus the sum of the other
cells in its row. Fix all ENS coefficient variables. Every PHP base image has
an NS proof through its original degree, and every retained ENS input is
projected. Thus NS or PC refutation degree, level count, and family count do
not increase. The bare reduced base has the same NS/PC degree as the original
weak PHP base for n>=2; the same holds with an identical already projected
family attached to both presentations.

This is not deletion of a hole, and pivot Booleanity remains a whole quadratic
equation. No same-row exclusion is added. Original-base image certificates can
still use pivot variables even though the projected input polynomials do not.
The current source-derived Booleanity portfolio can be rebuilt sharply; a
generic older certificate is not assumed to remain sharp after degree drops.

All pivot choices give affine coordinate isomorphisms of the row-ideal quotient,
so reduced degrees, ranks, and span/affine-bin criteria are invariant. The
collision-image expansion cost is minimized by one pivot in every column and
one additional pivot in one column. This gives order n^3 instead of n^4 for
common-column pivots. Actual ENS-input sparsity remains a separate consideration.

## Reproduce

From the repository root with resource controls active:

    ./compute.sh start row_projection_reproduction
    ./compute.sh run row_projection_reproduction --threads 1 --category local_processing --timeout 120 -- g++ -std=c++17 -O2 -Wall -Wextra -pedantic research/tools/check_php_row_projection.cpp -o /tmp/math-check-php-row-projection
    ./compute.sh run row_projection_reproduction --threads 1 --timeout 120 -- /tmp/math-check-php-row-projection --out research/results/row_projection_reproduction/checks.jsonl

Use a new output path. The checker reuses exact polynomial, rank, and NS
helpers through a small include guard; previous suites are not run. No new
dependency is installed. Original compilation and execution both succeeded.

## Complete evidence

`checks-01.jsonl` contains 18 cases: n=2,3; p=2,3,5; and last, first, or cyclic
row pivots. Its 612 NS certificates include:

- 441 complete full-PHP base-generator image certificates.
- 36 original/current input Booleanity certificates and 72 input/product
  identities witnessing the row-ideal kernel.
- Six original, eighteen projected, and eighteen packed NS consequences.
- Eighteen degree-five old proofs of a new degree-three companion.
- Three additional pivot-Booleanity proofs for the weak-row controls.

The consistent test tuple is g_i=x+(rho_0-1)y_i, with three distinct variables
from other rows. It has original rank three and degree-two inputs, then projects
to three copies of one affine value. The source NS consequences have degree six;
projected consequences have degree four or five, and rank-one packed consequences
degree two. All final ordinary-polynomial targets are nonzero.

For every pivot case, the output saves inverse affine coordinate matrices,
projected bases and inputs, pivot histograms, ranks, degrees, and actual monomial
counts. Collision-image counts are 15 versus 13 at n=2 and 66 versus 46 at n=3
for common-column versus balanced pivots, over every tested prime. The example's
projected ENS product has four terms when its chosen cell is not a pivot and
3n+1 when it is, showing why base and input sparsity should not be conflated.

All 1,326 Boolean models of the tested row subsystems are retained with a canonical
coefficient lift. Column constraints are omitted from these consistency models;
they are not asserted to model the unsatisfiable full PHP base. The enumeration
includes multi-one rows allowed by the weak modular row equation. Eighteen
separate points model all old row-subsystem axioms of degree at most four while
violating the new degree-three companion. With its saved degree-five old proof,
this gives an exact old-five/new-three NS and PC consequence-degree gap.

Three single-row controls of width p+1 set every entry to one. They satisfy the
row and Boolean equations, including the projected pivot Booleanity, while an
individual same-row product is one. They specifically exclude an interpretation
that silently adds row functionality.

## Schema, provenance, and timing

Polynomials are `[coefficient, [[variable, exponent], ...]]`, with zero encoded
as `[]`. NS records include complete axioms, cofactors, target, and maximum
ordinary summand degree. The arithmetic and ranks are exact over the stated
prime. Coordinates use row*n+column, and coefficient/free-variable ranges are
explicit. Projected base arrays are lists of nonzero original-generator images;
no unreported Boolean or collision simplification is used for their ranks.

`provenance.json` hashes the checker and its reusable sources/kernel, complete
output, this README, and claim index. Timing is embedded in the notebook and
full command evidence is archived under
`research/provenance/session-records/php_row_projection_20260912_45/`.
Source lookups used explicit reading windows followed immediately by the planned
mathematics marker. No rendering or historical-suite rerun was needed.
