# Moment, query and source-scope metadata batch

Baseline: b1948e9. Session: index_metadata_batch6_20260919.
Notebook: entry-2026-09-19-index-moment-query-metadata.

80 existing records were classified from original assessments and selected source
qualifications. Four reviewed edges record two scoped source-application corrections,
a query-criterion obstruction and a shallow-query refinement. No new mathematics.
Two further significance candidates remain pending a correctness/literature audit.

Reproduce through `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND`, using fresh output paths:

- `python3 research/results/index_metadata_batch6_20260919/collect.py --out PATH`
- `python3 research/results/index_metadata_batch6_20260919/curate.py --out PATH`
- `tools/claim-index.py changed --base b1948e9 --out PATH`
- `tools/claim-index.py validate --out PATH`
- `tools/claim-index.py graph audit --out PATH`

Coverage: status/topics 362 reviewed, 504 unreviewed; significance 355 reviewed,
seven pending, 504 unreviewed; relationships 17 reviewed, 345 pending, 504 unreviewed;
formalization 866 reviewed. Canonical graph: 43 edges. The algebraic statements
remain valid in scope despite the two recorded vacuous source applications.
