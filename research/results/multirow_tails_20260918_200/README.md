# Multi-row tails: round-trip checks of the both-endpoints decoder

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-multirow-tails) records the
results. Exact enumeration of the slack family (10080 restrictions per run); no rule or encoding changed.

- `roundtrip_both_3rows.jsonl`: two records of `research/tools/check_mixed_term_encoding.py --L 3 --L2 1
  --e 3 --w 1 --h 4 --rule both --tail-rows 3 --pinned-rows 4 --seed SEED --out ...` with SEED 7 and 8,
  fields as in `research/results/column_classes_20260918_196` (`terms` lists each term's pinned pair and
  tail rows). Both readers are role-separated and contain terms whose tails span three light rows
  (seed 7: one three-row tail, one one-row tail, four unary terms; seed 8: four three-row tails and one
  two-row tail). Rich bad paths 1056 + 1199 = 2255, round-trip failures 0, at most 4 heavy queries
  (2 rounds) on a path.
