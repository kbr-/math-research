# Pair-space round trips, cycle 210: the current-term code rule

Session `window_consolidation_20260918_210`. Tool: `research/tools/check_pair_space_encoding.py` with the new code rules
`current` and `current-two-role` (the code label of a move lies in E(rho) n C(p) outside the pin labels of the current
terms of the nodes up to and including the move's node; the two-role rule also excludes the moved row's own pinned
labels) and `--reveal-slots` (the decoder assigns a row marked at the k-th code label its label once the k-th move is
decoded). Diagnostic fields: `xcur_ok` / `xcur_fail` count decoded / failed pairs whose code used a label that was a
current term's pin label at the time, `noxcur_fail` the failures without one; `rich_moves_G` / `rich_moves_offG` count
the rich pairs whose encoded path has at least one move, `fail_moves` the failures among them. `G` is the event that
E(rho) meets no pinned label. Every run enumerates all pairs (rho, rho'') of Phi_e(S) over every S (fill domain
`notail`: filling rows outside every tail).

| batch | reader | rule | reveal | L2 | e | w | h | seed | pairs | bad | rich G | rich off G | with moves G/off | fail G | fail off G | xcur ok/fail | no-xcur fail |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7 | random role-separated | current | yes | 2 | 1 | 1 | 2 | 1 | 6720 | 5862 | 5094 | 0 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 1 | 3 | 3 | 5040 | 2538 | 136 | 0 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 1 | 3 | 4 | 7560 | 3318 | 492 | 1641 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 2 | 3 | 5 | 3024 | 2099 | 450 | 505 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 1 | 3 | 6 | 7560 | 6456 | 5264 | 0 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 1 | 4 | 7 | 5040 | 894 | 296 | 176 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 2 | 4 | 8 | 3024 | 836 | 0 | 4 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 1 | 3 | 9 | 3024 | 1762 | 0 | 556 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 1 | 3 | 10 | 5040 | 2996 | 368 | 1360 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 1 | 3 | 11 | 1512 | 581 | 0 | 219 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | yes | 2 | 2 | 1 | 4 | 12 | 3024 | 752 | 0 | 167 | -/- | 0 | 0 | -/- | - |
| 7 | two-role example | current-two-role | yes | 2 | 1 | 1 | 2 | 20260918 | 8064 | 4980 | 2100 | 0 | -/- | 0 | 0 | -/- | - |
| 7 | two-role example | current-two-role | yes | 2 | 2 | 1 | 2 | 20260918 | 7560 | 5160 | 1560 | 0 | -/- | 0 | 0 | -/- | - |
| 7 | two-role example | current-two-role | yes | 2 | 2 | 1 | 3 | 20260918 | 7560 | 5040 | 1320 | 0 | -/- | 0 | 0 | -/- | - |
| 7 | outside-pin example | current-two-role | yes | 2 | 2 | 1 | 2 | 20260918 | 7560 | 5740 | 2660 | 1800 | -/- | 0 | 0 | -/- | - |
| 7 | outside-pin example | current-two-role | yes | 2 | 2 | 1 | 3 | 20260918 | 7560 | 3380 | 1520 | 720 | -/- | 0 | 0 | -/- | - |
| 7 | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 21 | 5040 | 2778 | 406 | 1458 | -/- | 0 | 0 | -/- | - |
| 7 | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 22 | 5040 | 2298 | 1046 | 893 | -/- | 0 | 0 | -/- | - |
| 7 | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 23 | 3024 | 1302 | 438 | 390 | -/- | 0 | 0 | -/- | - |
| 7 | random two-role | current-two-role | yes | 2 | 2 | 2 | 3 | 24 | 5040 | 2694 | 30 | 152 | -/- | 0 | 0 | -/- | - |
| 7 | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 26 | 5040 | 2160 | 632 | 760 | -/- | 0 | 0 | -/- | - |
| 7 | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 27 | 1512 | 919 | 144 | 456 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | current | no | 2 | 2 | 1 | 3 | 4 | 7560 | 3318 | 492 | 1641 | -/- | 0 | 9 | -/- | - |
| 7 | random role-separated | current | no | 2 | 2 | 1 | 3 | 10 | 5040 | 2996 | 368 | 1360 | -/- | 0 | 0 | -/- | - |
| 7 | random role-separated | any | yes | 2 | 2 | 1 | 3 | 4 | 7560 | 3318 | 492 | 1816 | -/- | 0 | 175 | -/- | - |
| 7 | random role-separated | any | yes | 2 | 2 | 1 | 3 | 10 | 5040 | 2996 | 368 | 1498 | -/- | 0 | 181 | -/- | - |
| 7b | all-pairs | own | no | 2 | 2 | 1 | 2 | 20260918 | 7560 | 7560 | 2160 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | current | yes | 2 | 2 | 1 | 2 | 20260918 | 7560 | 7560 | 2160 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | any | yes | 2 | 2 | 1 | 2 | 20260918 | 7560 | 7560 | 2160 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | own | no | 2 | 2 | 1 | 3 | 20260918 | 7560 | 7560 | 0 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | current | yes | 2 | 2 | 1 | 3 | 20260918 | 7560 | 7560 | 0 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | any | yes | 2 | 2 | 1 | 3 | 20260918 | 7560 | 7560 | 0 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | own | no | 2 | 3 | 1 | 3 | 20260918 | 2880 | 2880 | 0 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | current | yes | 2 | 3 | 1 | 3 | 20260918 | 2880 | 2880 | 0 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | any | yes | 2 | 3 | 1 | 3 | 20260918 | 2880 | 2880 | 0 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 21 | 1512 | 587 | 0 | 13 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 22 | 1512 | 770 | 322 | 330 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 23 | 504 | 358 | 106 | 83 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | random two-role | current-two-role | yes | 2 | 2 | 2 | 3 | 24 | 1512 | 1192 | 0 | 37 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 26 | 5040 | 1665 | 0 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | random two-role | current-two-role | yes | 2 | 2 | 1 | 3 | 27 | 3024 | 1043 | 64 | 286 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | random role-separated | any | yes | 2 | 2 | 1 | 3 | 4 | 7560 | 3318 | 492 | 1816 | -/- | 0 | 175 | 0/175 | 0 |
| 7b | random role-separated | any | yes | 2 | 2 | 1 | 3 | 10 | 5040 | 2996 | 368 | 1498 | -/- | 0 | 181 | 16/181 | 0 |
| 7b | random role-separated | any | yes | 2 | 2 | 1 | 3 | 3 | 5040 | 2538 | 136 | 0 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | random two-role | any | yes | 2 | 2 | 1 | 3 | 22 | 1512 | 770 | 322 | 330 | -/- | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | own | no | 1 | 2 | 1 | 2 | 20260918 | 378000 | 118656 | 40152 | 44088 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7b | all-pairs | current | yes | 1 | 2 | 1 | 2 | 20260918 | 378000 | 118656 | 40152 | 64944 | 0/20856 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | any | yes | 1 | 2 | 1 | 2 | 20260918 | 378000 | 118656 | 40152 | 64944 | 0/20856 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | own | no | 1 | 2 | 1 | 3 | 20260918 | 378000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | current | yes | 1 | 2 | 1 | 3 | 20260918 | 378000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | any | yes | 1 | 2 | 1 | 3 | 20260918 | 378000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | own | no | 1 | 3 | 1 | 3 | 20260918 | 288000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | current | yes | 1 | 3 | 1 | 3 | 20260918 | 288000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | any | yes | 1 | 3 | 1 | 3 | 20260918 | 288000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | own | no | 2 | 2 | 1 | 2 | 20260918 | 7560 | 7560 | 2160 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | current | yes | 2 | 2 | 1 | 2 | 20260918 | 7560 | 7560 | 2160 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | any | yes | 2 | 2 | 1 | 2 | 20260918 | 7560 | 7560 | 2160 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | own | no | 2 | 3 | 1 | 3 | 20260918 | 2880 | 2880 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | current | yes | 2 | 3 | 1 | 3 | 20260918 | 2880 | 2880 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | any | yes | 2 | 3 | 1 | 3 | 20260918 | 2880 | 2880 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | own | no | 1 | 3 | 1 | 2 | 20260918 | 288000 | 74304 | 13248 | 36192 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | current | yes | 1 | 3 | 1 | 2 | 20260918 | 288000 | 74304 | 13248 | 55872 | 0/19680 | 0 | 0 | 0/0 | 0 |
| 7c | all-pairs | any | yes | 1 | 3 | 1 | 2 | 20260918 | 288000 | 74304 | 13248 | 55872 | 0/19680 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | own | no | 1 | 2 | 1 | 2 | 2 | 378000 | 147312 | 5544 | 17784 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | current | yes | 1 | 2 | 1 | 2 | 2 | 378000 | 147312 | 5544 | 60120 | 0/42336 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | any | yes | 1 | 2 | 1 | 2 | 2 | 378000 | 147312 | 5544 | 88992 | 0/71208 | 0 | 21504 | 11100/21504 | 0 |
| 7d | all-pairs | own | no | 1 | 2 | 1 | 3 | 2 | 378000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | current | yes | 1 | 2 | 1 | 3 | 2 | 378000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | any | yes | 1 | 2 | 1 | 3 | 2 | 378000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | own | no | 1 | 2 | 1 | 3 | 4 | 378000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | current | yes | 1 | 2 | 1 | 3 | 4 | 378000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | any | yes | 1 | 2 | 1 | 3 | 4 | 378000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | own | no | 1 | 2 | 1 | 2 | 1 | 378000 | 59520 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | current | yes | 1 | 2 | 1 | 2 | 1 | 378000 | 59520 | 0 | 7418 | 0/7418 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | any | yes | 1 | 2 | 1 | 2 | 1 | 378000 | 59520 | 0 | 26352 | 0/26352 | 0 | 14680 | 4254/14680 | 0 |
| 7d | all-pairs | own | no | 1 | 3 | 1 | 3 | 1 | 288000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | current | yes | 1 | 3 | 1 | 3 | 1 | 288000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |
| 7d | all-pairs | any | yes | 1 | 3 | 1 | 3 | 1 | 288000 | 0 | 0 | 0 | 0/0 | 0 | 0 | 0/0 | 0 |

