# Source-scope concern: negative association of uniform-bijection indicators

Baseline: dc1d95b4cb6a463436256b830afd69029c1dc3ed.
Claim: `lem:dense-labels-satisfied` (position 737).
Exact source: notebook anchor `dense-labels-satisfied`.
The complete short passage is preserved verbatim in `dense-labels-source.html`.

The proof states that the indicators of a uniform bijection are negatively
associated, and applies this to increasing events depending on disjoint columns.
It cites Joag-Dev and Proschan (1983), permutation distributions. No external
source was read afresh during this metadata review.

## Elementary control of the asserted general premise

Take a uniform bijection from rows {1,2} to columns {1,2}; its two equiprobable
outcomes are the identity and the transposition. Let X_ij be the indicator that
row i is matched to column j. Then

- P(X_11 = 1) = P(X_22 = 1) = 1/2;
- P(X_11 = 1 and X_22 = 1) = 1/2 > (1/2)(1/2) = 1/4;
- P(X_11 = 0 and X_22 = 0) = 1/2 > 1/4 as well.

X_11 and X_22 are increasing functions of disjoint indicator coordinates and
also of distinct columns. Thus the entire array of uniform-bijection indicators
is not negatively associated in the asserted sense. The same control at size q
has joint diagonal probability 1/(q(q-1)) > 1/q^2.

In the displayed proof the events A_x say that the occupant of column x belongs
to its designated pinned-row subset. Singleton subsets at distinct rows realize
this counterexample to the blanket probability-product step. The lemma's final
statement additionally assumes many sufficiently dense labels, so the 2x2
control does NOT by itself refute that quantitative conclusion. An alternative
permutation-avoidance bound might repair the proof. The scope of the cited
negative-association theorem and the precise density application require audit.

Keep the relationship review pending. Do not mark the theorem false or silently
rewrite its proof. Its downstream uses must be assessed by exact reliance, not
by treating all switching results as invalid. Positions 736 and 740 explicitly
use this imported mechanism or the dense-label lemma and are also flagged.
