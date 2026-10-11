# Shared pivot certificates and their depth limit

Work over F2 with rank equations F_ik=delta_ik+sum_l A_il B_lk,
all Boolean axioms b_x=x^2+x, m>n>=1. Circuits count unbounded-fanin
sum/product gates and wires. All certificates below are Hilbert-like in
matrix placeholders Y and Boolean placeholders Z.

The intended construction uses ONE child certificate for (m-1,n-1),
not one copy per pivot. Let u_j=A_1j, p_j=prod_(l<j)(1+u_l),
w_j=u_j p_j, w0=prod_l(1+u_l), w=sum_j w_j=1+w0.
For a selected j, list the other inner indices k_j(h) in increasing order,
h=1,...,n-1, and set
a^j_(i,h)=A_(i+1,k_j(h))+A_(i+1,j) u_(k_j(h)),
b^j_(h,k)=B_(k_j(h),k+1).
The actual mux matrices are a=sum_j w_j a^j, b=sum_j w_j b^j.
This is canonical pivot-to-first permutation, then one column elimination.
At w_j=1 the old pivot is one; at w0=1 the mux is zero.

Exact branch relation for i,k>=2:
G^j_(i-1,k-1)=F_ik+A_ij F_1k+(1+u_j)A_ij B_jk,
where G^j=I+a^j b^j. Hence w_j G^j has a full old certificate:
w_j Y_ik+w_j A_ij Y_1k+p_j A_ij B_jk Z_(u_j).

Full mux correction:
Supply K_j with K_j(x,Z)|_(Z=b)=w_j^2+w_j by literal telescoping.
For j<k,
L_jk=Z_(u_j) p_j u_k prod_(l<k,l!=j)(1+u_l)
certifies w_j w_k; take L_kj=L_jk.
Define M_jk=w L_jk for j!=k, and
M_jj=(w+1)K_j+sum_(l!=j)L_lj.
Then M_jk(x,b)=w w_j w_k+delta_jk w_j.
For each child equation use the old-placeholder circuit
H_ik=w Y_ik+sum_j w_j A_ij Y_1k
     +sum_j p_j A_ij B_jk Z_(u_j)
     +sum_(h,j,l) M_jl a^j_(i-1,h)b^l_(h,k-1).
It evaluates to w G_(i-1,k-1)(a,b) literally.

For each mux entry phi, its Boolean defect has the previous explicit
Frobenius certificate K_phi(x,b)=phi^2+phi, polynomial size/constant depth.
Use w K_phi for each child field placeholder. This uses all original
Boolean terms, not mere evaluation on the cube.

The all-zero first-row certificate is
H0=w0 Y_11+sum_j [prod_(l!=j)(1+u_l)] B_j1 Z_(u_j);
it evaluates to w0.

Given a complete child certificate C_(m-1,n-1), substitute its entry variables
by the mux entries, its matrix placeholders by H, and its field placeholders
by w K_phi, then add H0. Placeholder linearity implies the child copy
evaluates to w, so the parent evaluates to w+w0=1. The result is again
Hilbert-like. For n=0,m>0, use C_(m,0)=Y_11 (its generator is one).
Induction therefore constructs all m>n certificates.

Circuit accounting: compute each w_j,K_j,L_jk,M_jk and branch/mux entry once.
Each H_ik has at most (n-1)n^2 mux-correction summands; all input maps have
polynomial gate/wire size and absolute constant depth. They are connected to
ONE shared child circuit, with no expansion into coefficient monomials.
Thus S(m,n)<=S(m-1,n-1)+poly(m,n), d(m,n)<=d(m-1,n-1)+O(1).
The whole certificate has polynomial size and depth O(n).
With joint placeholder degree one, every input-map polynomial has degree
at most 3n+3: mux entries at most n+2, H matrix at most 3n+2,
and weighted field witnesses at most 3n+3. Hence the constructed certificate
has joint degree at most 3^n(n+1)! by induction from degree one. Its NS
summands after inserting degree-two axioms cost at most that bound plus one.
No original-degree-preserving PC transfer is asserted.
This is not claimed as a new general IPS upper bound for the rank principle.
It verifies the sharing question and the full field/cofactor interface.

