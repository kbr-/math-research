# Interpolated readers retain weighted core leaves

Proposed lemma: retained-core reader transfer. Binary only. Gamma(y) includes
all old Boolean axioms. One complete fresh block on old inputs t_i(y), accuracy
h>=1, maximum nonzero input degree delta, coefficient variables u, product P
of original degree v=h(delta+1). Drop zero slots; the empty block is omitted.
H(y) has degree e (take e=0 for constants). Above this block are arbitrary many
terminal complete blocks, each with inputs
  g_ai = L_ai(y) + [alpha_ai + beta_ai H(y)] P,
where L_ai is old affine and alpha,beta are binary constants. All fields are
present, accuracies positive, and original proof cofactors may use all variables.
This is one terminal reader layer, not unrestricted acyclic readers.

For every a and eps,eta in F2 define old-affine references
  L_ai + (alpha_ai + beta_ai eps) eta,
at reader a's original accuracy. Suppose there is one old polynomial f of
degree <=k and old coefficient maps gamma_(a,eps,eta,row,i) of degree <=T0,
T0>=1, such that on every old Boolean point where f!=0 all reference
companions vanish. This is an actual common-support normalizer hypothesis,
not just nonrefutability of four separate systems. Set T=T0+e+v.

Then any degree-B ordinary PC or NS refutation of the full source yields an
old PC derivation of f from Gamma through k+TB+delta. Consequently separation
of f from that old consequence space excludes the refutation.

Proof. Keep y,u fixed; replace each terminal coefficient by
  sum_(eps,eta) chi_eps(H) chi_eta(P) gamma_(a,eps,eta,row,i),
where chi_0(Z)=1+Z and chi_1(Z)=Z. Its degree is <=T. At each Boolean (y,u)
point where f(y)!=0, exactly one summand is active; the actual reader tuple
is its reference tuple, so every mapped reader companion is zero. Every
mapped coefficient field is also Boolean-zero. The original complete retained
core is unchanged, including its coefficient fields.

The needed relative certificate is slightly stronger than unqualified
Boolean division. If Q(y,u) has degree <=q and fQ vanishes on the full Boolean
cube, first reduce Q in the u variables alone, with each reduction summand
of degree <=q. Multiplying the resulting identity by f uses only leaves
f(u_j^2+u_j), with polynomial multipliers, through k+q. Write the remainder
as sum_S q_S(y) u_S. For each Boolean y with f(y)!=0, the multilinear
polynomial in u vanishes at all Boolean u, so every q_S(y)=0. At points with
f(y)=0, f(y)q_S(y)=0 as well. Therefore every old coefficient f q_S is
Boolean-zero in y. Old Boolean division certifies it through its actual degree;
multiplying by u_S stays <=k+q because deg q_S+|S|<=q. Thus fQ follows from
Gamma and the weighted core field leaves through k+q. No unweighted u-field
axiom is used. If a u variable does not occur, no field leaf is needed.

Apply this certificate to each mapped reader companion/field of original
degree d: deg Q<=Td, so cost<=k+Td. For every active retained core axiom A,
use only leaf fA, of degree<=k+deg A<=k+T deg A. Old axioms are fixed and
weighted as legal multiples of Gamma. Replay the original refutation with
line f Phi(q) by the usual degree-T substitution. It derives f through C=k+TB
from Gamma plus f-weighted core companions and f-weighted core fields only.
Each initial core leaf has old cofactor one. Later derived multipliers involving
u do not become new leaves; this is allowed in the weighted elimination lemma.

Apply lem:target-weighted-block-elimination with target f, old base Gamma,
one core, old input degree ceiling delta and p=2. Its exact old-only leaf
premise is satisfied. It derives f through C+delta. For NS start with its
ordinary PC replay. The conclusion is PC target derivability, not an NS=PC
assertion for the augmented system. QED.

