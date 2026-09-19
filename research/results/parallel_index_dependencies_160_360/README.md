# Parallel relationship inventory: canonical positions 160–259

The coordinator assigned positions [160,360), then reassigned [260,360) to another
worker. This worker's completed range is **[160,260)**: 100 claims.

`patch_160_260.json` is the cumulative integration proposal: 100 reviewed
relationship inventories and 202 typed, scoped edges. Earlier patch files are
superseded snapshots, retained to document incremental delivery. The script
`build_patch.py` reconstructs the proposed edges and dispositions from the current
registry's unchanged original claim fields; the final patch additionally records
exact notebook evidence hashes. The coordinator must check these hashes and
original fields before integration and create the canonical review fingerprints.
No canonical registry, notebook, plan, Git state or living section was edited by
this worker.

## Method and scope

Started with the saved equation-inclusive dependency candidates at
`research/results/index_dependency_review_20260919/candidates.json`, then read
focused owning sections to resolve proof role and intra-entry references missing
from hyperlinks. No full notebook import, new proof, numerical suite, Lean build,
or fresh paper audit was performed. Named comparison links remain `cites`;
applications and refinements remain separate from direct prerequisites. Imported
Razborov and historical duality endpoints reuse the already audited sources.

Examples of resolved ambiguities:

- Shared MOD-value section separates the scalar relation, recursion compiler and
  aggregate presentation compiler. Aggregate conclusions are not prerequisites
  of their component proofs.
- Sharp Booleanity sharing a section with interface recurrence is a separate
  argument. Its adjacent compiler links do not become its dependencies.
- Column-state finite evidence explicitly does not numerically test universal
  grouping or row-coordinate proofs; the patch scopes its links accordingly.
- The occupancy degree theorem and following one-row corollary share an explicit
  positive coefficient-map subargument. The aggregate theorem cites that shared
  subargument; the corollary depends only on the theorem's independently supplied
  negative moment-design argument. This avoids implying circular theorem use.
- Generic sampling, matching, completed-row and trimming lemmas have local proofs;
  their subsequent layout applications are not prerequisites of the generic lemma.

The patch declares closure at the indexed-claim granularity, retaining supplied
hypotheses and elementary local arguments. It does not enumerate every algebraic
identity or library fact as a graph node, or take transitive closure. Source
classification/formalization/significance fields are untouched.

## Suggested research-record paragraph

A parallel source-role review completed relationship inventories for 100 existing
claims covering virtual source interfaces, affine/column normalizers, occupancy
and partition projections, and deterministic exception trimming. The proposal
contains 202 scoped relationships, with citations, applications and refinements
kept distinct from proof prerequisites. Focused source passages resolved shared
anchors and implicit intra-entry ingredients. Existing mathematical statements and
proofs are unchanged; this is metadata curation, not new mathematics or fresh
formal verification. Full migration closure still requires the remaining assigned
batches and coordinator validation.

## Validation and timing

The final proposal has 100 unique claim IDs and 202 unique relationship IDs; every
source evidence target was resolved and hashed. Protected source extraction and
validation outputs are archived with session `parallel_dependencies_160_360`.
The first protected extraction lacked systemd access in the sandbox and failed
closed; the same command succeeded with escalation. This is an operational failure,
not a failed mathematical test. A short initial policy read preceded instrumentation.
Parallel worker durations must not be summed as elapsed wall time.
