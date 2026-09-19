# Recorded formalization metadata and dependency discovery

Baseline: `5ed10d8692edfc66d77f7425ee5cd31fa9b87124`.
Session: `index_formalization_metadata_20260919`.
Notebook: `entry-2026-09-19-index-evidence-discovery`.

This is source-metadata curation, not new mathematical verification. Original
claim summaries, assessments, records and ordering are unchanged.

## Reproduction

Run commands from the repository root through `./compute.sh run SESSION
--threads 1 --category local_processing -- COMMAND`. Use a fresh session and
output directory for a new audit; do not overwrite checkpoint evidence.

1. `python3 research/results/index_formalization_metadata_20260919/inventory.py
   --out PATH`: inventory explicit Lean mappings, headers, declarations and hashes.
2. `curate_formalization.py --out PATH` (same directory): use the inventory beside
   the script, claim links and recorded successful named axiom reports. This
   updates canonical registry metadata; the three earlier curated records are
   preserved. No Lean process is run. `formalization-curation-audited.json` is
   the final report; earlier reports/scripts retain development evidence.
3. `record_unmapped.py --out PATH` (same directory): record the bounded negative
   mapping census for claims without explicit mappings. A corpus fingerprint
   invalidates these dispositions when per-claim Lean files change.
4. `tools/claim-dependencies.py scan --out PATH`: regenerate evidence candidates.
   `dependency-candidates.json` is final; `dependency-candidates-initial.json`
   predates non-heading-anchor fallback and full fingerprint handling.
5. `tools/claim-dependencies.py show --input PATH --claim CLAIM -n 10`:
   inspect bounded excerpts. `decide` records judgments separately from graph
   edges; see `research/claims/README.md`. Accepted calibration candidate
   `ba9f0e8df88ec0a13f29bf5f` matches an already-reviewed publication dependency.
6. `tools/claim-index.py coverage --out PATH` and
   `tools/claim-index.py validate --out PATH` produce the coverage and validation
   reports. `python3 -m unittest discover -s tools/tests -p 'test_claim*.py'`
   runs the 28 focused registry/discovery tests.

## Scope and exceptions

- 76 per-claim Lean files: 75 index claims have explicit coverage; the otherwise
  unmapped publication-revision file is an import-only assembly.
- 74 complete, one partial, 791 bounded no-record dispositions. A no-record
  disposition is not proof of absence of formalization elsewhere.
- Shared source files have claim-specific declarations/scopes. The chessboard
  filling specification is retained separately from its proof artifact.
- Recorded verification selection requires actual named axiom reports with the
  standard axiom set. A misleading failed `kernel-verification-final.txt` was
  excluded after strengthening this check; the successful complete report is used.
  Exported helper names without individual reports remain in the inventory, not
  in the list of individually audited declarations.
- 1,901 dependency candidates cover 866 claims and 75 linked Lean files. Nine
  widened source regions carry ambiguity flags; two links have no mapped claim
  owner. No candidate scan creates a canonical edge. Lean name occurrences are
  heuristic evidence, not elaborated proof dependencies.
- The full graph, historical/external mappings and unindexed record passages
  still need curation. Other metadata fields retain 863 unreviewed claims each.

The session archive preserves command outputs and timing; provenance.json hashes
checkpoint artifacts. No packages were installed and no fresh kernel replay or
literature audit was performed.
