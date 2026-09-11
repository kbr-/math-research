# A spread resisting single-cell constant normalization — 11 September 2026

The general existence proof and scope are in [the notebook](../../../notebook.html),
entry `entry-2026-09-11-resistant-spread`. The
[claim index](../../CLAIM_INDEX.md) provides stable labels.
This is a counterexample to universal small-matching coverage by the stated
constant-normalization criterion, not to every restriction or elimination method.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic research/tools/find_restriction_resistant_spread.cpp -o research/tmp/find_restriction_resistant_spread
./compute.sh --threads 1 research/tmp/find_restriction_resistant_spread --out research/tmp/resistant-spread-recheck.jsonl --seed 20260911
```

The destination must be new. The fixed experiment uses p=2, n=7, m=8,
ambient dimension 48, and seven rank-24 graph spaces. The generator is
`std::mt19937_64`; all algebra uses exact binary operations in compiled C++.
Compilation used GCC 11.4.0. No package was installed.

The first matrix draw was invertible and satisfied all conditions. Compilation
and execution both passed on their first attempt. The program checks 21 pairwise
intersections, all 56 single-cell matching restrictions, and all 392 resulting
space–matching pairs. Every restricted space has rank 24.

## Certificate and coordinates

[certificate-01.jsonl](certificate-01.jsonl) preserves all 402 records, 160,298
bytes, including the matrix, every original and restricted input, and every dual
witness. [summary.json](summary.json) records the counts, exact source/output
hashes, and the prior notebook commit used for the restriction-quotient argument.

All vector words are hexadecimal strings, with bit zero the least significant
bit. Source coordinates enumerate `x_(i,j)` by bit `6*i+j`, for rows 0–7 and
columns 0–5; original column 6 is omitted using the row equations.

The `matrix_draw.images` array lists the images of the 48 standard basis vectors.
Apply the matrix by XORing the listed images for the set bits of an input.
The initial graph spaces use eight copies of F8, represented by
F2[X]/(X³+X+1). Alpha runs through 0–6, with binary digits as polynomial
coefficients. The input indexed j has a unit in first-half coordinate j and the
coordinates of alpha*X^(j mod 3) in the corresponding second-half copy.

For a matching `(row,column)`, the chosen cell becomes one and the other cells
of its row and column become zero. Residual coordinates have dimension 36:
bit 0 is one, followed by the seven remaining rows in increasing order, each
using its five independent columns in increasing order. The matched column and
the largest remaining column are omitted. The latter variable is replaced by
one plus the other five row variables.

Every `dual_witness` includes all 24 restricted inputs and a vector `dual`.
The exact certificate conditions are:

- bit 0 of `dual` is one;
- the parity of `dual & input` is zero for each restricted input.

These conditions separate one from the restricted input span modulo row
equations. The program checks them by dot products after constructing the
witness by Gaussian elimination. Flipping the constant bit is rejected in all
392 controls. These vectors are not satisfying assignments of PHP and are not
joint proof-system designs.

## Existence versus search

The notebook's uniform-random-embedding proof is independent of the pseudorandom
search. At these finite parameters its union bound is exactly
1,605,632 / 16,777,217 < 1. The saved matrix and witnesses establish the concrete
case without relying on a probability estimate.

The construction preserves the admissible spread input data. For any chosen
positive accuracy, its inputs specify all ENS companions in the usual way.
No low-degree augmented refutation or Frege proof is supplied or assumed.

## Timing

[timing.html](timing.html) is embedded in the notebook. The
[archived session](../../provenance/session-records/restriction_resistant_spread_20260911_03/)
preserves command evidence. Verification focused on the mathematical certificates
and newly added claim links; no routine notebook rendering checks were run.
