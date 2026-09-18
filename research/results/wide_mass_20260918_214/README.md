# Wide mass (cycle 214): census on the all-patterns reader

Session `wide_mass_20260918_214`. Supports the notebook entry `entry-2026-09-18-wide-mass`
(Theorem V, the row-mass dichotomy for pin-free single-row wide readers).

## Tool

`research/tools/wide_rows_tree_check.py` gained the reader `all-patterns`: every pattern of
`L-1` literals on every row of `B = {3,...,8}` (12 patterns per row, 72 terms for `L = 3`),
pin-free, of row mass `n|B| = 48`, which for `n = 8` lies below the split `4N(n+1)` of
Theorem V (so formally case (D2)) while exhibiting the satisfaction mechanism of case
(D1): every `S_j` is the whole label set and `|B| > N+1`, so some row of `B` is matched
and satisfies a term in every restriction. The census runs
the wide-round tree (`--tree wide`, default order wide-first) over every rho' in Phi_0 for
every flat of F_2^3 of dimension `L2`.

## Files

- `tree_heights.jsonl`, `tree_heights_L2_1.txt`, `tree_heights_L2_2.txt`: the census for
  the readers `all-patterns` and `same-pattern` (the shared-pattern reader of the wide-rows
  entry, row mass `2|B| = 12`, the small-mass case (D2)), `L2 = 1` and `L2 = 2`.
- `runs.log`: the commands and exit codes (batch 11).

## Results

The all-patterns reader has a term satisfied by rho' at the root in every restriction
(satisfied share 1.000 on all 1693440 two-hole and 42336 four-hole restrictions), since
every matched row satisfies the three terms whose cubes contain its label; its tree has
height 0 everywhere. The shared-pattern reader keeps the heights of the wide-rounds census
(maximum 2, the two hole queries at the cube's labels when the flat meets it, height 0
otherwise).

## Reproduction

```
python3 research/tools/wide_rows_tree_check.py --tree wide --readers all-patterns,same-pattern \
  --L 3 --L2 2 --out tree_heights.jsonl
```
