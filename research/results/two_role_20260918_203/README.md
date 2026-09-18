# Complete-term rule: round-trip checks with two-role rows

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-complete-term-rule) records the
results. Exact enumeration of the slack family (10080 restrictions per run, `--L 3 --L2 1 --e 3`) with
`research/tools/check_mixed_term_encoding.py`, which gained `--rule complete`: the heavy round (pigeon,
then hole unless the pigeon took it) comes first and the current term's uncovered tail rows are queried
afterwards whatever the round's outcome, so no row of a current term is left unassigned. Code labels
avoid the pinned labels, as before.

`roundtrip_complete.jsonl`, one record per run (fields as in `research/results/column_classes_20260918_196`):

| run | rule | rich bad paths | round-trip failures |
|---|---|---|---|
| two-role example, `--w 1 --h 3 --seed 11` | complete | 6640 | 0 |
| random two-role reader, `--w 1 --h 3 --seed 12 --pinned-rows 4` | complete | 5759 | 0 |
| random two-role reader, `--w 2 --h 4 --seed 13 --pinned-rows 5` | complete | 1076 | 0 |
| random two-role reader, `--w 1 --h 3 --seed 12 --pinned-rows 4` | both | 5429 | 0 |
| role-separated, `--w 1 --h 3 --seed 3` | complete | 1851 | 0 |
| role-separated, `--w 2 --h 4 --seed 4` | complete | 4978 | 0 |
| role-separated, `--w 1 --h 3 --seed 3` | both | 1541 | 0 |
| two-role example, `--w 1 --h 3 --seed 11` | both (negative control) | 6380 | 1800 |

The two-role example (row 0 pinned in the first term and light in the second) fails under the
both-endpoints rule, as recorded on 2026-09-18, and decodes without failure under the complete-term rule;
the random two-role reader of seed 12 happens not to exercise the gap under either rule. Maximum heavy
queries on a path: 3 or 4 in every run.
