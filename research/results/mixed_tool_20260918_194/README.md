# Mixed-term tree with hole queries: encoding round-trip tests

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-18-mixed-tool) records the
results. `roundtrip.jsonl` holds ten exact runs of `research/tools/check_mixed_term_encoding.py`
(one JSON record per run; the reader, the flat `Q`, and the pinned-row set `A` are listed):

- Labels `0..n-1`, `n = 2^L`; `Q` is a uniformly random affine subspace of dimension `L2`; the family
  `Phi_e` (residual set of size `N+1+e`, injection of the other rows into the outside labels, `e` free
  outside labels) is enumerated completely (`restrictions`).
- The canonical mixed tree uses the matched-first preference, queries all uncovered tail rows of the
  round's term, then makes one heavy query if the pinned pair is alive and unkilled: the pigeon if it
  has at least two unkilled pinned pairs, else the hole (branches over unassigned residual rows and the
  empty branch). `bad` counts restrictions with a path of at least `h` queries; `rich_bad` those whose
  lexicographically first such path can be encoded (a consistent free outside label, not a pinned label,
  exists for every moved light row); `round_trip_failures` counts decodings that do not return the
  restriction. `max_heavy_queries` and `heavy_histogram` describe the heavy queries over all paths.
- Runs 1-6 (`two_role: false`): pinned rows `A` and light rows disjoint (role-separated). All decode
  correctly: 0 failures over 3147 rich bad paths.
- Runs 7-8 (`--two-role`, random readers whose tails may use pinned rows): 0 failures observed; the
  random readers did not produce the failing configuration.
- Runs 9-10 (`--two-role-example`): the fixed reader with row 0 pinned in the first term and light in
  the second; 2610 of 4050 and 2130 of 4450 rich bad paths fail to decode, exhibiting the two-role gap.

Commands (each appends one record): `python3 research/tools/check_mixed_term_encoding.py --L 3 --L2 1
ARGS --out research/results/mixed_tool_20260918_194/roundtrip.jsonl` with ARGS as recorded in the
fields `e w h seed terms two_role` (defaults `--terms 6 --pinned-rows 5 --tail-rows 2`; run 4 uses
`--terms 7`, run 5 `--pinned-rows 4 --tail-rows 1`, run 6 `--terms 8`, run 8 `--terms 7`, runs 9-10
`--two-role-example`). Seeds 1-8, 11, 12. Exact integer arithmetic throughout.
