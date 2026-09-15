# Final R15 assembly

Continue original full R15 after checked coordinate/ordinary-ideal/numerical
release. No repeat of unchanged proof checks. Required endpoint: actual bit
variables Fin m × Fin ell, nonzero f in rowLinearSpace, literal coefficient
witnesses degree<=k-1 for every proper high-rank input span.

Use arbitrary finite affine-map families with finite input tuples. Their
polynomial images match R16/R18. First construct BlockRestrictionData for each
proper input span: polynomial-span rank, selected-coordinate embedding, actual
affine coordinates, zero-flat equivalence and literal original-tuple witnesses.
Prove map/polynomial span rank and unit-membership equivalence explicitly.

Then restrict the row-linear space at all proper high blocks, form the product
of their finite-dimensional image spaces, and use the concrete quarter bound
to contradict injectivity. If no proper high blocks exist, choose constantone;
if some exist, their coordinate embedding proves r*<=m*ell so the numeric
estimate applies. M need only bound the number of proper high blocks, and may
be a larger inventory bound. Expose k²>=m log(4M) core and originalceil wrapper.
Return unit-span OR literal witness at arbitrary high blocks to match the
verified R16 extension; this recovers the exact literal statement for proper
families and handles tautological clauses without changing inventory.

All module-level declarations/instances have unique qualified names. Parent
owns route/living sections. This cycle is incomplete until the actual final
kernel theorem and its full square-root/log application are verified.
