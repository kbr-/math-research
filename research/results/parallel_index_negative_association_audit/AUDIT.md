# Audit: uniform-bijection negative association

Status: **the imported permutation-matrix premise and the generic matched-pair
exponential bound are refuted; the dense-label lemma's displayed proof has a gap,
but this audit does not refute its final parameter-dependent conclusion.**

## Exact source and affected step

The owner is `lem:dense-labels-satisfied`, notebook anchor
[dense-labels-satisfied](https://kbr.is-a.dev/math-research/#dense-labels-satisfied).
The preceding [setup](https://kbr.is-a.dev/math-research/#unary-reader-setup)
allows an arbitrary set of unary row/label pairs. Given `(Q,R')`, write
`m=n-N`. For each outside label `x`, let `S_x` be its allowed matched rows and
`A_x={mu^{-1}(x) in S_x}`. The marginal `P(A_x)=|S_x|/m` is correct.

The proof then claims that the full set of permutation-matrix entries is
negatively associated and that events on disjoint columns inherit that property.
Its exact unsupported step is

    P(intersection_x A_x^c) <= product_x (1-P(A_x)).

The final elementary inequality `product(1-p_x)<=exp(-sum p_x)` and the dense-label
counting/degree estimates do not repair this first inequality.

The attribution is Joag-Dev and Proschan, *Negative association of random
variables, with applications*, Annals of Statistics 11 (1983),
[DOI 10.1214/aos/1176346079](https://doi.org/10.1214/aos/1176346079).
A primary-publisher search result confirms that bibliographic reference, but the
DOI page could not be opened in this audit. No full-paper theorem was verified or
copied. The refutation below is self-contained and does not accuse the cited
paper of making the false matrix assertion. A result about a random permutation
as a numeric vector, or membership indicators of a uniform subset, would not
imply the assertion used here: arbitrary label-set membership is not a common
coordinatewise monotone transform of numeric permutation coordinates.

## Self-contained counterexample

Choose a uniform bijection of two rows onto two labels. There are two equally
likely outcomes, the identity and the swap. Let

    X_11 = 1[mu(1)=1],  X_22 = 1[mu(2)=2].

These are distinct matrix coordinates, in distinct rows and distinct columns.
Both equal one for the identity and both equal zero for the swap. Consequently

    P(X_11=1)=P(X_22=1)=1/2,
    P(X_11=X_22=1)=1/2 > 1/4,
    P(X_11=X_22=0)=1/2 > 1/4.

Their covariance is `1/4>0`. Negative association already fails for the two
increasing coordinate functions. The decreasing-event product bound actually
used in the notebook also fails, independently of any closure theorem.

More generally, for distinct labels x,y and arbitrary allowed row sets S,T in an
m-row uniform bijection,

    P(A_x and A_y) = (|S||T|-|S intersect T|)/(m(m-1)),
    Cov(1_A_x,1_A_y) =
        (|S||T|-m|S intersect T|)/(m^2(m-1)).

There are `|S||T|-|S intersect T|` permissible distinct ordered occupants, each
with probability `1/(m(m-1))`. Disjoint nonempty S,T therefore give positive
covariance, however large those sets are. For example, m=4 and disjoint sets of
size two give joint probability `1/3>1/4`, and the same strict inequality holds
for the complements. Thus the issue is not restricted to singleton events.
The corresponding formula for events on distinct rows follows by transposition.

## Does the unary-reader structure repair it?

No narrower negative-association hypothesis is stated or implied by the setup.
The pair set is arbitrary; allowed matched-row sets for different labels may be
disjoint. Their degrees can both exceed a prescribed density threshold when
there are sufficiently many matched rows. Additional dense labels cannot turn
a positively correlated pair into a negatively associated family, since negative
association applies to every disjoint pair of coordinate subsets.

This specifically rules out the justification by disjoint columns/rows. It does
**not** establish a counterexample to the final dense-label inequality under
all of `|D|>=Delta_0`, `D*>=2(N+1)`, and the specified value of D*. A different
avoidance inequality, using the available degree slack, might prove that final
conclusion. Such a replacement has not been established in this bounded audit.

## An earlier stated lemma is itself false

The [pinned-class reduction](https://kbr.is-a.dev/math-research/#pinned-class-reduction)
claims for every matched pair set P that

    P(no pair of P is realized) <= exp(-|P|/(n-N)).

Set `m=n-N=2` and P equal to the two diagonal pairs above. The avoidance
probability is `1/2`, while the proposed bound is `exp(-1)<1/2`, since `e>2`.
This refutes the stated generic lemma, not just its proof. It is a legal
conditional random-flat fixture: choose `n=4`, `N=2`, any two-point affine flat
Q of `F_2^2`, any residual set R' of three of the five rows, and these two pairs
between the two remaining rows and two outside labels. Nothing in that lemma
requires the dense-label thresholds. The counterexample should not be presented
as violating the later dense-label theorem's stronger assumptions.

The same false generic avoidance estimate is invoked explicitly in
[alive-unmatched-comparison](https://kbr.is-a.dev/math-research/#alive-unmatched-comparison).
The separate first/second-moment estimates in that proof are not refuted by this
counterexample; the use of negative association for its exponential estimate is.

## Direct-use scope only

`direct-use-inventory.json` preserves all 37 notebook paragraphs containing the
searched terms, with exact HTML, line, owning article and nearest heading.
Narrative and verification paragraphs are not independent theorem failures;
nearest-heading association for an article preamble may point to the preceding
heading, so use the stored article field and exact text for those cases.

The following actual proof passages explicitly use permutation/bijection
row/column negative association, and their indicated steps require review:

| Anchor | Direct use |
| --- | --- |
| `pinned-class-reduction` | Generic matched-pair exponential avoidance; refuted above. |
| `dense-labels-satisfied` | Product of arbitrary allowed-occupant column failures. |
| `alive-unmatched-comparison` | Exponential avoidance from distinct matrix-entry zero events. |
| `single-row-full-theorem` | Case A satisfaction product over distinct tail rows. |
| `bounded-loading-theorem` | (ii), product/tail estimate over differently loaded rows. |
| `out-loading-lemma` | Product bound over row-specific outside-label sets. |
| `srf-theorem` | General bijection premise and (E5) row-count tail. |
| `matching-lemma` | Failure product for disjoint row-plus-pinned-column coordinate sets. |
| `bipartite-theorem` | General conditional-bijection premise and (F5) row-count tail. |
| `two-tier-lemma` | Failure product for matched row/label classes. |
| `two-tier-theorem` | General conditional-bijection premise used by the event audit. |
| `activated-sparse-lemma` | Comparison of correlated row activations with independent assignments. |
| `two-stage-reduction` | Product over row-specific residual/matched events. |
| `row-spread-theorem` | Column-count Chernoff claim and later row-satisfaction product. |
| `pattern-bounded-theorem` | (H4), product over row-specific matching events. |
| `multirow-mass-theorem` | (H4c), final product over disjoint row sets. |
| `few-rows-theorem` | (K1), product over column-specific allowed occupants. |
| `two-role-many-theorem` | (H4c), product over disjoint row sets. |
| `wide-mass-theorem` | (D1), row-specific cube-satisfaction failure product. |

This is a scope flag, not a proof that all listed final conclusions are false.
Some looser constants or additional hypotheses may admit other arguments. No
such repair is silently presumed. Downstream claims merely referencing these
results need a separate dependency-impact audit by the coordinator.

Do not conflate the invalid full permutation-matrix premise with negative
association for membership indicators of a *single uniformly chosen subset*.
For example, the uniform remaining-label subset concentration within
`multirow-mass-theorem` (H4c), and the exposed-label subset concentration in
`crowded-theorem`, have that different premise. This audit does not invalidate
those steps. In the same multirow paragraph the later product over different
bijection rows is the unsupported step. Other weighted/repeated-row subset
arguments have not been independently audited here.

## Recommended disposition

Register the elementary counterexample and correct the generic pinned-pair
avoidance lemma in a new dated notebook entry. Mark the dense-label proof and
directly identified uses as requiring a replacement probability argument;
retain exact statements and historical proofs unchanged. Do not claim a
refutation of their stronger final bounds without satisfying their full
hypotheses. This audit neither changes the main Frege goal nor develops an
alternative research route.
