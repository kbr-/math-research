# Paired-branch and restricted-limit review

Fresh-context correctness review, 28 September 2026. Reviewed the complete draft
`/tmp/bmd-paired-branch-entry.html`, the supplied branch-point symmetry record,
the generic balanced-limit statement and proofs (including the valuation and
ambient-kernel arguments), the restriction script, and its complete retained
output. This review ran no computation and spawned no agent.

Verdict: the main theorem and restricted-limit proposition pass. One small
scope clarification is required for the stated arbitrary-slope-set corollary.

## Required clarification

The paragraph beginning “Structured slope grids fail uniformly” allows an
arbitrary reflection-stable set B. Such a B need not contain zero, whereas the
theorem assumes an anchored zero branch. The preceding Scope paragraph only
explains scaling, which does not supply a zero branch.

Either impose zero in B, or explicitly include translation invariance. The
latter retains the intended generality: choose b0 in B, subtract epsilon b0
from every label, and replace B by B-b0. The reflected center becomes
1+epsilon(h-2b0), which is a nonzero element of k(epsilon), and can be scaled
to one. For a common shift by an existing branch a*, the local change is
T'=T/(1+a*T), and the root ratios w_i/w_* satisfy
(w_i/w_*)^2=1+(a_i-a*)T'. Division of degree-d homogeneous sections by w_*^d
is multiplication by a local unit. Consequently both the parameter change
and trivialization preserve the marked jet ranks. The digit grid and the
displayed equal/opposite families already contain zero, so their conclusions
are unaffected by this omission.

## Checks and attempted breaks

- The monic quadrics are a regular sequence. Independent square classes of
  the distinct nonzero linear factors give an injective chosen formal branch;
  homogenization and square reduction give precisely the stated filtered
  affine source as R_d. Its Hilbert series agrees with the weighted row count.
- The coordinate-square representation has the same plus/minus multiplicities
  as the coordinate permutation representation; its two-dimensional quotient
  has one of each. The equivariant Koszul identity therefore has exactly the
  numerator and denominator displayed. Evaluating the representation ring at
  the sign character computes integer multiplicity differences, including in
  characteristic three; it does not reconstruct them from modular traces.
  Both simplified Hilbert series and their coefficient formulas are correct.
- The all-one point is smooth: in the X0 chart the square-root equations have
  invertible derivatives in their root variables, and X1^2-1 is a parameter.
  Exchanging X0 and X1 gives the claimed involution of T. The local coordinate
  u is anti-invariant, and X0^d+X1^d is an invariant unit-valued section even
  when the characteristic divides d. Thus no hidden prime-to-d assumption is
  needed. The jet eigenspace counts give the rank bound. Parity gives the
  stated kernel bound, and imposing D^+-1 even coefficient conditions gives
  the order bound without ordinary derivatives or factorial division.
- For N=2 and the two parity cases the formula remains consistent; for degree
  two it gives chi=m and the claimed obstruction when m>=2. A fixed branch at
  1/2 is handled by the extra plus coordinate and relation. No unneeded
  substantive hypothesis was found. The condition chi>=2 on the last order
  assertion is a relevance restriction rather than a necessary condition for
  its elementary dimension argument; retaining it is harmless.
- The restriction script checks all eight saved mixed-block transformations
  after substitution, their invertibility, the full residue rank nine, and
  equality with the endpoint normal form. Together with the saved support
  identities this also preserves the seven-dimensional middle space. The
  three distinct internal slopes remain distinct over F3(b), so the two
  internal valuations nine persist. A rank-nine final mixed reduction proves
  saturation at the same divided valuation thirty-one. There is no unsupported
  inference from the final determinant alone.
- Substituting the two paths into the endpoint formula gives exactly O_+ and
  O_-. In endpoint coordinates, intersection with the ambient two-dimensional
  kernel is respectively zero and one-dimensional. This proves ranks seventeen
  and sixteen. The valuation lemma gives forty-nine for the equal-slope
  determinant; the paired-branch theorem gives an identically zero opposite
  determinant, not merely a higher-order leading coefficient.
- In characteristic three, differentiating Delta_B=b(b-1) gives -s_B, and
  differentiating Delta_C=cd(c-d) gives -d s_C and c s_C. These yield all three
  displayed gradients, including their signs. On c=rho,d=rho b, Delta_C squared
  scales by rho^6 and s_C cubed by rho^3, giving 1+rho^9=(1+rho)^9. The independent
  c derivative is nonzero on the indicated open set. The order-nine scaling
  contact therefore does not imply singularity of the hypersurface.

The distinction between the generic frame and special saturation strata is
maintained. Neither these restricted certificates nor the symmetry obstruction
establishes or refutes generic all-dimensional normality. No numerical rerun,
new source, or optional extension is needed for the reviewed claims.
