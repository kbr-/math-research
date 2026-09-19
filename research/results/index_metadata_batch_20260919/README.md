# First chronological metadata batch

Baseline: f9782de127b6c23ea41d0d3a0bd20b02ce0f53df.
Session: index_metadata_batch_20260919.
Notebook: entry-2026-09-19-index-first-metadata-batch.

The manually reviewed curation decisions live in `curate.py`. It updates 14
claims and the telescoping seed's incoming-relationship review, retaining original
text. Twenty-two scoped edges include seven historical citations. No new proof,
novelty claim, literature search or kernel verification is asserted.

Reproduce from the baseline plus checkpoint tools, through `./compute.sh run
SESSION --threads 1 --category local_processing -- COMMAND` with fresh outputs:

- `python3 research/results/index_metadata_batch_20260919/curate.py --out PATH`
- `tools/claim-index.py coverage --out PATH`
- `tools/claim-index.py validate --out PATH`
- `tools/claim-index.py graph audit --out PATH`
- `tools/claim-dependencies.py packet --claim thm:matching-affine-annihilators
  --out PATH -n 4`
- `python3 -m unittest discover -s tools/tests -p 'test_claim*.py'`

Coverage: 17 reviewed, 849 unreviewed for status/topics/significance/relationships;
866 reviewed formalization dispositions. Graph: 27 edges, no structural findings.
No complete source/graph audit is implied. The user identified avoidable broad
reading during this batch; packet-first curation is now documented and tested.
