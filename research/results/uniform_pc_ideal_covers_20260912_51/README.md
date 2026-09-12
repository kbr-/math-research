# Stable-ideal normalizers and coverage controls

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-stable-ideal-normalizers)
contains the general PC ideal-cover ledger, stable-ideal NS test, exact affine
feasibility criterion, high-rank example, and row-difference factor bounds.

## Reproduce

From the repository root, with active resource controls:

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_stable_ideal_normalizers.cpp -o /tmp/check_stable_ideal_normalizers
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_stable_ideal_normalizers --out PATH-TO-NEW-OUTPUT.jsonl
```

The saved session is `uniform_pc_ideal_covers_20260912_51`, with `checks-01.jsonl`
in this directory. Output is never overwritten. No random choices are used.
The checker reuses the exact normal-form and sparse-polynomial kernels from
`check_ens_input_reduction.cpp`, `check_small_probe_normalizers.cpp`, and
`pc_boundary.hpp`. The new `ENS_INPUT_REDUCTION_NO_MAIN` guard permits reuse
without executing the earlier suite or changing its standalone behavior.

Both builds succeeded; before the only mathematical run, the certificate check
was strengthened to enforce each image's own ordinary degree as well as the
original companion budget. The final build and every check succeeded.

## Linear systems

Fifteen systems cover primes 2, 3, 5:

- Two-row difference inputs on one through four columns, with interleaved old
  variables `x_(a,j), x_(b,j)` at indices `2j, 2j+1`. The proper base includes
  Boolean equations and one collision per column, with no row equations.
- One field-valued input a, with its actual field domain.

The shared unknowns are coefficients of the first affine coefficient row;
all other rows are zero. Six systems are feasible: the one-column difference
case in every field, the two-column case over F2, and the field input over F2/F3.
Nine are infeasible. Every solution is reconstructed against the full matrix;
every infeasibility dual annihilates every matrix column and is nonzero on the RHS.

The JSONL output retains each equation's input-component/monomial coordinate,
every matrix column and RHS, and the full sparse solution or dual. Unknowns are
ordered by input index, then the constant and each old variable. Sparse matrix
vectors use `[coordinate, coefficient]` pairs. Polynomials use the exact sparse
format of `pc_boundary.hpp`.

## Additional normalizers and row controls

- The binary four-column tuple is normalized with two affine coefficient rows,
  despite failure of its first-row-only system. This meets the binary factor bound.
- Six high-rank examples use m=2,3 and primes 2,3,5. Old variables are x,y, then
  z_1,...,z_m,w_1,...,w_m; the tuple is
  `(x+y-xy, x*z_1,...,x*z_m, y*w_1,...,y*w_m)`.
  Setting only the first coefficient to one gives `(1-x)(1-y)`. All image
  certificates have degree four, below original companion degree five.
- Every row-difference case separately records the old row-equation normalizer
  and its companion multiples. Those 42 certificates explicitly add one actual
  row equation to the proper base. They are not domain-only certificates.

Total: 15 affine systems, six feasible, nine infeasible; 13 normalizations;
153 NS certificates; 1,411 domain states and 1,064 canonical source lifts.
All proper base states are covered for the listed small instances. Source lifts
use the specified coefficient maps, not every possible coefficient completion.
These source-model records do not include the separately added row equation
and are not full PHP models.

The analytic proper-ideal row-difference bounds are `n<=2h` for affine coefficients
in every characteristic, and the stronger `2n<=3h` in odd characteristic.
The binary optimum is `ceil(n/2)`. Odd constant coefficients require exactly 2n
rows; the current odd affine interval is `ceil(2n/3)<=h_min<=n`.
The triple case n=3,h=2 is deliberately left for the next cycle.

These lower bounds exclude only normalization certified by the proper stable
ideal. The full PHP row equations supply a degree-two normalization error and
degree-three companion images at accuracy one, for every n.

`provenance.json`, `timing.html`, and the archived session preserve sources,
complete output, actual commands, and measured intervals.
