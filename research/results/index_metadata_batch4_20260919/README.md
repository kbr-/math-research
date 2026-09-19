# Probe, interface and column-profile metadata batch

Baseline: 2eed4da. Session: index_metadata_batch4_20260919.
Notebook: entry-2026-09-19-index-probe-column-metadata.

80 existing claims were classified from original assessments and selected source
qualifications. Five possible independent results retain pending significance
reviews with unknown novelty: odd affine-Booleanity classification, generic/full-PHP
reduced-product degree gaps, ternary coefficient frontier, heterogeneous profile
frontier. This screening is not a new correctness or literature audit.

Reproduce via `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND`, preserving checkpoint outputs and using fresh paths:

- `python3 research/results/index_metadata_batch4_20260919/collect.py --out PATH`
- `python3 research/results/index_metadata_batch4_20260919/curate.py --out PATH`
- `tools/claim-index.py changed --base 2eed4da --out PATH`
- `tools/claim-index.py validate --out PATH`

Coverage: status/topics 222 reviewed and 644 unreviewed; significance 217 reviewed,
five pending, 644 unreviewed; relationships 17 reviewed, 205 pending, 644 unreviewed;
formalization 866 reviewed. No canonical edge or original claim text changed.
The complete selected packets and manual classification rationale remain on disk.