Depth obstruction for THIS exact certificate:
Let c_(m,n) be its coefficient of Y_(n+1,n+1), obtained by substituting that
matrix placeholder to one and all other matrix/field placeholders to zero.
H0 contributes zero for n>=1. The special placeholder enters H only through
w Y_ik, since its row is never the current first row before the base case.
Thus c_(m,n)=w*c_(m-1,n-1)(mux A,mux B), with c_(m,0)=1.
Inductively it depends only on A. On Boolean A it is one iff the first n rows
form a nonsingular n by n matrix: a zero first row gives w=0; otherwise the
first nonzero pivot's elementary column elimination preserves rank and the
child top (n-1)-square matrix is nonsingular iff the parent top square is.
Therefore c_(m,n) equals the binary determinant FUNCTION of the first n
rows of A. It need not equal the formal determinant polynomial.

For m=2n, any polynomial-size uniformly bounded-depth circuit computing this
same Hilbert-like certificate polynomial would, by the placeholder evaluation
and fixing irrelevant entries, compute the determinant function at that size
and depth, contradicting the recorded Smolensky-based determinant corollary.
This is a limitation of the exact constructed certificate, not of ALL IPS
certificates. Unit-slice syzygies already show that a protected coefficient
cannot be assumed for every representative.

Put P=prod_(i,k)(1+F_ik). Normalize this C directly by the Hilbert-like
case of lem:prime-field-residual-normalization to obtain the
requested full residual Q(x,b(x))=P(x) with polynomial size/depth O(n). The depth
obstruction for C does NOT automatically apply to that Q: normalization changes
matrix coefficients to fixed selectors and may move or cancel the determinant
dependence. No reverse low-depth recovery of this particular C from Q is
proved. Thus the full Q target remains unresolved, despite the exact failure
of the unnormalized canonical pivot construction.

For this direct normalization there is a further exact control. Put
P_ik=prod_((a,b)!=(i,k))(1+F_ab), and use
Q=C(x,(P_ik K_Fik)_ik,(P Z_x)_x), where K_Fik(x,b)=F_ik^2+F_ik.
Let J be the ideal of all matrix-B entries, with A and Z independent.
Every diagonal factor 1+F_aa=sum_l A_al B_la belongs to J. Consequently
P is in J^m and every P_ik is in J^(m-1). Since C is linear in its
placeholders, Q is in J^(m-1). Thus its matrix-B Hasse derivatives of
total order below m-1 vanish at B=0. This covers this direct normalization
of any Hilbert-like C, not every representative of Q. At m=2n, bounded-order
jets cannot recover the determinant function. It does not justify free
extraction at order m-1 or greater, and gives no circuit lower bound.

Nonvacuity: n=1,m=2 has one child of inner dimension zero; the two first-row
cases and full Boolean fields are nonempty. The local identities also hold
for m=n>=2, giving satisfiable controls, but no refutation is claimed there.
Zero first rows use H0; nonzero rows select exactly one pivot. Repeated entries
and vanishing branch coefficients retain the literal identities. n=0 is only
the explicit constant-contradiction base. Unbounded witnesses are all m=2n.

Completed checker for the local elimination rule:
Native Singular symbolic identities, n=1,2,3 and m in {n,n+1,2n}, omitting
m=n=1 and duplicate pairs: 7 fixtures. Expected 53 child matrix identities,
52 child Boolean identities, 7 all-zero branch identities, and 14 first-one
truth assignments total (shared once per n). Products are expanded only for
the local maps, never the full m^2-factor rank residual or the recursive
certificate. At n=3, a mux A entry has at most14 raw terms, a mux B entry7,
w7; each weighted child equation has at most1379 raw terms before collection.
The negative controls omit the mux correction, pivot-field correction or
all-zero-row field correction and replacing first-one selectors by independent
bits. Accepted run 525998efc6 checked all 7 fixtures, 53 matrix identities,
52 fields, 14 selector assignments and 22 negative controls, with 215 total
checks and zero failures. Full output is check.txt. The first run 99b8796202
was rejected for mixed initialized Singular integer declarations and completed
no fixtures; failed-declarations.txt retains it. Separate declarations fixed
the parser error. No larger run is needed; complexity is proved for all
parameters, not fitted to cases.

Goal unchanged. The scheduled test obtains actual shared full certificates,
but only at growing depth, and a general lower-bound proof only for that
chosen certificate polynomial. Neither is the desired full-class bound.

