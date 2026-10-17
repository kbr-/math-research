BLIND STAGE

# Blind stage of a route review: the goal and what is proved

The goal: Talagrand's Ultimate Matching Conjecture (conj:ultimate-matching in statements.txt). Two
point sets X and Y of N i.i.d. uniform points in [0,1]^2. For exponents alpha_1, alpha_2 in [2,
infinity] with 1/alpha_1 + 1/alpha_2 = 1/2, with probability tending to one there is a permutation
pi such that, for j = 1, 2, sum_i exp[((sqrt N/(L sqrt(log N))) |X_i^j - Y_pi(i)^j|)^alpha_j] <= 2N,
with L universal. A sufficient form replaces Y by an evenly spread set.

/home/kbr/.claude/jobs/c0de408b/tmp/rp/blind11/statements.txt holds the registered statements and
assessments of the record's main results:
- the reduction of the goal to a discrepancy bound (cor:exponential-matching-discrepancy-reduction,
  lem:hopf-lax-matching-bound) and the open bound itself, conj:conjugate-class-discrepancy;
- the primal flow bound (lem:flow-matching-bound, lem:grid-flow-duality) and the dyadic flow's
  success at (2,2) and failure above;
- the exclusions: below the curve, linear flow rules, rank-cut transports, position-blind exits,
  flows with conditional pushes (pointwise or on coarse means);
- level counts and chain bounds on the dual side;
- a refutation, lem:per-level-gluing-fails.

The two open conjectures are conj:ultimate-matching and conj:conjugate-class-discrepancy. Their
evidence is in statements.txt: the reduction makes the second sufficient; its order is forced at
interior pairs (lem:leighton-shor-class-lower-bound); it is false below the curve.

Questions. Answer each in your own terms, from statements.txt.
1. What architecture for proving (or refuting) the goal at a pair such as (4,4) do these results
   suggest, and what would its first lemma be?
2. Which proved results constrain a proof most, and how?
3. Is there an approach materially different from the ones these results already work with (primal
   flows, dual discrepancy over a function class, level counts)? If you find one, give its first
   step and where it could break. If you find none, say what you looked at.
4. Which of the open conjecture's instances would you test first, and with what?

Read only the files in this folder. Run no computations. Do not edit any file. At most two claim
searches with tools/search-claims.py; name what you searched. Report: your answers, then any proved
statement here you think is wrong or misread, marked as such.
