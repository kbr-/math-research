# Copy, interface and cleanup metadata batch

Baseline: c838d05. Session: index_metadata_batch3_20260919.
Notebook: entry-2026-09-19-index-copy-cleanup-metadata.

80 existing claims have reviewed recorded status, topics and local significance.
The manually reviewed classification choices are in curate.py, keyed by immutable
packet order with exact summary/assessment checks. Original text and formalization
metadata remain unchanged. No new edges or novelty claims were inferred.

Reproduce through `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND`, using fresh output files:

- `python3 research/results/index_metadata_batch3_20260919/collect.py --out PATH`
- `python3 research/results/index_metadata_batch3_20260919/curate.py --out PATH`
- `tools/claim-index.py changed --base c838d05 --out PATH`
- `tools/claim-index.py validate --out PATH`

The saved packets preserve selected source passages and omission flags. Source
hypotheses, finite checks, repairs and rediscoveries are retained. This is recorded
metadata curation rather than a fresh correctness audit. Relationship reviews name
specific source-region follow-ups and remain pending: 17 reviewed, 125 pending,
724 unreviewed. Status/topics/significance: 142 reviewed and 724 unreviewed.
Formalization: 866 reviewed. The canonical graph remains at 39 edges.
