# Check of the sequential boost bound (Spin cycle 226, 18 September 2026)

Notebook entry: `entry-2026-09-18-parity-tree-concentration` (Lemma N).

`research/tools/sequential_boost_check.py --l L --trials T --maxtau M --out FILE` draws random
affine subspaces of (F_2^L)^n, n = 2^L, whose forms are supported on at most M rows (codimension
at most 8), computes by full enumeration the density boosts of the bijections S_0 and of S_1
(labelings with exactly one colliding pair), and asserts boost <= bound, where the bound is the
minimum over all orderings of the touched rows of the product over pivot positions i of
C / (n - i + 1), C = n for S_0 and C = n + 3 for S_1.

- `seqcheck_l2.json`: four holes, 2000 subspaces, M = 4: no violation; largest boost/bound 1.0
  (S_0) and 0.571 (S_1).
- `seqcheck_l3.json`: eight holes, 400 subspaces, M = 5: no violation; largest boost/bound 1.0
  (S_0) and 0.727 (S_1).

Both runs went through `./compute.sh run parity_tree_concentration_20260918_226 --threads 1`.

Power of the check: for S_0 the bound is attained, also on subspaces touching two or more rows
(282 of 571 and 43 of 120 samples with boost above one attain it), so an error in part (a) or in
the pivot count would show. For the constant of the S_1 bound the check has no power: the largest
S_1 ratios come from one-row subspaces, and no sample exceeds even the bound with constant n.
