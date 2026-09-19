# Claim-index migration and curation checklist

This plan covers **IDEAS.md item 5** and the agreed index-specific additions:
complete metadata population, graph-ready relationships, compact retrieval and
ongoing index maintenance. It does not implement the other framework ideas.

The structured index is authoritative for claim metadata; the notebook remains
authoritative for mathematical statements, proofs and current research status.
Preserve the historical handoff unchanged. Record already-existing formalization
coverage here; new Lean proof work belongs to the separate formalization plan.

Mark tasks complete only after implementation and validation. Record concrete
paths, decisions and checkpoint references as work proceeds. Leave partial tasks
unchecked and briefly note what remains.

## Completion — 19 September 2026

All tasks below are implemented and validated. The final
[acceptance report](../results/index_parallel_integration_20260919/acceptance.json)
and [coverage report](../results/index_parallel_integration_20260919/coverage-final.json)
cover **887 claims, 18 topics and 2,409 scoped relationships**. Every claim has
all five reviewed dispositions, with no stale or unreviewed field. All 866
original text records remain exact; 18 source-inventory omissions and three
dated probability-audit records were added. This completes index curation, not
the open mathematical program or external review of any paper.

Acceptance evidence by requirement group:

- Sections 6–8: disjoint classification patches, the complete 91-candidate
  [source adjudication](../results/parallel_index_source_adjudication/README.md),
  [formalization reconciliation](../results/parallel_formalization_route_reconcile/README.md),
  and [duplicate review](../results/parallel_index_duplicate_review/README.md).
  All 75 mapped claims/77 artifacts retain their exact verified scopes. All 22
  similarity candidates remain distinct; rediscoveries/refinements are linked.
  [Topic/lifecycle views](../claims/views/topics.md) expose scoped corrections
  without duplicating editable metadata or deleting historical qualifications.
- Section 9: the final dependency merger and scope decisions, full-record
  [citation utility](../results/parallel_record_citations/README.md), and final
  [graph audit](../results/index_parallel_integration_20260919/graph-final.json).
  Every direct-dependency inventory is reviewed. Automatic citation ownership
  remains explicitly ambiguous/unowned where appropriate; extraction flags are
  not unreviewed theorem metadata or an instruction to invent an edge.
- Section 10: nine completed targeted significance comparisons are integrated.
  Eight retain unknown novelty after bounded searches; the binary predecessor
  is the same publication candidate, not a second result. Follow-up expert/novelty
  questions remain in the assessments, distinct from unfinished index review.
- Sections 11–13: compact/exact retrieval, source packets, proposal authoring,
  registration/correction/formalization tests, interrupted proposal recovery,
  parallel append integration, generated-view freshness and changed-field gates
  are implemented. Root guidance, prompts, Resume and registry documentation
  share the maintenance contract. Full-record citation and evidence-normalization
  regressions are included in CI and checkout requirements.
- Combined acceptance: 79 claim tests, seven finalizer tests, seven parallel-merge
  tests, and 18 citation/discovery tests pass. Source targets, generated views,
  registration, graph and [portable checkout](../results/index_parallel_integration_20260919/checkout.json)
  checks pass. The final [machine-readable export](../results/index_parallel_integration_20260919/index-export.json)
  is retained with provenance. No new Lean build or publication is implied.

The curation uncovered an invalid permutation-probability premise. Its exact
counterexample, scoped corrections and remaining proof obligations are in the
dated notebook entry `entry-2026-09-19-permutation-probability-audit`. The index
records those limitations rather than treating reviewed metadata as proof truth.
Other IDEAS.md items remain owned by their separate plans.

## Scope and completion discipline

- Sections 1–5 record the completed structural migration, not completed metadata
  curation. Sections 6–13 record the completed enrichment and maintenance acceptance.
- Account for every claim, including additions during the pass, through resumable
  field-level coverage records. `null`, empty lists and "not reviewed" do not
  establish absence; record a reasoned disposition or an explicit unresolved item.
- Preserve stable IDs and original qualifications. Do not check off an unimplemented
  or unresolved task as complete, or infer dependencies/verification from links alone.
- Keep one editable source per fact. Other framework plans consume index metadata
  and interfaces; their implementation is not an acceptance condition of this plan.
- Planning does not authorize publication, silent historical edits or additional
  research/formalization/parallel runs beyond the assigned scope.

## Separate plans by idea

