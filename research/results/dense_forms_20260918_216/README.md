# Cycle 216: dense forms on the compact family

Session `dense_forms_20260918_216`. Supports the notebook entry `entry-2026-09-18-dense-forms`
(Lemma I, invariance of random dense forms under every restriction in Phi_0; Lemma P, packing
by restricted rank; Lemma C, covering certificate of degree the rank; Lemma B, the balanced rank).

## Tool

`research/tools/dense_forms_check.py --out checks.jsonl` (seed 1):

1. `invariance`: for `l = 3`, `l_2 = 1, 2`, every flat `Q`, every residual row set `R'` and a
   sampled bijection `mu'`, the F_2-linear map from the coefficients of a form to the
   coefficients of its restriction on `V = Q^{R'}` has rank `v + 1` (onto).
2. `span`: random readers of `a` terms of rank `w` on `F_2^v`, 40 trials: whether 1 lies in the
   F_2-span of the terms and whether they span all multilinear polynomials of degree `<= w`;
   the mean uncovered share of `F_2^v` against `(1 - 2^-w)^a`.

## Files

- `checks.jsonl`: two invariance records and ten span records.
- `runs.log`: the command and its output.

## Results

Invariance: 2352 and 1764 restrictions, none not onto. Span: for `(v, w) = (8, 2)`, `D_w = 37`,
1 is in the span in every trial at `a = 60, 120, 200` and in none at `a = 20`; `(10, 2)`,
`a = 250`: every trial; `(10, 3)`, `D_w = 176`: every trial at `a = 400, 1400`, none at
`a = 60`. Lemma C's bound for `eta = 0.01` is `a >= 122, 174, 1013`. Uncovered shares: 0.343
against 0.344 at `(10, 3, 8)` and 0.361 against 0.356 at `(10, 4, 16)`.
