# Index migration acceptance audit

Working-tree acceptance snapshot while coordinator integration is in progress, not immutable final acceptance.

HEAD `4747534a8c0b68d3eeb7d4e8f199c9d355febd1f`; canonical registry snapshot has 866 claims, 18 topics and 111 relationships.

The full plan and IDEAS item 5 were read. This audit covers every currently unchecked requirement without modifying the plan. Ready worker artifacts are separated from integrated, validated state.

## High-priority concrete gaps

1. Complete-record citation discovery is missing: current discovery traverses indexed source regions only.
2. New views/authoring modules and tests need CI push filters, CI execution, checkout inventories and authoritative documentation.
3. The topic-map Markdown needs navigation to group views, not only topic labels/counts.
4. Integrate semantic dependency/significance proposals and the new negative-association correction before final coverage.
5. Reconcile formalization route maps explicitly; the per-file census alone does not demonstrate this requirement.

## Fresh focused checks

The delivered authoring suite passed 7 tests and the views suite passed 5 tests under the shared protected launcher. These verify real component behavior, including CLI retrieval, not final coordinator integration. Existing merge/finalizer/full suites were inspected for coverage but not redundantly replayed here.

Current coverage: mathematical status, formalization and topics each 866 reviewed; significance 857 reviewed/9 pending; relationships 50 reviewed/312 pending/504 unreviewed. All counts are a dated snapshot and will change during integration.

## Requirement-by-requirement evidence

### 6.3 — partial

Inventory every claim against its source using automated parsing and evidence extraction, including corrections, formalization and publication records. Validate explicit declarations mechanically; reserve manual reading for ambiguous scope, contradictory evidence and semantic judgments rather than rereading every full notebook entry.

Evidence: coverage-snapshot.json; parallel_index_classify_* and dependency patch directories.

Remaining action: Finish semantic edge integration and new NA audit claims; rerun complete source/field coverage including added claims.

### 7.1 — partial

Inventory all per-claim Lean files, declarations, route maps, verification reports and notebook formalization entries; map them to stable claim IDs.

Evidence: index_formalization_metadata_20260919/inventory.json and README.md.

Remaining action: Per-claim files/declarations/reports were inventoried; explicitly reconcile route-map entries/assembly claims rather than inferring route completeness from the file census.

### 7.6 — partial

Populate the Res(⊕) bit-PHP publication theorem, exponential corollary and dependency route from their existing records, retaining both rule conventions and exact parameter/encoding scope.

Evidence: index_curation_20260919 seed; canonical publication/exponential records; existing formalization inventory.

Remaining action: The two result scopes exist, but accepted full route dependencies still need integration and a route-to-registry reconciliation.

### 7.7 — partial

Audit consistency between informal scope, structured coverage, Lean links and recorded verification evidence. Distinguish inspecting existing evidence from performing a fresh kernel replay.

Evidence: formalization-curation-audited.json; recorded named successful axiom reports.

Remaining action: Preserve the scope audit evidence, resolve route-level mapping acceptance and include any subsequently added/changed formalization records; no fresh kernel replay required.

### 8.1 — snapshot_satisfied

Populate mathematical status independently of formalization and significance: working proof, established/imported result, conditional result, conjecture, finite check, refutation, correction/retraction, or contextual record as appropriate.

Evidence: coverage-snapshot.json: 866 mathematical-status reviews.

Remaining action: Revisit directly impacted NA claims through a dated audit; rerun after adding new claims before final acceptance.

### 8.2 — snapshot_satisfied

Define a small reusable topic taxonomy with descriptions and stable IDs; allow multiple topics per claim. Separate topic, object/proof system, and current-route membership where those distinctions are useful.

Evidence: canonical topic_definitions: 18 stable IDs with nonempty descriptions.

Remaining action: Confirm final taxonomy covers integrated additions; do not create a separate route-state summary.

### 8.3 — snapshot_satisfied

Assign topics across all claims, resolving ambiguous and uncategorized cases explicitly rather than leaving an unexamined tail.

Evidence: coverage-snapshot.json: 866 topic reviews.

Remaining action: Recheck final additions and any unclassified topic report.

### 8.4 — ready_not_integrated