| IDEAS.md item | Owning plan | Boundary with this plan |
|---|---|---|
| 1. Fossick | [FOSSICK_PLAN.md](FOSSICK_PLAN.md) | Uses curated significance and lookup; implements scans/cursors separately |
| 2. Significance alerts | [SIGNIFICANCE_ALERTS_PLAN.md](SIGNIFICANCE_ALERTS_PLAN.md) | Owns flags, candidate queue and notifications; index stores claim assessments |
| 3. Parallel exploration | [PARALLEL_RESEARCH_PLAN.md](PARALLEL_RESEARCH_PLAN.md) | Owns exploration/adversary workflows; index merge compatibility remains here |
| 4. Formalization | [FORMALIZATION_PLAN.md](FORMALIZATION_PLAN.md) | Owns new proof work/policy; existing coverage metadata is curated here |
| 5. Claim index | This file | Migration, curation, relationships, retrieval and maintenance |
| 6. Smaller utilities | [WORKFLOW_UTILITIES_PLAN.md](WORKFLOW_UTILITIES_PLAN.md) | Owns interruption notes and benchmark map |
| 7. Context budget | [CONTEXT_BUDGET_PLAN.md](CONTEXT_BUDGET_PLAN.md) | Owns general Resume/overview/rule consolidation; index-specific retrieval stays here |
| 8. Graph visualization | [CLAIM_GRAPH_PLAN.md](CLAIM_GRAPH_PLAN.md) | Owns graph UI/Pages; reviewed relationship data and queries stay here |

## 1. Inventory and schema

- [x] Pin the pre-migration Git revision and inventory every row, label, link,
      status qualification, and formalization reference in `research/CLAIM_INDEX.md`.
- [x] Identify tools and instructions that read or edit the current Markdown index.
- [x] Choose and document the structured file location and schema version.
- [x] Define claim records with stable IDs preserving existing labels, statement
      summaries, mathematical status, source links, formalization coverage, and
      optional topics. Preserve exact legacy text where structured fields alone
      would lose qualifications.
- [x] Keep mathematical status, formal verification, and significance distinct;
      represent missing or unreviewed information explicitly without guessing it.
- [x] Define graph-ready relationship records: source and target IDs, type,
      supporting source location, and review status. Support `depends_on`,
      `refines`, `corrects`, `supersedes`, and other justified relationship types.
- [x] Specify how references to historical claims and external sources are
      represented without modifying or absorbing the historical handoff index.

## 2. Complete structural migration

- [x] Implement a reproducible importer with an explicit output destination and
      diagnostics for ambiguous or unparsed rows; do not silently drop content.
- [x] Convert every existing continued-research claim into the structured source.
- [x] Preserve every original label, summary, status qualification, link, and
      formalization scope; resolve parsing ambiguities against the original row.
- [x] Preserve existing ordering and grouping where applicable, without merging,
      renaming, or reclassifying mathematical claims during conversion.
- [x] Retain citations as citations. Leave dependency edges unreviewed or absent
      unless their type is supported by the record; a hyperlink alone is not a
      proof dependency.

## 3. Generated index and compact retrieval

- [x] Generate `research/CLAIM_INDEX.md` deterministically from the structured
      source, preserving usable public links and existing reference targets.
- [x] Clearly mark the Markdown as generated and document the authoritative edit path.
- [x] Adapt `tools/search-claims.py` to query the structured source and return
      bounded results containing the claim ID, concise summary, status, and source.
- [x] Add exact-label lookup that exposes the complete claim metadata and links
      to the relevant notebook statement or proof without loading the full index.
- [x] Support useful filters where metadata is available; make omitted results
      and unknown fields visible. Do not require a complete topic taxonomy first.
- [x] Provide a stable machine-readable lookup/export interface for later Fossick
      and graph tools, without building those tools in this migration.

## 4. Validation and regression coverage

- [x] Produce a migration reconciliation report against the pinned original:
      every row and label accounted for, all source text and links preserved,
      and any normalization or exception explicitly documented.
- [x] Validate unique IDs, required fields, schema versions, and relationship
      endpoints; preserve distinctions between unknown and verified metadata.
- [x] Check repository-local files and notebook anchors, and preserve external
      destinations without treating their availability as proof verification.
- [x] Verify deterministic generation and add a check that detects stale generated
      Markdown relative to the structured source.
- [x] Test meaningful retrieval and migration cases, including qualified or partial
      formalizations, multiple links, corrections, unusual table syntax, and
      malformed records. Ensure searches still find representative known claims.
- [x] Confirm graph consumers can distinguish citations from reviewed dependencies
      and that missing edges do not imply mathematical independence.

## 5. Structural workflow integration and completion

- [x] Update affected tools and concise workspace guidance to use the structured
      source; consolidate existing rules rather than adding duplicate instructions.
