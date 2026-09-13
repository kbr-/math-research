# Proper source OR comparison beyond the first band

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-proper-OR-source-interface)
contains the complete source-support reduction, cofactor extraction, and
computer-assisted local NS degree theorem. This is not a PHP lower bound.

The domain-only Booleanity theorem, equal-span quotient, affine packing,
and source OR-union identity already existed. This cycle applies their
exact budgets to the direct NS source and tests a proper comparison that
survives the stated scalar/span/rank passes. Binary Booleanity modules can
use no companions; canonical equal-flat comparison modules have zero targets.
Remaining affine ranks exceed 2h, but comparisons between different flats
can still carry larger complete-block supports.

## Actual source relation

Let I_0 be the disjoint union of I_1 and I_2. The saved source certificate is

    P_0-P_1*P_2 = sum_(i in I_1) U_i^1*E_(0,i)
                + sum_(k in I_2) P_1*U_k^2*E_(0,k)
                - sum_(i in I_1) P_2*U_i^0*E_(1,i)
                - sum_(k in I_2) P_1*U_k^0*E_(2,k).

The collected cofactor of E_(1,i) has degree 4h-1 and two complete foreign
blocks. Its selected coefficient is f_i^(h-1)*f_k^h. Multiplying by the
original degree-(2h+1) companion gives degree 6h and selected three-block
coefficient f_i^(2h)*f_k^h. These are nonzero in the independent-input
fixtures, including after Boolean reduction of the latter expression.

The whole identity's three-block coefficients still cancel. This local
cofactor is not asserted to survive every global certificate rewrite.
The first-band argument for omitting higher equations does not cover it;
no claim is made that every higher moment must have a nonzero value.

## Ordinary certificates above the packing threshold

`proper-OR-union-checks.jsonl` uses child rank r=2h+1 and independent old
coordinate inputs. The child spaces are distinct, exclude one, and have
rank exceeding the packing cutoff. The union has rank 2r.

| h | Child ranks | Union rank | Source NS degree | Support checks | Domain-only certificates |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | 3,3 | 6 | 6 | 18 | 3 through degree 4 |
| 2 | 5,5 | 10 | 12 | 50 | 3 through degree 8 |

The rank assertions are exact by coordinate construction, not estimates
from a sampled matrix. These fixtures survive the specified generic
normalizations; they do not prove essential survival under every
PHP-specific transformation.

The output preserves all products, source companion axioms and cofactors,
the complete union target, all selected foreign and triple coefficients,
and every domain-only Booleanity coefficient. Ordinary exponents are
retained. Two Boolean-domain assignments with P_0=1, P_1=0, P_2=1 show that
the comparison cannot be proved from domains alone, even though all three
products have domain-only Booleanity certificates.

## Exact minimum degree at accuracy one

`proper-OR-degree-five.jsonl` uses the same h=1, ranks-3+3 instance:
six old variables, twelve coefficient variables, twelve complete ENS
companions of original degree three, and all Boolean domains.

Degree-five Boolean normal form has 12,616 squarefree monomials. The
complete NS matrix consists of all 172 squarefree degree-at-most-two
cofactors for each companion, or 2,064 generator multiples. Domain
generators reduce to zero; Boolean reduction is degree-complete. This
matrix is an original-axiom NS span, not augmented PC closure.

Exact rank is 1,450. The target P_0-P_1*P_2 has a nonzero remainder and a
saved normalized separating functional with value one on the target.
Every basis row is checked against the functional; the complete generator
traces show that all allowed multiples lie in that span. If necessary,
evaluation at the all-zero satisfying point is added to normalize the
functional without changing its target value.

Thus the target is not an NS consequence through degree five. The complete
degree-six source certificate gives minimum NS degree exactly six. The
notebook extends this to jointly independent affine tuples of any ranks
r_1,r_2>=3 at h=1: an affine coordinate change and restriction to three
coordinates in each group preserve the original degrees. Extra old
equations could change this conclusion; it is not asserted over the PHP
base. No minimum-degree conclusion is claimed at h=2 or higher accuracy.

## Encoding

Ordinary polynomial terms use
`[coefficient, [[variable, ordinary_exponent], ...]]`; zero has degree -1.
Old coordinate inputs are first. B1 has h rows of r coefficients, B2
follows with the same shape, and B0 follows with h rows of 2r coefficients.
Each case records all starting indices. The h=2 case uses fifty variables;
the shared checker's capacity was raised to sixty-four for this case.

Domain-cofactor j multiplies the original field generator x_j^2-x_j.
Monomial division records the entire coefficient polynomial and verifies
the sum against P^2-P within degree 2*deg(P). It uses no companions.

The degree-five matrix lists squarefree monomials as integer masks, ordered
first by degree and then by increasing mask. A basis-vector index refers
to that list. Every generator record gives its axiom index, cofactor mask,
reduction trace, pivot, and new basis row if independent. Axioms 0..5 are
union companions, 6..8 first-child companions, and 9..11 second-child
companions. The target record includes its complete vector, reduction,
remainder, and normalized separating dual. The full ordinary companion
polynomials are also saved, so every matrix row is reconstructible.

## Reproduction

Use fresh output paths from the repository root:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_mp_composition.cpp -o /tmp/check_mp_composition
./compute.sh run TURN --threads 1 -- \
  /tmp/check_mp_composition --out NEW_UNION.jsonl --proper-or-union
./compute.sh run TURN --threads 1 -- \
  /tmp/check_mp_composition --out NEW_DEGREE_FIVE.jsonl --proper-or-degree
~~~

All arithmetic is exact and compiled. Both builds and both runs passed
within the shared CPU/memory boundary, with modest matrix storage. No
dependencies were installed and no historical suite was rerun. No
fifty-variable degree-eleven matrix was attempted. A draft notebook patch
had out-of-order hunks and was rejected, then corrected; it did not affect
the mathematical checks or previously saved entries.

`provenance.json` pins the source, binary linear-algebra helper, complete
outputs, and this record. `timing.html` and the archived session retain
actual timing, commands, and complete operational output.
Preparation includes some forward mathematical planning; no timing split
was retroactively estimated.

The next obligation is family-level incidence and composition of retained
proper comparison modules. A local three-block certificate or local degree
lower bound does not supply a global batch bound or a PHP lower bound.
