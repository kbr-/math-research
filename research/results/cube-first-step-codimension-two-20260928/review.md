# Invariant prefix review — 28 September 2026

Verdict: **Pass.** No substantive gap, incorrect order count, or unused essential
hypothesis found in the three new claims. This was the cycle's single
fresh-context medium-reasoning correctness review. No computation was needed.

Reviewed the draft `/tmp/bmd-codim-two-entry.html` and the appended notebook
entry `entry-2026-09-28-cube-invariant-prefix`. Read the root instructions and
computation policy, then the complete dependency passages:

- `cube-degree-two-normalization-quotient`;
- `cube-double-pair-local-module`;
- `cube-degree-two-cluster-defect`;
- `cube-marked-ore-deflation`;
- `cube-first-step-ext-degree`.

## Local differential prefix bound

The differential-field cyclicity observation is valid with a nonzero residue
derivation: a first dependence makes the preceding span connection-stable.
The hypothesis that the maximal ideal is invariant is exactly what permits
this reduction. When the cokernel is the residue field, it annihilates the
maximal ideal, and the image in the residual free module has dimension r−1.
The first r−1 vectors therefore extend to a free basis over the local ring.

Monic Ore division in the displayed orientation, D^j = Q_j L + R_j, is valid
over A without division by any coefficient. Left multiples of the monic
operator cancel successive highest powers; commutation introduces only lower
orders. The h=0 case is covered by L=1.

The connection preserves mF and mU+m²F. In particular D(U) is contained in
U+mF, so differentiating mU gives only mU and m²F terms. The indicated quotient
has dimension c because U is a direct summand of corank one. For completeness,
the cyclicity inference also uses U∩mF=mU: if w in mF is expressed as u+Qz,
then Qz lies in mF, so u lies in mU and disappears in the quotient. Thus z is
indeed cyclic on that entire c-dimensional quotient.

The first c iterates of z, together with the first h iterates of v, generate
Gamma/mGamma. Their largest order in v is h+c−1=r+c−2. Noetherianness makes
Gamma finite, so Nakayama applies and gives exactly r+c−1 prefix vectors.
The rank-one examples attain the claimed count for every c. No regularity,
characteristic-zero, or trivial residue-derivation hypothesis is covertly used
by the local lemma.

## Cube application and sufficient reducedness condition

The exact core quotient is the centered full cyclic defect by marked Ore
deflation. The normalization quotient identifies its generic double-pair
localization with the residue field; its lower-dimensional kernel vanishes
there. This uses the centered coefficient ring and does not confuse its length
one with the ramified distinguished-root lengths. The support and local
calculation dependencies agree with that use.

Root differences have derivative divisible by themselves, so contraction of a
double-pair diagonal gives an invariant coefficient prime. At its height-two
local ring, c=2, giving q+1 iterates, through order q. At any other invariant
height-two prime the full cokernel vanishes, giving the first q iterates.
The normalization kernel also vanishes at height two, establishing the stated
vanishing of L_N. This excludes no non-invariant prime, including special
loci within the collision divisor.

Differentiating each maximal minor gives enlarged-prefix minors and minus
trace(B) times the old minor. The containment delta(J_N)⊆J_N^+ holds for the
whole ideal by Leibniz and J_N⊆J_N^+. Under (GR), localization consequently
makes P S_P invariant. Explicitly, delta(j/s)=delta(j)/s−j delta(s)/s² is in
P S_P for j in J_N and s outside P. Contraction then makes P invariant in S,
contradicting the preceding exclusion. The prior duality theorem supplies the
absence of lower-codimension support and the stated conditional equality.
Generic reducedness remains a sufficient unproved condition; no global
graded bound follows from the local theorem alone.

## Uniform counterexample and scope

All derivatives, the radical (z,x^h+y), and the localized ideals
(y,x^(h−2)) and (y,x^(h−1)) are correct for every h≥3 in characteristic zero.
At (x,y), z is invertible, the full cyclic ideal is the unit ideal, and the
three-vector prefix quotient has length h−2. The grading makes the connection
degree one and the marker homogeneous. The marker is squarefree and coprime
to its first derivative. Thus the example genuinely refutes the stated
general surrogate while making no claim to be an actual cube instance.

The row-ratio obstruction to one common scalar making the pair rows
polynomial is also valid: an odd valuation prevents rationality. If one root
is zero, one of the two branch points is at infinity. No external
transversality theorem is used in the proof of any new claim.

## Required changes and unused hypotheses

No mathematical correction is required. The verification gate should replace
its pending text with the completed review outcome. Optional explanatory
additions are the identity U∩mF=mU and the displayed localization quotient
rule above; they merely expand steps already justified by the draft.

All essential hypotheses are used. The N≥5 scope matches the preceding
first-step theorem and is not asserted to be a sharp range for the standalone
local argument. The invariant-prime hypothesis cannot be dropped, as the
counterexample demonstrates. The global Ext initial-degree obligation stays
open.
