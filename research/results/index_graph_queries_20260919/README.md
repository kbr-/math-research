# Typed graph queries

Baseline: 1c3d349. Session: index_graph_queries_20260919.
Notebook entry: entry-2026-09-19-index-graph-queries.

Run from the repository root through `./compute.sh run SESSION --threads 1
--category local_processing -- COMMAND`:

- `python3 -m unittest discover -s tools/tests -p 'test_claim*.py'`: 34 tests.
- `tools/claim-index.py graph audit --out PATH`: all recorded graph diagnostics.
- `tools/claim-index.py graph impact audit:ordinary-restriction-affine-family
  --out PATH`: both publication users with witness paths.

Use fresh output paths to preserve these checkpoint artifacts. The registry
contains only five curated edges at this checkpoint. An empty diagnostic list is
not a completeness or mathematical correctness certificate. Graph discovery
candidates are separate from accepted relationships. No claims or proofs changed.
