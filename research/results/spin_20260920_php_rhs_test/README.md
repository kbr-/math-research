# Fixed-space PHP right-hand-side test

The checker performs one common leading-cubic elimination while carrying the
lower residues for all right-hand sides. It then reduces each residue modulo
the corresponding quadratic relation space and checks the affine variation law.
No polynomial proof certificate or Lean verification is claimed.

```bash
./compute.sh g++ -std=c++20 -O2 research/tools/check_php_rhs_residue.cpp -o /tmp/check_php_rhs_residue
./compute.sh /tmp/check_php_rhs_residue --holes 5 --constraints 0 --seed 1 --out /tmp/base-new.json
./compute.sh /tmp/check_php_rhs_residue --holes 6 --constraints 6 --seed 1 --out /tmp/six-new.json
./compute.sh /tmp/check_php_rhs_residue --holes 6 --constraints 5 --seed 1 --out /tmp/five-new.json
```

Bounds: holes 5..6, constraints 0..6; at most 64 right-hand sides. The preflight
bounds primary matrix storage below 200 MB; actual workload enforcement remains
with compute.sh. Heavy elimination is compiled binary arithmetic.

Linear parts are sampled directly in the row-quotient coordinates with
std::mt19937_64(seed), rejecting dependent rows. This is NOT the historical
raw-cell/label generator, despite sharing a seed number. Bit i*(N-1)+j represents
the j-th non-final coordinate of pigeon i, with zero-based indices. The final
coordinate is 1 plus the sum of that row's retained coordinates.

Reports preserve every original linear mask, the complete affine elimination
maps, and all right-hand-side results. A row's `rhs` is the bit vector of constants
of the original (pre-RREF) linear parts. In `affine_equations`, the low M bits are
the coefficients and bit M is the right-hand side; these are all distinct
nonzero equations encountered for vanishing quadratic residue, not just a basis.
`variation_rank` is the rank of this coefficient system, not the rank of one
residue map. `quadratic_affine_consistent` also tests its constant column.

`fall_dimension` is the degree-three NS fall quotient dimension. The quadratic
and lower ranks sum to it. `one_in_G3` tests the NS space, not iterated PC closure.
`leading_relation_count` includes old syzygies; quadratic faithfulness makes
the relative symbolic dimension equal to this count minus the old syzygy count.
The notebook proves that identity. The five-constraint file is the exact prefix
of the six-constraint linear parts. All output is preserved, including the
old-base positive control.