- [x] Update the resume reading guide only where navigation changes, keeping full
      index loading out of routine context restoration.
- [x] Document how to add or revise a claim, regenerate views, and validate changes.
- [x] Preserve conversion tooling, reconciliation evidence, and essential outputs
      in the repository. Follow the computation policy for substantial jobs.
- [x] Review and commit coherent implementation checkpoints locally, updating this
      checklist after each. Publishing remains subject to explicit authorization.
- [x] Confirm the structural migration is complete: structured source authoritative,
      Markdown generated, retrieval working, validation passing, and no unresolved
      loss of original index content.

## 6. Complete metadata inventory and review tracking

- [x] Pin the enrichment baseline and report population of every field. The first
      migration has 866 claims, all new classifications/significance null, all
      topics empty, and zero relationships; preserve this as the starting snapshot.
- [x] Define field-level review metadata: reviewed source revision/anchor, review
      date or checkpoint, disposition, evidence, and unresolved work. Avoid a
      single "reviewed" flag that conceals untouched fields.
- [x] Inventory every claim against its source using automated parsing and evidence
      extraction, including corrections, formalization and publication records.
      Validate explicit declarations mechanically; reserve manual reading for
      ambiguous scope, contradictory evidence and semantic judgments rather than
      rereading every full notebook entry.
- [x] Version and migrate the schema as needed for richer formalization,
      significance, topics, relationships, and review provenance; update exporters,
      generated views, merge support, validators, and tests together.
- [x] Add bounded commands/reports for missing fields, pending reviews, stale
      reviews, broken references, and coverage by field/topic. Include all claims
      added or corrected while the enrichment pass is in progress.
- [x] Establish one authoritative home for index metadata and its review queue.
      Expose data to the separate framework plans without duplicate editable fields.

## 7. Populate existing formalization coverage for every claim

- [x] Inventory all per-claim Lean files, declarations, route maps, verification
      reports and notebook formalization entries; map them to stable claim IDs.
- [x] Populate structured formalization records wherever coverage is already
      explicit, including source links and exact scope. Do not leave known
      complete or partial coverage null merely to avoid semantic extraction.
- [x] Distinguish full verification, partial verification, stronger hypotheses,
      statement-only specification, failed/discrepant formalization, and no
      recorded formalization; record evidence for the classification.
- [x] Support multiple formalization artifacts/scopes for one claim and shared
      supporting files without implying that a filename verifies every conclusion.
- [x] Resolve mixed cases such as `lem:mp-telescoping`: preserve the verified
      identity/bounds, the refuted equality, and the downstream audit limitation.
- [x] Populate the Res(⊕) bit-PHP publication theorem, exponential corollary and
      dependency route from their existing records, retaining both rule conventions
      and exact parameter/encoding scope.
- [x] Audit consistency between informal scope, structured coverage, Lean links
      and recorded verification evidence. Distinguish inspecting existing evidence
      from performing a fresh kernel replay.
- [x] Complete a coverage report for the entire index: every claim has a reviewed
      formalization disposition or a specifically recorded unresolved item.

## 8. Mathematical status, topics, compression and deduplication

- [x] Populate mathematical status independently of formalization and significance:
      working proof, established/imported result, conditional result, conjecture,
      finite check, refutation, correction/retraction, or contextual record as appropriate.
- [x] Define a small reusable topic taxonomy with descriptions and stable IDs;
      allow multiple topics per claim. Separate topic, object/proof system, and
      current-route membership where those distinctions are useful.
- [x] Assign topics across all claims, resolving ambiguous and uncategorized cases
      explicitly rather than leaving an unexamined tail.
- [x] Generate a compact topic map and topic-specific index views; choose their
      layout without creating a second editable source or breaking existing links.
- [x] Run similarity-based duplicate discovery as a review aid. Check hypotheses,
      encodings, quantifiers and costs before classifying any pair.
- [x] Record true duplicates, rediscoveries, refinements, supersessions and
      corrections with stable-label relationships. Do not delete or conflate claims
      because their wording is similar.
- [x] Provide active and historical/retracted views, retaining lookup of every old
      label and visible correction warnings. A parked result remains discoverable.
- [x] Compress generated display text and links where useful while retaining full
      exact scope through lookup. Ensure links work on GitHub, locally and on Pages;
      a bare notebook anchor in a Markdown file is not automatically a valid link.

## 9. Populate and audit relationship data

- [x] Extract candidate citations from the entire Research record and claim source
      passages, mapping entry anchors to claims without assigning an entry's every
      citation to every claim in that entry.
