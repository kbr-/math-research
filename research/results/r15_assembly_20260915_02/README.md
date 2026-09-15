# Complete R15 assembly

The full common ordinary affine-restriction kernel is verified. Full statements
and human-readable proofs: notebook entry
`entry-2026-09-15-lean-common-affine-kernel`.

| Claim | Module | Final report |
| --- | --- | --- |
| lem:proper-affine-block-restriction | claims/AffineBlockRestriction.lean | block-restriction-verification.txt |
| lem:common-affine-restriction-kernel | claims/CommonAffineRestrictionKernel.lean | kernel-verification-complete.txt |

Eight declarations pass with standard foundations only. Exact types and
transitive axiom reports are in these files. `kernel-verification.txt` is an
older successful three-declaration report; `kernel-verification-final.txt`
records a failed subtype-injection elaboration for the added inventory bridge.
The explicitly named complete report verifies all four current declarations.
No mathematical premise changed in that fix.

## Interface and original scope

`AffineInputMap`, `affineInputRank` and `BlockRestrictionData` use arbitrary
finite affine input tuples on the actual bit variable type. Polynomial span
rank and affine-map rank coincide; unit membership coincides as well. Proper
spans have rank-sized coordinate embeddings, exact common-zero-flat data and
literal original-tuple coefficients through degree k-1 from ordinary zero
restriction. `affineInputRank_le` supplies the ambient-rank bound.

`common_affine_kernel_of_square` accepts positive m, ell, M, positive k<=m,
k²>=m log(4M), and a bound M on proper high blocks. It produces nonzero f in
rowLinearSpace and the unit-span OR literal degree-(k-1) witness for every
rank>3ell(k+1) block. `common_affine_restriction_kernel` supplies the original
k=ceil(sqrt(m log(4M))) choice. `common_affine_kernel_inventory` accepts a bound
on the entire family. `proper_high_count_le_proper_count` recovers the source
proper-block inventory premise. The result matches affine_family_removal_with_units.

The empty high family is handled by the same noninjective joint-map argument
with zero-dimensional target. The concrete binomial estimate is used only if
a proper high block exists and hence r*<=m*ell. No abstract dimension hypothesis,
pointwise-zero substitution, custom axiom or sorry is used. R15 is complete;
publication assembly remains the coordinator's separate assignment.

## Reproduction

From repository root, using the pinned environment and new report paths:

```bash
./formalization/verify.sh --target claims/AffineBlockRestriction.lean --out /tmp/block-restriction.txt
./formalization/verify.sh --target claims/CommonAffineRestrictionKernel.lean --out /tmp/common-kernel.txt
```

Recorded runs use `--session r15_assembly_20260915_02` with the report paths above.
Checks were incremental under the shared computation limits. All retries and
complete outputs are retained in the archived session. Failures involved
Lean API/elaboration and finite-index transport, not falsified mathematical
claims. The earlier scope map is preserved; its suggested constant choice in
the empty-family case was replaced by the uniform joint-map argument described
in the notebook. No optional broad audits or additional dependencies were used.

`provenance.json` hashes the two sources, scope map and final reports. Timing
and complete outputs are archived under
`research/provenance/session-records/r15_assembly_20260915_02/`.
The coordinator owns living sections and route updates. No new discrepancy or
general framework rule was needed. Final commit work follows the timing snapshot.
