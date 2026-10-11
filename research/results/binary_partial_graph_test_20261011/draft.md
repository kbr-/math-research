# Partial local graphs

Task: intrinsic-shadow lead, child entry-2026-10-11-graph-image-test:s1,
binary-frege-lower-bound/general-step. Execute mixed count and complete
replay for omitted outside indicators, not another sample of the full graph.
Previous goal turn produced reviewed records/checkpoint (progress in
authoritative state), but no new Frege lower-bound exponent.

Theorem thm:partial-graph-source-exclusion.
Keep the full setup of thm:local-graph-source-exclusion, except block a exposes
x_e+F_(a,e)(core) only on a set E_a disjoint from core S_a.
Let s_a=|S_a|, t_a=|E_a|, r_a=m-s_a-t_a. Omitted pairs remain free.
Set
 L_a(k)=3^s_a sum_(i+j<=k) 2^i binom(r_a,i) binom(t_a,j).
If sum_a L_a(k)<H=dim[wU] and b+k+(k+s)B<=D, s=max s_a,
the same conclusion holds with maps of degree<=T=k+s:
one common surviving wQ kills every fresh companion/field and excludes
degree-B PC/NS refutations. All original accuracies/input degrees retained.

Proof: at a fixed core cell, an exposed pair leaves at most one free bit,
while each omitted pair retains its full three-state degree polynomial
1+2z. The conditional graph restriction image is at most the cumulative
coefficient count of (1+2z)^r (1+z)^t. Multiply by3^s for core cells.
A complement to the weighted kernel in U gives one common Q exactly as
before. In the local projection set exposed x_e->c_e,
y_e->(1+c_e)y_e, and leave omitted pairs unchanged. It preserves the local
domain and maps onto the graph. Monomial telescoping changes only exposed
variables: coefficients gamma have degree<=k, local error degree<=k+1.
Core-cell interpolation adds s_a, so beta degree<=k+s_a. On local points
H_a=sum beta_e g_e=Q. Use its first row, zero all others and extra columns.
Weighted companions are local-zero through b+k+T e_ai, fields through
b+k+2T; local reduction and original-degree replay fit b+k+TB.
Nothing requires deleting or conditioning the omitted pairs. The case
r=0 is the exact preceding finite theorem.

Count bound:
If every t_a>=q>=1, define mu=2-q/m in[1,2).
Represent the conditional count as elementary symmetric polynomials in
m nonnegative weights: s zeros, r twos, t ones. Their average is
(2r+t)/m=2-(t+2s)/m<=mu.
For each degree j, e_j(weights)<=binom(m,j)*mu^j.
Proof by pair averaging: e_j=A+(u+v)B+uv C with C>=0; replacing u,v by
their average increases the last product, preserving their sum.
Repeated averaging converges to equal weights, and continuity proves the
bound. For k<=m/3, the terms mu^j binom(m,j) decrease backwards at ratios
<=k/(mu*(m-k+1))<=1/2. Thus
 sum_a L_a(k)<=2 M3^s mu^k binom(m,k).
This is a positive integer counting argument, not arithmetic over F2.

Corollary cor:sublinear-exposure-source-exclusion.
Use the same fixed bounded-degree charged family with epsilon>2,
nonzero total ternary charge, proper D=Theta(m).
Fix constants 0<c0<1, 0<beta<=1, 0<=alpha<beta-2/epsilon,
A,c. Let M<=m^A, s_a<=m^alpha, t_a>=c0*m^beta, and original B<=log^c m.
Then the complete source has no degree-B PC or NS refutation for large m.
The family is independent of A,c. The old charged graph family is not changed.
Take q=min_a t_a, s=max s_a, and
 k=ceil((2m/q)*ln(8 M3^s)), T=k+s.
