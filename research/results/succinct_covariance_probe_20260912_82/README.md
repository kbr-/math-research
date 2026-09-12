# A compact finite-field generator for the covariance attack

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-succinct-covariance-obstruction)
contains the complete generator, bias proof, circuit construction, error
accounting, and comparison with the actual source budget.

Let E/Fp have degree k and size Q. Choose independent uniform a_i in E and
a uniform Fp-linear functional tau:E->Fp. For every squarefree monomial X^A
of degree at most t, set its coefficient to tau(product_{i in A} a_i).
Every nonzero linear test of the coefficient vector has character average
between zero and t/Q. The proof is finite-field orthogonality followed by
the polynomial root bound, proved explicitly in the notebook.

The polynomial is computed by the first t homogeneous components of
product_i(1+a_i*X_i), followed by coefficient-wise tau. In a field basis,
each multiplication by a fixed a_i is a k-by-k scalar matrix. A prime-field
circuit of size O(v*t*k^2) and ordinary degree at most t therefore suffices.
The full product is not substituted for its truncation, and tau is applied
to coefficients; no Frobenius powers of the original variables are introduced.

Replacing both random polynomials in the covariance probe by this distribution
gives the universal attack with a controlled error. For q=h+ceil(log2 S)-1,
take t=h (or ceil(h/2) over F2), epsilon=p^(-2h)/(2*(q+1)), and
k=2h+ceil(log_p(2*t*(q+1))). The non-conflict probability is at most

    2*p^(-h) - p^(-2h)/2 < S*(1-1/p)^h

for S>=2, with D>=2h, or D>=h+1 in the binary case. Each query/leaf circuit
has size O(v*t*k^2). For PHP and logarithmic h and log S, this is
O(n^2*log^3 n), within the preceding coarse source circuit budget.
The degree, height, and probability conditions match the earlier obstruction.

This closes the circuit-size-only sufficient criterion with that budget.
It does not give a constant-depth implementation, exclude every finer
source-syntax restriction, construct a Frege proof, or prove the target
lower bound. No design distribution is asserted to meet a surviving criterion.

## Exact finite checks

trace-generator-checks.jsonl preserves every output-polynomial frequency,
every dual-character sum, and the fixed-trace-multiplier control distribution.

| Variables | Degree | Extension field | Seeds | Nonzero tests | Maximum character bias |
| ---: | ---: | --- | ---: | ---: | --- |
| 2 | 1 | GF(4) | 64 | 7 | 16/64 = 1/4 |
| 3 | 2 | GF(8) | 4096 | 127 | 960/4096 = 15/64 |
| 3 | 3 | GF(8) | 4096 | 255 | 1352/4096 = 169/512 |
| 4 | 2 | GF(4) | 1024 | 2047 | 448/1024 = 7/16 |

All 2436 nonzero linear tests have nonnegative character sum and bias at most
t/Q. All 82176 evaluations of the truncated-product recurrence agree with
the independently formed coefficient polynomial, for every sampled seed and
every Boolean input. These are exhaustive fixtures, not random samples.
The fixed z=1 control has a constant-coefficient test of absolute bias one
in each case, exceeding the promised bound.

The finite code samples tau(w)=Tr(z*w); its trace pairing is checked directly
in GF(4) and GF(8), so uniform z gives the uniform dual functional used in the
proof. GF(4) uses x^2+x+1, represented by modulus bits 7; GF(8) uses x^3+x+1,
represented by 11. Field multiplication, units, trace linearity, and trace
pairing nondegeneracy are checked exactly.

feature_masks lists the squarefree monomials, ordered by degree then mask.
In each output row, index is a polynomial coefficient bit vector for the
histogram fields and a dual linear-test bit vector for the Fourier fields.
Character sums are signed integer sums, not floating-point estimates.
All source fixtures and outputs are complete; no PHP moment suite was rerun.

## Reproduction and provenance

Use a fresh timing session and output path for replay:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_trace_polynomial_generator.cpp \
  -o /tmp/check_trace_polynomial_generator
./compute.sh run TURN --threads 1 -- \
  /tmp/check_trace_polynomial_generator --out NEW_OUTPUT.jsonl
~~~

Compilation and execution succeeded within the shared resource limits.
No dependencies were installed. The probability theorem and circuit-size
bound are analytic; the finite checks target the generator and degree-safe
recurrence, not a sampled PHP attack.

The finite-field evaluation/random-linear-functional method is classical;
the authors' June 14, 1992 AGHP paper was read at its third construction in
the introduction. The multivariate low-degree coefficient version and its
application are proved fully here. sources.json records the primary links
and exact reading scope; no new third-party full text is committed.
provenance.json pins the code, full output, and preceding proof dependencies.

## Timing and process

Initial preparation includes the preceding checkpoint and publication.
Proof work, source lookup, and implementation were phase-marked. Some initial
planning of the finite fixtures occurred during mathematics before coding
began; no retrospective split was invented.

A first sum-of-products sampler had an exponential-in-t cost. The extension
field construction removes that loss without expanding the polynomial.
Testing the actual circuit-restricted class closed this refinement; no
additional framework rule was needed.
