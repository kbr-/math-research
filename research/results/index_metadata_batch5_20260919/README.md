# Column-freezing and profile-layout metadata batch

Baseline: 1f85a8a. Session: index_metadata_batch5_20260919.
Notebook: entry-2026-09-19-index-column-freezing-metadata.

60 existing records were classified from verbatim assessments and compact source
qualifications. Standard matching/sampling/replay inputs are marked known; the
source-family elimination bridge remains an open contextual obligation. No new
proof, novelty finding or canonical dependency edge was produced.

Reproduce through `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND` using fresh output paths:

- `python3 research/results/index_metadata_batch5_20260919/collect.py --out PATH`
- `python3 research/results/index_metadata_batch5_20260919/curate.py --out PATH`
- `tools/claim-index.py changed --base 1f85a8a --out PATH`
- `tools/claim-index.py validate --out PATH`

Coverage: status/topics 282 reviewed, 584 unreviewed; significance 277 reviewed,
five pending, 584 unreviewed; relationships 17 reviewed, 265 pending, 584 unreviewed;
formalization 866 reviewed. All pending inventories remain migration work.
