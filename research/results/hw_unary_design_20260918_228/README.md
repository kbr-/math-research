# Exact Nullstellensatz spaces of the unary base with avoidance clauses (cycle 228)

Notebook entry: `entry-2026-09-19-unary-avoidance-ns-spaces`.

Tool: `research/tools/hw_unary_ns_rank.cpp`, built with `g++ -O2 -march=native -std=c++17`.
Every run went through `./compute.sh run hw_unary_design_20260918_228 --threads 1 --timeout S -- BINARY OPTIONS`.

Options: `--holes N --deg B --h H --clauses M --seed S [--forms label] [--spanall 1|2] --out FILE`.
The clause generator does not depend on `--deg`, so runs at different degrees with the same
holes, h, forms and seed use the same clauses.

Files (`ns_l{N}_d{B}_h{H}[_label]_seed{S}.jsonl`): one JSON line with the pivots of the base by
degree of the leading monomial and the monomial counts, one line with the base ranks, then per
clause a line `pivots_by_leading_degree` (partial sums give dim of G_B cap P_{<=e}) and a line
with the increment of dim G_B, dim G_B / I_B, the quotient left, and whether 1 lies in G_B.

- six holes: degrees 2, 3, h = 2, seeds 1, 2 (80 clauses requested; the run stops when 1 enters);
- seven holes: degrees 2, 3, 4 with h = 2 (seeds 1, 2); degrees 3, 4 with h = 3 (seeds 1, 2, 3; seed 3
  with 352 clauses);
- eight holes: degrees 2, 3 with h = 2, general forms (seeds 1, 2, 3; seeds 2, 3 at degree 3 with 266
  clauses) and label forms (seeds 1, 2);
- `ns_l8_d{2,3}_h2_label_spanall.jsonl` (`--spanall 1`): span of I_B and all f g x_sigma, f, g in a
  basis of the label forms: the reachable top-degree space (22512 of 28224 at degree three);
- `ns_l8_d3_h2_label_subalgebra.jsonl` (`--spanall 2`): span of I_3 and all products of three label
  forms: dimension 15997, top-degree part 14448, of which 12180 belong to I_3.

- `ns_l8_d{1,2,3}_h1_label_seed{1,2,3}.jsonl`: label parity constraints (h = 1), 40 clauses; first falls at
  clauses 19, 19, 20 (degree two) and 15 (degree three); included in `analyze.py`;
- `ns_l8_d3_h2_label_seed1_postsub{123..126}.jsonl` (`--postsub 1`): after the given number of clauses the
  products of three label forms are added; the last line gives dim (I_3 + L^3 + G_3) - dim G_3: 70, 44, 18, 0;
- `series_compare.py`, `series_compare.txt`: first nonpositive coefficient of the generic-polynomial series of
  cycle 223 against the clause series (sixteen holes).

`analyze.py` prints, for every family, the increments, the clause at which 1 enters, the first degree
fall (clause, level, dim of G_B cap P_{<=e}, dim G_e) and the first clause at which the count
dim G_B - dim G_{B-1} > m_B forces a fall. Run: `python3 analyze.py`; its output is `analyze_output.txt`.

A first batch wrote the JSON lines through the standard output of `compute.sh`, which keeps only the
last 8000 bytes; those files were overwritten by the batch with `--out`. The monomial key of the tool
was widened (base 128) before the eight-hole runs; the six- and seven-hole outputs were checked to be
identical before and after the change on a three-clause prefix.
