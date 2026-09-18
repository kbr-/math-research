# Pair-space round trips on the compact tree (cycle 208, session weak_sparse_pinning_20260918_208)

Tool: `research/tools/check_pair_space_encoding.py` with `--tree compact` (new in this cycle): for every pair (rho, rho'')
with the filling on rows outside every tail (`--fill-domain notail`), it builds the compact complete-term tree
T_c(F, rho') of rho' = rho u rho'' (matched-first preference; at an alive pin the pigeon over the unused holes of Q,
then on every answer other than the pin the hole over the unassigned compact residual rows and the empty branch;
then every uncovered tail row), finds the lexicographically first path with at least h queries, encodes it with code
labels in E(rho) n C(p) chosen by `--code-rule` (`own`: the row filling the label is not pinned to it, the entry's
rule; `avoid-X`: outside every pinned label, the previous entry's rule; `any`: no exclusion, a control), records
sigma (the filling as E-labels or slot indices), beta (a bit per round, a position and last-of-node bit per move)
and delta (answers), and decodes by simulating T_c from rho* and sigma (functions first_long_path_compact,
encode_compact, decode_compact, status_dec, pick_term_c). G is the event that no free label is pinned; the compact
tree does not depend on it, so failures off G would be failures of the decoder's rule for pins at outside labels.
Runs are appended to `roundtrip_pairs.jsonl`; `runs.log` holds the console output of every invocation in order.
All boards: n = 8, N = 4 (L = 3, L2 = 2).

Batch 5 (`--tree compact --fill-domain notail --code-rule own`, the entry's encoding):

| e | w | h | labels | seed | terms | pairs | on G | rich bad on G | failures on G | rich bad off G | failures off G |
|---|---|---|--------|------|-------|-------|------|---------------|---------------|----------------|----------------|
| 1 | 1 | 2 | 2 | 1 | 6 | 6720 | 6720 | 5094 | 0 | 0 | 0 |
| 2 | 1 | 3 | 2 | 3 | 6 | 5040 | 5040 | 136 | 0 | 0 | 0 |
| 2 | 1 | 3 | 0 (all) | 4 | 6 | 7560 | 1260 | 492 | 0 | 1567 | 0 |
| 2 | 2 | 3 | 2 | 5 | 8 | 3024 | 1512 | 450 | 0 | 459 | 0 |
| 2 | 1 | 3 | 1 | 6 | 7 | 7560 | 7560 | 5264 | 0 | 0 | 0 |
| 2 | 1 | 4 | 2 | 7 | 8 | 5040 | 2520 | 296 | 0 | 176 | 0 |
| 2 | 2 | 4 | 3 | 8 | 9 | 3024 | 504 | 0 | 0 | 2 | 0 |
| 2 | 1 | 3 | 3 | 9 | 8 | 3024 | 504 | 0 | 0 | 516 | 0 |
| 2 | 1 | 3 | 0 (all) | 10 | 7 | 5040 | 840 | 368 | 0 | 1303 | 0 |
| 2 | 1 | 3 | 0 (all) | 11 | 12 | 1512 | 0 | 0 | 0 | 206 | 0 |
| 2 | 1 | 4 | 0 (all) | 12 | 12 | 3024 | 0 | 0 | 0 | 103 | 0 |

Controls on the compact tree (`--code-rule any`: a code label may be the label its own filling row is pinned to,
which the decoder cannot see; `--code-rule avoid-X`: the previous entry's rule, fewer rich pairs):

| e | w | h | labels | seed | terms | pairs | on G | rich bad on G | failures on G | rich bad off G | failures off G |
|---|---|---|--------|------|-------|-------|------|---------------|---------------|----------------|----------------|
| 2 | 1 | 3 | 0 (all) | 4 | 6 | 7560 | 1260 | 492 | 0 | 1816 | 184 | (any)
| 2 | 1 | 3 | 0 (all) | 10 | 7 | 5040 | 840 | 368 | 0 | 1498 | 181 | (any)
| 2 | 1 | 3 | 0 (all) | 10 | 7 | 5040 | 840 | 368 | 0 | 734 | 0 | (avoid-X)

Control for the variant that started the cycle (the slack tree of the previous entry with the pin test, the own-row
rule and the tail skipped after a killed pin, `--encoding entry --fill-domain notail --pin-test --skip-killed
--code-rule own`): it fails on G because a row moved later can sit in the tail of an earlier current term whose tail
was skipped, so the code label chosen for its later pattern falsifies the earlier term in the code. Traced failing
pair (seed 10 configuration): Q = {0,3,4,7}, mu = {0:5, 1:2}, E = {1,6}, filling {2:1, 4:6}; the path is the round at
term 1 (pin (3,4): pigeon 3 -> 0, hole 4 <- 5), then, term 1 being killed and its tail skipped, the move of row 6 at
term 2 to hole 3; the code label of row 6 is 6 (consistent with its pattern in term 2), but row 6 also lies in the
tail of term 1 with a pattern inconsistent with 6, so the decoder sees term 1 falsified at the root and picks term 2.

| e | w | h | labels | seed | terms | pairs | on G | rich bad on G | failures on G | rich bad off G | failures off G |
|---|---|---|--------|------|-------|-------|------|---------------|---------------|----------------|----------------|
| 2 | 1 | 3 | 0 (all) | 10 | 7 | 5040 | 840 | 302 | 120 | 1018 | 401 |
| 2 | 1 | 3 | 0 (all) | 4 | 6 | 7560 | 1260 | 192 | 0 | 390 | 39 |

Reading: batch 5 is the positive control for Lemma B of the entry (no failure on or off G on every rich bad pair,
including runs where every label is pinned and rows are pinned to several labels each); the `any` control exhibits
the failure the own-row rule prevents; the skip-the-tail control exhibits why the complete-term rule is needed.
The probability bounds of the entry are not tested; the boards are too small.
