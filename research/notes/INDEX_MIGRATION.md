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

## Scope and completion discipline

- Sections 1–5 record the completed structural migration, not completed metadata
  curation. Sections 6–13 track the ongoing enrichment; completion is marked item by item.
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
- [ ] Inventory every claim against its source using automated parsing and evidence
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

- [ ] Inventory all per-claim Lean files, declarations, route maps, verification
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
- [ ] Populate the Res(⊕) bit-PHP publication theorem, exponential corollary and
      dependency route from their existing records, retaining both rule conventions
      and exact parameter/encoding scope.
- [ ] Audit consistency between informal scope, structured coverage, Lean links
      and recorded verification evidence. Distinguish inspecting existing evidence
      from performing a fresh kernel replay.
- [x] Complete a coverage report for the entire index: every claim has a reviewed
      formalization disposition or a specifically recorded unresolved item.

## 8. Mathematical status, topics, compression and deduplication

- [ ] Populate mathematical status independently of formalization and significance:
      working proof, established/imported result, conditional result, conjecture,
      finite check, refutation, correction/retraction, or contextual record as appropriate.
- [ ] Define a small reusable topic taxonomy with descriptions and stable IDs;
      allow multiple topics per claim. Separate topic, object/proof system, and
      current-route membership where those distinctions are useful.
- [ ] Assign topics across all claims, resolving ambiguous and uncategorized cases
      explicitly rather than leaving an unexamined tail.
- [ ] Generate a compact topic map and topic-specific index views; choose their
      layout without creating a second editable source or breaking existing links.
- [ ] Run similarity-based duplicate discovery as a review aid. Check hypotheses,
      encodings, quantifiers and costs before classifying any pair.
- [ ] Record true duplicates, rediscoveries, refinements, supersessions and
      corrections with stable-label relationships. Do not delete or conflate claims
      because their wording is similar.
- [ ] Provide active and historical/retracted views, retaining lookup of every old
      label and visible correction warnings. A parked result remains discoverable.
- [ ] Compress generated display text and links where useful while retaining full
      exact scope through lookup. Ensure links work on GitHub, locally and on Pages;
      a bare notebook anchor in a Markdown file is not automatically a valid link.

## 9. Populate and audit relationship data

- [ ] Extract candidate citations from the entire Research record and claim source
      passages, mapping entry anchors to claims without assigning an entry's every
      citation to every claim in that entry.
- [x] Build reusable dependency discovery tools for notebook hyperlinks, explicit
      dependency language/lists, claim-label mentions, Lean imports and declaration
      references. Retain source anchors/lines, extraction method, ownership ambiguity
      and proposed relationship type for every candidate; report unresolved targets.
- [ ] Review every claim's direct proof dependencies through that evidence inventory.
      Accept justified explicit information without a redundant full-entry reread;
      inspect targeted passages when the tool cannot resolve meaning or ownership.
      Do not treat imports/citations alone as proof dependencies, or a partial
      publication/frontier audit as completion of the entire graph.
- [ ] Add bounded candidate lookup, deduplication and decision tracking so reviewed,
      rejected and pending suggestions survive reruns and compaction. Test ambiguous
      shared entries, unused imports, negated dependency language, local definitions,
      corrections and stale evidence; retain human review for semantic uncertainty.
- [ ] Populate `depends_on`, `cites`, `refines`, `supersedes`, `corrects`,
      `rediscovers`, `formalizes`, `applies`, and `obstructs` wherever justified;
      define direction and meaning consistently and preserve evidence locators.
- [ ] Distinguish required dependencies from alternative proofs, contextual
      citations, tests and counterexamples. Record scope/conditions where an edge
      applies to only part of a claim or one proof.
- [ ] Resolve historical and external endpoints through stable identities and
      locators, leaving the immutable handoff untouched. Decide how entry, method,
      Lean-artifact and publication nodes are represented when they are not claims.
- [ ] Seed reviewed edges with the documented publication dependency route and
      active tools, then continue through the complete index with coverage tracking.
