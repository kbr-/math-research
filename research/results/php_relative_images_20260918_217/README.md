# Cycle 217: hole axioms and images of dense-form blocks (exact closures)

Session `php_relative_images_20260918_217`. Supports the notebook entry
`entry-2026-09-18-php-relative-images`.

## Tool

`research/tools/php_relative_image_check.py`. Board with `N+1` rows and `N` holes, cell
variables over F_2. System A: Booleanity, row exclusions, row axioms (labelings). System B
adds the hole exclusions (functional PHP). `V_d` is the degree-`d` polynomial-calculus
closure of the row axioms inside the span `T_d` of the surviving monomials. For a block
with inputs `g_i` of degree `w` and parameter `s` the linear image conditions are
`P-hat in T_s`, `U_i in T_{s-w}`, `1 + P-hat + sum U_i g_i in V_s`, `g_i P-hat in V_{s+w}`
(Booleanity of `P-hat` not imposed). Options: `--N`, `--dmax`, `--readers`, `--affine`
(affine half-spaces of F_2^log2(N) as row label sets), `--only NAME`, `--rank2` (rank-two
terms at `s = w = 2` with the degree-4 closure, system B, plus a function-level check that
`P` has row-degree at least 3 on labelings).

## Files

- `images_N4.jsonl`: four holes; with the hole axioms `V_3 = T_3` (refutation degree 3), so
  every image condition is vacuous there.
- `images_N6.jsonl`, `images_N6_control.jsonl`: six holes, `d <= 3`, three readers for each
  codimension, a symmetric reader, the positive control.
- `images_N6_d4.jsonl`: six holes, `d <= 4`: `V_4 = T_4` with the hole axioms (refutation
  degree 4); codimension three has the image `P` at `s = 3` without them.
- `images_N8.jsonl`, `images_N8_control.jsonl`: eight holes, uniform half-sets.
- `images_N8_affine.jsonl`: eight holes, affine half-spaces, with the control.
- `images_N8_rank2.jsonl`: eight holes, degree-4 closure, rank-two readers.
- `runs.log`: commands and raw output.

## Results

Rank-one inputs (flat indicators), identical with and without the hole axioms in all 38
reader and parameter pairs: codimension 2 infeasible at `s = 1`, feasible at `s = 2`;
codimension 3 infeasible at `s = 1, 2`. Positive control (two rows pinned to one hole, one
dense form): infeasible at `s = 2` without the hole axioms, feasible with them, on both
boards. System A quotient dimensions equal `sum_{k<=d} C(N+1,k)(N-1)^k`.

Rank-two inputs on eight holes (`images_N8_rank2.jsonl`): `dim V_4 = 143643` in `T_4` of
dimension 241993, `1` not in `V_4`, closure equal to the span of the `t Q_j`. All six dense
readers (2, 4 and 8 terms, two each) are infeasible at `s = w = 2` with the hole axioms, and
`P` has row-degree at least 3 on labelings, so they are infeasible without them too. The
control (`t_1 t_2` killed by a hole exclusion) is feasible with the hole axioms only.

## Reproduction

```
python3 research/tools/php_relative_image_check.py --N 6 --dmax 3 --out images_N6.jsonl
python3 research/tools/php_relative_image_check.py --N 8 --dmax 3 --readers 3 --affine \
  --out images_N8_affine.jsonl
python3 research/tools/php_relative_image_check.py --N 8 --rank2 --out images_N8_rank2.jsonl
```

Note: `images_N6.jsonl`, `images_N8.jsonl` and `images_N8_rank2.jsonl` (no `affine` field)
were produced before the control reader and
the `--affine` option were added; the readers they contain are unaffected by those additions
(same seed, same sampling order for the dense and symmetric readers).
