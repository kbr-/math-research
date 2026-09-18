# Wide rounds (cycle 212): round trips and tree heights on the wide-round tree

Session `wide_rounds_20260918_212`. Supports the notebook entry
`entry-2026-09-18-wide-rounds` (the wide-round tree with a canonical minimum vertex
cover of the wide graph; Lemmas W0 to W5, Theorem W, Corollaries 1 and 2).

## Tools

- `research/tools/check_pair_space_encoding.py`, extended with `--tree wide`: at the
  root the encoder and the decoder build the wide graph (residual wide rows against
  the holes of Q inside their pattern cubes, over every term) and its canonical minimum
  vertex cover (least size, then fewest rows, then lexicographic). A wide row of the
  cover is queried as a pigeon; a wide row outside the cover is sought by hole queries
  at the unresolved holes of its cube in increasing order until found or exhausted, in
  which case its term counts as falsified. Light moves use the current-term rule
  (`--code-rule current`) with slot revelation (`--reveal-slots`); `beta` carries one
  bit per node (whether the node has a light move) and, per light move, its position and
  a last-of-node bit; wide answers are in `delta` only. `--wide-rows K` makes the last
  `K` rows of B wide (tails of `--wide-lits` literals); `--wide-example` builds the three
  readers of the wide-rows entry (`same-pattern`, `distinct`, `one-pin`, A = rows 0..2,
  B = rows 3..n, pattern bits 0..L-2 zero, pin (0, 1)); in that mode rows with L-1
  literals are wide. Per run the record adds `max_wide` (largest number of wide queries
  on an encoded path) and `wide_gt_cover` (pairs whose path has more wide queries than
  the cover's size; always 0).
- `research/tools/wide_rows_tree_check.py`, extended with `--tree wide`: the exhaustive
  census of the wide-rows entry (every rho' in Phi_0 for every flat of F_2^3 of dimension
  1 and 2, the three readers above) with the heights of the wide-round tree, the largest
  number of wide queries, the pairs where wide queries exceed the cover, and the mean
  cover size.

## Files

- `roundtrip_pairs.jsonl`: 16 records of batch 9 (`runs.log` has the commands and
  outputs). Runs 1 to 6: the three example readers on L2 = 1 (e = 1, h = 1, 120960
  pairs) and L2 = 2 (e = 2, h = 2, 1512 pairs). Runs 7 to 14: eight random mixed readers
  (7 to 10 terms, 4 or 5 pinned rows, 2 or 3 tail rows, 1 to 3 wide rows of two-literal
  patterns, h = 2 to 4, 3024 to 7560 pairs). Runs 15 and 16: controls with
  `--code-rule any` on the seed-4 and seed-13 readers.
- `tree_heights.jsonl`, `tree_heights_wide_L2_1.txt`, `tree_heights_wide_L2_2.txt`: the
  census with the wide tree.

## Results

Batch 9: every rich pair decodes in all 14 runs with the current-term rule (0 failures;
rich pairs per run from 288 to 95760); `wide_gt_cover` is 0 in every run, and
`max_wide` is 1 or 2. The two controls fail on 106 and 20 pairs, every failure through a
code label inside the excluded pin labels (`xcur_fail`), as the current-term rule
predicts.

Census (four-hole flats, 33264 restrictions whose flat meets the shared cube {0, 4}):
the shared-pattern reader has maximum height 2 (a path of length 2 in 27.3 percent,
where the complete-term tree had length at least 3 in 48.3 percent); the reader with
distinct cubes has a path of length at least 3 in 27.6 percent with maximum height 4 and
mean cover size 1.27 (its six rows share only four cubes); the one-pin reader has
maximum height 4 (the round plus two hole queries). On the flats missing the cube the
shared-pattern reader has height 0 and the one-pin reader at most the round. In every
restriction the wide queries are at most the cover's size. Two-hole flats: maximum
height 2 for all three readers.

## Reproduction

```
python3 research/tools/check_pair_space_encoding.py --tree wide --fill-domain notail \
  --code-rule current --reveal-slots --wide-example same-pattern --L2 2 --e 2 --w 1 --h 2 \
  --seed 20260918 --out roundtrip_pairs.jsonl
python3 research/tools/wide_rows_tree_check.py --tree wide --L 3 --L2 2 --out tree_heights.jsonl
```

The full command list is in `runs.log`; the batch script was
`batch9.sh` (session scratch), whose commands `runs.log` reproduces verbatim.
