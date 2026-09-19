# Source-clause and axiom-preprocessing dependencies

Baseline: dc1d95b. Session: index_source_dependencies_20260919.
Notebook: entry-2026-09-19-index-source-dependencies.

Fifteen existing inventories closed; 29 scoped edges added and four prior edges
retained. Exact source sections and the existing BIKPRS audit identify proof inputs,
encoding provenance and later refinements. No new paper/kernel/numerical audit.

Reproduce through compute.sh run SESSION --threads 1 --category local_processing:
- python3 research/results/index_source_dependencies_20260919/curate.py --out PATH
- tools/claim-index.py changed --base dc1d95b --out PATH
- tools/claim-index.py validate --out PATH
- tools/claim-index.py graph audit --out PATH

Use fresh output paths. Totals: 50 reviewed dependency inventories, 312 pending,
504 unreviewed, 111 edges. The two MOD records form a citation-only cycle because
one locates the isolated identity in the earlier record and the other discusses it
as an unused alternative. There is no proof-dependency cycle.
