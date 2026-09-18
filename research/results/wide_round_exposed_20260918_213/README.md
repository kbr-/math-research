# Wide rounds, exposed rows (cycle 213): the reordered wide-round tree

Session `wide_round_exposed_20260918_213`. Supports the notebook entry
`entry-2026-09-18-wide-rounds-exposed` (the node of the wide-round tree reordered: the
current term's wide rows first, then the round only if the term is still alive with an
alive pin, then the light moves; Lemma R0, Lemma X, Theorem T, Lemma Y, Corollaries A and B).

## Tools

- `research/tools/check_pair_space_encoding.py`, extended with `--wide-order`:
  `wide-first` (default) is the reordered node; `round-first` is the cycle-212 order.
  The path search, the encoder and the decoder process a node as a plan (`node_plan`):
  the wide rows in the term's order, the item `round`, then the light rows; at the round
  item the term's status and its pin are re-evaluated, and the round is made only if the
  term is neither falsified nor counting as falsified and the pin is alive. The path
  search records `max_rounds`, the largest number of rounds on a path.
- `research/tools/wide_rows_tree_check.py`, extended with `--wide-order`, `--readers`
  and a fourth reader `pins`: the terms `[a -> x] and [j in p]` for `a` in `A = {0,1,2}`,
  `x` in the cube `C(p) = {0, 4}` of the shared pattern `p` (bits 0 and 1 zero) and `j` in
  `B = {3,...,8}`, 36 terms, built so that a round-first node makes its round at a term
  whose wide row's cube is then exhausted by the round's own hole query at `x`.

## Files

- `roundtrip_pairs.jsonl`: 16 records of batch 10 (`runs.log` has the commands and
  outputs), the batch-9 configurations on the reordered tree: the three readers of the
  wide-rows entry on L2 = 1 (120960 pairs) and L2 = 2 (1512 pairs), eight random mixed
  readers with wide rows (3024 to 7560 pairs), and two `--code-rule any` controls.
- `tree_heights.jsonl` and `tree_heights_wide_{wide-first,round-first}_L2_{1,2}.txt`: the
  census over every rho' in Phi_0 for every flat of F_2^3 of dimension 1 and 2, four
  readers, both orders.

## Results

Batch 10: every rich pair decodes in all 14 runs with the current-term rule (0 failures),
`wide_gt_cover` is 0 and `max_rounds` at most 2 in every run; the controls fail on 106
and 12 pairs, all through a code label inside the excluded pin labels (`xcur_fail`).

Census: for the three readers of the wide-rows entry the two orders give identical
heights and wide-query counts in every restriction. For the pinned reader on the
four-hole flats meeting the cube (33264 restrictions, no term ever satisfied):
round-first has a path of length at least 2 in 73.6 percent, maximum height 4 and up to 2
rounds on a path; wide-first has such a path in 38.0 percent, maximum height 3 and at
most 1 round. Two-hole flats: 56.3 versus 26.1 percent, at most one round in either
order. Flats missing the cube: height 0 in both orders. Wide queries never exceed the
cover in any run.

## Reproduction

```
python3 research/tools/check_pair_space_encoding.py --tree wide --fill-domain notail \
  --code-rule current --reveal-slots --wide-lits 2 --L2 2 --e 2 --w 1 --h 3 --seed 4 \
  --terms 8 --pinned-rows 4 --tail-rows 2 --wide-rows 2 --out roundtrip_pairs.jsonl
python3 research/tools/wide_rows_tree_check.py --tree wide --wide-order round-first \
  --readers same-pattern,distinct,one-pin,pins --L 3 --L2 2 --out tree_heights.jsonl
```

The full command list is in `runs.log` (batch script `batch10.sh`, session scratch, whose
commands `runs.log` reproduces verbatim).
