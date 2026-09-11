# Wide products, Boolean generators, and retained ideal cores

11 September 2026. The [full notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-wide-products-and-generators)
records the exact-product costs, degree-adapted Boolean input quotient,
generator-cover and retained-core criteria, sharper NS copy bound, and a
directional unit identity awaiting its source-specific leaf audit. The cover
criteria remain conditional; no universal PHP elimination theorem is claimed.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_input_generator_cover.cpp -o research/tmp/check_input_generator_cover
./compute.sh --threads 1 research/tmp/check_input_generator_cover \
  --out research/results/wide_or_composition_20260911_23/generator-covers-REPRO.jsonl
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_weighted_core_product.cpp -o research/tmp/check_weighted_core_product
./compute.sh --threads 1 research/tmp/check_weighted_core_product \
  --out research/results/wide_or_composition_20260911_23/weighted-products-REPRO.jsonl
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_ideal_core_cover.cpp -o research/tmp/check_ideal_core_cover
./compute.sh --threads 1 research/tmp/check_ideal_core_cover \
  --out research/results/wide_or_composition_20260911_23/ideal-cores-REPRO.jsonl
```

Use new output paths; parent directories are created automatically. The runs
used GCC 11.4.0, C++17, one thread per process, and the unchanged sparse/ENS/domain
kernels. The first two independent builds and runs were parallel, sharing the
same enforced CPU and memory budget. No packages were installed. All builds
and checks passed. Complete output sizes are:

- `generator-covers-01.jsonl`: 168,881 bytes.
- `weighted-products-01.jsonl`: 233,207 bytes.
- `ideal-cores-01.jsonl`: 5,835,849 bytes.

## Degree-compatible bases and Boolean generator covers

Eight basis cases use p=2,3,5,7 and accuracy one or two. Original tuples are
(x,xy,x-xy) and (xy,x-xy), with common degree-ordered Boolean basis (x,xy).
The output saves every original and canonical block, the affine coefficient
maps, and NS companion-image representations. Field images are checked as
linear combinations of canonical field equations.

The bad basis (xy,x-xy) has companion degrees 3h+2. The transformed original
low-degree companion xP has degree 3h+1. The displayed point x=1,y=0, all
coefficients zero satisfies all axioms available at that lower degree and
violates the target. It is not claimed to satisfy the excluded higher-degree
companions of the full bad system. A separate F3 example shows why a linear
basis must also keep certified Boolean inputs if it is to be packed: the basis
(x+y,x-y) has packed product two and a nonzero companion at x=y=1.

Twenty-four ideal-cover cases use inputs x,xy_1,...,xy_m for m=2,7,31, all four
primes, and accuracy one or two. Their linear rank is m+1, verified by distinct
ordinary monomials. The single Boolean generator x has the exact input witnesses
g_i=q_i x; packing it makes every companion a degree-two or degree-three multiple
of x^2-x. The original parent remains fully specified in factored form, including
all input polynomials, coefficient coordinates, and the 3h product-degree ledger.

## Weighted prescribed products

Six patterns are tested over each of the four primes. Input monomials use
disjoint Boolean-variable sets; child coefficients have their Fp field equations.
Every factor partition is enumerated and saved. The parent polynomial, chosen
coefficient map, exact target product, companion certificates, and all nonzero
field-image domain certificates are explicit.

| Case | Input degrees | Child accuracies | Parent accuracy | Exact optimum T |
| --- | --- | --- | ---: | ---: |
| 0 | 1,1,1 | 1,1,1 | 2 | 3 |
| 1 | 4,3,3 | 1,1,1 | 2 | 5 |
| 2 | 1,2 | 2,2 | 2 | 3 |
| 3 | 1,3,4 | 1,1,1 | 3 | 1 |
| 4 | 1,1,1 | 2,2,2 | 2 | 5 |
| 5 | 1,1,1,1,1 | 1,1,1,1,1 | 2 | 5 |

The independently enumerated anchor/makespan formula agrees with every full
partition optimum. The ordinary-degree lower bound alone is strictly weaker
in cases 0,1,5. The general optimality proof reduces all polynomial realizations
to factor partitions using the stated disjoint-monomial hypothesis; the code
does not enumerate arbitrary coefficient polynomials.

Each parent companion image is a multiple of a retained child companion and
fits T times its original degree. Coefficient-field images have complete
mixed-domain NS certificates through pT. The old core system is satisfiable
at zero old inputs and zero coefficients. Separate Booleanity-only controls
make all child products one and a parent companion image nonzero; those points
are explicitly not models of all child companion axioms.

## Absorption into a retained wide core

Twenty-four cases use a core a=P_(x_1,...,x_k), k=3,7, accuracy two, and 1,5,17
residual inputs (1-a)(1-b_j), over all four primes. Inputs are the source-shaped
system after earlier conjunction packing. The pre-core-removal parent product
degree is 12; its core-coordinate and residual companion degrees are 13 and 17.

The affine map copies all core coefficient vectors and zeros residual slots,
giving parent product a. Prefix witnesses express each residual in the ideal
of the core inputs. All NS input and companion-image certificates are saved:
residual input witnesses have degree five and their companion images degree
nine. The residuals are outside the literal linear span of the core's x_i's,
as witnessed by their distinct b_j variables. No spare parent factor is used.

Models give the retained core both values zero and one while satisfying its
companions and every parent image. These are post-substitution image models;
the output does not claim that arbitrary unassigned original parent coefficients
also satisfy the original parent system. The core remains retained.

## Encoding, provenance, and timing

All polynomial terms use `[coefficient, [sorted repeated variable IDs]]`.
Domain certificates list the powers of each old variable and every NS cofactor.
Original gates deliberately kept factored are fully determined by their saved
input polynomials, accuracy, and coefficient-variable arrays; no computed result
is silently truncated. The tools save mathematical evidence, not an arbitrary
Frege-proof compiler.

`provenance.json` hashes all three tools, the unchanged shared kernels, and all
three complete outputs. The source read was the notebook's exact earlier
factor-packing theorem, whose t<=h condition was confirmed; no correction to
that theorem was needed. No new paper was downloaded or imported. The sharper
NS copy estimate and the directional unit identity are analytic derivations;
the latter's detailed source-leaf audit is explicitly deferred to the next cycle.

`timing.html` is embedded in the notebook. Initial preparation includes the
previous checkpoint, source-history audit, and authorized push. Reading was
marked for the targeted old-theorem check. Coding markers ran in separate calls
before implementation; mathematics includes the proof development and notebook
drafting. The absorption extension received a new focused checker without
rerunning completed suites. Overlapping protected jobs are counted once. No
rendering build or unrelated suite ran. Full command evidence is archived under
`research/provenance/session-records/wide_or_composition_20260911_23/`.
