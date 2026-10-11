# Complementary parents defeat a universal common target

Draft for correctness review. Goal progress unchanged. This is an application
of the recorded degree-paid case-splitting proof to the common-target demand,
not a new normalization method or a lower bound.

Let Gamma be any old F2 system containing Booleanity, on distinct old bits
x,y_1,...,y_r and possibly other variables, r>=1. Fix common accuracy h>=2.
For each i retain two complete bottom blocks: inputs (1+y_i,1+x), with genuine
product P_i, and inputs (1+y_i,x), with genuine product R_i. Every block has
private coefficients, all companions and all coefficient Boolean fields.
Write Gamma_0 for Gamma plus these bottom blocks. Form two genuine terminal
parent input tuples G_+=(y_i+P_i)_i and G_-=(y_i+R_i)_i, also at accuracy h
when building their complete ENS extensions. These have literal old-affine
part y and constant mixtures of genuine shared products.

Claim: for C>=2h+1, if an old Q belongs to the degree-C ordinary NS consequence
spaces of both Gamma_0 union G_+ and Gamma_0 union G_-, then Q belongs to the
degree-(C+1) NS consequence space of Gamma. The analogous implication holds
for PC consequences. Thus a common old target separated at C+1 cannot be
supplied for these two parents, even by using the retained bottom axioms.

Proof. In every bottom block select its first affine input in row one, its
second in row two, and set all other rows to zero. These are constant coefficient
maps. They send P_i to y_i x and R_i to y_i(1+x). All bottom companions are
Boolean multiples through degree three, all fresh fields zero; hence any
degree-C proof over Gamma_0 transfers to the indicated old system without a
degree increase. This is a single coherent map for both proofs and every shared
occurrence. In detail, substituted bottom companions have Boolean certificates
no larger than their original degree 2h+1; NS cofactor degrees and PC predecessor
degrees are retained. Parent input axioms become (1+x)y_i and x y_i through
degree at most two. The map fixes Q and Gamma.

Multiply the proof from Gamma+((1+x)y_i)_i by x, and the proof from
Gamma+(x y_i)_i by 1+x. Every new weighted input is y_i(x^2+x), a Boolean
consequence through degree three, at most C+1. Old axioms and PC steps cost
at most C+1, and the two conclusions are xQ and (1+x)Q. Adding them gives Q.
For NS, multiply each complete certificate by the corresponding selector;
each summand fits C+1 and the same addition applies. This is the recorded
case-split proof with target Q instead of target one. No Boolean evaluation
of the inconsistent old base is used.

Positive control: these two parents are nevertheless cheaply normalizable.
Use the same constant bottom maps and select parent input position 1 in the
first row of each parent, zero elsewhere. Let W=y_1. Writing H=1+x or x,
the corresponding weighted parent companion is

    y_1 y_i H (1+y_1 H).

It is a Boolean zero, with ordinary degree at most five, since y_1^2=y_1 and
H^2=H. Bottom weighted companions cost at most four and fields are zero.
If y_1 survives in a proper old J_D containing Gamma, this gives one surviving
weight and complete simultaneous normalization through D>=B+1, for the
original source ceiling B>=max(width Gamma,2h^2+3h). All maps are constant;
the original product and companion costs, including zero-padded rows, are
unchanged. The weighted products are not both zero: modulo Booleanity they
are y_1 x and y_1(1+x), whose sum is y_1. This explains why the successful
normalizer does not contradict the common-target obstruction.

Nonvacuity: for every r>=1 take Gamma=BOOL, h=2, C=5. The two premise systems
both derive Q=y_1(x^2+x) already from Gamma at degree three, so the implication
has actual inputs. More informatively, the complete source normalization uses
the proper Boolean J_15, W=y_1, B=14, D=15; every number fits and W survives
at unbounded variable counts. This is an algebraic control, not a hard-family
claim. For a hard Gamma the conclusion is conditional on its stated surviving
y_1 and degree window, not on the existence of a global satisfying point.

Degenerate cases: r=0 and h<2 are excluded from this realization. Q=0 is
harmless. Old variables additional to x,y are fixed. If y_1 is in J_D the
positive-control survival premise fails; no survival is inferred merely from
nonzero syntax. Coincident parent inputs are unnecessary; all listed y_i are
distinct. The original-degree costs apply even though the constant bottom
images have degree two.

Record comparison: lem:term-value-case-split at #term-value-clamping already
proves the F2 PC selector gluing for refutations; audit:adaptive-query-fixed-
distribution-gap at #old-query-case-split-budget has the NS argument.
lem:full-base-relative-learning and lem:affine-product-learning assume a common
separated target. cor:factored-batch-removal already handles tuples H_a q_ai
when its rate/window premises hold; the positive control here directly selects
one shared y_1 instead. No new factor-removal engine is claimed. The prior
cor:graph-input-common-target remains valid, because these pivot-dependent
tuples fail its independent-offset hypothesis.

The review's decisive test has a negative answer for universal common targets,
including retained-relative targets. This leaves companion normalization open
and shows the direction must use it directly, rather than just replace Boolean
vanishing by relative ideal membership in that same universal target demand.

Reviewer assistance: what concrete operation on actual mixed parent tuples
could exploit old quotient relations without requiring one target in every
parent input ideal? Existing affine residuals, literal factored tuples and
degree-paid input pruning do not by themselves give source-wide coverage.
Please distinguish a new mechanism from those existing interfaces.
