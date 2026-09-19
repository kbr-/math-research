# Isolated dependency merger

`merge.py` creates a registry **proposal** and review report. It never modifies
canonical registry/notebook/Git state. Its outputs are restricted to this
isolated directory. Start from the live registry on every run; do not install an
old proposal over later coordinator changes.

```bash
./compute.sh run YOUR_SESSION --threads 1 --category local_processing --timeout 180 -- \
  python3 research/results/parallel_index_dependency_merge/merge.py \
  --manifest research/results/parallel_index_dependency_merge/manifest-reviewed.json \
  --out research/results/parallel_index_dependency_merge/FINAL-proposal.json \
  --report research/results/parallel_index_dependency_merge/FINAL-report.json
```

`--patch PATH` adds ordered patches after the manifest (repeatable). A manifest
has `patches` in integration order; entries may be paths or `{path,sha256}`
objects. Explicit candidate evidence files use `candidates`, or repeat
`--candidates PATH`. Without a manifest, discovery follows the worker READMEs and
520–680 delivery list, choosing cumulative final files rather than old snapshots.
`--write-manifest PATH` records that selection; review coverage if workers are
still writing final batches. Amendments/resolutions are last in each worker's
sequence. Delivered patch contents are never rewritten.

## Safety and output interpretation

- Pinned baseline commits, exact claim core fields and evidence are checked.
  Both Python JSON ASCII serialization conventions are accepted only when the
  hash actually matches the pinned/current core. Source rows with explicit
  evidence hashes must match them too. Rows lacking explicit evidence hashes
  are compared directly against the source at their pinned revision.
- Endpoint namespace/type determines canonical edge IDs. The generic external
  BIKPRS year-bearing alias is normalized to `BIKPRS-audited-source-inputs`.
- Canonical reviewed scope text is retained for exact duplicates or explicitly
  reviewed equivalent descriptions in `equivalent_scopes`; arbitrary different
  scopes are reported as conflicts, never silently combined. Fourteen exact
  pairs in the supplied reviewed manifest were compared, including the six
  already identified by the 48–160 worker.
- The reviewed manifest has one explicit source typo repair for the homological
  cover article. Paragraph-only references widen to their exact containing
  section via the existing excerpt helper. Original and normalized locators are
  both retained in the report. Such broadening is not semantic ownership proof.
- Proposed-edge removals cannot delete a canonical edge. Existing/new root
  claims and every non-relationship field are preserved. The merger never
  changes mathematical status; incoming corrections/supersessions produce an
  explicit coordinator status-review list.
- Merge all edges before fingerprinting inventories and incident endpoints.
  Untouched outgoing inventories retain their prior state; absent ones remain
  specifically pending. A new reviewed worker disposition cannot erase a newer
  pending coordinator question silently. Changed pinned core/source data blocks
  that stale worker disposition.
- Candidate decisions require their actual inventory fingerprint, current source
  and claim evidence, and matching accepted-edge endpoints. ID remappings are
  applied to decisions. Existing canonical decisions are preserved, not newly
  certified by this merge.
- Report includes exact input revision/registry hash, patch hashes, source and
  semantic conflicts, local link validation, graph cycles/locator diagnostics,
  missing inventories and correction targets. Input mutation during the run is
  detected and makes the proposal unready. Dependency cycles require review;
  readiness is not certification of mathematical correctness or plan completion.

The first run reported genuine formatting/duplicate descriptions, retained in
`report.json`. The explicitly reviewed normalization run yielded 816 proposed
inventories, no conflicts and no dependency cycles, before the coordinator's
final live edits. Rerun for current numbers. `proposal-reviewed.json` is a
snapshot for inspection only.

`test_merge.py` exercises stale core rejection, stale candidate rejection,
canonical scope preservation under conflict, refusal to delete canonical edges,
endpoint/BIKPRS normalization, canonical output-path protection, and preservation
of new root claims/non-relationship fields. Seven tests passed under protected
execution. No semantic claim curation or mathematical argument was added here.