Nonvacuity: Gamma=BOOL(y), f=1, H=x, t=(z), core h=1, and a reader with
one input 1+[alpha+beta x]P can be normalized on every reference tuple by
setting its first coefficient to the reference constant if L=1. Each reference
input is a binary constant, so its companion is zero, T0=1. There are nonzero
inputs in the core and reader; f is separated from BOOL at every degree. Adding
unused old variables and copies of reader blocks gives unbounded variable and
inventory counts. The theorem does not claim this satisfiable control is a
Frege hard family. To test genuinely nonconstant affine references, take
L=z: one-input binary affine references g have first coefficient 1 (product
1+g), giving companion g+g^2 Boolean-zero. This works for every reference.

Degeneracies: f=0 gives a vacuous derivability statement and no lower bound;
zero reference tuples use any normalizer; constants H reduce selector cost;
inactive high-degree axioms are not inserted. Empty core has P=1 and can be
omitted with delta=v=0, reducing to the old affine reader setting. All inputs
and all original degree ceilings are retained; image cancellation earns no
additional cofactor budget.

Comparison: thm:costed-partition-direct-semantic-map supplies the same
interpolation mechanism for old-only partitions. Here partitions involve u,
so its old-only statement cannot be applied as written. The u-first relative
Boolean certificate supplies exactly f-weighted leaves; the already proved
lem:target-weighted-block-elimination removes the retained block with additive
delta. This is a composition/refinement of recorded tools, no new general
normalization engine. Pure-reader theorem excludes old-affine parts; greedy
internal-reference theorem instead clamps all internal products and charges
internal reference types. This lemma leaves one arbitrary old-polynomial core
unclamped until the end. Arbitrary many independent cores and unrestricted
nested readers are not covered by the present statement.

Goal progress unchanged. This verifies a paid composition for the specific
post-merge reader template. No complete source coverage theorem or new
lower-bound exponent follows merely from the interface hypothesis. The next
question is whether known affine common-support normalizers supply f with
separation through k+TB+delta on the actual chosen family; do not replace
that hypothesis by separate affine nonrefutability.

## Finite fixed-graph application (proposed corollary)

Take Gamma_H and nondistinguished coordinates Y from the fixed-graph affine
endpoint; core inputs, H and reader old-affine forms use Y. The old base also
retains its distinguished coordinates, fixed throughout. For M>=1 readers put
M_ref=4M, s=|E|-m, A0=2 d_graph Delta_graph,
k=ceil(sqrt(s ln(16(M_ref+1))/A0)), R=(4A0+1)k and T0=R.
Assume the exact FG-pairs conditions: k<=s/(4(A0+1)), k<=m-L_graph,
z=8*Euler*d_graph^2*Delta_graph*k/(delta_graph*s),
xi=Euler*m*z^(delta_graph/4)<=1/4. Require
B_final=k+(T0+e+v)B+delta <= delta_graph L_graph/(4d_graph), with that
separation ceiling at least d_graph. Then no degree-B refutation exists.

Proof. Use the fixed-graph affine construction on ONE inventory of all 4M
references. Its separated matching space has dimension at least
(1/2)exp(-2A0 k^2/s) binom(s,k). Each proper reference span of rank above R
has flat-restriction image <=exp(-4A0 k^2/s)binom(s,k); the sum is smaller
than that dimension. Choose a nonzero f in the joint kernel. For high ranks,
Boolean affine-ideal membership expresses f by indexed inputs with cofactors
of degree <=k-1. Put these in row one: the product is 1+f modulo Booleanity,
so companions vanish where f=1. Low ranks use exact basis-prefix maps of
degree <=R; unit and zero tuples use constants. All later rows are zero.
Thus the construction supplies actual common-support maps, not separate
nonrefutability results. Fixed-graph separation keeps f outside the old PC
space through the stated ceiling, contradicting the lemma's derivation. QED.

On the recorded robust family with linear s,L_graph,m, fixed d_graph and
delta_graph>8, and polylog Delta_graph, polynomial M gives k,T0 of order at
most sqrt(n)polylog n. For B,e,v,delta polylog n, B_final=o(n) and FG-pairs
holds eventually as in the fixed-graph theorem. This covers polynomial-in-n
terminal mixed-reader inventory above one arbitrary old-polynomial core with
polylog product degree. It does not cover polynomially many independent cores,
unrestricted nested readers, or the growing-family encoding-length inventory
regime. Goal progress remains unchanged.
