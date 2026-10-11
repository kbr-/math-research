# General circuit equations reduce to Boolean corrections

Fixed prime p; all coefficients in F_p. Let B_j=x_j^2-x_j and F_i be
arithmetic circuits of total gate/wire size s and depth Delta. Use unbounded
fanin sum/product gates, without division or succinct power gates. Define
A=prod_i(1-F_i^(p-1)), A_i=prod_(l!=i)(1-F_l^(p-1)), and
d_i=F_i^(p-2)prod_(l<i)(1-F_l^(p-1)), with zero power one at p=2.

Proposed lemma: prime-field residual normalization. A size-S depth-d GENERAL
IPS certificate C(x,Y,Z), C(x,0,0)=0, C(x,F,B)=1, gives a circuit Q(x,Z)
linear in Z, with Q(x,0)=0 and Q(x,B)=A, of polynomial size in S+s+n+m
(fixed p) and depth O(d+Delta+1). Conversely such a Q gives a certificate
with input coefficients exactly d_i at polynomial size and depth
O(depth(Q)+Delta+1). No PC-degree, multilinearity-in-x or extension-field
preservation is claimed.

Step 1. Put G=(F,B). At each gate g of C store a_g=g(x,G), b_g=g(x,0)
and R_g(x,V), linear in V, with R_g(x,G)=a_g-b_g. Placeholder leaves use
V_l, old-variable/constant leaves zero, sum gates sum. For ordered product
children 1..t use
R_g=sum_j R_gj prod_(l<j) a_gl prod_(l>j) b_gl.
Product telescoping proves the invariant. At the output R(x,G)=1 since
C(x,0,0)=0 formally. The multipliers contain no V, so R is linear in V.
Shared gate values and O(t^2) wires per gate give polynomial size and
depth O(d+Delta+1), without extracting a high homogeneous component.

Step 2. Construct K_F(x,Z), linear in Z, evaluating to F^p-F at Z=B.
Constants in F_p give zero; x_j gives Z_j sum_(a=0)^(p-2) x_j^a.
Sum gates add the certificates (Frobenius). At an ordered product gate use
sum_j K_aj prod_(l<j) a_l^p prod_(l>j) a_l.
This specializes to prod a_l^p-prod a_l by telescoping. Shared actual child
values give polynomial size and depth O(Delta+1). K_F(x,0)=0. Extension
constants are excluded because c^p-c need not vanish there.

Step 3. Put Q(x,Z)=R(x,(-A_i K_Fi(x,Z))_i,(A Z_j)_j).
The replacements specialize to A F_i and A B_j, since
-A_i(F_i^p-F_i)=A F_i. Hence by linearity Q(x,B)=A R(x,F,B)=A.
All inserted circuits have polynomial size/depth O(Delta+1), so the claimed
bound follows. Q is linear in Z and Q(x,0)=0.
Conversely sum_i d_iF_i=1-A literally; sum_i d_iY_i+Q(x,Z) is the full
certificate. This is an equivalence, not a claim that Q is easy.

Nonvacuity: p=2,F1=x,F2=1+x gives A=B_x and Q=Z_x; the original
certificate is Y1+Y2. Unused variables and duplicated equations give
unbounded counts. Empty equations give A=1 and no certificate; a unit input
gives A=0, and zero inputs are harmless. No unsatisfiability premise is
needed for the transformation: existence of either certificate implies it.

Comparison: lem:clause-coefficient-normalization already proves the literal
CNF Hilbert-like case over any field, with sharper additive constant depth.
This statement changes both inputs and the certificate premise, but uses its
same scaling argument after gate linearization. It does not subsume that
all-field result. Frobenius gate certificates are also the mechanism in the
published algebraic-to-CNF transfer. No independent novelty or lower bound
is claimed. Functional coefficients d_i are cheap; full Boolean-correction
complexity remains. General IPS origin imposes no extra restriction on a
candidate linear Q at this polynomial-size/constant-depth granularity,
because the converse supplies an IPS certificate for every such Q.

Goal unchanged. The paper's multilinear/ROABP lower bounds do not supply
general binary IPS hardness; its author-PDF Theorem28 requires p>=5.
Read source: Theorem64 and full proof, Corollary65, Section3.2 and relevant
statements in Sections1.4/1.5. No full new audit of its lower-bound proofs.
Open point for reviewer: can the exact residual formulation support a
certificate-sensitive test that avoids imposing a harder canonical component
extraction? The current argument gives no hard family or new lower exponent.
