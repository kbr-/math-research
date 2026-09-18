# PHP on a random affine subspace in residual coordinates (Spin cycle 223, 18 September 2026)

Notebook entry: `entry-2026-09-18-subspace-residual`.

By Lemma R of the entry the polynomial-calculus refutation bit degree of the compact bit base
with the equations of an affine subspace W (dimension k) equals that of the collision-flat
system in k residual coordinates, for degrees at least l. The tool
`research/tools/subspace_flat_cover_closure.cpp` computes that closure exactly over F_2.

Build: `g++ -O2 -march=native -std=c++17 -o sfc research/tools/subspace_flat_cover_closure.cpp`

Runs (all through `./compute.sh run subspace_design_20260918_223 --threads 1`):

- `php_l{L}_d{D}.jsonl`: `sfc --ell L --d D --kmin D --seed S` for S = 1, 2, 3; n = 2^L holes,
  n + 1 rows; the scan raises k until the first k that is not refuted at bit degree D.
- `bij_l{L}_d{D}.jsonl`: the same with `--rows n` (bijective control).
- `full_l3_d5_identity.jsonl`: `sfc --ell 3 --d 5 --kmin 27 --kmax 27 --identity`, the full
  eight-hole base in its original coordinates; refuted at bit degree five.
- Sanity checks quoted in the entry: `sfc --ell 2 --d {2,3} --kmin 10 --kmax 10` with and without
  `--identity` (refuted at degree three, not at two, in both coordinate systems).
- Semantic status of the controls (`control_injective_points.jsonl`), for S = 1, 2, 3:
  `sfc --count --ell 3 --rows 8 --seed S --kmin 6 --kmax 11`,
  `sfc --count --ell 4 --rows 16 --seed S --kmin 12 --kmax 21` and
  `sfc --count --ell 5 --rows 32 --seed S --kmin 12 --kmax 18` (brute-force number of points of
  W_k with pairwise distinct labels).

Limits and incidents: each seed's scan had a time limit of 1700 s; the degree-seven scans
(seed 1 only) were stopped by hand shortly before that limit while still refuting, so that the
other seeds would not start (exit 144 of the two batch drivers). The batch for four and eight holes was stopped by hand once the
full eight-hole base was refuted at degree five, which makes the eight-hole scans at degrees
five and six redundant (every subspace is then refuted at degree five).

`summarize.py` prints the largest refuted k per seed next to the generic count (first degree at
which the coefficient of t^d in (1+t)^k (1+t^l)^(-m) is not positive, m the number of row pairs).
