# Structured Git merge drivers plan

Draft: 20 September 2026. Implements
[IDEAS.md item 10](../../IDEAS.md#10-structured-git-merge-drivers-for-notebook-and-claim-additions).
Status: **planned, not implemented**. Planning does not install drivers or
change Git behavior. Mark tasks complete only after implementation and validation;
record concrete decisions, evidence and checkpoint references here.

## Intended outcome

Resolve independent notebook appends, claim-registry changes and attention-history
additions automatically during merge/rebase, while retaining genuine conflicts.
Preserve mathematical records and review provenance; a syntactically valid merge
must not silently certify incompatible mathematical changes.

This works for the existing main notebook without requiring side notebooks.
[SIDE_BRANCHES_PLAN.md](SIDE_BRANCHES_PLAN.md) separately owns research-thread
identity, creation, serving and tool selection. When side notebooks are available,
the same merge rules should apply through their shared identity/source interfaces.

## 1. Merge rules

Consolidate/generalize `tools/merge-formalization-appends.py`; avoid a parallel
one-off resolver. Support ordinary merges and merge-backend rebases. Document any
unsupported backend explicitly. Extra whitespace and line-based `merge=union`
are not substitutes for preserving complete structured records.

- [ ] Notebook driver: parse complete articles by stable ID, verify base records
      are preserved byte-for-byte and in order on both sides, and combine independent
      additions without splitting HTML or timing tables. Deduplicate identical
      additions; reject differing content with the same ID, altered/deleted history,
      malformed markup and incompatible ordering constraints.
- [ ] Preserve each branch's sequence of additions. Define a deterministic ordering
      for independent additions and respect explicit dependency constraints where
      available. Do not globally reorder historical entries by timestamps.
- [ ] Merge living sections and surrounding structure with ordinary three-way
      semantics. Preserve genuine competing edits as conflicts; never silently
      choose the main overview and discard a side's changes to the same notebook.
      Distinct side notebooks should survive integration intact.
- [ ] Registry driver: three-way merge claims and relationships by ID; accept
      independent additions and compatible field changes. Reject divergent same-ID
      additions, same-field competing edits and delete/edit conflicts. Treat arrays
      according to their schema rather than blindly concatenating them.
- [ ] Handle coupled review fields conservatively. Combining a statement edit on
      one branch with a review on another must not certify the combined statement.
      Existing evidence/value hashes determine staleness; require explicit review
      when needed, never fabricate a refreshed approval to make the merge pass.
- [ ] Attention driver: combine distinct events while preserving each side's history
      order. Deduplicate only identical events; equal timestamps alone are not
      identity. Conflicting dispositions without a justified ordering require review.
- [ ] Generated views: regenerate claim indexes, topic views and attention Markdown
      only after authoritative inputs are merged. Define a reliable integration
      command/checkpoint because Git does not guarantee per-file driver order.
      A clean Git merge is not a successful checkpoint while derived views are stale.
- [ ] Track code and `.gitattributes`, and provide idempotent per-clone Git driver
      registration without overwriting unrelated configuration. Fresh clones must
      detect missing setup; ensure unsupported/missing drivers cannot silently
      bypass required validation. Installation does not authorize publication.
- [ ] Rewritten commit hashes: a `post-rewrite` hook (rebase and amend) applies the
      old→new pairs to recorded hashes (registry review `revision` fields, publication
      Lean pins and repository citations) and regenerates derived views. A check
      rejects any recorded revision or pin that is not an ancestor of the checked
      branch. See the 25 September 2026 note in IDEAS.md item 10, which also records
      21 stale revisions already on `main` and how their mapping was recovered.
- [ ] On driver failure, leave recoverable inputs and actionable conflicts. Test
      abort/retry/continue paths and require the existing post-merge checks before
      committing or publishing the integrated result.

## 2. Validation and rollout

- [ ] Inventory the existing resolver, generated-view workflow and Git configuration.
      Pin representative conflict fixtures before changing behavior.
- [ ] Test real merges and merge-backend rebases in disposable repositories:
      concurrent notebook appends, identical/divergent IDs, altered/deleted history,
      malformed structure, living-section conflicts and incompatible entry order.
      Verify complete articles and timing tables survive without interleaving.
- [ ] Test independent and competing claim/relationship changes, delete/edit cases,
      coupled statement/review edits and stale evidence. Confirm no review hashes
      or dispositions are fabricated and genuine conflicts remain actionable.
- [ ] Test hash remapping: rebase and amend a branch whose registry and publication
      pins name its own commits; confirm every recorded hash is remapped, and that the
      ancestor check fails on a deliberately stale hash.
- [ ] Test attention-event deduplication, equal timestamps, incompatible history
      order and conflicting decisions. Confirm the current disposition is not
      chosen accidentally by concatenation order.
- [ ] Verify generated views become current only after authoritative inputs merge.
      Test regeneration failures and ensure checkpoint checks reject stale output.
- [ ] Test per-clone installation, missing configuration, unsupported backends,
      abort/retry/continue and driver failures. Preserve unrelated Git settings.
- [ ] Run structural, append-only, registry/evidence and generated-view checks
      against both input histories. Retain reproducible fixtures and results.
- [ ] Document setup and recovery in existing workflow guidance, replacing obsolete
      resolver instructions. Enable automatic resolution only after acceptance;
      commit locally and publish only under applicable user authorization.

Suggested order: pure merge functions and falsifying fixtures; real Git-driver
integration; coordinated regeneration and validation; setup/recovery documentation.
Support the current notebook first, then cover registered side notebooks when that
separate feature exists. Do not delay ordinary side-notebook use until drivers ship.

## Boundaries with other plans

[SIDE_BRANCHES_PLAN.md](SIDE_BRANCHES_PLAN.md) owns notebook identity and source
routing. [INDEX_MIGRATION.md](INDEX_MIGRATION.md) owns the authoritative claim and
review schema. [PARALLEL_RESEARCH_PLAN.md](PARALLEL_RESEARCH_PLAN.md) owns agent
coordination. This plan supplies integration mechanics, not new mathematical
review policy, permission to spawn agents or automatic publication authorization.
