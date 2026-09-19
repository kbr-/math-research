# Normalizer and finite-certificate dependency cluster

Baseline: 9f9b33c. Session: index_normalizer_dependencies_20260919.
Notebook: entry-2026-09-19-index-normalizer-dependencies.

Twelve existing inventories are closed by source-relative proof review. Twenty-seven
edges separate proof inputs, applications, method refinements and dataset provenance.
Three equation candidates are accepted using the saved discovery report from
index_dependency_review_20260919. No historical computation or paper audit was rerun.

Reproduce through `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND`, using fresh outputs:

- `python3 research/results/index_normalizer_dependencies_20260919/curate.py --out PATH`
- `tools/claim-index.py changed --base 9f9b33c --out PATH`
- `tools/claim-index.py validate --out PATH`
- `tools/claim-index.py graph audit --out PATH`

Totals: 35 reviewed dependency inventories, 327 pending, 504 unreviewed; 82 edges.
Status/topics remain 362 reviewed, significance 355 reviewed plus seven pending;
formalization remains 866 reviewed. Accepted finite evidence is reported with its
original scope, not presented as newly verified numerical output.
