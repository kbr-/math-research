# Compact-evidence normalization/source metadata batch

Baseline: 9d54a664e2fc42d9552628482f7c5b41070e9fcb.
Session: index_metadata_batch2_20260919.
Notebook: entry-2026-09-19-index-normalization-metadata.

45 claims have reviewed recorded status/topics/significance and explicit pending
relationship inventories. Twelve scoped edges were added, while incoming reviews
on three previously curated records were refreshed. All original claim text and
formalization dispositions remain unchanged. No new mathematical or novelty audit.

Reproduce via `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND` with fresh paths:

- `python3 research/results/index_metadata_batch2_20260919/collect.py --out PATH`
- `python3 research/results/index_metadata_batch2_20260919/curate.py --out PATH`
  uses packets-reviewed.json beside the script and checks exact summary/assessment
  identity before applying the manually reviewed classifications.
- `tools/claim-index.py changed --base 9d54a66 --out PATH`
- `tools/claim-index.py validate --out PATH`
- `tools/claim-index.py graph audit --out PATH`
- `python3 -m unittest discover -s tools/tests -p test_claim_dependencies.py`

packets.json predates inequality-safe markup stripping; packets-final.json is an
intermediate repair; packets-reviewed.json is the final TeX-protected output.
They are preserved as extraction evidence, not competing editable claim sources.
The compact log excerpts were bounded; complete selected packets stay on disk.

Coverage is included in maintenance.json: 62 reviewed/804 unreviewed for status,
topics and significance; relationships 17 reviewed, 45 pending, 804 unreviewed.
Formalization: 866 reviewed. Graph: 39 edges, no structural findings. Unlinked
local equations/setup are a specific remaining source of graph-review work.
