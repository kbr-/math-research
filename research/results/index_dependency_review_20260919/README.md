# Connected dependency review and equation-reference discovery

Baseline: 54f2079. Session: index_dependency_review_20260919.
Notebook: entry-2026-09-19-index-dependency-route-review.

Six exact claim sections resolved previously pending equation/setup ownership in
the early matching/normalization cluster. Twelve scoped edges distinguish direct
proof prerequisites, applications and historical provenance. An external Razborov
theorem endpoint uses the existing public source audit, not a newly accessed paper.

Reproduce through `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND`, preserving checkpoint evidence and writing fresh reports:

- `tools/claim-dependencies.py scan --out PATH`: 2,091 candidates including equation references.
- `python3 research/results/index_dependency_review_20260919/curate.py --out PATH`
  consumes the saved candidates.json and applies explicit reviewed decisions.
- `python3 -m unittest discover -s tools/tests -p test_claim_dependencies.py`: 11 passing.
- `tools/claim-index.py changed --base 54f2079 --out PATH`
- `tools/claim-index.py validate --out PATH`
- `tools/claim-index.py graph audit --out PATH`

Equation targets remain ambiguous where tags are shared/reused. Definition hashes
participate in staleness; references to a locally defined equation do not create
cross-claim dependencies. Six complete reviews are a bounded cluster, not a
complete graph audit. Totals: 23 reviewed, 339 pending, 504 unreviewed inventories;
55 reviewed canonical edges. Classification and significance totals are unchanged.