Generate a compact topic map and topic-specific index views; choose their layout without creating a second editable source or breaking existing links.

Evidence: tools/claim_views.py, five passing test_claim_views tests, parallel_index_acceptance_tools samples.

Remaining action: Expose/document the CLI, generate final views, and make topic-map entries navigate to their topic group/view; current Markdown map only shows labels/counts/descriptions.

### 8.5 — partial

Run similarity-based duplicate discovery as a review aid. Check hypotheses, encodings, quantifiers and costs before classifying any pair.

Evidence: claim_views duplicate discovery; parallel_index_duplicate_review candidates/packets/explicit-refinement-inventory.

Remaining action: Finish source-reviewed candidate dispositions and retain the full candidate set; lexical generation alone is not semantic completion.

### 8.6 — partial

Record true duplicates, rediscoveries, refinements, supersessions and corrections with stable-label relationships. Do not delete or conflate claims because their wording is similar.

Evidence: reviewed existing typed graph plus delivered scoped worker patches.

Remaining action: Integrate true rediscovery/refinement/correction dispositions and preserve stable IDs; do not force each relationship type to occur.

### 8.7 — ready_not_integrated

Provide active and historical/retracted views, retaining lookup of every old label and visible correction warnings. A parked result remains discoverable.

Evidence: claim_views claim_view/markdown; lifecycle and correction-warning tests pass.

Remaining action: Document active versus historical meaning, expose/generate the views and verify old-label retrieval after integration.

### 8.8 — partial

Compress generated display text and links where useful while retaining full exact scope through lookup. Ensure links work on GitHub, locally and on Pages; a bare notebook anchor in a Markdown file is not automatically a valid link.

Evidence: compact view preserves original summary/source fields; public_markdown path conversion tests.

Remaining action: Generate and link final human views; preserve exact lookup. More semantic compression is optional, not a demand to truncate mathematics.

### 9.1 — missing_scope

Extract candidate citations from the entire Research record and claim source passages, mapping entry anchors to claims without assigning an entry's every citation to every claim in that entry.

Evidence: claim-dependencies.py scan loops indexed claim source anchors; unindexed-record passages are not traversed as a separate inventory.

Remaining action: Add a full Research-record citation inventory with unresolved/unowned entries and ambiguity rather than assigning every article citation to all its claims; test a citation in an unindexed passage.

### 9.3 — ready_not_integrated

Review every claim's direct proof dependencies through that evidence inventory. Accept justified explicit information without a redundant full-entry reread; inspect targeted passages when the tool cannot resolve meaning or ownership. Do not treat imports/citations alone as proof dependencies, or a partial publication/frontier audit as completion of the entire graph.

Evidence: dependency worker proposals cover broad disjoint ranges; snapshot has 50 reviewed/312 pending/504 unreviewed.

Remaining action: Integrate every reviewed patch, retain genuine unresolved items, refresh incident evidence and produce final full coverage; do not count delivered proposals as canonical completion.

### 9.4 — mostly_ready

Add bounded candidate lookup, deduplication and decision tracking so reviewed, rejected and pending suggestions survive reruns and compaction. Test ambiguous shared entries, unused imports, negated dependency language, local definitions, corrections and stale evidence; retain human review for semantic uncertainty.

Evidence: scan/show/decide plus tests for negation, shared anchors, unused imports, local equations and stale hashes.

Remaining action: Check explicit correction-source candidate regression coverage (not found as a dedicated discovery test); retain semantic human review and persisted decisions.

### 9.5 — partial

Populate `depends_on`, `cites`, `refines`, `supersedes`, `corrects`, `rediscovers`, `formalizes`, `applies`, and `obstructs` wherever justified; define direction and meaning consistently and preserve evidence locators.

Evidence: schema supports nine types; snapshot has six represented; worker patches add scoped data.

Remaining action: Integrate justified roles and review their direction; absent types need no fabricated edges.

### 9.6 — ready_not_integrated

Distinguish required dependencies from alternative proofs, contextual citations, tests and counterexamples. Record scope/conditions where an edge applies to only part of a claim or one proof.

Evidence: worker edge scope fields distinguish proof/application/context/finite controls.

