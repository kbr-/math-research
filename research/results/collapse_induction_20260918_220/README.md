# Cycle 220: tipping counts of low-degree closures under generic dense axioms

Session `collapse_induction_20260918_220`. Supports the notebook entry
`entry-2026-09-18-collapse-induction` (Section 4, finite check for Question H).

## Tool

`research/tools/term_avoidance_check.py` builds the exact degree-`d` polynomial-calculus closure over
F_2 of a board (functional PHP with `N+1` rows, bijective control with `N` rows, labelings control
without hole axioms), then adds random dense axioms `Z_c = 0` one at a time (`w = 1`: a parity
constraint; `w = 2`: a clause of two parities) and records the closure dimension after every axiom and
the first count at which 1 enters. Forms: `uniform` (every row contributes a uniform subset of the
holes) or `affine` (the zero set of a uniform affine function of the label, `N = 8`).

## Files

- `tipping_N{N}_d{d}_w{w}_{family}.jsonl`: one record per board and seed with `base_closure`,
  `closure_dims` (after each axiom), `tipping_count`, `monomials`, `seconds`.
- `tipping_*.txt`: the console output of the same runs (written when a run ends).

## Reproduction

```
python3 research/tools/term_avoidance_check.py --N 8 --d 3 --w 1 --family affine \
  --seeds 1,2,3 --max-a 150 --out tipping_N8_d3_w1_affine.jsonl
```

Runs used `./compute.sh run collapse_induction_20260918_220 --threads 1`. Sizes: 673 to 45385
monomials; the eight-hole degree-three runs take two to three minutes per seed on the PHP and longer
on the labelings control. Eight holes at degree four (241993 monomials) is beyond this Python tool.

## Reading

See the entry. If 1 is in the closure the closure is the whole space, so the informative number is
the codimension of the closure after the axiom before the tipping one (`monomials - closure_dims[-2]`).
