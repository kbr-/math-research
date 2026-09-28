# Consolidated correctness review

Verdict: **Pass.** No substantive mathematical gap or unused substantive hypothesis found.

Scope: the draft `entry-2026-09-28-cube-boundary-radical-control`, its Macaulay2
driver, and the retained run `6010173ba2`. This was a fresh-context medium-reasoning
review; no computation was rerun.

Dependencies read in full at their statement/proof anchors:

- `cube-centered-filtered-cokernel`;
- `cube-marked-ore-deflation` (the supplied complete excerpt);
- `cube-degree-two-schur-hull` and `cube-four-degree-two-free-hull`;
- `cube-degree-two-polar-decomposition`;
- `cube-first-step-rational-resolution`;
- `cube-invariant-prefix-stabilization`.

The positive-grading argument compares finite matrices in each weighted degree
over the local integers. Its inequality has the correct direction and gives the
required characteristic-zero dimension bound without a flatness assumption on
the quotient. A nonzero height-sized Jacobian minor at every minimal prime gives
generic reducedness; unmixedness then excludes embedded primary components.
Geometric reducedness over the perfect field of rationals justifies arbitrary
characteristic-zero field extension.

The driver forms the four iterates of the actual retained rank-three rational
core, with the displayed connection and marker, rather than recomputing a kernel
in finite characteristic. The retained output records denominator 12800, prime
32003, boundary codimension two and singular-ideal codimension three. The
homogeneity checks, independent boundary-polynomial comparison and nonreduced
negative control address the stated specialization and encoding concerns. The
complete singular-ideal Gröbner basis is retained. A useful expositional addition
is to state the maximal-minor height bound explicitly: a proper 3-by-4 maximal-
minor ideal has height at most two; reduction gives height at least two, and
Hilbert–Burch then gives unmixedness. This does not require a new calculation.

The Fitting-ideal identification is compatible with the finite-prefix centering
and polynomial deflation: source and target changes are invertible, and removing
identity blocks preserves the zeroth Fitting ideal. The free hull supplies the
primitive normalization. The exact degree-two saturation dependency supplies
the identification with the original next-order ideal.

Reducedness is transferred only after collision localization. The derivative
of the marked-root equation is a unit there because its value is, up to sign,
the product of the four nonzero anchored roots. The labeled-root extension is
étale after the discriminant is inverted. Étale base change preserves
reducedness; contraction from localization preserves radicality. Flatness of
the symmetric-root extension commutes with each fixed-power colon and hence
with the stabilized saturation. These steps avoid the invalid general assertion
that ramified base change preserves radicality.

The reduced degree-120 ACM curve, genus 1021 and unique degree-twelve surface
follow with precisely the scope of the rational-resolution dependency. Neither
irreducibility, smoothness, higher-degree reducedness nor the all-N conjecture is
asserted proved. The latter is correctly described as a stronger sufficient
mechanism, using the prior differentiated-minor argument, rather than a necessary
endpoint for the degree bound.
