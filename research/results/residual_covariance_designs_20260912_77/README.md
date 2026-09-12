# Residual covariance and higher-degree marginals

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-residual-covariance-and-marginals)
contains the complete moment law, probability proof, measure comparison, and
boundary-filling criterion.

For uniform degree-two functional-PHP designs, conditional pair-moment matrices
are independent uniform off-diagonal matrices with prescribed margins. Four-cycle
variations yield an exponential-in-N covariance kernel-weight bound. A
regularity/counting argument also handles the uniform set of distinct lifted
maps. Thus the degree-two uniform law fails the sufficient ENS probability rate.
The higher-degree conclusion requires its actual quadratic marginal.

The matching-moment equations identify a sufficient extension condition:
vanishing of reduced H_(k-2) of the k-by-N chessboard complex for 3<=k<=R.
The relevant source-range connectivity input was not verified in this cycle.

## Exact finite spaces

The accepted complete output, moment-spaces.jsonl, is 846,224 bytes.
It records all monomial masks, original row-moment equations via their indices,
Gaussian elimination traces, reduced basis equations, and complete sample vectors.
The system contains NS constraints only; there is no PC closure iteration.

| Holes N | Degree | Moments | NS equation rank | Design dimension | Quadratic image |
| -: | -: | -: | -: | -: | -: |
| 4 | 2 | 141 | 75 | 65 | 65 |
| 4 | 3 | 381 | 325 | 55 | 45 |
| 6 | 2 | 673 | 238 | 434 | 434 |
| 6 | 3 | 4,873 | 2,793 | 2,079 | 434 |

Normalization fixes the free constant moment to one, accounting for the extra
one in the design-dimension formula. Highest-pivot elimination identifies every
relation on the lower-degree coordinates; equal dimensions certify surjectivity
at N=6. At N=4, cubic extendibility imposes twenty additional quadratic relations.

Each space also has 32 saved samples. Their ranks are:

- N=4, degree 2: six rank-12, twenty-six rank-14.
- N=4, degree 3: eight rank-12, twenty-four rank-14.
- N=6, degree 2: six rank-32, twenty-six rank-34.
- N=6, degree 3: five rank-32, twenty-seven rank-34.

Their exact empirical kernel weights are in the output. These are finite sampled
values, not the exact expectations over the full design spaces. The universal
degree-two probability bound is proved analytically.

## Reproduction and encoding

~~~bash
./compute.sh --threads 1 --category local_processing \
  g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  research/tools/check_functional_design_marginals.cpp \
  -o /tmp/math-functional-design-marginals
./compute.sh --threads 1 /tmp/math-functional-design-marginals \
  --out research/results/functional-design-marginals-recheck.jsonl
~~~

Use a new output path. The checker uses the existing binary_php.hpp exact F2
linear algebra. A matching monomial has hexadecimal cell mask with bit i*N+j,
zero-based; monomials are ordered by degree and the producer's nested cell loops.
Reduced rows list moment indices. Each elimination trace gives the previously
installed pivot rows XORed with the indicated original row multiple.
Moment samples use little-endian 64-bit hexadecimal words in this monomial order.

The fixed case order is (4,2), (4,3), (6,2), (6,3). A single std::mt19937_64
stream, seed 20260912, chooses free coordinates by its low bit; pivot coordinates
are solved exactly and the constant coordinate is fixed to one. All original
relations and sample moments were checked, along with covariance symmetry,
zero diagonal, row-sum kernel vectors, and even rank. The strict-warning build
and single computation passed under the shared limits with one thread.

## Provenance and timing

The earlier affine-Booleanity-rigidity construction was read and reused.
The covariance probe and ENS probability budget are in the preceding entry.
The manifest fingerprints the helper, new checker, full output, and dependencies.

Initial preparation includes the preceding checkpoint. The mathematical phase
also includes the initial moment-space/check design before the coding marker;
that mixing is not retrospectively split. Coding, compilation, execution, and
mathematical interpretation are then marked separately. No new dependency or
framework rule was introduced, and historical numerical suites were not rerun.
