# Selected paired rows retain arbitrary residual errors

Correctness draft. Goal progress unchanged. This is the scheduled next test of
actual paired mixtures, not a new general source-exclusion theorem.

Over F2 let J_D be a Boolean degree-D pseudoideal. Let q_i be old affine
polynomials, H and r_i arbitrary old binary polynomials, and define
g_i=H q_i+r_i and g'_i=(1+H)q_i+r_i, i=1,...,m, m>=1. Take delta>=1 with
deg H+1<=delta and deg r_i<=delta; then both tuples have degree<=delta.
Let w have degree<=b, U subset V_K, and W=w q_1. Select actual input position
one in the first row of each complete block and zero every other coefficient.
The effective products are 1+g_1 and 1+g'_1. Fields vanish. Original source
product/companion ceilings are retained separately, not reset here.

Put A_i=r_i+q_i r_1. If b+K+2delta+2<=D, the two maps on U

  f -> ([W f g_i(1+g_1)], [W f g'_i(1+g'_1)])_i,
  f -> ([W f A_i])_i

have identical kernels, hence equal ranks. Both factor through the same image
[W U]. No rank deficit is inferred.

Proof. On every Boolean point, q_1 is a bit and all polynomials are binary.
If q_1=0, W=0. If q_1=1, g'_1=1+g_1, g'_i=q_i+g_i, and
g_i=q_i g_1+A_i (since H q_i cancels). Therefore the following identities
hold modulo Booleanity:

  W f g_i(1+g_1) = W f A_i(1+g_1),
  W f g'_i(1+g'_1) = W f A_i g_1,
  their sum = W f A_i.

Each difference has degree at most b+K+2delta+2. Boolean division certifies
the identities through that degree. Vanishing of both errors implies vanishing
of their sum. Conversely W f A_i has degree<=b+K+delta+2; its multiplication
by g_1 or 1+g_1 fits the displayed window, so bounded closure gives both
errors. If Wf is in J_D, multiplication by either error factor or A_i fits
the same window; thus both maps factor through [W U]. Equal kernels on U,
or on that same weighted image, give equal ranks by rank-nullity.

This residual is a proportionality defect on q_1=1, equivalently the minors
q_1 r_i+q_i r_1 after multiplying by W. The common H disappears, but an
arbitrary residual tuple remains possible.

Decisive trivial control, established before any computation: take q_1=1,
r_1=0, q_i=0 for i>1, and r_i=t_i for any old binary tuple t. Then W=w,
A_1=0, A_i=t_i, and the paired errors are exactly w f t_i(1+H) and
w f t_i H. Hence the residual map is an arbitrary original multiplication
map, with exactly its rank. Zero t gives zero rank; t_2=1 gives full rank
dim[wU]. These are not lower bounds against optimizing other rows.

The embedding respects the source grammar whenever the t_i already are
affine combinations of genuine, coherently interpreted bottom products and
old forms: add one rank-one bottom whose exact value is an old bit H=x;
the parents have tuples (P_x,t_2,...) and (1+P_x,t_2,...). One active row
normalizes the added bottom, at any original accuracy; earlier shared products
are not independently reassigned. The two-parent description duplicates the
given tuple, so it adds no hidden truth table. Its original accuracy-dependent
ceilings still need to fit the supplied full replay. This is a control of the
selected-row mechanism, not an assertion that every small Frege proof contains
these parents or that arbitrary t is automatically affordable in its encoding.

Independent remainders do not supply a cancellation: for g=Hq+r and
g'=(1+H)q+s, the two companion identities above cannot identify the same A
unless the difference r+s is separately controlled. The common-remainder
subclass already carries arbitrary t, so no generic easier remainder is obtained
by allowing two independent ones.

Nonvacuity: on old bits x,z with the proper truncated Boolean ideal J_6,
w=1, b=K=0, U=span(1), m=2, H=x, q=(1,0), r=(0,z), delta=2,
the maps have rank one and all degree hypotheses hold. Extra unused bits
give unbounded variable counts. Taking r=(0,0) gives rank zero, and r=(0,1)
gives full rank. These are symbolic controls, not a new finite computation.
Degenerate cases: m=1 gives zero maps by Booleanity. q_1=0 or [WU]=0 gives
zero weighted rank, not survival. H=0 and H=1 satisfy the same identities.
Repeated inputs or unused rows do not change the fixed-row identity or its
displayed window; source arity, encoding and original accuracy costs remain
separately charged. No properness or old unsatisfiability is needed for the kernel
identity; a lower-bound application would require those separately.

Record search: paired-parent, residual, proportionality/minor, wedge/kernel
and complementary-prefix searches found cor:paired-parent-normalization,
cor:factored-batch-removal, cor:complementary-parent-target-collapse and the
stable-core/relative-image mechanisms. Full paired-parent proof read: it uses
U^T(V+MU)=ab for alternating M and a constructed surviving common target,
not this equality of actual error kernels. No general rank estimate is imported.

Assessment: the paired-remainder test produces an exact residual description,
but the unit-pivot control prevents treating that description as automatic
contraction. No source-derived small remainder or lower-bound exponent was
obtained. Do not spend further cycles sharpening this generic identity. A new
attempt needs a proved additional property of actual proof-generated inputs or
a different mechanism with a source-size-sensitive estimate.

Review assistance: after checking correctness and title/process, suggest a
concrete way to exploit proof-generated relations that this arbitrary-t control
does not satisfy, or state none found. Do not suggest another equivalent rank
or module interface without a quantitative source construction.

Additional control to avoid relying on an uncleaned unit tuple: take independent
old bits x,z, H=x, q=(1,0), r=(0,z), and incoming w=z. The parents are
(x,z) and (1+x,z), neither of whose binary spans contains one. On every paid
weighted domain [zU], multiplication by t_2=z is identity modulo Booleanity,
so selecting position one has full rank dim[zU]. Selecting position two in
both parents instead gives products 1+z and weighted companions z g_i(1+z),
which are all Boolean zeros. Thus the fixed-row full-rank control does not
obstruct optimized choices, even at the same incoming weight and without
constant-one input spans. Its identities cost no more than the displayed
window (delta=2 conservatively, b=1).
