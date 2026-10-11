# Bounded Boolean ranges give full certificates

Proposed theorem: certified range exclusion. Fixed prime p. Features U_j(x),
j<=r, have circuits and linear-Z certificates K_j(x,B)=U_j^2-U_j,
K_j(x,0)=0, where B_l=x_l^2-x_l. Let beta in F_p be outside the residues
{0,...,r}. Then F=sum U_j-beta has a full Hilbert-like IPS refutation of
size polynomial in the supplied total size plus O(r^2 2^r), and depth the
maximum supplied depth plus O(1).
Circuits have unbounded-fanin addition/multiplication gates, with gates and
wires counted and no division or succinct powering gates.

For eps in {0,1}^r put c_eps=sum eps-beta, E_eps(z)=prod_j
(eps_j ? z_j : 1-z_j), and D(z)=sum_eps c_eps^-1 E_eps(z).
Since sum E_eps=1,
D(z)(sum z-beta)-1=sum_j a_j(z)(z_j^2-z_j),
where a_j=sum_eps c_eps^-1(2eps_j-1)prod_(l!=j)
(eps_l ? z_l : 1-z_l). This follows termwise by multiplying E_eps
by z_j-eps_j. Hence D(U)Y-sum_j a_j(U)K_j(x,Z) is the full certificate.
Sharing supplied circuits and explicit products proves the size/depth bound.
Overlaps, repeated features and r=0 cause no problem. In F_p a beta with
this property cannot exist at r>=p-1. Cofactors need not be multilinear.

The application requires cheap Booleanity of the WRITTEN multilinearized
features. Within each group i take atoms that are distinct x-variables or
ORs G_S=1-prod_(y in S)(1-y). After identifying duplicate atoms, assume their
variable supports are pairwise disjoint. Let S_i=sum_sigma M_i,sigma,
each M a squarefree product of atoms, and L_i=ML(S_i^(p-1)) in the original
variables. Let U_i=1-L_i. Different groups may overlap arbitrarily.
For fixed p, these features and their full Booleanity certificates have
polynomial size in the total explicit atom/term/literal description T,
and constant depth.

An atom G has an explicit Booleanity certificate K_G. For a variable use Z.
For an OR write E=prod(1-y): G^2-G=E^2-E; product telescoping in literals
expresses this using old Boolean axioms, with O(|S|^2) wires and constant
depth. Expand only the p-1 copies of S_i, giving N_i^(p-1) ordered term
tuples. Do not expand the ORs. A resulting term has form prod_G G^a_G,
with 1<=a_G<=p-1. Replace it by prod_G G. Remaining atoms are multilinear
with disjoint supports, so this is exactly its original-variable multilinear
reduction. For a>=2, G^a-G=(G^2-G)sum_(b=0)^(a-2)G^b.
Product telescoping and K_G therefore give a linear-placeholder certificate
for the difference of a term and its reduction. Sum over ordered tuples:
R_i(x,B)=S_i^(p-1)-L_i. The tuple count and every factor list are polynomial
in T for fixed p, all powers are bounded by p-1, and unbounded-fanin
prefix/suffix products give constant depth. This is a special structured
multilinearization, not a generic one.

Set V_i=1-S_i^(p-1). The previous cycle's explicit Frobenius gate certificate
gives K_Si(x,B)=S_i^p-S_i. Because U_i-V_i=R_i(x,B), the circuit
K_Ui=S_i^(p-2)K_Si+(U_i+V_i-1)R_i
certifies U_i^2-U_i. Indeed V_i^2-V_i=S_i^(p-2)(S_i^p-S_i).
It has polynomial size and constant depth. Aggregate products
A_j=prod_(i in I_j)U_i likewise have Booleanity certificates by product
telescoping, without monomial expansion. Apply the first theorem to fixed
r aggregate products to obtain the full small certificate for sum A_j-beta.

Source match: Section3.2 of the author PDF defines, for fixed positive i,
f_sigma^(i,j) as an OR on negative strings with a specified overlap pattern.
Two such sets in the same negative block are identical or disjoint;
different negative blocks and the positive x variables are disjoint.
Its S_i therefore satisfies the atom hypothesis. Its local feature is
exactly 1-ML(S_i^(p-1)), and the scattered classes form the aggregates.
In the p>=5 hard family r<=3; beta can be chosen outside {0,1,2,3}.
The explicit description is polynomial in the source's written parameters.
This recovers the paper's advertised nonmultilinear upper bound with all
Boolean corrections, not an independently new lower-bound result.
No binary version of its multilinear lower bound is asserted.

Complete telescoping witnesses (empty sums are zero): if E=prod_a ell_a,
K_E=sum_a Z_(variable of ell_a) prod_(b<a)ell_b^2 prod_(b>a)ell_b;
each ell is 1-y here, and ell^2-ell=B_y. Set K_G=K_E for G=1-E.
For one expanded term t=prod_b G_b^a_b, its reduction witness is
K_t=sum_b K_Gb*(sum_(q=0)^(a_b-2)G_b^q)*
prod_(c<b)G_c^a_c*prod_(c>b)G_c.
For an aggregate A=prod_i U_i, use
K_A=sum_i K_Ui prod_(j<i)U_j^2 prod_(j>i)U_j.
Each specializes to precisely the corresponding difference, and is linear
in the original Boolean placeholders.

Nonvacuity: p=5, S=sum_(i=1)^n x_i, U=1-ML(S^4), F=U-2 has unbounded
variable counts, nonconstant features and polynomial description. Zero or
repeated terms cancel by field arithmetic; duplicated atoms are handled by
the displayed power reduction. Constants and empty groups are allowed.
The polynomial exponent is allowed to depend on fixed p.

Structural conclusion: cheap feature Booleanity plus impossibility on the
ENTIRE feature cube gives the upper bound. An outer target possible on that
cube but missing from the actual feature image escapes this argument, without
being proved hard. The existing binary AB=I_(n+1) family is an unbounded
nonvacuous example of that distinction: AB has rank<=n, while the unconstrained
Boolean feature matrix can be identity. Its description is polynomial.
Prior full-certificate extraction gaps remain; this does not reopen a solved
calibration or assert rank-family hardness.

Goal unchanged. This disqualifies the cited restricted-hard knapsack as a
direct general-IPS candidate and explains why, rather than confusing a cheap
functional inverse with a full certificate. Next is the scheduled review
after six research entries. Review must compare image-sensitive algebraic
hardness and direct proof-local actual-error control, without treating
canonical determinant extraction as mandatory.

