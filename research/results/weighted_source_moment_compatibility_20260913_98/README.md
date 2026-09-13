# Exact moments for canonical affine-flat source modules

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-flat-source-module-moments)
proves an exact reduction of formal module-design extension to singleton
low-rank join equations in the band D=6h+u, 0<=u<2h. Pair moments extend by
old-base filtration stability once those equations are feasible. Canonical
sharing and the supplied witness costs are explicit hypotheses.

The compatible PHP preprocessing and the rank-at-most-4h corollary are proved
analytically. This finite computation uses four free Boolean variables,
not a PHP base or a full concrete ENS moment system.

## Complete affine-flat registry

The file <code>flat-module-moments.jsonl</code> uses F2 and h=1. Old coordinates
are x_0,...,x_3. Define the invertible dense signals

    u_i = sum_(j != i) x_j.

Their bit masks are 14,13,11,7. The matrix is its own inverse. A flat record
contains a mask of constrained signals and their prescribed bit values.
Its input basis consists of u_i+value_i for the constrained indices. These
are nonliteral affine forms in the x coordinates.

There are 81 consistent partial-assignment flats, including the whole cube.
The inconsistent intersection has a separate empty-flat ID. Of the consistent
flats, 48 have rank three or four and retain selectors. Ranks at most two
are packed to their exact old indicator products.

Each flat saves its complete old indicator polynomial and its formal value.
The latter is either that packed polynomial, a retained selector, or zero.
Formal selector coordinate 4+selector_id has weight two. Old coordinates have
weight one. Polynomial records are [coefficient, [variable,...]] terms, using
repeated variable indices for powers; identities are ordinary polynomials.

Every ordered pair of consistent flats gives a source comparison, with parent
their intersection: union the compatible affine input constraints, or use
the empty flat when they conflict. All 6,561 comparisons are included;
4,160 have empty intersections. No gate or input relation is sampled.

## Full moment components

The root functional is the sum in F2 of point evaluations at old bit vectors
0,1,2, each with coefficient one. Its total mass is one in F2. It is not
multiplicative: the means of x_0 and x_1 are one, while their product moment
is zero.

The file contains separate complete component data for D=6 and D=7, with
u=0 and u=1 respectively:

- Root moments through degree D.
- One singleton component for every retained flat, through old degree 4+u.
- One component for every unordered distinct selector pair, through old degree 2+u.
- Every distinct triple component is identically zero through old degree u,
  specified once as a complete rule rather than repeating zero arrays.

Repeated selector powers use the component for their distinct support.
Every component array is indexed by the squarefree old-monomial bit mask.
Ordinary old powers are Boolean-reduced when evaluating the functional.
A null entry is outside that component's stated degree domain.

Singletons are the root's point evaluations weighted by the corresponding
zero-flat indicator. Pair components copy the union-flat singleton restriction
through old degree u, and set their other available squarefree moments to zero.
Over this free Boolean base these are valid old functionals. In the PHP theorem,
the analogous extension uses the proved old-base filtration, not this arbitrary
zero assignment.

These tables and the distinct-triple rule determine every moment in the entire
weighted degree-D domain. They are not joint moments of individual raw ENS
coefficient variables.

## Exact module constraints

The tested witness costs are two for old Boolean equations, four for retained
selector Booleanity, and six for every OR comparison. Every allowed ordinary
monomial cofactor is enumerated, respecting those costs rather than only the
degree of the target polynomial.

| D | Old-domain multiples | Selector-Booleanity multiples | OR-module multiples |
| ---: | ---: | ---: | ---: |
| 6 | 7,864 | 3,024 | 6,561 |
| 7 | 30,744 | 13,200 | 32,805 |

All 94,198 values are zero. Each gate record stores its child and parent IDs,
witness cost, constraint type, and all cofactor moments. The type codes are:
0 for entirely packed/constant values, 1 for a retained parent with two packed
children, 2 for one retained child, and 3 for two retained children. There are
609,480,3168,2304 comparisons of those types.

For D=6, the OR cofactor list is just one. For D=7, its order is
one,x_0,x_1,x_2,x_3. Old- and selector-domain enumeration includes repeated
old and selector variables; the counts are not only multilinear cofactor tests.

## Nonextension and canonical-sharing controls

Take the zero-valued signal constraints on subsets {0,1,2}, {0,1,3}, and their
union {0,1,2,3}, called A,B,C. All three retain distinct selectors. The polynomial

    Z_C * (Z_C-Z_A*Z_B)

has weighted degree six and moment one in both saved designs. Its supplied
module cost is eight, so it is not required to vanish at D=6 or D=7.
At D=8 it is an allowed multiple. Thus neither of these particular designs
has a moment-preserving extension to degree eight. Other designs can extend;
this is not a degree-eight refutation or impossibility result.

The second control records the full one-unknown incompatibility that arises
without canonical sharing: one child-pair moment is required to equal parent
means zero and one simultaneously. It has no solution. This does not assert
that every noncanonical registry is inconsistent; arbitrary singleton choices
need compatibility when equal-flat parents remain distinct.

## Reproduction

Use a fresh output path from the repository root:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_flat_module_moments.cpp -o /tmp/check_flat_module_moments
./compute.sh run TURN --threads 1 -- \
  /tmp/check_flat_module_moments --out NEW_MOMENTS.jsonl
~~~

The checker refuses existing output paths. No random seed, new dependency, or
large PHP moment computation is used. The code, exact-polynomial header, this
description, and full output are pinned by <code>provenance.json</code>.
The matching timing archive preserves every command and its full output.
