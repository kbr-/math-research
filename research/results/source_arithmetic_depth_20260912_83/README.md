# A shallow degree-mixture generator closes the generic query route

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-shallow-query-obstruction)
contains the full source-depth refinement, generator proof, exact degree and
probability accounting, and research decision.

For a nonzero linear functional on the Boolean polynomial quotient, let d be
its least nonzero degree. Multiplication by a random homogeneous linear form
annihilates the functional with probability at most p^(-d): a nonzero
degree-d monomial gives a diagonal d-by-d minor of the contraction map.
Every surviving contraction has least degree d-1.

Consequently, the character average on a product of d random linear forms is
at most sum_{j=2}^d p^(-j) <= 1/(p*(p-1)) <= 1/2.
Choose a random degree J in 0..t; at J=0 choose a uniform scalar, and
otherwise use a product of J random homogeneous linear forms. Every nonzero
coefficient test has character average in [0,1-1/(2*(t+1))].
Summing L>=2*(t+1)*log(1/epsilon) independent draws gives epsilon bias.

The queries retain their unexpanded product formulas. Their Boolean
reductions are used only in the analysis. The resulting sampler has
degree at most t, depth three, and formula size O_p(v*t*L).
The covariance attack therefore has depth-four queries and size
O_p(v*t^2*log(1/epsilon)). At the ENS parameters this is
O(n^2*log^3 n), with non-conflict probability below S*(1-1/p)^h.
It uses only prime-field operations, with no extension field or deep circuit.

The source audit also replaces the local 4^h OR expansion by the existing
prefix identity and unrolls MP cofactor paths. This gives source cofactor
formulas of fixed arithmetic depth and size (v+T+h+1)^c, with c and depth
independent of h. That refinement still admits the shallow attack with the
supplied source budget. Generic query guarantees based on degree, height,
polynomial size, and a depth bound at least four cannot supply the required
rate in this regime.

This is a method obstruction, not a PHP lower bound or a Frege upper bound.
The generic query-distribution route is parked absent a new proof-specific
mechanism. The next task returns to the one-level affine-input ENS bridge,
which covers the original level-one source inputs over F2. Later blocks are
not renumbered after pruning; their transformed inputs need not be affine.

## Exact finite checks

degree-mixture-checks.jsonl contains every output-polynomial frequency by
selected degree and every dual test's value counts and character averages.

| p | Variables | Maximum degree | Nonzero tests | Maximum mixture bias |
| ---: | ---: | ---: | ---: | --- |
| 2 | 3 | 3 | 255 | 107/128 |
| 3 | 3 | 2 | 2186 | 19/27 |
| 3 | 3 | 3 | 6560 | 569/729 |

All 9001 tests satisfy the mixture gap and the stronger least-degree bound.
For each degree, nonzero field values occur equally often, so character
averages are computed exactly as (p*N_zero-N_total)/((p-1)*N_total).
No complex floating-point Fourier computation is used.

The fixed-positive-degree control has a constant-coefficient test of bias one,
showing why mixing degrees, including degree zero, is needed for the full
coefficient space. A separate raw-power control before Boolean reduction has
bias 3/4 over F2 and 5/9 over F3 for degree three. It violates the claimed
least-degree bound, verifying that the Boolean-quotient hypothesis matters.

All indices are zero-based. feature_masks lists squarefree monomials by degree
and then mask. Polynomial and dual-test indices are base-p coefficient vectors
in that order. Products in the finite checker reduce repeated variables by
X_i^2=X_i. The actual query formulas need no such expansion/reduction.
Per-degree distributions share the denominator p^(v*t), padding unused random
linear-form coefficients; the mixture is uniform over t+1 degree choices.
Every value count and polynomial weight is retained, including zero entries.

## Reproduction

Use a fresh session and output path:

~~~bash
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  research/tools/check_degree_mixture_generator.cpp \
  -o /tmp/check_degree_mixture_generator
./compute.sh run TURN --threads 1 -- \
  /tmp/check_degree_mixture_generator --out NEW_OUTPUT.jsonl
~~~

Compilation and execution succeeded under the shared limits.
No dependencies were installed. These are exhaustive sampler checks over
small coefficient spaces, not sampling of PHP designs or a rerun of earlier
PHP moment suites. The universal application follows from the notebook proof.
provenance.json pins the code, full output, and preceding source/proof records.

## Source and process scope

The source-depth proof uses the already audited BIKPRS local simulation,
the notebook's mp-telescoping and mp-certificates identities, and the
direct PHP boundary substitution. The prefix identity is reused, not
rediscovered as a new basic lemma.

Two targeted literature queries did not identify an exact match for the
degree-mixture sampler. This is not a novelty claim or a complete literature
survey. The elementary contraction and bias proofs are self-contained.
No new third-party paper was needed or acquired.

Initial preparation includes the preceding checkpoint and publication.
The opening reading window includes the initial source-depth reasoning.
The coding window includes the final strengthening from a tensor argument
to the diagonal contraction minor while designing the checks. These are
materially mixed marked windows; no retrospective split was invented.
One notebook patch failed its context check before changing files; the
corrected patch succeeded. This was an editing failure, not a mathematical one.

The source representation improved, but the stronger sampler still closed
its generic query criterion. Parking that route avoids another unsupported
restriction on query complexity. No new framework rule was needed.