- [x] Build reusable dependency discovery tools for notebook hyperlinks, explicit
      dependency language/lists, claim-label mentions, Lean imports and declaration
      references. Retain source anchors/lines, extraction method, ownership ambiguity
      and proposed relationship type for every candidate; report unresolved targets.
- [x] Review every claim's direct proof dependencies through that evidence inventory.
      Accept justified explicit information without a redundant full-entry reread;
      inspect targeted passages when the tool cannot resolve meaning or ownership.
      Do not treat imports/citations alone as proof dependencies, or a partial
      publication/frontier audit as completion of the entire graph.
- [x] Add bounded candidate lookup, deduplication and decision tracking so reviewed,
      rejected and pending suggestions survive reruns and compaction. Test ambiguous
      shared entries, unused imports, negated dependency language, local definitions,
      corrections and stale evidence; retain human review for semantic uncertainty.
- [x] Populate `depends_on`, `cites`, `refines`, `supersedes`, `corrects`,
      `rediscovers`, `formalizes`, `applies`, and `obstructs` wherever justified;
      define direction and meaning consistently and preserve evidence locators.
- [x] Distinguish required dependencies from alternative proofs, contextual
      citations, tests and counterexamples. Record scope/conditions where an edge
      applies to only part of a claim or one proof.
- [x] Resolve historical and external endpoints through stable identities and
      locators, leaving the immutable handoff untouched. Decide how entry, method,
      Lean-artifact and publication nodes are represented when they are not claims.
- [x] Seed reviewed edges with the documented publication dependency route and
      active tools, then continue through the complete index with coverage tracking.
- [x] Mark pending edge reviews and claims whose dependencies have been inspected
      but found empty. Do not conflate either case with unexplored dependencies.
- [x] Validate endpoints, duplicate/conflicting edges, self-links, and cycles;
      distinguish genuine circular proof dependencies from harmless cycles of citation.
- [x] Add predecessor/successor, ancestor/descendant, "what cites this", and
      correction-impact queries. Report that impact is an audit scope, not a proof
      that every descendant is invalidated.

## 10. Populate claim significance

- [x] Define structured significance assessments with rationale, exact scope,
      novelty status, source evidence, review date and suggested action. Keep
      independent interest, novelty, correctness and publication readiness separate.
- [x] Populate the known Res(⊕) publication result and its corollaries first, using
      the recorded literature/dependency audits and current external-review status;
      do not leave them null or promote an internal assessment to external confirmation.
- [x] Screen every remaining claim for independent interest, reusable tools,
      meaningful negative results and corrected published claims. Include finite
      checks and failed attempts that expose valuable counterexamples.
- [x] Perform targeted literature checks for plausible candidates, preserving
      exact formulations, encodings, versions, dates, uncertainty and source links.
- [x] Complete significance coverage for all claims: a reasoned disposition or an
      explicit pending novelty/audit question, not unexplained nulls.

## 11. Minimal-output claim retrieval

- [x] Extend the existing claim tool with an explicit all-claims listing mode and
      selectable output fields, for example `list --fields id,summary --format tsv`.
      Emit one claim per line with untruncated values and no JSON syntax, field
      names, headers, scores, metadata, or footers in this minimal mode. Preserve
      registry order; do not silently apply search limits to an all-claims listing.
- [x] Support the same field projection/plain-text format for filtered retrieval
      where useful, with explicit limits only when requested. Define delimiter and
      escaping behavior, retain a lossless machine-readable option, and send any
      diagnostics or requested omission notices to stderr rather than data stdout.
- [x] Document minimal listing in the registry guide and agent retrieval guidance;
      test that every claim appears exactly once, summaries are not truncated,
      selected fields stay in the requested order, and no display fluff is emitted.

- [x] Evaluate whether compact `packet` evidence is useful beyond metadata curation
      for ordinary research orientation and claim triage. Compare representative
      packets with exact statements, hypotheses and correction records; test whether
      omitted qualifications could mislead a research agent. Distinguish orientation
      from proof readiness, and record the evaluation and limitations.
- [x] If that evaluation supports research use, expose `packet` alongside minimal
      claim listing in the research workflows: root/scoped agent guidance, Resume,
      registry guide and applicable research prompts. Link to one authoritative
      usage rule; require exact statement/proof reading before mathematical reliance.
      Do not prescribe research use merely because the command exists.

## 12. Index acceptance and maintenance

- [x] Publish a coverage report for all baseline and subsequently added claims:
      populated metadata, reviewed dispositions, pending questions and stale evidence.
