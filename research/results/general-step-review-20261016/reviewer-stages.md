# Reviewer stages for the general-step goal review of 16 October 2026

The review's single medium reviewer (Claude Code `medium-reviewer` agent) first received only the
goal, the three open statements and ten registered proved results (no conjectures are registered for
the route), then, in a second stage of the same agent, the current route and the review draft. Its
two reports are kept here as returned; claims in them are the reviewer's, and the review entry says
which were checked and adopted.

## Stage 1: blind

**Independent alternative.** Blind-stage proposals; one registry search ("collapsing modular
counting Nullstellensatz depth Frege hybrid") found no recorded collapse or hybrid result, only the
historical BIKPRS Frege-to-ENS simulation, and showed IPS work already on record.

- A. Functional IPS route (Razborov–Smolensky on the certificate): rejected. Over F2 every
  unsatisfiable CNF has polynomial-size depth-3 coefficients g_i = f_i prod_{j<i}(1 - f_j), the
  first-falsified-clause indicator, with sum g_i f_i = 1 - prod_j(1 - f_j), equal to 1 on the cube.
  The g_i carry no hardness; all of it sits in the Boolean-axiom coefficients.
- B. Collapse plus hybrid restriction: Buss–Kołodziejczyk–Zdanowski (TAMS 2015, "Collapsing modular
  counting ...") collapse AC^0[p]-Frege, with quasipolynomial loss, into bounded-depth Frege with
  low-degree F_p Nullstellensatz reasoning. Recalled, not read: an untested hypothesis. Needs a
  family requiring size 2^{n^eps} in the hybrid at every fixed depth. Uses
  cor:weighted-restriction-cube and lem:error-cube-floor (degree hardness survives pinning). Breaks
  where the surviving coordinate set depends on w and J_D, while switching lemmas need random
  restrictions; matching the exact hybrid interface is a second risk.
- C. Noncommutative lower bound (weakest algebraic endpoint): a lower bound against
  placeholder-linear F2 noncommutative IPS of depth d+10 and tree size S^12 with Boolean and
  commutator axioms (thm:shallow-noncommutative-sequent-simulation). Breaks where the commutator
  placeholders' coefficients can absorb rank; a coset-robust rank measure is needed.

Strongest necessary endpoint, ranked by how weak a statement would suffice: (1)
thm:shallow-noncommutative-sequent-simulation; (2) the commutative Hilbert-like IPS lower bound of
imp:depth-preserving-IPS-simulation. Both are sufficient, not necessary. The degree-side results are
tools inside a replay route; cor:proof-observation-rank ends in a rank equality; the thin-tail,
character and shadow-ratio results are obstructions or local criteria.

Suggestion (unverified): read the collapse theorem first; if its hybrid lets the NS degree side be
checked after the Frege restriction is chosen, the question is whether the pins of
cor:weighted-restriction-cube can be random.

## Stage 2: revealed

Verdict: pass with corrections.

1. The corollary (sparse weights keep the thin tail) is correct: kernel direction, closure under
   variable multiplication, h_E(K-t) <= h(K-t) by absorption, h_E(K) >= h(K)/s > 0, the growth step
   for K <= D, the sum of (1+1/t)^i at most e t; t >= c b log m with an absolute c. Trivia: b + K <=
   D is redundant as b <= e; the log bound needs b >= 1; keep 2t <= K <= D - e beside the "every
   tuple" phrase.
2. Parts (1)-(2) of prop:character-error-thin-tail are the s = 1 case of lem:sparse-weight-survival
   composed with the growth step; "sharpens s = 2" is correct (t >= 10 at h/2, t >= 9 at 2h/3). The
   conditional-use paragraph was not in the excerpt and could not be checked.
3. The posing of the short-range test is correct, and the sparse bound also holds for whole tuples.

Required changes: the sentence that every nonzero residual error family contains a free cube of
standard monomials, so caps need X >= D-a-d-1, says more than the registered lem:error-cube-floor,
which states a cumulative floor only; the Prediction's "near-half is intrinsic" uses the wrong
direction (an ambient-like ratio shows only that ratio-based repair needs near-half); Downstream
must state that L must fit b + K + 2L <= D; Independent alternative should record the break points
and the endpoint ranking.

Answer on the Attempt (sketch, not checked): over F4 take independent low-support characters chi_j =
m_{beta_j} and binary q_j = chi_j + chi_j^2. Then 1 - q_j = 1 + chi_j + chi_j^2 and P = prod_j(1 +
chi_j + chi_j^2) = sum over the span H of the beta_j of m_eta, so s = 3^t. For a class
representative alpha, P m_alpha is the sum over the H-orbit of alpha; with a + K <= D every term
stays in the window. If the 3^t translates stay in distinct cut-code classes, c(k) is the coset
count of the enlarged code C + H; for single-edge beta_j this is the code punctured at t <= D
coordinates, of dimension R - t, with h'(K-d)/h'(K) of the same order as canonical. Density alone
gives no better ratio.

The revealed route does not change the blind-stage view: caps are dead at wide ranges, and natural
dense errors point to ambient-like short-range ratios, supporting a redirection soon.

Suggestion (unverified): prove c = h_{C+H} for subgroup-averaging P under a non-collision condition,
then compare h' with h by puncturing; a lemma-first next entry.

Process audit: title and status were placeholders; the queue grew while draining and the Decision
did not say how that is reversed; the builds' reason for waiting never expires; three counts cited
no tool output; the ambient claim through lem:cut-ball-occupancy rests on a statement not in the
excerpts. The Decision otherwise follows from the evidence.
