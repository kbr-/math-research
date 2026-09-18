# Hole-only rule: counterexample to the adaptive rule and round-trip tests

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-bipartite-theorem) records
the results.

- `adaptive_counterexample.json`: `python3 research/tools/check_adaptive_rule_counterexample.py --L 4
  --L2 3 --classes 3 --out ...`. Labels `0..15`, flat `Q = {0..7}` (`N = 8`), 17 rows; light rows
  `0,1,2` carry one class each with labels `0,1,2` in `Q` and tails satisfied by the restriction; the
  9 residual rows `3..11` and all other rows are pinned in every class (42 terms). The whole canonical
  tree of the one restriction is explored under the adaptive rule (pigeon query when the pinned row has
  at least two unkilled pairs) and under the hole-only rule; `max_heavy_queries` is the maximum number
  of heavy queries on a path: 8 (adaptive) against 3 (hole-only).
- `roundtrip_hole_only.jsonl`: five records of `research/tools/check_mixed_term_encoding.py --L 3 --L2 1
  --hole-only ARGS --out ...` with the same fields as in `research/results/mixed_tool_20260918_194`
  (`hole_only: true` added). ARGS: `--e 2 --w 1 --h 3 --seed 2`; `--e 3 --w 1 --h 3 --seed 3`;
  `--e 3 --w 2 --h 4 --seed 4`; `--e 3 --w 1 --h 3 --seed 5 --pinned-rows 4 --tail-rows 1`
  (role-separated: 1561 + 138 + 1254 + 310 = 3263 rich bad paths, 0 round-trip failures); and
  `--e 3 --w 1 --h 3 --seed 11 --two-role-example` (2610 of 4050 rich bad paths fail, as without the
  option). Exact integer arithmetic; complete enumeration of the family.