- [x] Demonstrate a new claim travelling through registration, exact/minimal lookup,
      topics, relationship recording, significance and formalization metadata without
      duplicated manual bookkeeping. No graph UI or Fossick implementation is required.
- [x] Demonstrate a correction updating source links, scope, affected relationships
      and review tasks without rewriting the historical notebook record.
- [x] Exercise interrupted/resumed curation and existing parallel append integration
      against the structured source, preserving stable IDs and accepted records.
- [x] Run schema, generation, retrieval, metadata, relationship and portability
      checks; preserve full evidence and reproducibility data at checkpoints.
- [x] Document the minimal index editing/curation workflow and remove superseded
      index instructions or tools after compatibility is accounted for.
- [x] Review completion against IDEAS.md item 5 and the conversation's index-specific
      requirements. Report every metadata gap explicitly; do not make completion
      depend on implementing the separately owned framework plans.

## 13. Enforce metadata maintenance in every subsequent research cycle

This is an ongoing requirement, not only a one-time enrichment pass. Update the
workflow during implementation of this phase. The changed-claim contract and the acceptance checks below are implemented.

- [x] Define the per-claim completion contract for all new or substantively revised
      claims: precise mathematical status, topics, formalization disposition and
      scope, significance assessment, source references, applicable relationships,
      and field-level review provenance. Require explicit justified dispositions
      for genuinely unknown or inapplicable information, not unchecked placeholders.
- [x] Require the research cycle to identify and record dependencies, refinements,
      corrections, rediscoveries, tests and obstructions introduced by its work.
      Distinguish a reviewed absence of relationships from missing review; do not
      invent edges or significance merely to satisfy a completeness check.
- [x] Make each cycle update affected existing claims and relationships as well
      as new ones, including formalization-scope changes, correction impact and
      significance assessments. Preserve historical records and stable IDs.
- [x] Update root AGENTS.md as the authoritative ongoing rule, and align scoped
      research/formalization instructions and Codex/Claude entry points by linking
      to that rule rather than duplicating it.
- [x] Update `research/notes/RESUME.md` to restore the populated index, taxonomy,
      relationship semantics, pending reviews and the maintenance contract through
      bounded tools. Restoration must not silently revert to Markdown-only editing
      or import the entire index into context.
- [x] Update `PROMPTS.md`: Spin, ordinary research guidance, Formalize,
      Spin-formalize and existing parallel variants must apply the same index
      maintenance contract within their assigned scope. Expose that contract for
      future prompts owned by the separate plans; do not implement those prompts here.
- [x] Update the registry guide, authoring tools and templates so a new claim is
      created with the required metadata and relationship review, rather than
      inheriting the initial migration's all-null defaults.
- [x] Add changed-claim/relationship completeness checks to cycle finalization
      and CI, with useful diagnostics. Track historical backlog separately so the
      checks neither excuse incomplete new work nor repeatedly demand a full audit
      of the whole registry on every turn.
- [x] Regenerate human/topic views and machine-readable exports at checkpoints;
      keep pending index metadata reviews visible after compaction, branch integration
      or migration. Graph rendering and notifications are owned by their separate plans.
- [x] Close the omitted-registration gap: compare newly appended research records
      with declared/indexed claim IDs, flag explicit new claim labels without registry
      records, and require an explicit disposition for entries introducing no claims.
      Test that a notebook-only new labelled claim cannot pass finalization or CI.
      Document the unavoidable semantic limit: software cannot prove that arbitrary
      unlabelled prose contains no new theorem or that a declared inventory is honest.
- [x] Test a fresh cycle, a correction, a formalization update and parallel branch
      integration end to end. Verify that incomplete new metadata is caught and
      that justified unknown/not-applicable states are represented honestly.
- [x] Include this ongoing-maintenance phase in the overall acceptance review;
      a fully backfilled index is insufficient if subsequent cycles leave its new
      fields empty again.

## Implementation notes

Completed structural implementation session: `index_migration_20260919`.
Local checkpoint: `c53b032`, "Migrate the complete claim index to a structured registry".

- Baseline: `21603c76b82afcc8d91014fa752e61e5cab690ac`.
- Imported all 866 claims to `research/claims/index.json`, schema version 1.
- `summary`, `assessment`, and `record` preserve the original three text cells
  verbatim. Machine-readable references are derived from those fields, avoiding
  a second editable copy. Classification fields remain explicitly unknown.
- Relationships have namespaced endpoints and evidence/review state; none was inferred.
- Initial reconciliation preserves every label, text field, link and row order.
  All 1,242 references (including the preamble) resolve locally.
