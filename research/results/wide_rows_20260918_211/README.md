# Wide tail rows, cycle 211: unplaced moves and tree heights

Session `wide_rows_20260918_211`.

## Batch 8: round trips with unplaced wide moves

Tool: `research/tools/check_pair_space_encoding.py` with `--wide-w W`: a tail row with more than W literals is moved
without a code label (it stays residual in rho*; beta records the kind 'W' with the position; delta the answer). All runs
use the compact tree, `--fill-domain notail`, the current-term rule with `--reveal-slots`. `--wide-w 0` makes every move
unplaced, `--wide-w 1` places one-literal rows and leaves two-literal rows unplaced. Columns as in cycle 210's README.

| reader | rule | wide-w | L2 | e | w | h | seed | pairs | bad | rich G | rich off G | with moves G/off | fail G | fail off G |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| random role-separated | current | 0 | 2 | 1 | 1 | 2 | 1 | 6720 | 5862 | 5862 | 0 | 990/0 | 0 | 0 |
| random role-separated | current | 0 | 2 | 2 | 1 | 3 | 3 | 5040 | 2538 | 2538 | 0 | 2532/0 | 0 | 0 |
| random role-separated | current | 0 | 2 | 2 | 1 | 3 | 4 | 7560 | 3318 | 568 | 2750 | 568/2750 | 0 | 0 |
| random role-separated | current | 0 | 2 | 2 | 2 | 3 | 5 | 3024 | 2099 | 1102 | 997 | 1102/997 | 0 | 0 |
| random role-separated | current | 0 | 2 | 2 | 1 | 4 | 7 | 5040 | 894 | 516 | 378 | 516/378 | 0 | 0 |
| random role-separated | current | 0 | 2 | 2 | 2 | 4 | 8 | 3024 | 836 | 100 | 736 | 100/736 | 0 | 0 |
| random role-separated | current | 0 | 2 | 2 | 1 | 3 | 10 | 5040 | 2996 | 510 | 2486 | 510/2470 | 0 | 0 |
| random role-separated | current | 1 | 2 | 2 | 2 | 3 | 5 | 3024 | 2099 | 916 | 765 | 916/765 | 0 | 0 |
| random role-separated | current | 1 | 2 | 2 | 2 | 4 | 8 | 3024 | 836 | 68 | 366 | 68/366 | 0 | 0 |
| random role-separated | current | 1 | 2 | 2 | 2 | 3 | 13 | 3024 | 1125 | 0 | 1075 | 0/1075 | 0 | 0 |
| random role-separated | current | 1 | 2 | 2 | 2 | 3 | 14 | 5040 | 3230 | 1264 | 1075 | 1264/1075 | 0 | 0 |
| two-role example | current-two-role | 0 | 2 | 2 | 1 | 3 | 20260918 | 7560 | 5040 | 5040 | 0 | 5040/0 | 0 | 0 |
| outside-pin example | current-two-role | 0 | 2 | 2 | 1 | 3 | 20260918 | 7560 | 3380 | 1660 | 1720 | 1660/1720 | 0 | 0 |
| random two-role | current-two-role | 0 | 2 | 2 | 1 | 3 | 22 | 1512 | 770 | 420 | 350 | 420/350 | 0 | 0 |

Reading: every rich pair decodes in all 14 runs (0 failures). With `--wide-w 0` no pair fails richness (no code label is
needed), so rich G equals bad G on G; the mixed runs (`--wide-w 1`) have fewer rich pairs than the all-placed runs of
cycle 210 on the same configurations only where the one-literal rows' labels run out, as expected.

## Tree heights of the complete-term tree on wide-row readers

