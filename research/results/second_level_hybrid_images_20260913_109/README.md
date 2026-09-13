# Bottom-level removal over a conditioned compact base

The [full notebook proof](https://kbr-.github.io/math-research/#entry-2026-09-13-second-level-hybrid-images)
tracks the actual multilevel binary source after the first hybrid step.
High bottom products become 1-H_a, with f-H_a an old Boolean consequence;
low products become exact affine-flat indicators. Factoring each formal
high-selector difference gives a weighted comparison over old Booleanity.

Adding the explicit old axiom 1-f permits unweighted source replay through
kD, with the original bottom level removed. The conditioned base retains
PC degree at least n/2-deg(f)+1, through the transported class
J_B^f={g: f*g belongs to J_(B+deg f)}.
The later inputs are nonlinear; the affine exclusion theorem is not
automatically iterated.

## Complete source-image certificates

<code>source-images.jsonl</code> contains 59 complete NS certificates
and all source definitions and controls. The two generic Boolean fixtures
use k=3 and accuracies h=1,2:

| h | Highest original level checked | Largest original companion degree | Conditioned ceiling kD | Weighted ceiling k(D+1) |
| --- | ---: | ---: | ---: | ---: |
| 1 | 3 | 7 | 21 | 24 |
| 2 | 2 | 14 | 42 | 45 |

Each fixture has a bottom rank-4h packing block and a rank-(4h+1) learning
block. The weight is x0*x1*x2. The learning membership contains a nonzero
Boolean remainder, so H is not silently identified with f as an ordinary
polynomial.

Later formal inputs use both bottom selectors and independent old affine
terms. Every later input, product, and companion has:

- Its complete formal polynomial and high-selector-zero form.
- The verified formal quotient Q in F-F|_(Z_high=0)=Z_high*Q.
- The evaluated quotient and the full weighted and conditioned NS target.
- Every NS cofactor, actual ordinary degree, and checked ceiling.

Factoring before evaluation avoids expanding terms that cancel between the
two images. It retains the complete certificate, rather than merely checking
values at sample points.

Weighted comparisons use only old bit Booleanity generators. Conditioned
comparisons add 1-f. Input Booleanity is separately checked using only old
and strictly earlier coefficient domains. The h=1 fixture includes a third
original level, and h=2 checks multiple factor rows.

Two unweighted controls have actual and virtual parent products one and
zero at an old point where f=0. The conditioned axiom has value one there.
These controls show why the weight or condition is required.
The fixtures are generic source-image tests, not full PHP refutations.

## Namespaces and polynomial encoding

The two bottom selectors are formal placeholders, with IDs stated in each
fixture. Their original weights are 2h. Old bits and all later coefficient
variables have weight one. Genuine degree reflection converts the formal
weighted degree into the original ordinary source degree.

The fixture also supplies the actual bottom blocks and all their coefficient
images. Formal selector IDs are not Boolean-domain variables in the
resulting image system. They disappear on evaluation.

Polynomials use [coefficient, sorted variable-ID list with repetitions].
An NS certificate's domain list gives the variable IDs of its Booleanity
axioms in order. If its condition polynomial is nonempty, that polynomial
is the final additional axiom. Its cofactor array follows exactly this order.

Later products and companions are retained in complete factored form through
the formal polynomial, the bottom evaluations, and the new input lists.
Original and new degree ledgers are explicit. No original cofactor budget is
enlarged because a specialized polynomial has lower degree.

## Nonlinear geometry and product controls

The separate nonlinear fixture constructs six inputs y0*yj as images of
rank-two bottom flat indicators. A conditioning weight on three independent
variables is fixed to one; the seven displayed variables remain free.
Their common zero set contains 65 of the 128 assignments.

The complete degree-two restriction map has 29 source monomials and rank
23. An affine codimension-six prediction on those seven free variables
would have dimension two. All zero points, monomials, column vectors,
elimination traces, and reduced vectors are saved. All six inputs have
degree-four Booleanity certificates.

This example has a simple common factor and is not claimed to be hard
to eliminate. It disproves the inference from polynomial span rank to
affine zero-space dimension in the actual image class.

A final certificate records f*(1-y7)=0 modulo Booleanity for
f=y7*y8*y9, although both factors are nonzero Boolean functions.
This explains why a further weight must be nonzero in the conditioned
class, not merely nonzero before conditioning.

## Reproduction

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_second_level_hybrid_images.cpp \
  -o /tmp/math-second-level-hybrid-images
./compute.sh run TURN --threads 1 -- \
  /tmp/math-second-level-hybrid-images --out NEW_OUTPUT.jsonl
~~~

Compilation and the sole numerical run passed on the first attempt.
The checker refuses existing outputs and installs no dependency.
Source, shared polynomial and binary-linear-algebra headers, this record,
and all output are pinned by <code>provenance.json</code>.
The session archive retains complete command output and the timing journal.