Remaining action: Integrate and review collisions; finish alternative-proof/correction scope audit, especially NA affected claims.

### 9.7 — partial

Resolve historical and external endpoints through stable identities and locators, leaving the immutable handoff untouched. Decide how entry, method, Lean-artifact and publication nodes are represented when they are not claims.

Evidence: registry README namespaced endpoint contract; validator local locators; scoped worker endpoints.

Remaining action: Normalize duplicate historical/external identities and explicitly document how nonclaim methods, entries, Lean artifacts and publications are referenced rather than silently invented as claims.

### 9.8 — partial

Seed reviewed edges with the documented publication dependency route and active tools, then continue through the complete index with coverage tracking.

Evidence: publication seed edges exist; distributed route/dependency patches ready.

Remaining action: Reconcile complete publication route and all active-tool/remaining-index inventories after merge.

### 9.9 — partial

Mark pending edge reviews and claims whose dependencies have been inspected but found empty. Do not conflate either case with unexplored dependencies.

Evidence: field review schema distinguishes pending, reviewed-empty and unreviewed; coverage currently shows all three.

Remaining action: Integrate dispositions with source-specific empty rationale and retain real pending questions.

### 9.10 — ready_not_integrated

Validate endpoints, duplicate/conflicting edges, self-links, and cycles; distinguish genuine circular proof dependencies from harmless cycles of citation.

Evidence: claim_graph.audit tests; individual patch validation reports.

Remaining action: Run union graph audit after all edges; investigate each proof cycle/conflict instead of treating citation cycles as proof cycles.

### 10.1 — snapshot_satisfied

Define structured significance assessments with rationale, exact scope, novelty status, source evidence, review date and suggested action. Keep independent interest, novelty, correctness and publication readiness separate.

Evidence: schema significance fields and five-field review provenance.

Remaining action: Preserve current separation; no additional field needed solely to restate existing metadata.

### 10.3 — ready_not_integrated

Screen every remaining claim for independent interest, reusable tools, meaningful negative results and corrected published claims. Include finite checks and failed attempts that expose valuable counterexamples.

Evidence: 866 classified records; nine pending significance reviews; targeted worker audits delivered.

Remaining action: Integrate audited significance dispositions, including reasoned unknown novelty rather than claiming known priority.

### 10.4 — ready_not_integrated

Perform targeted literature checks for plausible candidates, preserving exact formulations, encodings, versions, dates, uncertainty and source links.

Evidence: parallel_index_significance_{normalizers,calculi,query_obstructions} reports.

Remaining action: Check all plausible candidate IDs have completed scope-specific audits and record remaining uncertainty; current reports are not automatic publication approval.

### 10.5 — snapshot_satisfied_with_pending

Complete significance coverage for all claims: a reasoned disposition or an explicit pending novelty/audit question, not unexplained nulls.

Evidence: coverage-snapshot.json: 857 reviewed and nine explicit pending, no unreviewed significance.

Remaining action: The wording permits explicit pending questions, but integrate ready audits and do not call unresolved novelty proven.

### 12.1 — pending_final_state

Publish a coverage report for all baseline and subsequently added claims: populated metadata, reviewed dispositions, pending questions and stale evidence.

Evidence: this coverage snapshot is complete only for current 866 records.

Remaining action: Save final all-claims coverage after integration and new audit registration; publication here means retained checkpoint evidence, not permission to git push.

### 12.2 — ready_component_evidence

Demonstrate a new claim travelling through registration, exact/minimal lookup, topics, relationship recording, significance and formalization metadata without duplicated manual bookkeeping. No graph UI or Fossick implementation is required.

Evidence: seven passing authoring tests include source hashing, registration, render, actual exact/minimal CLI lookup, topic filtering and review metadata.

Remaining action: Wire authoring into documented workflow/CI and run final suite; optional end-to-end finisher fixture can connect these components if required.

### 12.3 — ready_component_evidence

Demonstrate a correction updating source links, scope, affected relationships and review tasks without rewriting the historical notebook record.

Evidence: test_correction_preserves_old_record_and_requires_target_review plus root NA audit in progress.

Remaining action: Complete actual append-only NA correction registration, target reviews and dependency-impact queue; verify no historical rewrite.

