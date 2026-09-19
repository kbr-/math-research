# Packet evaluation for research orientation

Baseline: 63e1351. Session: index_packet_evaluation_20260919.
Notebook: entry-2026-09-19-index-packet-research-review.

Five purposive cases: partial formalization with a refuted equality, conditional
interface, correction/repair history, finite check and a theorem whose definitions
can be omitted by bounded extraction. Evaluation: useful for orientation and
source triage; unsuitable for proof readiness. The unchanged indexed assessment
retains qualifications but is not independently certified by the packet tool.

Reproduce through `./compute.sh run SESSION --threads 1 --category local_processing
-- COMMAND` using fresh output paths:

- `python3 research/results/index_packet_evaluation_20260919/evaluate.py --out PATH`
- `python3 -m unittest discover -s tools/tests -p test_claim_dependencies.py`

The script preserves sampled packets, checked assessment phrases, selected versus
available source block counts and the manual interpretation of each failure mode.
Eight tests pass. No new mathematical proof or full-corpus accuracy claim is made.