- Rendering repairs: remove table-internal blank lines, including the break before
  `third-party:chessboard-star-nerve`, and escape bare math pipes in 22 rows.
  Entry contents are unchanged. Evidence: `research/results/index_migration_20260919/`.
- Affected consumers: ranked search, parallel append merger, checkout verification,
  root guidance, resume navigation, and public documentation.

At the structural checkpoint, metadata enrichment remained open in this plan;
the later completion record below closes it. Other framework features have separate plans.

- Generated view and compact lookup are implemented; the complete export and
  qualified/ranked lookup examples are preserved with the evidence.
- Parallel append merges operate on JSON and regenerate Markdown; existing-record
  changes remain manual. Turn finalization, checkout validation and CI detect stale views.
- Focused suites pass: 14 registry, seven append-merge and six finalization tests.
- The user confirmed the repaired table renders correctly. No mathematical entries
  or original claim text were edited. Semantic curation remains pending here; visualization is tracked separately.

Scope correction, 19 September 2026: the earlier expansion incorrectly included all
framework ideas in the index plan. Pending tasks were split into seven sibling
plans, one for each other numbered idea. The original completed index tasks remain
checked; no moved feature was marked implemented by this reorganization.

Curation checkpoint `index_curation_20260919`: schema v2 and per-field review
provenance are implemented, with anchored evidence hashes and coverage/staleness
queries. Minimal TSV listing and field projection are implemented and tested.
Three claims have source-reviewed status, formalization, topics, significance and
relationships; 863 remain unreviewed in every field. Five reviewed relationships
and five initial topic definitions are present. The complete taxonomy, dependency
route, field backfill and ongoing-maintenance enforcement remain unfinished.
Next batch: inventory all existing Lean mappings and recorded scope before further
curation. No new formalization or external novelty verification was performed.


Evidence-discovery checkpoint `index_formalization_metadata_20260919`:
- Inventoried all 76 per-claim Lean files: 75 index claims have explicit mappings;
  the remaining file is an import-only publication assembly. Recorded scopes,
  shared-file ownership and actual named axiom reports are preserved. No new
  kernel replay was performed. Route-map semantic dependency review remains open.
- All 866 formalization fields have a reviewed disposition: 74 complete, one
  partial, and 791 with no explicit mapping in the audited inventory. The latter
  is a bounded census result, not proof of absence; changes to the Lean corpus
  make these negative census reviews stale automatically.
- `tools/claim-dependencies.py scan/show/decide` inventories source evidence for
  all 866 claims and 75 linked Lean files. There are 1,901 candidate records,
  nine flagged widened regions, and two unresolved target mappings. This does
  not yet scan every unindexed Research-record passage or complete the graph.
- Evidence distinguishes notebook links, claim labels, module imports and Lean
  identifier references. Nested comments/strings are excluded from code evidence;
  imports and negated dependency language do not become accepted dependencies.
  Stable decisions survive rescans; changed source/claim fingerprints go stale.
- One candidate is calibrated against an already-reviewed publication edge.
  The full semantic relationship pass, corrections/local-name interpretation,
  historical/external endpoint mapping, and 863 claims' other metadata remain open.
- Evidence: `research/results/index_formalization_metadata_20260919/`.
  Twenty-eight focused registry/discovery tests pass; all 3,492 references resolve.


Graph-query checkpoint `index_graph_queries_20260919`: implemented typed direct
and transitive traversals, incoming citations and correction-impact review scope,
with shortest edge witnesses, explicit review/type filters, bounded display and
complete saved output. Structural diagnostics distinguish dependency and citation
cycles and report duplicate edges, self-links and conflicting metadata. These
checks are implemented; semantic graph curation and resolving any later findings
remain open, so the full relationship-validation checklist item stays unchecked.


Initial chronological metadata batch `index_metadata_batch_20260919`:
14 additional claims have reviewed status, topics, significance and relationships;
17 are now reviewed in those fields and 849 remain unreviewed. Twenty-two scoped
relationships bring the graph to 27, including historical citations distinct from
proof dependencies. Recorded obstructions target omitted hypotheses or stronger
methods, not the qualified theorems. Ten topic definitions now exist; the global
taxonomy/backfill is still open. No independent novelty was asserted for this batch.

Process correction requested by the user: this batch read full claim sections
rather than only ambiguous evidence, which was avoidable overhead. Dependency
extraction alone did not cover the other metadata fields. Added `packet --claim`
to `tools/claim-dependencies.py` for verbatim assessments plus bounded statement,
status and qualification snippets with hashes and omission flags. Start curation
with packets and relationship candidates; open larger passages only for unresolved
scope, conflicting evidence or unsupported judgments. Resume and registry guidance
now point to this path. Do not turn every claim inventory into a full proof reread.


