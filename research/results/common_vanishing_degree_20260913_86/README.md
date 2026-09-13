# Exact common vanishing degree for jointly independent affine groups

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-common-vanishing-degree)
contains the full coordinate proof, uniform residual construction, degree
obstruction, and remaining quadratic-PHP interface.

Over F2, jointly independent affine input groups can all be included in an
invertible affine coordinate system. A common Boolean vanishing class then
has exactly the monomials meeting every input group. With M nonempty groups
of sizes r_b and R=sum r_b, the first nonzero degree is M, and the integer
generating polynomial for degree dimensions is

    (1+z)^(v-R) * product_b ((1+z)^r_b - 1).

Degree refers to the canonical multilinear Boolean class, not an arbitrary
formal polynomial. Formal Boolean equations already belong to the old base.

Pairwise independence is insufficient: the spaces span(u1,u2), span(u3,u4),
and span(u1+u3,u2+u4) have pair ranks four and joint rank four. The nonzero
quadratic u1*u4+u2*u3 vanishes on every block-zero space.

For each integer r<=floor(n/2)+1, construct r blocks of r homogeneous affine
inputs. A uniform full-stack rank bound gives an inventory retaining
r=floor(N/2)+1 groups and joint rank r^2 modulo rows on every matching
residual N>=4*ceil(log2(n+1)). The entire inventory has O(n^2) blocks,
O(n^3) forms, and O(n^5) binary coefficients.

At h>=ceil(log2(n+1)), D>=2h+1, every usable residual lies in that range.
Its selected class has no nonzero common Boolean class through floor(N/2),
and none at any k fitting the current learning ceiling
B=max(1,k-1)*D+k with N>=2B-1. Because the full stack is independent modulo
rows, the same conclusion holds after imposing the affine row equations.
Quadratic PHP exclusions have not been incorporated into that membership
calculation; that richer interface is the next task.

This obstructs the actual current Boolean/row common-vanishing method,
not all proof transformations. It constructs no augmented refutation and
does not establish essential use of the inventory in a source certificate.

## Exact finite kernel certificates

common-kernel-checks.jsonl retains each invertible affine coordinate map,
input group, union of block-zero points, monomial map, row-echelon basis,
original-row combination witnesses, and complete kernel basis at every degree.

| Fixture | First degree | Degree spaces | Verified kernel vectors |
| --- | ---: | ---: | ---: |
| Three pairs in six variables | 3 | 7 | 81 |
| Three pairs and two free coordinates | 3 | 9 | 432 |
| Four pairs in eight variables | 4 | 9 | 297 |
| Three pairwise-independent, jointly-dependent pairs | 2 | 5 | 12 |

All 30 degree spaces and 822 basis vectors pass. Vector counts are summed
over separate degree spaces, not asserted to be distinct Boolean functions.
Every independent fixture agrees with the complete Hilbert coefficient
count. The dependent fixture has a one-dimensional quadratic kernel.
These are Boolean affine-space checks, not PHP refutation searches.

Masks use bit j for coordinate j, with all indices zero-based.
affine_rows and affine_constant_mask specify u=A*x+c.
Input probes are masks of linear combinations of the u coordinates.
Feature lists contain squarefree old-variable monomial masks in increasing
mask order, filtered by degree. The constant feature has mask zero.
Bitset strings have 256 characters, with index zero at the right;
unused higher positions are zero. Pivot row and kernel strings index the
feature list. Pivot origin_combination strings index union_zero_points.
Each pivot witness reconstructs that row from the original evaluation
matrix; every kernel vector is checked against every original row.

The same output saves all exact joint-stack union summands and sums:
n=64 with cutoff 28 and n=128 with cutoff 32 both have bounds below one.
At h=ceil(log2(n+1)), D=2h+1, all 35 and 95 usable board budgets are checked.
The n=64 cutoff-eight control fails the sufficient union bound.
No large affine matrices are constructed. The existence claim uses the
analytic union-bound proof, instantiated by these exact arithmetic checks.
Large integers are decimal strings. No floating point or randomness is used.

## Reproduction and provenance

Use a fresh session and output path:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_common_vanishing_degree.cpp \
  -o /tmp/check_common_vanishing_degree
./compute.sh run TURN --threads 1 -- \
  /tmp/check_common_vanishing_degree --out NEW_OUTPUT.jsonl
~~~

Compilation and execution succeeded within the shared CPU and memory limits.
Boost multiprecision was already available; no dependencies were installed.
provenance.json pins this record, the checker, full output, and the preceding
common-vanishing and residual-rank provenance. No external paper was needed.

The opening reading window included mathematical planning. The coding window
included sharpening the uniform construction to r=floor(N/2)+1. These marked
windows are mixed; no retrospective timing split is invented. The first idea
of testing the actual kernel arose in the preceding cycle.

The notebook records the process assessment: the exact-kernel calculation
strengthens the prior numerical obstruction, and the dependent control
isolates joint independence. Consolidating superseded working-context detail
is warranted; another workflow rule is not.
