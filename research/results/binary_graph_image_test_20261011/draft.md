# Local graphs and small-core source exclusion

Task: intrinsic-shadow item entry-2026-10-09-realization-goal-review:1,
binary-frege-lower-bound/general-step. Execute the degree-filtered graph-image
test promised by the last cycle. Both prior developments (nonlinear-shadow,
outside-basis) and common graph targets were read fully. The fixed-basis value
criterion fails on this class; seek one common weight rather than separate
one-block repairs. Goal unchanged unless compiler coverage is obtained.

Proposed theorem thm:local-graph-source-exclusion.
Old variables are m Boolean-exclusive pairs (x_e,y_e), local ideal
I_loc=(x_e^2+x_e,y_e^2+y_e,x_e*y_e). A degree-L local-zero polynomial has a
local certificate through L, by square reduction and deleting mixed monomials.
Let J_D be a proper binary Boolean PC-closed space containing the old base
and I_loc through D, with surviving old w of degree<=b.
Take U in the span of local normal monomials of degree<=k, k>=1,
H=dim[wU]>0. Let M be the number of terminal blocks. Each block a has private coefficients,
positive original accuracy h_a, old-only actual inputs, and a core S_a of
s_a edges. For every edge outside S_a, its tuple contains
g_(a,e)=x_e+F_(a,e)(core variables); a per-block swap of x_e/y_e is allowed.
The offsets are arbitrary binary old polynomials supported on that core.
Extra old-only inputs are allowed. Let s=max s_a and T=k+s (M>=1).
Let B>=2 cover all original source axioms and the hypothetical PC proof,
including e_(a,i)=h_a(delta_a+1)+d_(a,i), delta_a actual max input degree.
If
  sum_a 3^(s_a) N_(m-s_a)(k) < H,    b+k+T B <=D,
N_t(k)=sum_(j<=min(k,t)) binom(t,j),
then there are old binary coefficient maps degree<=T and one Q in U with
[wQ]!=0 killing all mapped fresh axioms after weighting by wQ; hence no
degree-B source refutation. Maps need not have polynomial size.

Image count:
At each of the 3^s_a local core states sigma, zero graph inputs fix each
outside x_e to the bit F_e(sigma). Its partner y_e is zero when this bit is
one and is a free Boolean bit otherwise. Thus restrictions of degree<=k
local-normal polynomials to this graph, conditional on sigma, lie in the
degree<=k function space on at most m-s_a Boolean variables.
No degree blowup is charged to F here: core coordinates have been fixed for
the count, not freely substituted into a polynomial. Rank<=3^s_a N_(m-s_a)(k).
Choose a complement U0 of the weighted kernel in U. The joint restriction
map from its H dimensions has rank below H, so a nonzero Q in its kernel
survives w and vanishes on every actual local zero graph.

Coefficient maps (not an uncharged nonlinear retraction):
For a fixed a,sigma, specialize Q's core variables to sigma, giving Q_sigma,
degree<=k on outside pairs. Let c_e=F_e(sigma). Apply the linear local
projection pi_sigma: x_e ->c_e, y_e ->(1+c_e)y_e. It maps local points onto
the outside zero graph. Thus pi_sigma(Q_sigma) is local-zero.
Telescoping each normal monomial gives
 Q_sigma=sum_e gamma_(sigma,e)(x_e+c_e)+L_sigma,
 deg gamma<=k, and L_sigma local-zero with certificate through k+1.
Indeed x_e-c_e is the input; when c_e=1, y_e changes to zero, and
 y_e=(x_e+1)y_e+x_e*y_e. The cofactor then has degree at most k; the extra
local term costs at most k+1. When c_e=0, y_e is unchanged.
Let chi_sigma be the product of the core's one-hot state indicators
(1+x+y), x or y, degree<=s_a. Define beta_(a,e)=sum_sigma chi_sigma gamma_sigma,e,
put those on the first coefficient row, set all extra-input and later-row
coefficients to zero. Degree beta<=k+s_a<=T.
At every old local point precisely one selector is one. Therefore
 H_a=sum_e beta_(a,e)g_(a,e)=Q as a local function. All points where Q=1
have P_a=1+H_a=0, and points where Q=0 have weight wQ=0. Consequently all
wQ times mapped companions vanish on the local domain, including extra
inputs. Their actual degree is <=b+k+T e_(a,i), because this is a genuine
global variable substitution retaining original source degrees.
Mapped fields likewise vanish, cost<=b+k+2T. Old axioms are fixed and
weighted; local-zero reduction certifies every image inside J_D.
Replay original PC lines as wQ Phi(v), paying b+k+TB, including actual-degree
resets and raw coefficient cofactors. The final unit would kill wQ.
This proves the theorem; the old input coefficient maps are coherent globally.
The core assignment maps have no asserted small size (3^s terms are allowed).

