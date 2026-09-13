# Faithful affine pairs and coherent singleton components

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-faithful-pair-coordination)
contains the complete working proofs, exact hypotheses, degree accounting,
finite application, and remaining source gap. This directory preserves the
computational evidence and its reproduction instructions.

At the first boundary D=3h+1, the relevant pair arrays are affine. If the
old bounded NS quotient introduces no relation in the sum of the two raw
Boolean input-square spaces, their polynomial-array kernel is zero unless
the input spans are equal. Equal spans leave one scalar, which can be
chosen coherently using the supported root construction. This gives a
same-degree old-target NS-to-PC transfer. The notebook also proves a
certificate-specific extension for 3h<D<=4h when the actual extracted
arrays Boolean-reduce to affine polynomials.

These are sufficient hypotheses. The actual source's old quadratic
relations, larger supports, and multilevel propagation remain open.

## Files and inherited evidence

- `ambient-certificate.json` extracts one rank-six affine space from the
  complete eleven-hole certificates of cycles 87 and 88. It preserves all
  six affine input vectors and the inherited pivot/dimension evidence.
- `nested-pair-checks.jsonl` preserves eight small pair-kernel calculations,
  all 2,145 comparisons in a 66-block translated family, its complete
  zero-space cover, and three singleton/pair-component controls.
- `provenance.json` pins new code, outputs, this record, and the inherited
  source records and their manifests.
- `timing.html` and the archived session record preserve actual timing,
  commands, and complete operational output.

The ambient extractor is a small Python streaming/metadata controller.
It does not recompute matrix ranks. Its inputs are:

    research/results/quadratic_relative_kernel_20260913_87/relative-kernel-checks.jsonl
    research/results/affine_mixed_moment_interface_20260913_88/square-pairs-N11.jsonl

It cross-checks the ambient inputs, joint independence modulo rows,
degree-compatible pivot counts, recorded ranks, and absence of the unit.
All original numerical elimination was performed by the existing C++
checker; these old runs were not repeated for this cycle.

There are 132 cells and 12 independent row equations, leaving 120 Boolean
row coordinates. For the selected six inputs U, the degree-two relative
ideal has dimension 705 and affine intersection dimension six. Adding
the 121-dimensional affine space gives dimension 820 both before and
after mapping to the full functional-PHP quotient, whose dimension is
5995. This certifies injection of the whole linear-plus-relative-ideal
space. The input-product space has dimension 21 and does not contain one;
its unital degree-two span has dimension 22. The JSON field called
`unital_quadratic_algebra_dimension` records this truncated vector-space
dimension, not closure under arbitrary multiplication.

## The 66-block application

For every c in F2^6, form (U_1+c_1,...,U_6+c_6). Add the first five U's
as a nested tuple and an invertible prefix-basis change of the zero
translate. Each pair-product sum lies in the certified 22-dimensional
space, so all pairs satisfy the new faithful-map hypothesis.

| Square-space intersection dimension | Pair count |
| ---: | ---: |
| 14 | 62 |
| 15 | 3 |
| 20 | 2,079 |
| 21 | 1 |

There is one equal-span pair and three strict nestings. No pair passes
the previous separation test. Every ambient value has exactly one zero
tuple among the 64 translates. Thus the global Boolean common vanishing
space is zero at every degree. The notebook uses the stronger
820-dimensional injection to prove that the full-base degree-two common
relative space is also zero. Neither statement is inferred from pairwise
rank tests alone.

At N=11, h=1, D=4, old filtration stability and the analytic transfer
therefore give an augmented ordinary degree-four design and rule out an
NS refutation through degree four. No full eleven-hole joint moment array
was explicitly constructed. The 2,145 product-space comparisons are
computed; their pair-component feasibility follows from the proved kernel
classification and scalar coordination, rather than separate numerical
solutions of 2,145 functional systems.

The aggregate input equations already contain a linear refutation:
U_1+(U_1+1)=1. Consequently the cheap necessary test obtained by setting
all fresh variables to zero does not already exclude this example.
The family uses 2^r translations in rank r; it is a finite application,
not a polynomial-size asymptotic inventory at rank proportional to N.

## Pair kernels and component controls

The pure Boolean pair fixtures are separation, strict nesting, proper
overlap, identical inputs, an invertible basis change, affine offsets,
and a redundant equal-span tuple. Polynomial-array kernel dimensions are
0,0,0,1,1,0,1. In the redundant case the coefficient kernel has dimension
three, including two directions representing zero polynomial arrays.

The eighth fixture uses spans <a> and <a,b> on the domain ab=0. It has an
additional one-dimensional kernel even though its spans differ; this is a
failed-faithfulness control. Its extra relation is harmless for the actual
root-coupled singletons, as the notebook proves. It is not a counterexample
to transfer.

The component control has only Boolean old axioms in three variables,
two identical three-input blocks, h=1, and original companion degree
three. All 256 squarefree joint monomials through degree four in nine
variables are recorded for each case, along with 24 root checks, 18 own
checks, and all 60 allowed companion/cofactor checks.

| Singleton scalars | Pair choice | Companion violations |
| --- | --- | ---: |
| 0,1 | zero | 2 of 60; a nonzero dual kernel value excludes any repair |
| 0,0 | zero | 0 of 60 |
| 1,1 | diagonal supported components | 0 of 60 |

The two matched cases are ordinary joint degree-four designs, extending
the same root evaluation at 000. Boolean axioms hold by the representation.
The mismatched components separately pass their root and own equations.
This is a nonvacuous test of the need to coordinate equal-span scalars.

## Encoding

All arithmetic is exact F2. Small affine words use bit zero for the
constant and bit j+1 for variable j. Pair unknowns are row-major C[j,i_b],
followed by row-major D[k,i_a]. Every pointwise equation, row-reduction
trace, pivot, coefficient-kernel vector, and represented polynomial array
is retained. Kernel vectors are checked against the original equations.

The translated family uses degree-two words ordered as one, the six
linear variables, then lexicographic unordered pairs. Product records
identify both inputs and retain reduction traces and pivot basis rows.
Each pair adds its right square-space basis to the left basis and records
every elimination step. The cover records every one of the 64 values.

Joint-moment masks use old variables in bits 0..2, first-block fresh
variables in 3..5, and second-block fresh variables in 6..8. Multiplier
-1 denotes one. Companion construction retains the original degree-three
budget even when Boolean reduction reduces individual monomial degrees.
The inherited ambient affine encoding is separate: index zero is one,
and index 1+i*N+j is the board cell x_(i,j).

## Reproduction

From the repository root, use fresh paths and a fresh timing session:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  python3 research/tools/extract_ambient_certificate.py \
  --relative research/results/quadratic_relative_kernel_20260913_87/relative-kernel-checks.jsonl \
  --squares research/results/affine_mixed_moment_interface_20260913_88/square-pairs-N11.jsonl \
  --out NEW_AMBIENT.json
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_nested_pair_compatibility.cpp \
  -o /tmp/check_nested_pair_compatibility
./compute.sh run TURN --threads 1 -- \
  /tmp/check_nested_pair_compatibility --out NEW_CHECKS.jsonl
~~~

The extractor, compilation, and exact checks passed within the shared
resource boundary; no dependencies were installed. Coding included some
mathematical planning, and context restoration remained mixed with the
active proof phase. These intervals are disclosed without inventing a
retrospective timing split.
