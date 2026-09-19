# Parity constraints at degree two: checks of the two-form criterion (cycle 229)

Notebook entry: `entry-2026-09-19-parity-degree-two-first-moment`.

Tool: `research/tools/two_form_criterion_check.py` (exact linear algebra over F_2 with Python integers).
Every run went through `./compute.sh run parity_degree_two_first_moment_20260919_229 --threads 1 -- python3 TOOL OPTIONS`.

- `criterion_l4_uniform.jsonl`, `criterion_l4_label.jsonl`: four holes, 200 random instances for each number M
  of parity constraints (`--holes 4 [--label] --trials 200 --seed 1 --mmin 1 --mmax 7|8`);
- `criterion_l6_uniform.jsonl`: six holes, 40 instances, M = 11..17;
- `criterion_l8_uniform.jsonl`: eight holes, 20 instances, M = 29..34;
- `criterion_l8_label.jsonl`: eight holes, label forms, 40 instances, M = 15..22.
- `criterion_l16_label_M{46,50,52,53,54,55}.jsonl`: sixteen holes, label forms, 5 instances each (seed 1): no
  fall for M <= 53, every instance falls for M >= 54 (forced count C(14,2) = 91 < 102).

Fields per line: `d` (dimension of the annihilator U in V^*), `independent` (instances whose forms are
independent modulo the row sums), `star` (criterion (*) holds: the restriction of the conflict two-forms to
U has rank dim Kbar), `fall` (dim of G_2 cap P_{<=1} exceeds dim G_1), `star_and_fall` (violations of
Theorem T2: none), `nostar_nofall`, `count_ok` (dim G_2 equals the count).

- `structure_l{4,8,16}.json` (`--structure N`): dim Kbar, the rank of Kbar restricted to the annihilator of the
  label forms, and their difference dim (Kbar cap (Lbar wedge V)): 850 on sixteen holes (the same-row part,
  17 * 50), 171 = 135 + 36 on eight holes, 45 on four.

- `isotropy_bounds.jsonl` (`research/tools/isotropy_bounds_check.py --nmax 8`): exact probability that the
  alternating form of rank 2 rho vanishes on a uniform d-subspace of F_2^n (all subspaces enumerated,
  n = 4..8, d = 2..4), against the bounds of Lemmas R1 and R2; last line: largest ratios 0.59 and 0.16.
