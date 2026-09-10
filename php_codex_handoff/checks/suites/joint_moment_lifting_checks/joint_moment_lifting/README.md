# Joint-moment lifting in a degree window

This directory contains an exact-arithmetic test suite for the joint-moment
construction described in the accompanying conversation. It does not contain a
proof of the unrestricted ENS/PHP lifting or an AC0[p]-Frege lower bound.

## Main characteristic-two statement

Let F be a polynomial system over F_2 containing y^2-y for every old variable.
Take one level of disjoint fresh ENS blocks

    E_ai = g_ai * product_{u=1}^h (1 - sum_j r_auj g_aj).

Degrees here are the original degrees in both old and new variables, before any
Boolean reductions or substitutions. Let D be the target degree. Suppose every
nonzero active companion has

    D-h < deg(E_ai) <= D.

Then every normalized degree-D design of F has a degree-D extension annihilating
F, all ENS companions and all new field equations. The extension preserves all
old-variable moments. There is no hypothesis on the number of blocks, fan-in, or
structure of the input polynomials. The statement iterates without loss when the
same window hypothesis holds for each level.

## Operators and local consistency proof

Set M=D-h. For a block a and input j, substitute r_auj=t_u for all u and all
other new variables to 0. Let T_aj(P) be the coefficient of t_1...t_h after
multilinear reduction in t. This is an F_2-linear, not multiplicative, operator,
and deg T_aj(P)<=deg P-h whenever its value is nonzero.

Let I_b(F) be the vector space of bounded-degree consequences, i.e. sums qf
with deg(qf)<=b term by term. It is not the unrestricted ideal. Let V_a be the
space of G=sum_i q_i g_ai with deg q_i<=D-deg E_ai for active companions.
There exist functionals mu_aj on old polynomials of degree at most M such that

    mu_aj(I_M(F))=0,
    sum_j mu_aj(G g_aj)=lambda(G) for all G in V_a.

For completeness, the consistency proof is finite-dimensional duality. If
G g_aj is in I_M(F) for every j, write G=sum_i q_i g_ai, and put
k_a=max_i(D-deg E_ai)<h. Then

    G^2=sum_i q_i (G g_ai) belongs to I_(M+k_a)(F).

Also G^2-G is a consequence of the old Boolean equations in degree at most
M+k_a. Indeed, if delta_a=max_j deg g_aj, delta_min=min_i deg g_ai, and
s_a=D-h(delta_a+1), then deg G<=s_a, k_a=s_a-delta_min,
and M+k_a-2s_a=h delta_a-delta_min>=0. Hence G is a consequence within
M+k_a<=D and lambda(G)=0. This is exactly the dual consistency condition.

The functional is

    Lambda(P)=lambda(P(y,0)) + sum_(a,j) mu_aj(T_aj(P)).

For a multiplier H of E_ai, deg H<h. Under a selected substitution its
new-variable part is t_A with |A|<h. Its full t coefficient in H E_ai is

    q g_ai (1-g_aj)^|A| (-g_aj)^(h-|A|).

Modulo the old Boolean equations this is q g_ai g_aj when A is empty,
and zero otherwise. Cross-block corrections vanish because H has degree <h.
All degree bounds are retained before reduction. The consistency identity above
therefore proves Lambda(H E_ai)=0. Old axioms and field equations are checked
directly under T; T kills all old-only polynomials, so old moments and
normalization are preserved.

The mu components need not be normalized or positive. In particular, a nonzero
component may have mu(1)=0.

## Odd characteristic version

For p>2 and alpha nonzero in F_p, put

    chi_alpha(g)=1-(g-alpha)^(p-1).

Define T_ajalpha(P) as chi_alpha(g_aj) times the full multilinear t coefficient
after r_auj=t_u/alpha and other new variables are set to 0.
For a block with input maximum degree delta_a set

    M_a=D-h+(p-1)delta_a,
    s_a=D-h(delta_a+1),
    k_a=max_(active i)(D-deg E_ai),
    B_a=M_a+k_a+(p-2)s_a.

If every k_a<h, an input design of degree

    B=max(D,max_a B_a)

suffices. Let mu_ajalpha annihilate I_(M_a)(F), and choose them so that

    sum_(j,alpha!=0) mu_ajalpha(G chi_alpha(g_aj))=lambda(G).

They exist: in the dual obstruction, all G chi_alpha(g_aj) are in I_(M_a).
The exact identity g=sum_(alpha!=0) alpha chi_alpha(g) gives G g_aj in the
same space. Then

    G^p=sum_i q_i G^(p-2) (G g_ai)

is a consequence within B_a, and G^p-G belongs to the old field ideal within
that degree. The latter degree check follows from

    B_a-p s_a=(h+p-1)delta_a-delta_min >= 0.

Set

    Lambda(P)=lambda(P(y,0)) + (-1)^(h+1) sum mu_ajalpha(T_ajalpha(P)).

