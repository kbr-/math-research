# Full-base relative learning and exact quadratic PHP kernels

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-quadratic-relative-kernel)
contains the complete conditional transfer, its strict example, the exact
shared-space target, the finite comparison, and the remaining source gap.

If f has actual degree s<=c and belongs to I_c(F union G_b) for every
one-level affine input group, a degree-D augmented PC or NS refutation
learns f from F through

    B=max(1,c-1)*D+s,       D>=2h+1.

This extends the earlier Boolean-membership argument to all old base
relations and separates certificate degree from actual target degree.
For binary functional PHP, a nonzero relative class outside I_c(F), with
N>=2B-1, contradicts base filtration stability. No rank condition is asserted
to guarantee such a class.

## Exact spaces and parameters

The fixture has N=11 holes, 12 pigeons, and 132 old variables. The base
includes Boolean equations, same-row and same-column exclusions, and row
sums equal to one. There are 7393 matching monomials through degree two.
The remaining row-generator NS span has rank 1398, so Q_2 has dimension 5995.

Each family has six groups of six affine inputs, with all 36 linear parts
jointly independent modulo the 12 row-sum vectors. The combined rank is 48.
These are local fixtures with the preceding construction's rank geometry,
not globally verified restrictions of the asymptotic inventory.

The random fixture uses std::mt19937_64 with seed 2026091387.
The collision-span control uses seed 2026091388. Each of its groups begins
with a collision pair in column zero, then receives independent additional
forms vanishing at the all-column-zero row assignment. An invertible prefix
basis change is applied within every control group.

| Groups intersected | Random fixture | Collision-span control |
| ---: | ---: | ---: |
| 1 | 705 | 695 |
| 2 | 36 | 45 |
| 3 | 0 | 13 |
| 6 | 0, forced after group 3 | 13 |

Dimensions are in Q_2. Remaining random block spaces were not computed
after the intersection became zero. Their complete inputs and full joint
rank were still verified. All six control block spaces were computed.

At h=1,D=4, a degree-two membership certificate and target degree s<=2
give B=4+s<=6, which fits N>=2B-1. This is outside the old NS window D<=3h.
The random fixture has no affordable shared class under this ledger:
R_2=0, R_1 injects into R_2 by base filtration stability, and c>=3 costs
at least 8, above the stable ceiling 6.
This is a finite method obstruction, not an asymptotic source theorem or
a computation of the augmented ENS refutation degree.

## Meaningful controls

The collision control reuses the established clause-pruning identity

    1 = xy + (1-x) + x*(1-y).

After prefix mixing, the input contribution is G_0+x*(G_0+G_1).
Every column-zero variable z also follows through degree two by using
z=z*(1-w)+zw for a different selected cell w in that column. One and all
twelve column-zero variables give thirteen independent relative affine
classes; the computed dimension makes this exactly the control's shared
space. It is an already handled clause-span mechanism.

No PC closure is performed. Although each control relative NS space
contains one, its additional rank is 695, not the entire quotient dimension.
Multiplying that derived certificate would generally increase its NS degree.

Remove the column-collision axioms and assign every pigeon to column zero.
This satisfies all remaining Boolean, same-row, row-sum, and control input
constraints. The checker verifies 1596 row-generator multiples and 4788
input multiples there, all zero; one evaluates to one. This explicitly
satisfiable control verifies the role of column collisions and the normal form.

## Full certificates and encoding

relative-kernel-checks.jsonl retains the complete 19,723,290-byte output:
board monomial maps, all emitted affine inputs, Gaussian reductions,
block-space bases, intersection traces, dimension identities, old normalized
design and separating functionals, and the satisfiable control.

All arithmetic is exact F2 XOR, with compiled packed-word kernels.
The existing binary_php.hpp supplies the generic Space implementation;
its weak degree-three Board class is not used here.
The new QuadraticBoard explicitly includes same-row exclusions and can
omit column exclusions for the satisfiable control.

All indices are zero-based. Cell i*N+j denotes x_(i,j).
Monomial pairs (-1,-1), (a,-1), and (a,b) denote the constant, a cell, and
a two-cell matching. Sparse vectors list nonzero monomial indices.
Multiplier -1 denotes one; other multiplier values are old cell indices.
Affine input lists therefore use index zero for the constant and 1+cell
for each linear coefficient. No ENS coefficient variables enter these
old-input relative-space computations.

The base is generated only by original row equations times one or a variable,
after exact Boolean/exclusion normal form. Blocks add only their original
affine inputs times those same multipliers. Quotient projection uses the
base row-echelon basis. Every new row records the pivots used to reduce it.

Intersections start with the left basis and add the right basis. Each joint
pivot carries its left-space component. A dependence yields an intersection
vector, which is checked in both parent spaces. The saved trace and left
components reconstruct the certificate; each intersection dimension is
checked against rank(left)+rank(right)-rank(union).
Source rows and previous intersection bases are all retained.

## Reproduction and provenance

Use a fresh session and output path:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_quadratic_relative_kernel.cpp \
  -o /tmp/check_quadratic_relative_kernel
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_relative_kernel --out NEW_OUTPUT.jsonl
~~~

Compilation and execution succeeded under the shared limits. No dependencies
were installed. The full matrix output is committed, not left in runtime logs.
provenance.json pins the checker, shared header, output, this record, and the
preceding kernel/learning provenance. No new external paper was needed.

Initial preparation includes the preceding research checkpoint, the separate
working-context consolidation, and their publication. The mathematics window
included computation design before the coding marker; this overlap is
disclosed without an invented split. The conditional transfer and algebraic
control arguments are proved in the notebook, not inferred from finite ranks.

The source-facing gap remains: a global shared class is only a sufficient
method condition. The next task examines the actual augmented NS cofactor
compatibility equations rather than assuming that condition follows from
the input ranks.