## Reading

Batch 7: the eleven batch-5 configurations (random role-separated readers) under `current --reveal-slots` decode every
rich pair, and the rich counts are at least those of the own rule of batch 5 on every configuration (seed 4: 1641
against 1567 off G; seed 10: 1360 against 1303; seed 12: 167 against 103). The two-role example, the outside-pin example
and six random two-role readers (default term counts) under `current-two-role --reveal-slots`: 0 failures. Controls:
`current` without `--reveal-slots` fails on 9 pairs off G (seed 4), so the decoder must learn a slot's label when its
move is decoded; `any --reveal-slots` fails on 175 and 181 pairs off G (seeds 4 and 10).

Batch 7b: the batch-6 random two-role readers in their exact configurations under `current-two-role --reveal-slots`:
0 failures, rich counts at least those of batch 6. Diagnostic re-runs of the `any --reveal-slots` controls: every
failure used a current term's pin label (`noxcur_fail` 0; 16 pairs used one and still decoded on seed 10). The first
all-pairs runs of 7b used a reader with a spare unpinned row and are superseded by 7c.

Batch 7c and 7d: the all-pairs reader of the dense-cube obstruction (rows 0 to 5 pinned to every label of the cube of
one literal, bit 0 = 0; each term's tail is that literal on row 6 + (i + y) mod 3). Under the own rule no path with a
move is encodable on any flat (`rich_moves` 0: every filling row is pinned to every cube label). Under
`current --reveal-slots` every rich pair decodes: flat {2,6} inside the cube (seed 20260918, L2 = 1): 20856 and 19680
paths with moves at e = 2 and e = 3; flat {0,1} meeting the cube in one hole (seed 2): 42336; flat {1,3} missing the
cube (seed 1): 7418; 0 failures. On the flats {0,1} and {1,3} the control `any --reveal-slots` fails on 21504 of 71208
and 14680 of 26352 rich pairs with moves, every failure through a current term's pin label (11100 and 4254 such pairs
decoded, none failed without such a label); on the flat inside the cube every move ends its path (both holes satisfy
the literal), the current terms of move nodes are round terms whose pin labels lie in Q, and `any` coincides with
`current`. The four-hole flats (L2 = 2) and the height-3 thresholds produced no encodable path on this reader (the
four-hole flat is the cube itself, so no outside cube label exists; no path has three queries) and are uninformative.

Provenance: `provenance.json` records the hashes of the tool and these files; the commands are in `runs.log`.
