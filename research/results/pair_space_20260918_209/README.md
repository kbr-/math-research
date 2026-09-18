# Pair-space round trips on the compact tree for two-role readers (cycle 209, session two_role_compact_20260918_209)

Tool: `research/tools/check_pair_space_encoding.py --tree compact --two-role` (new options in this cycle): tails may use
pinned rows, so a row may be pinned in one term and light in another; the filling stays on rows outside every tail
(`--fill-domain notail`); `--code-rule own-two-role` excludes from a moved row's code labels the labels its own
filling row is pinned to (the own-row rule of cycle 208) and the labels the moved row itself is pinned to (the
recorded two-role decoder's rule); `--code-rule own` is the control without the second exclusion.
`--two-role-example` is the recorded two-role counterexample of the mixed-term tool (pins at holes of Q, where the
second exclusion is vacuous); `--two-role-example2` pins a two-role row at an outside label consistent with its own
light pattern, where the second exclusion matters. Runs are appended to `roundtrip_pairs.jsonl`; `runs.log` holds
the console output of every invocation in order. All boards: n = 8, N = 4. A run with 0 pairs (random seed 25)
has fewer than e rows outside every tail and is recorded as empty.

Batch 6 (`--code-rule own-two-role`, the entry's rule):

| reader | code rule | e | w | h | labels | terms | pairs | on G | rich bad on G | failures on G | rich bad off G | failures off G |
|--------|-----------|---|---|---|--------|-------|-------|------|---------------|---------------|----------------|----------------|
| two-role example | own-two-role | 1 | 1 | 2 | 0 (all) | 3 | 8064 | 8064 | 2100 | 0 | 0 | 0 |
| two-role example | own-two-role | 2 | 1 | 2 | 0 (all) | 3 | 7560 | 7560 | 1560 | 0 | 0 | 0 |
| two-role example | own-two-role | 2 | 1 | 3 | 0 (all) | 3 | 7560 | 7560 | 1320 | 0 | 0 | 0 |
| random, seed 21 | own-two-role | 2 | 1 | 3 | 0 (all) | 8 | 1512 | 252 | 0 | 0 | 13 | 0 |
| random, seed 22 | own-two-role | 2 | 1 | 3 | 2 | 8 | 1512 | 756 | 322 | 0 | 304 | 0 |
| random, seed 23 | own-two-role | 2 | 1 | 3 | 3 | 9 | 504 | 252 | 106 | 0 | 65 | 0 |
| random, seed 24 | own-two-role | 2 | 2 | 3 | 0 (all) | 9 | 1512 | 0 | 0 | 0 | 35 | 0 |
| random, seed 25 | own-two-role | 2 | 1 | 4 | 2 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| random, seed 26 | own-two-role | 2 | 1 | 3 | 2 | 7 | 5040 | 840 | 0 | 0 | 0 | 0 |
| outside-pin example | own-two-role | 2 | 1 | 2 | 0 (all) | 3 | 7560 | 3780 | 2660 | 0 | 1800 | 0 |
| outside-pin example | own-two-role | 2 | 1 | 3 | 0 (all) | 3 | 7560 | 3780 | 1520 | 0 | 720 | 0 |
| random, seed 27 | own-two-role | 2 | 1 | 3 | 0 (all) | 8 | 3024 | 504 | 64 | 0 | 282 | 0 |

Controls (`--code-rule own`, the moved row's own pinned labels not excluded):

| reader | code rule | e | w | h | labels | terms | pairs | on G | rich bad on G | failures on G | rich bad off G | failures off G |
|--------|-----------|---|---|---|--------|-------|-------|------|---------------|---------------|----------------|----------------|
| two-role example | own | 2 | 1 | 3 | 0 (all) | 3 | 7560 | 7560 | 1320 | 0 | 0 | 0 |
| random, seed 22 | own | 2 | 1 | 3 | 2 | 8 | 1512 | 756 | 322 | 0 | 304 | 0 |
| random, seed 25 | own | 2 | 1 | 4 | 2 | 10 | 0 | 0 | 0 | 0 | 0 | 0 |
| outside-pin example | own | 2 | 1 | 2 | 0 (all) | 3 | 7560 | 3780 | 2660 | 0 | 1800 | 880 |
| outside-pin example | own | 2 | 1 | 3 | 0 (all) | 3 | 7560 | 3780 | 1520 | 0 | 1320 | 520 |
| random, seed 27 | own | 2 | 1 | 3 | 0 (all) | 8 | 3024 | 504 | 64 | 0 | 282 | 0 |

Reading: with both exclusions the decoder never fails, on or off G, on the recorded two-role counterexample, on the
outside-pin example and on the random two-role readers (positive control for Lemma B of the entry); without the
moved row's exclusion it fails on the outside-pin example off G, where a two-role row is moved to the outside label
it is pinned to, so that in the code its pin looks matched and satisfied while in reality the label is filled by
another row (negative control); on the recorded two-role example, whose pins lie in Q, and on the random readers, whose two-role
rows are pinned outside Q only at labels inconsistent with their light patterns (seed 22: row 0 pinned to 7;
seed 27: row 1 pinned to 2), the two rules admit the same code labels, which is why those controls do not fail. The probability bounds
of the entry are not tested; the boards are too small.
