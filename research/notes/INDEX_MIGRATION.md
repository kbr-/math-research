# Claim-index migration checklist

Migrate the complete continued-research index before restarting research, with
compact retrieval and future graph navigation in mind. This implements item 5
of [IDEAS.md](../../IDEAS.md), preparing for items 7 and 8.

The structured index will be authoritative for claim metadata; the notebook
remains authoritative for mathematical statements, proofs, and current research
status. Preserve the historical handoff unchanged.

Mark tasks complete only after implementation and validation. Record concrete
paths, decisions, and checkpoint references here as work proceeds. Leave partial
tasks unchecked and briefly note what remains.

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

## 5. Workflow integration and completion

- [x] Update affected tools and concise workspace guidance to use the structured
      source; consolidate existing rules rather than adding duplicate instructions.
- [x] Update the resume reading guide only where navigation changes, keeping full
      index loading out of routine context restoration.
- [x] Document how to add or revise a claim, regenerate views, and validate changes.
- [x] Preserve conversion tooling, reconciliation evidence, and essential outputs
      in the repository. Follow the computation policy for substantial jobs.
- [x] Review and commit coherent implementation checkpoints locally, updating this
      checklist after each. Publishing remains subject to explicit authorization.
- [x] Confirm the full migration is complete: structured source authoritative,
      Markdown generated, retrieval working, validation passing, and no unresolved
      loss of original index content.

## Deferred work

- [ ] Schedule semantic deduplication, topic curation, and dependency review as
      separate follow-ups; preserve all stable labels and correction history.
- [ ] Build Fossick and significance tracking on the structured source when assigned.
- [ ] Build interactive graph navigation after sufficient relationship data has
      been reviewed; visualization is not a prerequisite for this migration.

## Implementation notes

Completed implementation session: `index_migration_20260919`.
Local checkpoint title: "Migrate the complete claim index to a structured registry".

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

Deferred work is not part of the migration's completion criterion.

- Generated view and compact lookup are implemented; the complete export and
  qualified/ranked lookup examples are preserved with the evidence.
- Parallel append merges operate on JSON and regenerate Markdown; existing-record
  changes remain manual. Turn finalization, checkout validation and CI detect stale views.
- Focused suites pass: 14 registry, seven append-merge and six finalization tests.
- The user confirmed the repaired table renders correctly. No mathematical entries
  or original claim text were edited. Semantic curation and visualization remain deferred.
