# R10 complete: prescribed moment extension and old filtration

Full indexed target audit:matching-extension-arbitrary-row-count is verified, with the redundant m≥B hypothesis removed. Final hypotheses are arbitrary natural m,B,k, N≥1, N≥2B−1, k≤B. The actual bounded-degree functional extends preserving every low value; NS filtration intersection, ordinary PC=NS, normalized existence/span and nonrefutation all follow. Full MathJax proof: entry-2026-09-15-lean-matching-extension-filtration.

## Verified files and interfaces

Namespace MathResearch.PolynomialCalculus throughout, with H's Augmented coefficient/boundary types reused.

- MatchingMomentCycles.lean: momentLayer, matching_moment_cycle for s≥1, and matching_moment_filling using the proved H12 chessboard_homological_bound and stable-range arithmetic. s=1 is the augmented empty-face cycle and nonempty-board filling; s=2 includes augmentation. For s≥2 every codimension-two matching misses exactly two rows, so its boundary coefficient is z+z=0. No abstract filling assumption is used.
- MatchingMomentRelabeling.lean: injective rowEmbedding preserves matchings, unused rows/columns and all marginal sums. rowSetEmbedding enumerates exactly a retained row set, and its product embedding exhausts RowsWithin. Every transported chain map is the existing checked H03 push, not merely a face-cardinality correspondence.
- MatchingMomentExtension.lean: rowset_moment_filling returns a globally supported filling restricted to its exact rows and matching prescribed lower boundary coefficients. matching_moments_step updates each top matching from its unique row set. matching_moments_extend preserves all old finite-set coordinates of cardinality≤k; matching_annihilator_extension and bounded_matching_annihilator_extension turn this into actual ambient/bounded functional extension, using R09/R04. matching_normalized_annihilator preserves constant1. Pure array extension also permits N=0 when B=0, but final ordinary-system statements require N≥1.
- MatchingFiltration.lean: functionalUnary_ns_stable and functionalUnary_ns_filtration give actual-degree stability. Derives.functionalUnary_ns proves primitive PC closure, including zero predecessors; functionalUnary_pc_eq_ns gives equality. No-NS/PC-refutation, normalized bounded designs, and normalized-span equality cover the original audit's remaining statements.

## Generalization and boundaries

There is no m≥B assumption in the construction: every size-s matching has exactly s rows, and for s>m both top matchings and their row-set selector type are empty. A required top marginal with an additional unused row would itself produce a size-s row set, so it cannot create an omitted case. This is a useful generalization of the source, not a correction. The N≥1 hypothesis remains explicit because an empty-column row equation is−1 of degree0. No augmented ENS stability is asserted.

All new dependency claims are indexed with full proofs in the R10 entry: lem:matching-marginal-cycle, lem:matching-moment-row-relabeling, lem:prescribed-matching-moment-extension. Their statements are project formulations/application interfaces; source topology attribution is preserved and no novelty claim is made.

## Verification and retained evidence

Four targeted incremental audits print exact declaration types and all transitive axioms: cycle-verification.txt (9), relabeling-verification.txt (7), extension-verification.txt (12), filtration-verification.txt (10, including imported complete extension declarations). Only standard propext,Classical.choice,Quot.sound are allowed. Full command outputs and timing are canonically archived; imports are pinned and no dependency version was changed.

Proof retries concerned finite-index/elaboration details, classical-if comparison, variable-domain annotations and metadata/scope closings. One unchanged failing dependency was inadvertently retried once while advancing its consumer; its complete failed output is retained, with no mathematical failure inferred. No source discrepancy was found. Some initial R10 design during the clean integration wait preceded instrumentation. Parent owns all living notebook/route changes; this worker updated only appended records, new claim links and formalization files. No pushes or main edits.

R14 cube/residual separation remains assigned next and is not implied by this checkpoint. The post-all-Rxx generalization sweep has not begun.