Comparison to prior tools:
cor:graph-input-common-target counts the whole remaining Boolean function
space, 2^(m+s) in the one-indicator-per-outside-edge setting. It does not
discard partner variables. The local graph count keeps them, at filtered
dimension N rather than full truth-table dimension.
thm:costed-domain-offset-compression already supplies local-domain reduction
and cell interpolation from common reference maps. We reuse those mechanisms,
not claim they are new. Here the common target is constructed on the actual
core graphs, and degree k+s is paid directly; no hash of nonlinear offsets or
general recursive compression ledger is needed. Do not claim qualitative
small-core interpolation was absent or generic dominance over that theorem.
lem:local-feature-batching instead compares named-feature images with the
same weighted domain and retains its contraction conditions; it does not
automatically supply the present graph relation.

Proposed corollary cor:small-core-graph-exclusion.
Use the recorded binary charged quotient on any fixed bounded-degree graph
family with expansion epsilon>2 and nonzero total ternary charge, with
proper old cutoff D=Theta(m) in max(4,2Delta)<=D<epsilon*n/8.
Fix 0<alpha<1-2/epsilon and constants A,c. M<=m^A terminal blocks of
the theorem with s_a<=m^alpha and original B<=log^c m admit no degree-B
refutation for large m. B covers all original generator degrees; no unused
large-axiom artifact. Same graph family works for all A,c.
Take w=1, U=all local normal polynomials degree<=k,
 k=ceil(log2(8 M 3^s)), s=max s_a, T=k+s.
Then k=O(m^alpha+log m), T=O(m^alpha+log m), so k+TB=o(m)<D.
By lem:cut-collision-bound and lem:binary-charged-descent,
 H=h(k)>=B_m(k)/(1+2 eta), B_m(k)=sum_(j<=k)2^j binom(m,j),
 eta=(1+2*(2sqrt(k/m))^epsilon)^n-1=o(1):
 n=Theta(m) and 1-(1-alpha)epsilon/2<0.
Thus H>=2^(k-1)binom(m,k) eventually.
For k<=m/3, N_(m-s_a)(k)<=N_m(k)<=2binom(m,k), since descending binomial
ratios are <=k/(m-k+1)<=1/2. The summed numerator is <=2M3^s binom(m,k)
<=2^(k-2)binom(m,k)<H. This proves the finite criterion.
Fixed-degree high-expansion graph existence is already recorded in
cor:charged-block-exclusion via Friedman's stated theorem and the elementary
spectral expansion inequality; no new graph construction is asserted.
The result handles the independent-outside graph class, including nonlinear
offsets on polynomially many edges. It does not turn arbitrary source tuples
into that class, or establish a fixed-depth Frege lower bound.

Nonvacuity:
m=4, local-only proper J_D, w=1,k=1,s=0,M=1, all g_e=x_e gives H=9,
numerator N4(1)=5, T=1,B=3,D=4. This is a satisfiable old-base control.
For a genuine nonlinear finite test use m=4,s=2,k=4,M=2:
block1 F3=x1*x2,F4=y1+y2+x1*y2; block2 uses their complements.
Q=(x3+F3)*(x4+1+F4), degree4, is zero on both graphs and is one at
core zero,x3=1,x4=0,partners zero. H=81, summed upper bound72.
Original accuracy one gives delta2,B=5,T=6,D=34; local-only old base
still proper. Accuracy3 can be checked with original B=11, not reset.
Unbounded hard instances are the stated charged graph family; constant/degree2
offsets on two core edges give explicit nonvacuous source instances for every
large m. No proof of compiler coverage is claimed.

Degeneracies:
With no blocks use old hardness; no interpolation is needed.
If s_a=m, its graph is the full local domain and the strict criterion cannot
hold (3^m>=H). k=0 is excluded; constants cannot vanish on nonempty graphs.
Constant offsets, repeated inputs and empty core are covered. Extra inputs
are zero-coefficient columns but all their companions remain checked.
The point-set arguments use only the local domain, never satisfying points
of the inconsistent charged old system.

Next action for this cycle: exact local interpolation check at the nonlinear
fixture (all81 local states, 9 core branches per block), all local-normal
monomials for the projection rule, degree bounds, weighted companions and
fields. Negative controls drop the partner guard and drop core selectors.
Finite evidence supplements the all-parameter argument; no scaling run.

Completed verification: accepted protected Singular run 920c7accf6, check.txt,
1331 checks, 18 core cells, 162 distinct outside basis checks (nine per cell
span every specialized local-normal monomial, avoiding duplicate work), all
81 local points, graph cardinalities 28 and13, two negative controls, zero
failures. Explicit common Q and all nonzero coefficient maps are printed.
The first run 5c741c70a5 was rejected for out-of-range dynamic ideal reads and
unsupported indexed increment syntax. Fixed-size matrices and explicit
indexed assignments repaired the checker; failed-containers.txt retains it.

Comparison precision: the older offset-compression proof's one-level degree
recurrence is additive before its stated coarse bound. With core-cell selectors
it already suggests degree T0+s rather than a product of costs. The present
proof deliberately reuses that mechanism; no claim that interpolation on
small cores was absent, nor a generic speedup, is made. The contribution is the
actual local graph rank, common-target construction and complete hard-quotient
composition at these stated parameters.