### 12.4 — ready_component_evidence

Exercise interrupted/resumed curation and existing parallel append integration against the structured source, preserving stable IDs and accepted records.

Evidence: authoring JSON roundtrip/resume and stable-ID append merge; existing real-rebase merge test.

Remaining action: Run the existing real-rebase/merge suite on final code and preserve evidence; compare immutable integration revisions.

### 12.5 — pending_final_state

Run schema, generation, retrieval, metadata, relationship and portability checks; preserve full evidence and reproducibility data at checkpoints.

Evidence: existing validators; new authoring/views 12 tests pass in this audit.

Remaining action: After all merges run full touched-tool suites, schema/render/retrieval/graph/changed/append-only/checkout checks; preserve final outputs and tracked tool modes.

### 12.6 — partial

Document the minimal index editing/curation workflow and remove superseded index instructions or tools after compatibility is accounted for.

Evidence: registry README already owns core contract; worker READMEs explain new tools.

Remaining action: Merge concise authoring/views instructions into the authoritative registry guide; retain justified legacy importer/old-worktree compatibility rather than deleting it blindly.

### 12.7 — in_progress

Review completion against IDEAS.md item 5 and the conversation's index-specific requirements. Report every metadata gap explicitly; do not make completion depend on implementing the separately owned framework plans.

Evidence: this requirement-by-requirement report plus IDEAS item 5 review.

Remaining action: Close real gaps and perform final acceptance on integrated current state; do not add unrelated Fossick/graph UI/parallel research plans.

### 13.5 — partial

Update `research/notes/RESUME.md` to restore the populated index, taxonomy, relationship semantics, pending reviews and the maintenance contract through bounded tools. Restoration must not silently revert to Markdown-only editing or import the entire index into context.

Evidence: Resume exposes list, packet, coverage and changed gate but not taxonomy/views/graph semantics commands.

Remaining action: Add bounded topic/relationship/pending-review navigation via one authoritative registry guide link and concrete commands; no full-index load.

### 13.7 — ready_not_integrated

Update the registry guide, authoring tools and templates so a new claim is created with the required metadata and relationship review, rather than inheriting the initial migration's all-null defaults.

Evidence: claim_authoring.py template/prepare and seven passing fixture tests.

Remaining action: Document/expose authoring CLI and include tool/test in CI/checkout; optional claim-index alias is not intrinsically required.

### 13.9 — pending_final_state

Regenerate human/topic views and machine-readable exports at checkpoints; keep pending index metadata reviews visible after compaction, branch integration or migration. Graph rendering and notifications are owned by their separate plans.

Evidence: generated primary Markdown exists; samples under acceptance_tools are historical snapshots.

Remaining action: Regenerate current primary/topic/lifecycle views and machine export after integration, with current fingerprints and checkpoint links.

### 13.11 — ready_component_evidence

Test a fresh cycle, a correction, a formalization update and parallel branch integration end to end. Verify that incomplete new metadata is caught and that justified unknown/not-applicable states are represented honestly.

Evidence: authoring tests cover fresh/correction/formalization/parallel component flows; finalizer tests cover rejection before clock stop.

Remaining action: Run final combined tests and at least one actual accepted research checkpoint with new claims; retain existing finalizer and real-rebase tests rather than requiring new mathematical work.

### 13.12 — in_progress

Include this ongoing-maintenance phase in the overall acceptance review; a fully backfilled index is insufficient if subsequent cycles leave its new fields empty again.

Evidence: maintenance gate already enforced by finish-turn and CI; new tool integration outstanding.

Remaining action: Finish CI push-path/test and checkout inventories, docs and final evidence before marking overall acceptance complete.

## Scope notes

The new authoring tests combine modules and actual retrieval subprocesses; they do not invoke a successful full finish-turn in each fixture. Existing finalizer tests separately cover pre-stop rejection and the merge suite contains a real Git rebase case. Treat this as compositional acceptance evidence, and retain a final real coordinator checkpoint to cover orchestration.

The plan does not require graph visualization, Fossick, new Lean proofs, publication, a new virtual environment or dependence on user approval for ordinary integration. No such work was added here. No blanket proof-validity claim follows from coverage or passing tests.