- [ ] Mark pending edge reviews and claims whose dependencies have been inspected
      but found empty. Do not conflate either case with unexplored dependencies.
- [ ] Validate endpoints, duplicate/conflicting edges, self-links, and cycles;
      distinguish genuine circular proof dependencies from harmless cycles of citation.
- [x] Add predecessor/successor, ancestor/descendant, "what cites this", and
      correction-impact queries. Report that impact is an audit scope, not a proof
      that every descendant is invalidated.

## 10. Populate claim significance

- [ ] Define structured significance assessments with rationale, exact scope,
      novelty status, source evidence, review date and suggested action. Keep
      independent interest, novelty, correctness and publication readiness separate.
- [x] Populate the known Res(⊕) publication result and its corollaries first, using
      the recorded literature/dependency audits and current external-review status;
      do not leave them null or promote an internal assessment to external confirmation.
- [ ] Screen every remaining claim for independent interest, reusable tools,
      meaningful negative results and corrected published claims. Include finite
      checks and failed attempts that expose valuable counterexamples.
- [ ] Perform targeted literature checks for plausible candidates, preserving
      exact formulations, encodings, versions, dates, uncertainty and source links.
- [ ] Complete significance coverage for all claims: a reasoned disposition or an
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

- [ ] Publish a coverage report for all baseline and subsequently added claims:
      populated metadata, reviewed dispositions, pending questions and stale evidence.
- [ ] Demonstrate a new claim travelling through registration, exact/minimal lookup,
      topics, relationship recording, significance and formalization metadata without
      duplicated manual bookkeeping. No graph UI or Fossick implementation is required.
- [ ] Demonstrate a correction updating source links, scope, affected relationships
      and review tasks without rewriting the historical notebook record.
- [ ] Exercise interrupted/resumed curation and existing parallel append integration
      against the structured source, preserving stable IDs and accepted records.
- [ ] Run schema, generation, retrieval, metadata, relationship and portability
      checks; preserve full evidence and reproducibility data at checkpoints.
- [ ] Document the minimal index editing/curation workflow and remove superseded
      index instructions or tools after compatibility is accounted for.
- [ ] Review completion against IDEAS.md item 5 and the conversation's index-specific
      requirements. Report every metadata gap explicitly; do not make completion
      depend on implementing the separately owned framework plans.

## 13. Enforce metadata maintenance in every subsequent research cycle

This is an ongoing requirement, not only a one-time enrichment pass. Update the
workflow during implementation of this phase. The changed-claim contract is now
active; the unchecked items below still need implementation or acceptance evidence.

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
- [ ] Update `research/notes/RESUME.md` to restore the populated index, taxonomy,
      relationship semantics, pending reviews and the maintenance contract through
      bounded tools. Restoration must not silently revert to Markdown-only editing
      or import the entire index into context.
- [x] Update `PROMPTS.md`: Spin, ordinary research guidance, Formalize,
      Spin-formalize and existing parallel variants must apply the same index
      maintenance contract within their assigned scope. Expose that contract for
      future prompts owned by the separate plans; do not implement those prompts here.
- [ ] Update the registry guide, authoring tools and templates so a new claim is
      created with the required metadata and relationship review, rather than
      inheriting the initial migration's all-null defaults.
- [x] Add changed-claim/relationship completeness checks to cycle finalization
      and CI, with useful diagnostics. Track historical backlog separately so the
      checks neither excuse incomplete new work nor repeatedly demand a full audit
      of the whole registry on every turn.
- [ ] Regenerate human/topic views and machine-readable exports at checkpoints;
      keep pending index metadata reviews visible after compaction, branch integration
      or migration. Graph rendering and notifications are owned by their separate plans.
- [ ] Test a fresh cycle, a correction, a formalization update and parallel branch
      integration end to end. Verify that incomplete new metadata is caught and
      that justified unknown/not-applicable states are represented honestly.
- [ ] Include this ongoing-maintenance phase in the overall acceptance review;
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

The structural migration is complete. Index metadata enrichment remains in this
plan; the other framework features now have separate plans linked above.

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
