# H04–H07 handoff

All assigned H04–H07 claims are verified, indexed, and recorded separately.
No new mathematical gaps were found. The final H07 audit verifies 15 proof files
and one statement-only file, with 90 declarations and only propext,
Classical.choice, Quot.sound. H remains statement-only until parent H12–H13.

## Interfaces

Namespace `MathResearch.ThirdParty.Augmented`:

- `claims/AugmentedCone.lean`: `IsCone K v := ∀s∈K.faces,insert v s∈K.faces`;
  `ExactAt K k := ∀c, Supported K k c → boundary c=0 →
  ∃b,Supported K (k+1) b ∧ boundary b=c`;
  `AcyclicThrough K n := ∀k<n,ExactAt K k`.
  `cone_exact K v hv k` supplies every cell count for cones.
- `third-party-claims/SimplexBoundary.lean`: `simplex T` has subset faces;
  `simplexBoundary T hNonempty` has proper-subset faces.
  `simplexBoundary_exact T h k (hk:k+1<T.card)`;
  `simplexBoundary_acyclic T h n (hn:n<T.card)`.
- `claims/CoverDoubleComplex.lean`: finite double coefficient model with exact
  nerve support, commuting square-zero boundaries, support shifts, zero outgoing
  edge differentials, total differential squared zero, horizontal exactness
  in positive vertex count. Generic helper declarations are all audited.
- `third-party-claims/HomologicalCover.lean`:
  `IntersectionExact L n := ∀ J, J.Nonempty → J∈(nerve L).faces →
    ∀r,J.card+r≤n → ExactAt(intersection L J)r`.
  `homological_cover K L hsub hcover n hnerve hex : AcyclicThrough K n`.
  This is exactly the paper's q-acyclicity statement at n=q+2, including r=0
  at the largest relevant intersection size. H12 should use n=chessboardNu a b.
  H11's additive inequality ν+1≤μ+t then turns t+r≤ν into r<μ.

## Remaining assembly glue

No general nonempty-to-augmentation theorem was needed internally, so it was not
added speculatively. For the H12 ν=1 base case, a vertex v of K suffices:
all supported 0-cell chains vanish away from ∅; their cone at v has support
only on {v}, which is a face. The ambient `cone_identity` gives its boundary.
This is a short direct proof, without needing K itself to be a cone.

H03 already supplies `push_supported`, `boundary_push`, `push_equiv_inverse`,
and the transpose chain maps. To transport exactness through a vertex equivalence
preserving faces both ways, pull a cycle back, fill it there, push the filler
forward, and use naturality plus inverse identity. Chessboard worker's H09
already supplies a specialized intersection `ExactAt` transfer; use that for
column complements. Parent may add only the remaining transpose/base-case glue.

## Provenance/index audit

New index rows: lem:augmented-cone-contraction;
third-party:simplex-boundary-acyclicity; lem:finite-cover-double-complex;
third-party:homological-cover-lemma. No known omissions.
The cone and double-chain files are project interfaces adapting standard algebra,
not novelty claims. Simplex-boundary vanishing and cover lemma are standard
attributable statements. Existing foundational paths were not moved. Parent's
promised final per-statement provenance audit may relocate these if appropriate.
Private H07 edge/column/lifting helpers organize one proof with unchanged cover
hypotheses; independently reusable H06 has its own claim/file/record.

## Operational history

H04 initially overlapped a private cache copy and build; this caused file-creation
errors and avoidable rebuilding, not shared-tree mutation. Later builds ran after
the copy finished, and full pinned dependency audits passed. No new packages or
upgrades were requested; the already approved pinned dependencies were restored.
All substantial commands used shared protected compute.sh with threads=2.
No pushes, main changes, subagents, or H12–H13 attempts by this worker.
