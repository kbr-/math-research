# Cycle 215: route review of the literal frontier, with one finite check

Session `pinned_wide_mass_20260918_215`. Supports the notebook entry
`entry-2026-09-18-route-review-literal`. The cycle opened as the pinned single-wide-row
dichotomy and was closed as a route review: the literal line is parked as Conjecture L and
the next step returns to terms with dense forms (Question D). The only computation is the
control below, run before the review; nothing is built on it.

## Tool

`research/tools/wide_mass_sim.py`: Monte Carlo control of the intended, unproved
matched-mass mechanism. Reader: pinned rows `A` (half the rows), pins `(a, y)` for every
`a` in `A` and every label `y`, each with full-label incidences `[j = z]` on `k` wide rows.
For a uniform rho' in Phi_0 it computes `F`, the sum over matched wide rows `j` of
`|S_j^m cap Rem|` (`S_j^m` the union over matched pinned rows of the cubes on `j` of the
matched pins, `Rem` the labels outside `Q` not taken by pinned rows), the candidate bound
`b' Sigma_cap / (4 n^2)`, and whether some term is satisfied by rho'.

## Files

- `matched_mass_sim.jsonl`: eight records (batch 12), 300 samples each, seed 1.
- `runs.log`: the commands, outputs and exit codes.

## Results

| n | N | k | mean F | min F | candidate bound | satisfied share |
|---|---|---|---|---|---|---|
| 64 | 4 | 33 (all) | 343.3 | 296 | 123.2 | 1.000 |
| 64 | 4 | 8 | 98.3 | 78 | 30.0 | 0.960 |
| 64 | 4 | 2 | 25.9 | 14 | 7.5 | 0.533 |
| 128 | 4 | 65 (all) | 1495.2 | 1397 | 503.9 | 1.000 |
| 128 | 4 | 8 | 224.7 | 192 | 62.1 | 0.960 |
| 128 | 8 | 65 (all) | 1361.3 | 1238 | 486.8 | 1.000 |
| 256 | 8 | 129 (all) | 5935.3 | 5633 | 1998.8 | 1.000 |
| 256 | 8 | 4 | 230.0 | 198 | 61.9 | 0.853 |

The smallest observed `F` exceeds the candidate bound in every configuration (by a factor
between 1.8 and 3.2). This is a finite check of an unproved claim.

## Reproduction

```
python3 research/tools/wide_mass_sim.py --L 7 --L2 2 --k 8 --samples 300 --seed 1 \
  --out matched_mass_sim.jsonl
```
