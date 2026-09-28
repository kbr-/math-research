# Consolidated mathematical review — 28 September 2026

Fresh-context reviewer, medium reasoning. Reviewed the ramification-review draft,
the complete first-step duality and invariant-prefix dependency excerpts, and the
previous residual-filtration route review. No numerical computation was needed.
This review is part of the coordinator's instrumented cycle; no separate elapsed
time is added to that interval.

Verdict: the three new mathematical arguments pass, subject to the explicit
statement/format corrections below. The uniform cube vanishing remains open.

Required corrections identified in the reviewed draft:

- State characteristic zero explicitly in the all-h proposition. Its linked
  original family has that hypothesis, but discarding all derivative factorials
  does require it for the stated unbounded range of h.
- Index the normalization parameters as weights 1 and 2, together with weights
  j for 2 <= j <= N-4. At N=5 the entire additional list is empty: there are two
  parameters, not three. The displayed normalization end formula is correct.
- Add the required Obstacle heading and Answers clauses for all three Outside
  leads and both Absurd bridges. Their mathematical tests already have outcomes.

Checks of the new arguments:

1. There are N-1 weighted polynomial variables. Local duality at cohomological
   degree N-3 therefore uses Ext degree two. With generator shifts S(-d),
   Ext(C,S(-W)) = Ext(C,S)(-W), so its initial degree is e+W=-a.
   Since p-W=3-N, the exact prior formula becomes
   alpha=min(lambda,lambda+3-N-a). Equality with lambda is precisely a<=3-N.
   The normalization's Ext initial degree -(4N-5) gives end 4N-5-W;
   its Ext injection gives a lower bound on a, correctly not the desired upper
   bound. The normalization shift by -4 is included.

2. A nontrivial rank-one sign character branched at s even points contributes
   s-2 dimensions to H1 of its middle extension: these are the anti-invariants
   of the double cover. End(V) has only trivial or two-point characters.
   End(exterior-square V) has four-point characters precisely for disjoint
   ordered pairs. There are six such ordered decompositions per four-element
   subset, each contributing two. Thus 12 binom(N,4) is correct. The infinity
   signs cancel in both relevant character products. The Wronskian rows have
   the stated pair characters. The text correctly restricts this to complex
   local systems and does not infer a polynomial-lattice or deformation theorem.
   Substituting the j-th scalar-operator term leaves
   (-1)^j P^(j)(t)(t-b_i)^j/j! after the common factor; their sum is P(b_i).

3. Modulo f, cancellation gives (zx^(h-1)):(z^2 x^(h-2))=(x), hence
   the original colon is (x,y), of initial degree two. For g=zx^(h-2),
   the kernel of T/g(x,z) -> T/(g) is k shifted by -(2h-1).
   Its first two Ext groups over the three-variable regular ring vanish.
   Thus Ext2 is that of the complete intersection of weights 2h and 2h-1,
   with initial degree -(4h-1). The full cyclic saturation is (f,z), whose
   complete-intersection weights are 2h and 3. Local duality with W=2h+5
   gives ends 2h-6 and -2 respectively. This is a genuine all-h control,
   not an assertion about extra components of the cube.

4. The Hilbert–Burch diagnostic has length h-1 and Jacobian rank one at the
   stated prime. The mechanical rank-nullity counterexample has colon
   (x^a,y^a), so fixed generic nullities indeed do not control initial degree.
   A rank-(s-1) symmetric Laplacian has adjugate tau times 11^t; constant
   invertible changes cannot make that vector simultaneously primitive and
   have a nonconstant coordinate. The rejection is correctly limited to
   this direct cofactor model, leaving parameter-dependent models unproved.

The prior passed lead and bridge follow-ups are retained and do not silently
claim closure. The new next step targets the actual all-N graded vanishing,
permits bounded extra components, and distinguishes generic reducedness as a
stronger sufficient mechanism. It forbids another dimension catalogue and
does not replace the polynomial lattice by its complex local system.

Unused hypotheses: none requiring removal. Characteristic zero is stronger
than needed for an individual finite h, but is justified by the stated all-h
derivative family and by the characteristic-zero cube application. Complex
coefficients and distinct punctures are used by the topological argument.

## Resolution by the producing agent

All three requested corrections are incorporated: the family explicitly assumes
characteristic zero; the normalization weights are 1,2 plus j for 2<=j<=N-4,
with that entire additional list empty at N=5; the review has its explicit
Obstacle paragraph and Answers clauses in all five lead/bridge items.
