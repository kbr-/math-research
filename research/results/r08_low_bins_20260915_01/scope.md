# R08 no-retained-core low-rank packing

Assigned remaining targets R08 then R16. R07 complete. R08 target is the exact
paper §5 low-rank construction, not the stronger retained-core optimality claim.

Use any finite family g of degree<=1 ordinary F2 polynomials in finitely many
retained variables. Given a spanning family F_j of size r with mutual constant
span representations and r<=h(k+1), pack the r indices into h bins of capacity
k+1 using a finite embedding into Fin h × Fin(k+1). Ordered factor telescoping
gives explicit coefficient polynomials of degree<=k, and the canonical fresh
ENS product specializes exactly to Z=product_j(1-F_j). Evaluation makes Z the
common-zero indicator; g_i Z is zero on the binary cube and has degree<=r+1,
so checked Boolean reduction supplies ordinary NS witnesses through r+1.

Then recover the stated rank-only interface by choosing a finite basis of the
input span. No independence is needed in the intermediate spanning-family
construction, and no properness is needed for its Boolean identity. Empty bins,
r=0, h=0 with r=0, k=0, and zero inputs must be handled. The full route later
uses k>=1 and h>=1 in the weighted-removal ledger.

Separate useful polynomial telescoping/bin construction from its final
rank-only application only if a concrete proof/interface benefit emerges.
All claims remain project supporting adaptations, not novelty assertions.