Then k=O(m^(1-beta+alpha) log m), k=o(m), T=O(k+s)=o(m/polylog m)
for any fixed requested logarithmic power, so k+TB=o(m)<D.
The extra log is a harmless upper bound including alpha=0.
The old collision expression eta=(1+2*(2sqrt(k/m))^epsilon)^n-1=o(1)
because 1-(beta-alpha)*epsilon/2<0. Hence
 H>=2^(k-1)binom(m,k).
The displayed numerator divided by this bound is at most
 4M3^s (1-q/(2m))^k <=4M3^s exp(-qk/(2m))<=1/2.
This proves the finite criterion. beta=1 with c0=1/2 recovers the preceding
small-core asymptotic class for all sufficiently large m; the theorem is
stronger because beta<1 allows a sublinear exposed set.

Parameter witness: use an available fixed graph family with expansion8,
choose beta=1/2,alpha=1/8,c0=1/2. The core has <=m^(1/8) edges and
only >=(1/2)m^(1/2) exposed indicators are needed; k=O(m^(5/8)log m),
k+TB=o(m), and eta=o(1). Fixed-degree graph existence is already recorded:
for example the stated fixed-degree spectral existence with degree128
gives expansion well above8 by (128-(2sqrt127+1))/2>8.
No new graph-existence claim or quantitative progress probability.

Comparison with old obstruction:
Our L_a(k)>= [z^<=k](1+2z)^(m-t_a)(1+z)^t_a, since replacing the core
factor (1+2z)^s by its total coefficient sum3^s can only increase the
cumulative count. This is precisely the old affine pivot profile with
t_a single pivots. Under the recorded fixed-expansion budget, including
k+t_a<=D, prop:affine-collision-budget says its certified normalized
upper bound is >=1-o(1) uniformly in k if t_a=o(m^(2/epsilon)).
Our numerator is no smaller and the collision denominator no better.
Thus the displayed counts plus the published expansion-only denominator
cannot certify a summed deficit even for two such low-exposure blocks.
In our polylog-B regime k<=D/B<=D/2 and t_a=o(m), so that extra window
holds eventually. This concerns the estimate, not actual ranks, maps,
all choices or all Frege sources. At zero exposure the graph is the whole
local domain; no surviving Q can vanish there. A zero-input block itself
can still be removed trivially, so this is a limitation of the graph target,
not a proof-system obstruction.

Nonvacuity / finite verification planned:
m=4,s=2,t=1,r=1,k=3,w=1, local-only proper J_D.
H=B4(3)=65; L=9*(1+3+2)=54<H; T=5, delta2,h1,B5,D28.
Core edges1,2; expose only edge3 with g=x3+x1*x2; leave edge4 untouched.
Q=local-reduce(x2*g*y4), degree3, nonzero at core edge1 empty,
edge2 x2=1,edge3 x3=1,edge4 y4=1. It vanishes on the graph.
Check all9 core cells and their9 distinct outside normal monomials
(81 basis checks total), all81 local states, coefficients/fields/extra
companions, degree ceiling, mixed count, and the all-omitted three-state
identity. Negative controls: dropping the partner guard, dropping the
core selectors, and treating an omitted pair as a single free bit.
No larger-size sweep: the exponent statement is proved analytically.

Degeneracies: r=0 returns the old theorem. t=0 makes the target graph full
and defeats this criterion, not arbitrary removal. Empty core, constants
and repeated inputs remain legal. The theorem excludes k=0; zero H fails
the strict inequality. Additional inputs are zero-coefficient positions
but all their companions stay. B covers original generators, not their
smaller specialized images. Multiple blocks/cores may differ.

Goal unchanged, bearing some only for the specified source class.
The next issue should be replacing the coordinate-exposure hypothesis
by genuine affine mixtures, not sharpening constants below the known
exposure threshold. Audit the exact affine-flat removal proof and
coefficient interpolation before proposing a new interface.

Completed exact check 942216376c: 464 checks, nine core cells, 81 outside
basis checks, all81 local points, actual graph51 versus mixed bound54,
old local degree-three domain65, three negative controls, zero failures.
Full output and the constructed Q,beta are in check.txt. No parameter sweep.

