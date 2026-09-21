# Duplicate-block NS/PC control

These are exact F2 computations on a satisfiable Boolean-domain system, not PHP.
The full symbolic proof is in notebook entry
[heterogeneous-helper-review](https://kbr.is-a.dev/math-research/#entry-2026-09-21-heterogeneous-helper-review).

Two independent accuracy-two blocks P,Q have inputs x_1,...,x_r and all
companions x_i P,x_i Q. Their original companion degree is five. Every variable
is Boolean. The queried target is P+Q. Variable positions and integer monomial
mask encoding are included in each JSON report.

Reproduce from the repository root, using fresh output paths:

    ./compute.sh g++ -std=c++17 -O2 -Wall -Wextra -Werror research/tools/check_duplicate_block_filling.cpp -o /tmp/check_duplicate_block_filling
    ./compute.sh /tmp/check_duplicate_block_filling --rank 3 --out /tmp/duplicate-rank3.json
    ./compute.sh /tmp/check_duplicate_block_filling --rank 4 --out /tmp/duplicate-rank4.json

The checker enumerates squarefree columns through degree 5 or 6, spans every
legal original-generator NS multiple, and computes PC closure. Echelon columns
are sorted by descending degree. Hence the rows with leading degree below the
ceiling span exactly the eligible multiplication subspace. Each such basis row
is multiplied once by every variable; new eligible rows are queued. A final
pass verifies the resulting closure. This does not allow multiplication of a
ceiling-degree line merely because Boolean reduction would lower its degree.

For every absent target, the report preserves a separating dual as integer
monomial masks; its value is one on those monomials and zero on all other
columns. Every dual is checked against the whole echelon basis and target.
Positive membership in the rank-three PC closure is an exact elimination
result, not an independently exported derivation trace. The separate symbolic
argument in the notebook proves the rank-at-least-four lower bound without
relying on these rank outputs.

A separate degree-six polynomial identity is checked with a fresh accuracy-one
helper R; its cofactors, degree and verification are saved in the reports.
The larger augmented system is not exhaustively eliminated. In this identity,
the cofactor of each original companion is the corresponding helper coefficient;
the saved helper cofactors are the sums of the P and Q prefix coefficients.

Results:

| Rank | Degree | NS rank | PC rank | P+Q in NS | P+Q in PC |
| ---: | ---: | ---: | ---: | :---: | :---: |
| 3 | 5 | 6 | 6 | no | no |
| 3 | 6 | 80 | 382 | no | yes |
| 4 | 5 | 8 | 8 | no | no |
| 4 | 6 | 144 | 144 | no | no |

The largest column space has 60,460 columns; its worst full dense basis would
use 457,077,600 bytes before small indexing/container overhead. The actual basis
has only 144 rows. Enumeration is capped at 20 variables and degree six; both
runs used the shared 14-CPU/10-GB controls with one computation thread. No new
packages were installed. Full command output is preserved in the timing archive.
