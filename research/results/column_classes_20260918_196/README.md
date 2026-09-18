# Both-endpoints rule: scenarios and round-trip tests

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-both-endpoints-rule) records the
results. All runs use exact integer arithmetic and complete enumeration.

- `scenario_column.json`: `python3 research/tools/check_adaptive_rule_counterexample.py --L 4 --L2 3
  --classes 3 --scenario column --out ...` (the full-column reader of the previous cycle, one explicit
  restriction, whole tree explored under each rule): maximum heavy queries on a path 8 (adaptive),
  3 (hole), 6 (both).
- `scenario_sparse.json`: `... --L 4 --L2 3 --scenario sparse --out ...`: the unary reader `OR_x [0 -> x]`
  over all 16 labels with row 0 residual (`Q = {0..7}`, residual rows `0..8`): 1 (adaptive), 8 (hole),
  2 (both).
- `roundtrip_both.jsonl`: five records of `research/tools/check_mixed_term_encoding.py --L 3 --L2 1
  --rule both ARGS --out ...` with the fields of `research/results/mixed_tool_20260918_194` plus `rule`.
  ARGS: `--e 2 --w 1 --h 3 --seed 2`; `--e 3 --w 1 --h 3 --seed 3`; `--e 3 --w 2 --h 4 --seed 4`;
  `--e 3 --w 1 --h 3 --seed 5 --pinned-rows 4 --tail-rows 1` (role-separated: 8481 + 1541 + 3447 + 1750
  = 15219 rich bad paths, 0 round-trip failures); `--e 3 --w 1 --h 3 --seed 11 --two-role-example`
  (1800 of 6380 rich bad paths fail: the two-role gap is independent of the rule).
