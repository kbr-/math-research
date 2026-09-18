# Cycle 222: scaling of the tolerated free dimension under random parity constraints

Session `parity_subspace_20260918_222`. Supports the notebook entry
`entry-2026-09-18-parity-subspace` (Section 3).

- `tipping_N16_d2_w1_affine_{php,bij,lab}.jsonl` and `.txt`: `research/tools/term_avoidance_check.py`
  on sixteen holes at degree two, parity constraints in the affine family (forms linear in the label
  bits), three seeds, on the functional PHP (17 rows, 32913 monomials), the bijective control (16 rows)
  and the labelings control. Record format as in `research/results/collapse_induction_20260918_220`.

The eight-hole rows of the entry's table come from that earlier directory
(`tipping_N8_d2_w1_affine.jsonl`, `tipping_N8_d3_w1_affine.jsonl`).

Reproduction:

```
python3 research/tools/term_avoidance_check.py --N 16 --d 2 --w 1 --family affine --boards php \
  --seeds 1,2,3 --max-a 120 --out tipping_N16_d2_w1_affine_php.jsonl
```

One to two minutes per seed. Sixteen holes at degree three (about 2.3 million monomials) is out of
reach of this tool.