Maintenance checkpoint `index_maintenance_contract_20260919`: root guidance and
all prompts now share the changed-claim contract. The CLI `changed --base REV`
pins the comparison revision; finish-turn checks HEAD before stopping timing,
and CI checks the push/PR integration base. New or substantively revised claim
text requires all five current dispositions. Metadata-only backfill checks its
changed fields; affected edge endpoints and correction targets require refreshed
reviews. Source changes, stable-ID deletion and stale metadata are detected;
untouched backlog is reported separately. Explicit pending questions pass the
accountability gate without becoming completed curation. Eight focused contract
tests plus a real pre-stop finalizer rejection cover new claims, corrections,
formalization updates and parallel complete additions. Full authoring/retrieval
acceptance scenarios and template support remain unchecked; no claim is made
that these focused tests close every end-to-end requirement.

User addition: evaluate `packet` for ordinary research use before exposing it in
research workflows (section 11). Current packet guidance concerns metadata
curation only; proof readiness must not be inferred from a selected excerpt.


Packet research-use evaluation `index_packet_evaluation_20260919`: five purposive
cases preserve critical indexed qualifications (partial proof/counterexample,
conditional premise, correction/repair history, finite check, working theorem) but
also demonstrate omitted definitions and proof details. Useful for orientation and
source triage; explicitly not proof readiness. Packets now report that distinction
and show recorded formalization scope. Root guidance owns the research-use rule;
research instructions, Resume, prompts and registry documentation expose it next
to minimal listing. Full statement/proof/correction reading remains required before
reliance. Evidence and limitations are in the cycle's evaluation.json; this is not
an exhaustive extraction benchmark or renewed mathematical verification.


Compact-evidence batch `index_metadata_batch2_20260919`: classified 45 additional
claims (matching/spread normalization through copy agreement). Status, topics and
significance now have 62 reviewed and 804 unreviewed records. Formalization stays
866 reviewed. Twelve scoped edges bring the graph to 39; 45 direct-dependency
inventories remain explicitly pending because local equation/setup references
are not fully mapped by hyperlink extraction. Seventeen relationship inventories
are reviewed, 804 untouched. No pending inventory is counted complete.

The packet workflow avoided whole-entry rereading. A concrete extraction fault
was found and fixed: broad HTML stripping could swallow raw mathematical less-than
expressions. Known markup stripping now protects TeX spans; regression tests cover
ordinary and tag-like variable inequalities. The original/intermediate packet
outputs are retained, with `packets-reviewed.json` the final evidence. Nine
packet/discovery tests, changed-scope validation and 3,870 source-target checks pass.


Registration gate `index_registration_gate_20260919`: new notebook articles declare
`data-claims` or a reasoned no-claim disposition. The changed-command gate checks
explicit code/backtick labels against current/historical IDs and checks declared
claims bidirectionally against source links in the entry. Finalization and CI use
that same gate. Entries through immutable 552e562 are grandfathered without edits.
Seven registration tests and a real finalizer test cover a notebook-only labelled
claim that previously escaped the JSON-only check. Unlabelled mathematical novelty
and false no-claim declarations still require editorial judgment; that limit is
explicit, not claimed solved by text parsing.


Compact-evidence batch `index_metadata_batch3_20260919`: 80 further claims from
line-scoped simulation through private modified-forest controls have reviewed
status, topics and significance. Totals: 142 reviewed / 724 unreviewed for those
three fields; 866 reviewed formalization dispositions; relationships 17 reviewed,
125 pending, 724 unreviewed. No canonical graph edge was inferred during this
classification pass. Explicit conditional interfaces, finite fixtures, support
corrections and rediscovery qualifiers are retained. Packets and the exact manual
classification decisions are saved in the cycle evidence. Dependency ownership
and correction/refinement mapping remain pending rather than being called complete.

Clarification of registration enforcement: absence of both an inventory and an
explicit no-claim disposition already fails. A nonempty but semantically incomplete
inventory remains possible; the registry guide now states that exhaustiveness
still requires editorial review, alongside the unlabelled-mathematics limitation.


