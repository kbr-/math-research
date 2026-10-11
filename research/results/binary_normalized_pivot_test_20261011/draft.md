# Normalized pivot isolation

Proposed result: lem:normalized-pivot-mask. Goal binary-frege-lower-bound unchanged.
This executes the previous cycle's owed circuit-cancellation test on the actual
normalization, not an invented generic source. No computation is needed: identities
are literal products and the already checked gate telescoping rule.

Use F_ik=delta_ik+sum_l A_il B_lk, m>n>=1, over F2, P=prod(1+F).
C=sum c_ik Y_ik+sum d_x Z_x is any Hilbert-like certificate. Fix the explicit
Frobenius witnesses K_Fik=sum_l(B_lk Z_Ail + A_il^2 Z_Blk).
Q=sum c_ik P_ik K_Fik + P sum d_x Z_x is its direct normalization.

Fix j=n+1. Let rho set the entire matrix-B column j to zero, matrix-A row j
to e_1, the Boolean placeholder Z_B1j to one and every other Z to zero.
Leave all other A and B entries formal. Then
rho Q = (rho c_jj) R,
where R=rho P_jj.
Indeed 1+F_jj=0 under rho, so P and all P_ik for (i,k)!= (j,j) vanish.
For the sole remaining witness rho K_Fjj=1. This proves the identity for
every original certificate, regardless of its circuit syntax. rho is a
constant/zero substitution, hence no depth increase or size increase.

For the canonical shared-pivot C, c_jj depends only on the top n rows of A,
so survives rho and computes the determinant function there. It is nonzero
as a formal polynomial. R is also a nonzero formal polynomial: with j deleted,
its diagonal factors are nonzero bilinear sums, and all off-diagonal factors
have constant term one. n>=1. Thus rhoQ is nonzero in the polynomial domain.
This rules out COMPLETE formal cancellation of this coefficient/probe; it is
not a circuit lower bound for the product.

Write I={1,...,m}\{j}, t_k=B_1k for k in I, T=prod_(k in I)(1+t_k).
Then R=T H, with
H=prod_(i,k in I)(1+delta_ik+sum_(l=1)^n A_il B_lk).
Set the first row t of B to zero and call H_0=P'. This is exactly the residual
for (m-1)-by-(n-1) and (n-1)-by-(m-1) matrices, with consistent row/column labels.
There are polynomial-size constant-depth L_k for
H+H_0=sum_(k in I)t_k L_k.
Explicitly order the factors h_a, let h_a^0 be their zero-t restriction:
H+H0=sum_a(h_a+h_a^0) prod_(b<a)h_b prod_(b>a)h_b^0.
For a=(i,k), h_a+h_a^0=A_i1 t_k.
Group by k to get L_k=sum_i A_i1 prefix_(i,k) suffix^0_(i,k).
Consequently
R = T P' + sum_k [prod_(r!=k)(1+t_r)] L_k (t_k^2+t_k).
Thus the mask is a smaller rank residual times T plus a completely explicit
small constant-depth Boolean certificate. No formal division or extraction
of a high homogeneous component is used. Multiplication by c_jj retains its
actual circuit cost; the identity does not remove that coefficient.

R is Boolean-zero: T=0 kills it, or all t_k=0, when H=P'; rank m-1 cannot be
achieved with inner dimension n-1. This holds even at m=n+1, not just m=2n.
It also follows after first evaluating rho since the normalized certificate's
coefficients have zero cube trace, but here it is direct.
For n=1, P'=0 (zero inner dimension); R has the stated cheap Boolean
certificate. For n>=2, P' is nonzero formally and Boolean-zero. R is never
a nonzero Boolean scalar one could invert to peel off the hard coefficient.
For m<=n the refutation premise does not exist; local factor identities remain.

Circuit bounds: R,T,H,H0,L_k together have polynomial size in m,n and absolute
constant depth, because they are explicit products/sums of degree-two factors.
The scalar restriction uses only constants. This supplies no division closure
for circuits, no small C from its coefficient function, no hard Q for all
representatives, and no depth-preserving extraction of det from c_jj R.

Relation to records: previous theorem provided direct Q in J^(m-1) and hard
chosen C; unit-slice syzygies already rule out protected coefficients across
all C; binary-oracle-closure-gap already rules out scalar black-box Boolean
recovery from Q. This lemma identifies the actual surviving masked coefficient
and its smaller residual, rather than treating nonzero formal Q as hardness.

The reviewer's unit-slice suggestion is already implied by the recorded lemma,
and is verified here as an application, not an independently new mechanism.
Let rho_x be rho on old variables only; it is a coordinate retraction and
rho_x F_jj=1. Index this generator as F0 and all other full generators as G_i.
If C=sum c_i Y_i, including Boolean placeholders, set h_i=rho_x c_i for i>0,
c'_i=c_i+h_i F0, c'_0=c_0+sum_(i>0)h_i G_i.
The added contributions cancel in sum c'_i G_i; under rho_x all c'_i, i>0,
vanish and c'_0=1 by the original certificate identity. Therefore C' is a
full certificate, and the same direct normalization and probe give rho Q'=R.
The determinant dependence disappears from this probe at polynomial size and
at most max(d,2)+4 depth for C', followed by constant-depth normalization.
No globally small-depth C' is constructed from nothing. Thus the hard chosen
cofactor cannot be protected even on this normalized scalar restriction.

Next decision: same size-sensitive full-coset gap persists. Rather than study
this removable coefficient further, take the existing child asking whether
unit-slice syzygy normalization can be realized inside the exact Frege-to-IPS
simulation image. Compare the published circuit construction with the explicit
patch above, seeking either a costed realization or a specific provenance
constraint that excludes it. This weakens the target from arbitrary certificates
to the matched image; it is not an assumption that every general IPS operation
is realizable by the given simulation. No further factor-extraction task is added.

