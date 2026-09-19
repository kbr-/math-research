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

- [ ] Pin the pre-migration Git revision and inventory every row, label, link,
      status qualification, and formalization reference in `research/CLAIM_INDEX.md`.
- [ ] Identify tools and instructions that read or edit the current Markdown index.
- [ ] Choose and document the structured file location and schema version.
- [ ] Define claim records with stable IDs preserving existing labels, statement
      summaries, mathematical status, source links, formalization coverage, and
      optional topics. Preserve exact legacy text where structured fields alone
      would lose qualifications.
- [ ] Keep mathematical status, formal verification, and significance distinct;
      represent missing or unreviewed information explicitly without guessing it.
- [ ] Define graph-ready relationship records: source and target IDs, type,
      supporting source location, and review status. Support `depends_on`,
      `refines`, `corrects`, `supersedes`, and other justified relationship types.
- [ ] Specify how references to historical claims and external sources are
      represented without modifying or absorbing the historical handoff index.

## 2. Complete structural migration

- [ ] Implement a reproducible importer with an explicit output destination and
      diagnostics for ambiguous or unparsed rows; do not silently drop content.
- [ ] Convert every existing continued-research claim into the structured source.
- [ ] Preserve every original label, summary, status qualification, link, and
      formalization scope; resolve parsing ambiguities against the original row.
- [ ] Preserve existing ordering and grouping where applicable, without merging,
      renaming, or reclassifying mathematical claims during conversion.
- [ ] Retain citations as citations. Leave dependency edges unreviewed or absent
      unless their type is supported by the record; a hyperlink alone is not a
      proof dependency.

## 3. Generated index and compact retrieval

- [ ] Generate `research/CLAIM_INDEX.md` deterministically from the structured
      source, preserving usable public links and existing reference targets.
- [ ] Clearly mark the Markdown as generated and document the authoritative edit path.
- [ ] Adapt `tools/search-claims.py` to query the structured source and return
      bounded results containing the claim ID, concise summary, status, and source.
- [ ] Add exact-label lookup that exposes the complete claim metadata and links
      to the relevant notebook statement or proof without loading the full index.
- [ ] Support useful filters where metadata is available; make omitted results
      and unknown fields visible. Do not require a complete topic taxonomy first.
- [ ] Provide a stable machine-readable lookup/export interface for later Fossick
      and graph tools, without building those tools in this migration.

## 4. Validation and regression coverage

- [ ] Produce a migration reconciliation report against the pinned original:
      every row and label accounted for, all source text and links preserved,
      and any normalization or exception explicitly documented.
- [ ] Validate unique IDs, required fields, schema versions, and relationship
      endpoints; preserve distinctions between unknown and verified metadata.
- [ ] Check repository-local files and notebook anchors, and preserve external
      destinations without treating their availability as proof verification.
- [ ] Verify deterministic generation and add a check that detects stale generated
      Markdown relative to the structured source.
- [ ] Test meaningful retrieval and migration cases, including qualified or partial
      formalizations, multiple links, corrections, unusual table syntax, and
      malformed records. Ensure searches still find representative known claims.
- [ ] Confirm graph consumers can distinguish citations from reviewed dependencies
      and that missing edges do not imply mathematical independence.

## 5. Workflow integration and completion

- [ ] Update affected tools and concise workspace guidance to use the structured
      source; consolidate existing rules rather than adding duplicate instructions.
- [ ] Update the resume reading guide only where navigation changes, keeping full
      index loading out of routine context restoration.
- [ ] Document how to add or revise a claim, regenerate views, and validate changes.
- [ ] Preserve conversion tooling, reconciliation evidence, and essential outputs
      in the repository. Follow the computation policy for substantial jobs.
- [ ] Review and commit coherent implementation checkpoints locally, updating this
      checklist after each. Publishing remains subject to explicit authorization.
- [ ] Confirm the full migration is complete: structured source authoritative,
      Markdown generated, retrieval working, validation passing, and no unresolved
      loss of original index content.

## Deferred work

- [ ] Schedule semantic deduplication, topic curation, and dependency review as
      separate follow-ups; preserve all stable labels and correction history.
- [ ] Build Fossick and significance tracking on the structured source when assigned.
- [ ] Build interactive graph navigation after sufficient relationship data has
      been reviewed; visualization is not a prerequisite for this migration.

## Implementation notes

Implementation has not started. This checklist records the agreed scope; the
deferred work is not part of the migration's completion criterion.
