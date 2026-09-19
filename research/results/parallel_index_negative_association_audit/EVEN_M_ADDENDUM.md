# Addendum: the generic avoidance bound fails at arbitrarily large sizes

Status: exact analytic refutation of the generic bound in
[pinned-class-reduction](https://kbr.is-a.dev/math-research/#pinned-class-reduction),
compatible with the recorded random-flat parameters. This strengthens the
small fixture in `AUDIT.md`; it does not change its dense-label verdict.

Let `m` be any positive even integer. Fix a reference bijection between `m`
matched rows and `m` outside labels, and let P be precisely its `m` pairs.
Relabel so that P is the diagonal. A uniformly chosen bijection avoids every
pair of P exactly when its permutation has no fixed point. Inclusion–exclusion
therefore gives

    P(no pair of P is realized)
      = D_m/m!
      = sum_{k=0}^m (-1)^k binom(m,k)(m-k)! / m!
      = sum_{k=0}^m (-1)^k/k!.

For even m this is strictly greater than `exp(-1)`. Indeed, using the absolutely
convergent exponential series, their difference is

    sum_{j=0}^infinity [1/(m+1+2j)! - 1/(m+2+2j)!] > 0.

Every bracket is positive. Since `|P|/m=1`, the notebook's asserted upper bound
is exactly `exp(-1)`. Thus it fails for every positive even m, however large.
The discrepancy becomes small but remains strictly positive; the claim stated
an exact inequality, without an asymptotic error term.

## Compatibility with the actual restriction family

The [random-flat definition](https://kbr.is-a.dev/math-research/#random-flat-preservation)
has `n=2^ell` labels, an affine flat Q of size `N=2^ell_2`, `N+1` residual rows,
and a uniform bijection of the `n-N` remaining rows onto the labels outside Q.
Whenever `1<=ell_2<ell`, both n and N are even and

    m=n-N

is a positive even integer. The counterexample therefore applies for every such
parameter pair. In particular it applies along arbitrarily large n with N a
power-of-two polylogarithmic parameter, as allowed by the surrounding
[window-height discussion](https://kbr.is-a.dev/math-research/#window-height-budget).
No small-n exception is needed.

Fix one admissible Q_0 and one residual row set R'_0 before drawing the matching.
Choose P to be a reference perfect matching between their complements. This is
a fixed allowed unary reader pair set, not a choice made after seeing the random
bijection. Condition on `(Q,R')=(Q_0,R'_0)`, an event of positive probability.
The displayed derangement calculation then applies exactly. The generic lemma
is explicitly conditional on fixed Q and R' and permits every such pair set.
There are only m terms, hence a polynomial-size unary reader even if each pin is
written with its O(log n) bit literals.

## Scope remains narrow

Every label of this reader has degree at most one. The construction does not
meet the later dense-label threshold `D*>=2(N+1)` and therefore does not refute
that lemma's final high-density conclusion, the unary switching theorem, or the
main Frege objective. It refutes the unrestricted conditional matched-pair
avoidance bound and the permutation-matrix negative-association justification.
A replacement estimate with a slack constant or additional density assumptions
would require a separate proof; none is asserted here.

No enumeration or new numerical computation is needed: the finite
inclusion–exclusion identity and the positive series remainder are the complete
proof. This addendum leaves all previously delivered audit files unchanged.
