# Consolidated correctness review

Verdict: **PASS** for both new mathematical claims. No required corrections.

Reviewed the stable entry draft and the complete supplied excerpts for the odd
Schur normalization, pair recurrence, four-root criterion, characteristic-zero
factorization refutation, tame-chain model and point-fixing involution theorem.
Inspected the GP driver and the entire retained balanced-boundary output. No
computation was rerun, and no broader source or novelty audit was undertaken.

## Ternary balance failure

- The driver uses lexicographic pair rows and columns q_0 through q_9. Its
  recurrence indexes the convolution correctly, including the empty sum for
  q_1. It uses delta=(a_i-a_j)^2 and the original characteristic-three square
  root normalization, with no odd scalar discarded.
- The Schur determinant identity gives det(Q)=V^3 Phi_5 with this pair order
  and V=product(a_j-a_i), without an extra sign. Equivalently the original
  determinant is V^2 det(Q)=V^5 Phi_5. The saved exact quotient is polynomial
  and has t-degree 11 and leading coefficient u^2+2u+1=(u+1)^2, as stated.
- The five labels are distinct over F_3(t,u); their first four obey the claimed
  balance. The nonzero restriction to this slice suffices to exclude the full
  balance hyperplane as a divisor. If the phrase generic hyperplane is read
  literally, translation and homogeneity recover its dense scaled chart from
  this normalized slice; the nondivisibility argument needs only the slice.
- The four-root zero control selects exactly the six appropriate pair rows
  and their first six columns. Independently, the cited four-root formula has
  e_1=-(1+t), so its factor e_1+(1+t) vanishes. Thus the four-subset product
  vanishes while the normalized five-root polynomial does not.
- Symmetry of the unanchored polynomial and translation invariance justify
  re-anchoring after each root permutation. The fifteen forms are the three
  pair partitions of each of five four-element subsets; they remain distinct
  up to scalar in characteristic three and form one S_5 orbit. Therefore all
  fifteen are excluded. The old colliding characteristic-zero specialization
  is correctly distinguished from this characteristic-three certificate.

## Canonical chain obstruction

- The inherited involution preserves the actual stage lengths, fixes the
  selected edge pointwise and works at vertices as well. Its quotient has the
  asserted degree-two harmonic map, integral descended infinity divisor and
  pullbacks phi^*P'=2P and phi^*H'=H.
- With k=n-2>=3 and M=2^k, g=1+(k-1)M is odd. The fixed-locus Euler
  characteristic 2^j+2^(k-j+1)-4 is at least 4, including both endpoint stages.
  Consequently g'=(g+1-chi)/2 <= (g-3)/2.
- B=(k-1)H'-(g+1)P'/2 is integral and has degree (g-3)/2 >= g'. Metric
  Riemann--Roch therefore gives an effective representative. Pulling back
  yields K-(g+1)P up to equivalence; adding P proves the desired K-gP
  statement. The canonical rank g-1 gives precisely the stated ordinary
  canonical tropical Weierstrass condition.
- This does not substitute canonical degree into the earlier nonspecial
  theorem. It uses that theorem's geometric construction and a stronger
  numerical bound, so its odd dimension and canonical degree cause no gap.

## Hypothesis and scope audit

No hypothesis needs removal from either stated claim. Characteristic three is
essential to this coefficient certificate. Distinctness is used on the symbolic
slice and holds there. The graph proof needs positive lengths equal within each
stage, as supplied by the defined graph; it needs neither rational lengths nor
an algebraic lifting assertion. The bound n>=5 supplies the quotient-genus
margin. The graph's algebraic origin is context, not an additional premise for
metric Riemann--Roch. Neither claim proves a new algebraic generic-normality
range, coefficient independence for arbitrary N, or a lifting theorem.
