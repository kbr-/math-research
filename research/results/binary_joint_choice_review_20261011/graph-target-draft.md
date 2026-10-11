# Common targets for graph inputs — draft for the same reviewer's second stage

This is a restricted construction, not an advance of the unrestricted Frege
lower bound. It tests whether the all-basis value-diversity obstruction also
obstructs joint polynomial coefficient choices. It does not.

Work over F2 with a proper Boolean degree-D PC-closed space J_D. Let w have
degree at most b and survive modulo J_D. Let U be a space of multilinear
polynomials of degree at most k, k>=1, and let H=dim[wU]. For each of M terminal
blocks, partition the old variables into y_a and z_a, with |z_a|=s_a, and suppose
its actual input tuple contains every y_(a,i)+F_(a,i)(z_a). Write delta_a>=1
for that block's actual maximum input degree and delta=max_a delta_a.
Thus every F_(a,i) has degree at most delta_a. Other inputs are allowed. The partition
and F may differ between blocks. Inputs are old-only. All coefficient variables
are private, all accuracies are positive, and all original companions and fields
are retained. Let B be an original PC refutation ceiling, with B>=2delta+1;
the usual original product/companion costs still apply individually.

If sum_a 2^s_a < H and b+k+T B<=D, where T=max(1,delta(k-1)), there is one
Q in U with [wQ]!=0 and old coefficient maps of degree at most T for all
blocks, making every weighted companion and field image vanish modulo J_D.
Thus no degree-B PC refutation of the old base plus these blocks exists.

Proof. Choose a linear complement U0 of ker(f -> [wf]) in U. It has dimension
H. Map U0 to the direct sum of Boolean function spaces on the z_a cubes by
Q -> (Q(F_a(z_a),z_a))_a. The target dimension is at most sum_a 2^s_a. A
nonzero kernel vector Q exists and [wQ]!=0. This step uses the full actual
zero graph for each block, not a quotient pretending that J_D has points.

For a multilinear monomial of Q of degree t<=k, replace its y factors one
at a time by F. The telescoping difference is a sum of y_i+F_i times products
of at most t-1 factors, each of degree at most delta_a. Consequently

    Q = sum_i beta_(a,i)(y_i+F_(a,i)) + R_a(z_a),

literally, with deg beta<=delta_a(k-1) and deg R_a<=delta_a k.
The function R_a is zero on its Boolean cube. Boolean division expresses it
in the Boolean ideal without exceeding degree delta_a k: successive division
by z_i^2+z_i never increases degree and leaves the unique multilinear
representative, which is zero on the entire cube and therefore identically zero.
This is an explicit
certificate, not only radical membership.

Use beta in the first coefficient row at the indicated input positions and
zero at every other position and row. Write H_a=sum beta_i g_i=Q+R_a.
Then P_a maps to 1+H_a. For every input g_j, including extra inputs,

    w Q g_j(1+H_a) = w g_j(Q+Q^2) + w Q g_j R_a.

These are Boolean-ideal certificates through, respectively, b+d_j+2k and
b+k+d_j+delta_a k. The field images have certificates through b+k+2T.
Each fits b+k+T e_j for the original companion ceiling
e_j=h_a(delta_a+1)+d_j, and through b+k+2T for fields:
T(delta_a+1)>=max(k,delta_a k) for k>=2; for k=1, T=1 and
delta_a+1>=delta_a k. The old generators are simply weighted by wQ.

Replay the original PC proof with the one fixed substitution and weight wQ.
Every variable image has degree at most T, every axiom is paid at its original
degree, and each nonzero multiplication predecessor has original degree at
most B-1. Every replayed line fits b+k+TB. A refutation would put wQ in J_D,
contradicting its selection. No substitution makes the inconsistent old base
globally satisfiable; only bounded-degree membership is used.

Degenerate cases. If M=0, choose any surviving vector and use old hardness.
A block with no y variables has s_a equal to the total number of variables;
the strict dimension premise cannot hold. If some F is constant, delta remains
at least one and the telescoping bound remains valid. k=0 is excluded: every
zero graph is nonempty and a nonzero constant cannot vanish there. Empty U or
H=0 fails the strict premise. Extra zero inputs need no nonzero certificate.
Coincident graphs and redundant input positions cause no problem; place the
chosen coefficient at any one indicated occurrence.

Comparison. The common-target/weighted-replay principle is already present in
lem:full-base-relative-learning and lem:affine-product-learning. The additional
ingredient here is construction of the target and cofactors on different
nonlinear coordinate graphs. thm:costed-domain-offset-compression already
supports different offset features if a common reference normalizer is supplied.
No claim of general dominance or independent literature novelty is intended.

Open point for reviewer assistance: can the graph requirement be replaced by
an applicable structural property of actual mixed inputs L+A P, without just
assuming small zero-set images or bounded certificates? The input P consists
of shared genuine earlier products, not free formal coordinates. Complete
source-wide compatibility and the paid degree ledger must remain explicit.