Compact-evidence batch `index_metadata_batch4_20260919`: 80 further records from
constant propagation through categorical-profile certificates were screened.
Status/topics: 222 reviewed, 644 unreviewed. Significance: 217 reviewed, five
pending targeted novelty audits, 644 unreviewed. The five possible independent
results are the odd affine-Booleanity classification, generic and full-PHP
reduced-product Booleanity gaps, ternary coefficient frontier and heterogeneous
scalar-profile frontier. They are not claimed novel or publication-ready; exact
statement/correctness and primary-literature comparisons remain explicit tasks.
Relationships: 17 reviewed inventories, 205 pending, 644 unreviewed; formalization
866 reviewed. No new canonical edge was inferred in this classification batch.


Compact-evidence batch `index_metadata_batch5_20260919`: 60 records covering column
freezing, local partitions, compatible layouts, selector profiles and the open
source bridge were classified. Status/topics: 282 reviewed, 584 unreviewed.
Significance: 277 reviewed, five pending audits, 584 unreviewed. Relationships:
17 reviewed, 265 pending, 584 unreviewed. Formalization remains 866 reviewed.
Standard matching/sampling/replay inputs are explicitly treated as known, and the
open source-family bridge is context rather than an established theorem. No new
canonical edge or mathematical result was inferred. Source packets and decisions
are retained in the batch evidence directory.


Compact-evidence batch `index_metadata_batch6_20260919`: 80 matching, moment-design,
query-obstruction and affine-pair/source-interface records classified. Status/topics:
362 reviewed / 504 unreviewed. Significance: 355 reviewed, seven pending targeted
audits, 504 unreviewed. Relationships: 17 reviewed inventories, 345 pending,
504 unreviewed; canonical edges now 43. Two edges correct only vacuous source
applications, retaining the algebraic statements; query attacks obstruct a criterion's
premise and refine its description class, not Frege itself. Two further possible
independent query-rate results are queued for audit, with no novelty assertion.
Added reusable topic definitions for moments, query models, pseudorandomness and
topological methods. Full dependency inventories remain the largest semantic
backlog; the next route review should assess closure of that backlog rather than
using classification counts as completion evidence.


Dependency route review `index_dependency_review_20260919`: classification counts
were advancing while complete relationship reviews remained at 17. A connected
six-claim matching/normalization audit now closes six pending inventories and adds
12 scoped current/historical/external edges. Totals: 23 reviewed inventories,
339 pending, 504 unreviewed; 55 canonical edges. Abstract-lemma prerequisites are
separated from later applications and historical provenance. The source-relative
review reuses the existing Razborov audit, not a new paper verification.

The discovery tool now indexes named equation references against source tags;
local definitions are excluded, repeated/shared ownership is flagged, and target
definition hashes participate in staleness. This finds 190 additional candidates
(2,091 total) and fixes the concrete omission that blocked this cluster. One RA
reference is accepted against the reviewed proof edge. Eleven discovery tests
pass. This is a scalable retrieval improvement, not automatic semantic acceptance.
Continue closing connected dependency clusters alongside the remaining backfill;
neither sampled closure nor candidate count completes the full graph plan.


Normalizer dependency cluster `index_normalizer_dependencies_20260919`: twelve
pending inventories closed, from the resistant finite example through affine
companion inconsistency. Twenty-seven scoped edges distinguish imported reuse/
field reduction/substitution, NS cofactor reasoning, method refinements, positive
controls and dataset provenance. Three QA-7/C3-7/CAD equation candidates accepted
against the actual finite deduction. Totals: 35 reviewed inventories, 327 pending,
504 unreviewed; 82 canonical edges. Historical computation reports were inspected
for meaning, not rerun or recertified. Classification totals and seven pending
significance audits are unchanged.


Source/preprocessing cluster `index_source_dependencies_20260919`: fifteen pending
inventories closed, 29 new scoped edges (four existing edges retained), bringing
totals to 50 reviewed / 312 pending / 504 unreviewed inventories and 111 edges.
Imported BIKPRS inputs point to the existing source audit. Accuracy-two refinements
and the distinct 6p-2/4p-2 MOD images retain their actual scope. The MOD identity and
its surrounding certificate have a provenance citation cycle, not a proof cycle.

User explicitly authorized parallel migration work on 19 September 2026. The completed
bounded assignments were: classifications [360,520), [520,680), [680,end); dependency
closure [48,160), [160,360); derived topic views and duplicate-discovery tooling.
Workers write disjoint patch/evidence directories under research/results/parallel_index_*;
the coordinator alone integrates canonical metadata, notebook records and checkpoints.
Respect existing reviewed seeds, validate source fingerprints, and retain pending
questions. This authorizes delegation for the migration, not publication or new
formalization work. Worker artifacts are integrated only after review; do not stage
other workers' in-progress files into an unrelated checkpoint.
