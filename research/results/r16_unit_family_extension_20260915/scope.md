# Required R16 generalization: unit-span high blocks

A concrete R24 registry may contain tautological affine clauses. R15 provides
literal degree(k−1) witnesses only for proper high blocks. Extend the R16 high
condition to: polynomial1 is in the block's constant span OR the existing
literal target witness. Keep the old theorem as a wrapper via the second arm.
No DAG tautology elimination or global pruning/inventory transform is needed.

For a unit-span block choose constants c withΣc_i g_i=1, assign them to one
coefficient row and zero to all other rows. The block value becomes0, hence
all weighted companion images vanish. Coefficient degrees are0 and the existing
Boolean-image proof applies unchanged. Low-block packing, proper high-block
specialization, old-axiom images, and primitive weighted replay are unchanged.
The stronger unit-or-literal theorem lives in its own per-claim file; existing
imports retain the original API through the compatibility wrapper.
Preliminary source reading and coordination preceded instrumentation.