The indicators make partial nonempty t supports vanish modulo the old field
ideal, while empty support contributes (-1)^h G chi_alpha(g_aj). The new
field equations vanish because t/alpha lies in F_p for t=0,1. This proves the
same annihilation statement. Monic univariate Boolean/field reductions do not
increase degree.

A simpler sufficient bound, when k_a<=k<h and delta_a<=delta, is

    B=D+max(0,(p-1)k+(2p-3)delta-h).

The characteristic-two proof above is sharper: B=D under k<h without the extra
delta term. The odd-characteristic theorem concerns one level; iteration must
respect both the degree budgets and window hypotheses at each step.

## What is not proved

When a permitted multiplier can contain all h groups of another block, distinct
single-block corrections can interact. Full-group support in the same block
also produces g_i(1-g_j), which is not automatically annihilated. The present
single-block-sum construction does not resolve these additional constraints.
They occur for active low-degree companions with deg E<=D-h. Mixed-block moment
components or another construction are still needed for general ENS systems.
The window condition is not asserted for all BIKPRS simulation output.

## Reproduction and test scope

Run:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python checks.py

Only NumPy and the Python standard library are required. Elimination updates are
vectorized modulo p; independent instances use four worker processes. Symbolic
bookkeeping retains original multiplier degree limits.

There are 42 instances over F_2, F_3 and F_5, with 126 blocks and 396 companion
polynomials. Twelve instances have genuinely unsatisfiable Horn-chain base
systems, but normalized degree-3 designs; these test the moment-space solver
rather than only pointwise satisfaction. Their h=1 extension axioms have degree
3 and are active. The remaining tests use signed finite-domain functionals to
check higher accuracies, nonlinear inputs, odd characteristics and mixed
multipliers. They do not test a complete PHP design at large n.

The suite performs 24,654 annihilation checks. It also contains a boundary
control demonstrating that omitting mixed corrections outside k<h can fail.
This is a failure of that restricted construction, not of the general lifting
claim outside the window.

`horn_example.npz` contains exact moment and relation-space data for seed 100;
all input tuples and the other instances can be reproduced from the seeds in
`results.json` and the code. No floating-point rank calculations are used.

## Cofactor-sensitive variant, without the top-window restriction (F_2)

Keep arbitrary active ENS blocks and arbitrary target D. Let

    k=max_(active a,i)(D-deg E_ai),
    B=max(D,D-h+k) <= 2D.

A degree-B old design suffices to construct the same single-block-sum Lambda.
It annihilates all old degree-D multiples and all new field equations. It also
annihilates each degree-D extension multiple H E_ai whenever every monomial of H
misses at least one of the h factor groups in every block of new variables.
There is no restriction on the old-variable degree of H beyond its original
allowed total degree.

Proof: the local dual consistency calculation above uses only B>=M+k. The
hypothesis on monomials of H, rather than k<h, is exactly what makes all
cross-block and partial-support contributions vanish. The top-window theorem
is the special case where this cofactor property follows automatically from the
total degree bound.

Consequently, if the old system has a degree-2D design, any degree-D augmented
refutation must have a cofactor monomial touching all h factor groups of some
block. This is a necessary cofactor property, not a proof that no unrestricted
refutation exists.

## A sufficient full mixed-moment hierarchy (F_2, one level)

For a set S of blocks and a choice J=(j_a : a in S), let T_(S,J) set
r_(a,u,j_a)=t_(a,u) for a in S, all other new variables to zero, and extract the
coefficient of the product of all h|S| auxiliary Boolean t variables.
It lowers degree by at least h|S|. Let mu_(S,J) be a homogeneous old-system
design of degree D-h|S|, and mu_empty=lambda. Put

    Lambda(P)=sum_(S,J) mu_(S,J)(T_(S,J)(P)).

A sufficient system of compatibility equations is:

For b not in S, every companion i, and deg q<=D-deg E_bi-h|S|,

    mu_(S,J)(q g_bi)
      = sum_j mu_(S union {b}, J union {b->j})(q g_bi g_bj).

For b in S, the same q degree limit,

    mu_(S,J)(q g_bi (1-g_b,j_b))=0.

Empty multiplier ranges impose no conditions. The original (unreduced) degrees
of E are used throughout. Normalization is mu_empty(1)=1.

To check sufficiency, examine a multiplier monomial. If its new variables use
different coefficient indices within a block, every diagonal operator above
kills it. If it touches a block other than b only partially, every operator
also kills it. If it touches b partially, Booleanity makes the relevant
coefficient g_bi*g_bj*(1-g_bj) vanish. The remaining monomials consist of a
full-group diagonal monomial in each block of S. They give exactly the two
equations displayed above, depending on whether b is in S. Old and field
axioms are automatic under the operators and old-design conditions.

This hierarchy is a sufficient construction, not a claim that all joint designs
have this representation. Its feasibility for general PHP extension systems
at affordable degree has NOT been proved. The top-window argument solves the
first independent layer; lower-degree extensions require the mixed layers.
