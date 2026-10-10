# Scheduled goal review: stable mathematical draft

Historical reviewer draft, superseded by entry.html and the appended notebook record.
The completed gate is in review-evidence.md. Both Frege lower-bound targets remain open.

## Route disclosed after blind stage

The active queue item asks for Tseitin-specific depth-preserving interpolation.
An actual ladder Tseitin instance has linear-size width-15 resolution proofs
but its left/right projections force MOD3 separators. Thus "Tseitin-specific"
alone is insufficient. On expanders, the last cycle proved a barrier only for
binary linear combinations of vertex charge equations. It does not extract
such an annotation from arbitrary Frege. A bound on all charge annotations is
not a bound on arbitrary Frege proofs. The alternative source route needs a
size-dependent estimate for actual errors under one coherent choice and one
surviving old weight. Complete proof observations already have full rank, so
an estimate independent of the hypothesized proof size cannot work.

The near-half thinness lemma was ALREADY imported here as
cor:intrinsic-shadow-ratio. The blind brief incorrectly called it new; this
review must explicitly correct that description and avoid a duplicate import.
The proposed new composition below excludes one attempt to use its sufficient
premise on our current old closure. It does not settle thin actual error kernels.

## Proposition: charged thin-tail obstruction

Use the existing proper binary charged pseudoideal J_D on a connected graph
with n vertices and m edges, in its recorded expansion/degree window. In
particular it contains Booleanity and the original axioms, and its filtered
quotient dimension h(j), j<=D, equals the number of ternary cut-code cosets
meeting the radius-j Hamming ball. Let C_D be any Boolean degree-D pseudoideal
contained in J_D (including the actual degree-D PC closure of the old axioms).
Assume m>=8n and D<=m/8. Fix any degree-compatible monomial order.

For integers 8<=t, 2t<=K<=D there is no real X satisfying

    K <= X <= 2(K-t)+1+(K-t+1)/t

such that the number b_j(C_D) of degree-j standard monomials of C_D is at most
binom(X,j) at every level K-t<j<=K.

Proof. The cut-code quotient has dimension R=m-n+1>=7m/8. For z=1/14,

    h(D) <= sum_{j<=D} 2^j binom(m,j)
         <= z^{-D}(1+2z)^m
         <= [(8/7) 14^(1/8)]^m
         < 3^(7m/16) <= 3^(R/2).

For the strict numerical inequality, raising the bases to the sixteenth
power reduces it to 2^50 < 147^7. Indeed
147^7>144^7=2^28*3^14>2^50, since 3^7=2187>2048=2^11.
The registered code-ball growth theorem (eta=1/2, radius D) therefore gives

    h(K)/h(K-t) >= (3/2)^t.

Initial-space inclusion follows from C_D subset J_D; hence every standard
monomial of J_D is standard for C_D, in this same order. A proposed cap on
C_D therefore also caps J_D. Apply cor:intrinsic-shadow-ratio to J_D with
the singleton error E=1 (e=0). Its actual rank at cutoff k is h(k). With
rho=(X-K+t)/(K-t+1), the displayed X bound gives rho<=1+1/t, and thus

    h(K)/h(K-t) <= 1+sum_{i=1}^t rho^i <= 1+e*t.

This contradicts (3/2)^t>1+3t>1+e*t for t>=8. At t=8,
(3/2)^8=6561/256>25. The induction step uses
(3/2)(1+3t)>1+3(t+1) for t>=2. Properness ensures h(K-t)>0.
All quotient statements are filtered; no global charged algebra or satisfying
assignment is assumed. Binary descent preserves these dimensions. QED.

Application. In the standing growing-degree family, m>=n*Delta/8 and
D=floor(n*Delta/64). For Delta>=64, m>=8n and D<=m/8, so this applies to
every admissible t,K above. It is a whole-old-closure obstruction, not an
obstruction to smaller error standard families or a different containing
pseudoideal that is not contained in this canonical J_D. No qualifying
near-half family elsewhere is excluded. It gives no actual Frege lower bound.

## Correction: flat-shadow harmonic threshold

The earlier prop:flat-shadow-limits correctly writes

    rho=(X-K+delta)/(K-delta+1).

But its subsequent rearrangement of rho<=1+1/delta is incorrect. The correct
upper bound is

    X <= 2K-2delta+1+(K-delta+1)/delta,

not 2K-delta+1+(K-delta+1)/delta. Its claimed iff threshold (1), when
r>m and q=2m-r>=K, must have the same correction: replace its right side by
the corrected expression. X=q remains the smallest cap-certifying choice.
The graded cap proof and the complementary-flat nonadditivity control are
unchanged. Its exclusion for r<=m in K<m/4 remains true: the corrected upper
bound is even smaller and still <=3K-1. Its q<K caveat remains necessary.
For a decisive symbolic counterexample to the old iff, set K=2, delta=1,
q=6. The old threshold permits q=6; the correct upper bound is 5.
The minimum X=6 gives rho=5/2>2=1+1/delta.

Choose m=9,r=12 to realize q=2m-r=6 with r>m and K<m/4. The counting
polynomial is (1+z)^6, so its degree-two cap forces X>=6; the old threshold
allows 6 and the correct harmonic condition forbids it. The two lower degrees
and the actual family can be realized by setting 12 pivot variables to zero
in the pair model with six pairs having one pivot and three having two.
Only the threshold for the majorant, not a hard-instance claim, is tested.

## Goal assessment

New mathematics: the conditional charged thin-tail obstruction is a
composition of two recorded results; the flat-shadow threshold is corrected.
Goal progress: unchanged. The current family does not automatically qualify
for the whole-closure thinness alternative, while the actual-error and
arbitrary-Frege extraction obligations remain open. Do not add a near-half
duplicate lemma or count this correction as a superpolynomial bound.

## Requested stage-two assessment

Check the proposition and correction against the exact excerpts supplied.
Challenge the unchanged-goal assessment and whether the proposed result merely
duplicates an existing charged-growth consequence. Compare the unsupported
Frege extraction with the actual-error route; no source-size estimate is
currently supplied. Identify any concrete weaker extraction that the recorded
charge barrier would actually suffice for. Do not assert it exists.
