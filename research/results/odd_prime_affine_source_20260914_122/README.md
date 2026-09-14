# All-prime affine exclusion and actual MOD source inputs

The [full notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-odd-prime-affine-source)
extends old matching stability and signed bit separation to every field, then
proves the one-level affine-bit exclusion over each fixed prime. The compact
collision encoding is explicitly changed to its correct prime-field version.

An actual complete system with inputs L_i^(p-1) transfers to affine inputs at
degree 2D, including arbitrary use of its coefficients. The local source profiles
fit the original product weight. A complementary MOD3 family has a large common
zero set despite high affine rank, but also has its own degree-preserving raw
transfer. General complementary inputs and the full Frege source remain open.

## Reproduce

From the repository root with active resource controls:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_cube_dual_design.cpp \
  -o /tmp/math-cube-dual-design-prime
./compute.sh run TURN --threads 1 -- \
  /tmp/math-cube-dual-design-prime --out NEW_MOMENT_PATH --prime 3

./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_odd_prime_affine.cpp \
  -o /tmp/math-odd-prime-affine
./compute.sh run TURN --threads 1 -- \
  /tmp/math-odd-prime-affine --out NEW_INITIAL_NS_PATH
./compute.sh run TURN --threads 1 -- \
  /tmp/math-odd-prime-affine --out NEW_COMPLETE_NS_PATH --raw-transfer
~~~

Outputs must be new. No dependencies are installed. Both programs use exact
compiled field/integer arithmetic and retain their complete output.

## Evidence

- cube-dual-F3.jsonl: two complete sparse signed-moment fixtures, including k>ell,
  all potentially nonzero row marginals, selected bit-axis evaluations, omitted
  top-moment controls, and failures when signs are replaced by all ones.
  The first nonzero coefficient of each edge is -1, the second +1. The residual
  pair path has values +1,-1,+1. Every unlisted moment is zero.
  Marginal extension IDs refer to stored moment values, not unit coefficients.
  All nonzero moments contribute every face, and all nonzero lower moments
  contribute every missing-row right side; unlisted marginal rows are zero.
- NS-profiles.jsonl: the accepted initial six cases with 51 complete certificates.
- NS-profiles-with-raw-transfer.jsonl: the strengthened six cases with 72 complete
  certificates, including every companion and coefficient-field image of the
  complete raw source maps. The initial invocation remains reproducible.

Polynomial format is [coefficient,[variable IDs with repetitions]], so powers
are ordinary powers. Each case states its prime, full typed-domain and companion
axioms, and original source weights. Each NS certificate gives its target,
cofactors, actual witness degree, and declared ceiling. A certificate's equality
and degree are checked over the stated field before it is written.

The model controls retain every assignment and every axiom value. A model with
non-Boolean ENS product satisfies the typed domains but fails companions, as
intended; a separate valid core model falsifies the naive complement transfer.
The full positive-MOD rank example has 33 common zeroes in 64 Boolean assignments.

The local maps and profiles are tested over F3 and F5. The signed matching run
uses F3. These tests do not instantiate the asymptotic dimension/rank threshold
or numerically prove a PHP size lower bound.

## Source scope

The primary BLVZ Theorem 1.1 was rechecked at the authors' public copy. Its
connectivity conclusion is field independent; the oriented moment argument
and proof-complexity consequences here are our working derivations. No new
copy of the paper is published in this checkpoint.

The historical factor-packing lemma and the notebook's earlier signed source
convention were read in targeted local excerpts. Negative MOD children produce
power inputs; positive MOD children produce their complements. No assertion
about the usual odd-prime equation-clause calculus is imported or inferred.

Source hashes, complete command evidence, and measured timing accompany the
checkpoint. Final builds and all mathematical checks passed; preliminary
compiler indentation warnings were corrected.
