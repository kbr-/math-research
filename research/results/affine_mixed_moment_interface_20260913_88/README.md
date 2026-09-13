# Pair compatibility at the first affine ENS interaction band

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-first-mixed-band)
contains the exact component equations, necessary-and-sufficient pair
duality condition, conditional transfer, source-cofactor relation, and
finite applications.

For binary affine input blocks with original companion degree 2h+1, put
D=3h+u, 1<=u<=h, L=D-h, H=D-2h. Cofactors have degree at most h+u-1<2h.
The historical diagonal mixed system therefore needs only singleton
functionals through L and pair functionals through H.

Write U_b=span{q*g_bi : deg q<=u-1} and let W_b be the span of the classes
q*g_bi*g_bj, deg q<=u-1, in P_<=H/I_H(F). Pair feasibility for fixed
singletons is exactly the following condition:

    A_j in U_b, B_k in U_a,
    A_j*g_bk + B_k*g_aj in I_H(F) for all j,k
    implies sum_j mu_aj(A_j) + sum_k mu_bk(B_k) = 0.

If W_a intersect W_b = 0 for every distinct pair, this is automatic.
Each product in the kernel is separately an old NS consequence, and the
Boolean square argument puts A_j and B_k in I_(h+2u-1), inside the
singletons' annihilation domains.

The PC-based supported construction supplies all singletons from the same
old functional annihilating C_D. Each pair can then be filled independently.
The resulting functional annihilates the augmented degree-D NS space and
preserves all old moments. By duality, every old-only augmented NS
consequence transfers to old PC through the same D, without a block-count
or fan-in charge. This does not apply to an augmented PC input derivation.

For functional PHP with N>=2D-1, base filtration stability supplies
normalized old designs and identifies the old NS/PC spaces. The criterion
therefore excludes augmented NS refutations through D.

## The supplied-certificate interface

Extract a complete diagonal monomial R_(a,j) from a block-b companion
cofactor, obtaining coefficients c_(b,i;a,j) of degree at most u-1.
The full certificate forces

    (sum_i c_(b,i;a,j)*g_bi)*g_bk
    + (sum_i c_(a,i;b,k)*g_ai)*g_aj in I_H(F).

These are the same pair-kernel relations as the component-duality test.
For a particular old-target certificate, separation is needed only on
pairs with surviving pure complete-diagonal cross support. The proof
annihilates the terms of that certificate; it does not assert a full joint
design on unrelated omitted interactions.

Actual source MP-A tuples can be nested, so their product spaces need not
be separated. At u>=2, the separation test is additionally restrictive:
every cross-input product lies in both spaces through diagonal Boolean
reduction. Source budgets can exceed 4h, where higher mixed components
become necessary. These remain application gaps, not completed source coverage.

## Exact finite applications

| N | h | D | Groups | Inputs per group | Square-space rank | Separated pairs |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 11 | 1 | 4 | 6 | 6 | 21 | 15 of 15 |
| 13 | 2 | 7 | 7 | 7 | 28 | 21 of 21 |

square-pairs-N11.jsonl and square-pairs-N13.jsonl preserve every input,
old quadratic quotient, product generator, and pair comparison.
All 36 random-fixture pairs have zero intersection.
The corresponding clause-span controls have the same individual ranks,
but every one of their 36 pair intersections has dimension one and
contains the old unit class. This is an intended failed-hypothesis control.
The controls are still handled by known clause pruning.

The N=11 inputs are exactly the preceding independent fixture whose global
degree-two relative intersection was zero. Its within-block product spaces
are smaller: they multiply one input only by another input of that block,
rather than by every old affine polynomial.
The new theorem applies despite the old global shared-class failure.

Since N>=2D-1 in both fixtures, the exact pair checks and the analytic
theorem give normalized augmented designs through degrees four and seven,
and corresponding NS degree exclusions. This is not an augmented PC
lower bound or a full asymptotic source theorem.
No degree-seven joint moment array was explicitly constructed.

## Complete trace encoding

All arithmetic is exact F2 packed-word linear algebra. The original
quadratic quotient convention and its complete old row-generator basis
are retained from the preceding checker. Input vectors and base reductions
are fully recorded.

Each square product is specified by its two input indices, then its base
reduction trace, square-space reduction trace, and new pivot. These data
reconstruct the basis row exactly; a duplicate expanded matrix is unnecessary.
Each pair starts with its left square-space basis and adds the right basis,
recording every row-reduction trace and pivot. The final intersection
dimension is rank(left)+rank(right)-rank(union).

Indices are zero-based. Multiplier -1 denotes one in old base records.
The board's monomial map and sparse vector conventions are unchanged:
(-1,-1) is one, (cell,-1) is a variable, and (cell_a,cell_b) is a matching.
The existing result record describes the shared encoding in full.
No operational output or derived rank certificate is left only in scratch.

## Reproduction and validation

Use fresh output paths and a fresh timing session:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_quadratic_relative_kernel.cpp \
  -o /tmp/check_quadratic_relative_kernel
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_relative_kernel --out NEW_N11.jsonl --square-pairs
./compute.sh run TURN --threads 1 -- \
  /tmp/check_quadratic_relative_kernel --out NEW_N13.jsonl --square-pairs --holes 13
~~~

The default mode remains unchanged. After adding the optional mode, it was
rerun to a temporary output and compared with the preceding complete
19,723,290-byte result using cmp. The files were byte-for-byte identical.
This was a code-regression check, not new mathematical evidence; its full
output already exists in the preceding committed result.

Compilation, both new runs, and the regression comparison passed within
the shared resource boundary. No dependencies were installed.
provenance.json pins the code, helper, new outputs, this record, preceding
evidence, and exact historical moment/lifting arguments. No external paper
was needed.

Initial preparation included forward mathematical planning as well as
checkpoint work. The coding window also included generalizing the proof
from the first boundary to the displayed first band. These mixed windows
are disclosed without retrospective timing reclassification.
The notebook records the process assessment and the actual source gap.
