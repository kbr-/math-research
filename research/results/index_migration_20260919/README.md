# Claim-index migration evidence

Baseline: `21603c76b82afcc8d91014fa752e61e5cab690ac`.
The [notebook record](https://kbr.is-a.dev/math-research/#entry-2026-09-19-structured-index-migration)
describes the completed framework cycle; the [registry guide](../../claims/README.md)
documents schema, editing, commands, and reproduction of the original import.

- `reconciliation.json`: every original row and all three text fields compared
  verbatim, 866 labels/order preserved, 1,241 claim links accounted for, and
  rendering-only escapes listed for 22 rows. Table-internal blank lines are removed.
- `initial-validation.json` and `validation.json`: schema/target/generation checks,
  including all 1,242 references with the preamble. No external retrieval or proof
  verification is implied by a successful link check.
- `claims-export.json`: complete versioned machine view with derived reference
  objects and explicit incomplete relationship coverage. No dependency was inferred.
- `qualified-lookup.json`: exact lookup retaining the telescoping claim's mixed
  verification/correction scope. New classification fields are explicitly unknown.
- `ranked-lookup.json`: three complete selected search records, with 310 omitted
  matches reported. The known support lower bound ranks first for the recorded query.
- `provenance.json`: hashes of the registry, tooling, tests, documentation and reports.
- `timing.html` and the accompanying session archive: measured phases and complete
  outputs of the import, validation, lookup/export and focused test commands.

Final focused coverage: 14 registry tests, seven legacy append-merge tests, and
six turn-finalization tests. The registry suite includes a real structured rebase;
the finalizer suite checks stale generated data does not stop a running clock.
Tests and tooling use the standard library; no package was installed.

The source Markdown is reproducible via `git show BASELINE:research/CLAIM_INDEX.md`.
Importing is a one-time operation with new output paths. Routine edits change
`research/claims/index.json` and regenerate the Markdown; semantic curation is
separate. The notebook and historical handoff remain the mathematical sources.