Tool: `research/tools/wide_rows_tree_check.py` (imports the checker). For L = 3 (n = 8 labels, rows 0..8, A = {0,1,2},
B = {3,...,8}) and every affine subspace Q of F_2^3 of dimension L2 = 1 (28 flats, N = 2) and L2 = 2 (14 flats, N = 4), every
rho' = (Q, R', mu') in Phi_0 is enumerated and the height (longest path) of T_c(F, rho') computed, with and without the
static skip (terms with a residual tail row whose pattern cube misses Q removed, i.e. the sub-reader F_{Q,R'}). Readers:
same-pattern: [j in p] for j in B, p = (bit0 = 0, bit1 = 0), cube {0,4}; distinct: [j in p_j] with p_j the two-literal
pattern of the binary digits of j's index in B (only four such cubes exist, so rows 3,7 and 4,8 share cubes); one-pin:
[0 -> 1] and [j in p] for j in B. `meets` says whether the cube {0,4} meets Q. Fractions are over the rho' of the flats
in that class; `satisfied` is the fraction with a term satisfied by rho' at the root (height 0, not counted in h >= k).
Outputs: `tree_heights_L2_1.txt`, `tree_heights_L2_2.txt`, records in `tree_heights.jsonl`.

```
same-pattern  skip=False meets=True   rho'= 786240 satisfied=0.615 h>=1:0.384 h>=2:0.275 h>=3:0.000 max=2 mean|R' n B|=2.00
same-pattern  skip=False meets=False  rho'= 907200 satisfied=0.917 h>=1:0.083 h>=2:0.083 h>=3:0.000 max=2 mean|R' n B|=2.00
same-pattern  skip=True  meets=True   rho'= 786240 satisfied=0.615 h>=1:0.384 h>=2:0.275 h>=3:0.000 max=2 mean|R' n B|=2.00
same-pattern  skip=True  meets=False  rho'= 907200 satisfied=0.917 h>=1:0.000 h>=2:0.000 h>=3:0.000 max=0 mean|R' n B|=2.00
distinct      skip=False meets=True   rho'= 786240 satisfied=0.646 h>=1:0.351 h>=2:0.285 h>=3:0.000 max=2 mean|R' n B|=2.00
distinct      skip=False meets=False  rho'= 907200 satisfied=0.680 h>=1:0.318 h>=2:0.259 h>=3:0.000 max=2 mean|R' n B|=2.00
distinct      skip=True  meets=True   rho'= 786240 satisfied=0.646 h>=1:0.276 h>=2:0.094 h>=3:0.000 max=2 mean|R' n B|=2.00
distinct      skip=True  meets=False  rho'= 907200 satisfied=0.680 h>=1:0.203 h>=2:0.045 h>=3:0.000 max=2 mean|R' n B|=2.00
one-pin       skip=False meets=True   rho'= 786240 satisfied=0.064 h>=1:0.081 h>=2:0.073 h>=3:0.000 max=2 mean|R' n B|=2.00
one-pin       skip=False meets=False  rho'= 907200 satisfied=0.071 h>=1:0.114 h>=2:0.114 h>=3:0.000 max=2 mean|R' n B|=2.00
one-pin       skip=True  meets=True   rho'= 786240 satisfied=0.064 h>=1:0.081 h>=2:0.073 h>=3:0.000 max=2 mean|R' n B|=2.00
one-pin       skip=True  meets=False  rho'= 907200 satisfied=0.071 h>=1:0.107 h>=2:0.107 h>=3:0.000 max=2 mean|R' n B|=2.00
same-pattern  skip=False meets=True   rho'=  33264 satisfied=0.485 h>=1:0.515 h>=2:0.515 h>=3:0.483 max=4 mean|R' n B|=3.33
same-pattern  skip=False meets=False  rho'=   9072 satisfied=0.917 h>=1:0.083 h>=2:0.083 h>=3:0.083 max=4 mean|R' n B|=3.33
same-pattern  skip=True  meets=True   rho'=  33264 satisfied=0.485 h>=1:0.515 h>=2:0.515 h>=3:0.483 max=4 mean|R' n B|=3.33
same-pattern  skip=True  meets=False  rho'=   9072 satisfied=0.917 h>=1:0.000 h>=2:0.000 h>=3:0.000 max=0 mean|R' n B|=3.33
distinct      skip=False meets=True   rho'=  33264 satisfied=0.503 h>=1:0.497 h>=2:0.497 h>=3:0.456 max=4 mean|R' n B|=3.33
distinct      skip=False meets=False  rho'=   9072 satisfied=0.571 h>=1:0.429 h>=2:0.429 h>=3:0.397 max=4 mean|R' n B|=3.33
distinct      skip=True  meets=True   rho'=  33264 satisfied=0.503 h>=1:0.490 h>=2:0.443 h>=3:0.350 max=4 mean|R' n B|=3.33
distinct      skip=True  meets=False  rho'=   9072 satisfied=0.571 h>=1:0.377 h>=2:0.178 h>=3:0.024 max=3 mean|R' n B|=3.33
one-pin       skip=False meets=True   rho'=  33264 satisfied=0.030 h>=1:0.283 h>=2:0.283 h>=3:0.242 max=4 mean|R' n B|=3.33
one-pin       skip=False meets=False  rho'=   9072 satisfied=0.036 h>=1:0.372 h>=2:0.372 h>=3:0.248 max=4 mean|R' n B|=3.33
one-pin       skip=True  meets=True   rho'=  33264 satisfied=0.030 h>=1:0.283 h>=2:0.283 h>=3:0.242 max=4 mean|R' n B|=3.33
one-pin       skip=True  meets=False  rho'=   9072 satisfied=0.036 h>=1:0.357 h>=2:0.357 h>=3:0.000 max=2 mean|R' n B|=3.33
```

Reading: on the four-hole flats meeting the cube, the same-pattern reader has height at least 3 in 48.3 percent of the
restrictions and a satisfied term in 48.5 percent, so nearly every restriction without a satisfied term carries the
lemma's path of length min(|R' n B|, N-1) = 3 (plus the forced last answer, maximum 4); the static skip changes nothing
there and sets the height to 0 on the flats missing the cube. The distinct reader's height >= 3 fraction on flats
missing the shared cube drops from 39.7 to 2.4 percent under the skip. The one-pin reader keeps its long paths under
the skip when the cube meets the flat (24.2 percent with height >= 3) and is reduced to the round (height 2) otherwise.

Provenance: `provenance.json` records the hashes of the tools and these files; commands are in `runs.log` and the
session record.
