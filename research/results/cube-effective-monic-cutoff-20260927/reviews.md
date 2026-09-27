# Review record — 27 September 2026

Both native reviewers were explicitly started with medium reasoning and no inherited
conversation context. They performed read-only reviews; no computation was rerun.

## Pre-proof novelty and scope

Reviewer: controlled_chain_novelty.

The reviewer inspected the proposed statement and the exact earlier Tor/monic and
residual-source records, with two bounded claim searches. Verdict: suitable to develop;
the earlier records give qualitative monic existence and the first-syzygy reduction,
but no explicit dimension-only bound. This is a quantitative refinement, not a claim
of independent novelty. The broad search results do not establish exhaustive novelty.

Required details, incorporated in the proof:

- Use translated coordinate orthants and split only the selected orthant.
- Bound local exponent sums by global exponent sums and hence by the current control.
- Pad a split with empty children to match the exact displayed recursion.
- Verify the normalization second-syzygy shifts in the reverse Tor bound.
- Correct the previous claim that cube-specific relations are necessary: fixed graded
  free ambient data give another sufficient route. The previous abstract counterexample
  does not fix those data and remains valid.
- Do not present the recursion as a threshold classification or polynomial bound.

## Fresh correctness review

Reviewer: controlled_cutoff_correctness.

Reviewed the full draft and exact notebook excerpts for marked deflation, minimal
normalization resolutions, and the residual-source/monic identity.

Verdict: pass, with one notation correction. The optional ordinal expression must be
written in descending Cantor normal form, omega^s a_s + ... + omega a_1 + a_0.
Ascending ordinal addition can absorb lower coordinates. The independent lexicographic
termination proof was already correct. The expression was corrected before checkpoint.

The reviewer passed both claims, including translated orthants, retained supersets,
empty padding, time indexing, homogeneous Groebner remainders, first dependence versus
least monic order, exact deflation shifts, reverse Tor inequalities, normalization
maxima, and the symbolic controls. The limited correction of the prior necessity
assessment was justified. No unused substantive hypothesis or further mathematical
gap was identified. No strengthening was introduced after review.
