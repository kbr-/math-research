BLIND STAGE

# Blind stage of a route review: the goal and what is proved

The goal: Talagrand's Ultimate Matching Conjecture (conj:ultimate-matching in statements.txt). Two
point sets X and Y of N i.i.d. uniform points in [0,1]^2. For exponents alpha_1, alpha_2 in [2,
infinity] with 1/alpha_1 + 1/alpha_2 = 1/2, with probability tending to one there is a permutation
pi such that, for j = 1, 2, sum_i exp[((sqrt N/(L sqrt(log N))) |X_i^j - Y_pi(i)^j|)^alpha_j] <= 2N,
with L universal. A sufficient form replaces Y by an evenly spread set.

/home/kbr/.claude/jobs/c0de408b/tmp/rp/blind12/statements.txt holds the registered statements and
assessments of 30 of the record's results:
- reductions of the goal: to a discrepancy bound over a Lipschitz class
  (cor:exponential-matching-discrepancy-reduction, conj:conjugate-class-discrepancy), to a flow or a
  discrete class on cells of the Leighton-Shor side (thm:cell-scale-reduction, lem:grid-flow-duality,
  cor:coarse-discrete-sufficiency), to one-height chains (thm:one-height-chain-reduction), and to a
  gluing condition on box graphs (prop:universal-completion-sufficiency, thm:local-completion-dichotomy);
- bounds on parts of the discrete class (lem:cost-weighted-slope-bound, lem:multilevel-chain-bound,
  lem:separated-bundle-chains, lem:staircase-bundle-chains, lem:band-family-discrepancy);
- exclusions of flow designs and of the gluing condition at small constants, and per-level results.

The open conjectures are conj:ultimate-matching and conj:conjugate-class-discrepancy; the reductions
in cor:coarse-discrete-sufficiency and prop:universal-completion-sufficiency are conditional, their
hypotheses not known to hold.

Questions. Answer each in your own terms, from statements.txt.
1. Which of the sufficient statements here would you try to prove, and what would its first lemma
   be? Say what makes it more or less tractable than the others.
2. Which proved results constrain a proof most, and how?
3. Is there an approach materially different from the ones these results work with (flows, a dual
   discrepancy over a function class or chains, gluing per-level matchings)? If you find one, give
   its first step and where it could break. If you find none, say what you looked at.
4. What test would you run first, on which instance, and what outcome would change your answer
   to question 1?

Read only the files in this folder. Run no computations. Do not edit any file. At most two claim
searches with tools/search-claims.py; name what you searched. Report: your answers, then any proved
statement here you think is wrong or misread, marked as such.
