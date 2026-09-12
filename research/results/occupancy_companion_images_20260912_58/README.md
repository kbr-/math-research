# Exact affine accuracy for occupancy companions

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-occupancy-affine-accuracy)
contains the universal proof: row averaging reduces a putative affine one-row
normalizer to a quadratic in column statistics; freezing forces zero values on
small zero-column slices; binomial reconstruction contradicts its value at the
common-zero probe profile.

The theorem concerns original-degree companion proofs on the unchanged weak PHP
base. When p divides n, one affine row is impossible even with PC degree-three
image proofs for n>=18 in F2 and n>=6(p-1) in odd characteristic. Two rows suffice
by the existing Hall construction. When p does not divide n, the preceding
one-row NS construction works for n>=3. Broader projections, nonlinear maps,
larger image budgets, and additional ENS context are outside this lower bound.

## Exact coefficient checks

The reconstruction target is z_0=0 and z_j=1 for 1<=j<n. A K-slice consists
of every K-subset of T={1,...,n-1}, interpreted as its Boolean indicator vector.
Each point in an active slice has the same recorded field weight.

| n | p | Active slice sizes | Residual holes | Ordinary monomials checked |
| -: | -: | :-- | :-- | -: |
| 18 | 2 | 1, 3 | 17, 5 | 190 |
| 20 | 2 | 3 | 5 | 231 |
| 12 | 3 | 2 | 5 | 91 |
| 15 | 3 | 2 | 6 | 136 |
| 25 | 5 | 4 | 5 | 351 |
| 42 | 7 | 6 | 6 | 946 |

All 1,945 ordinary degree-at-most-two monomials, including squares, satisfy
the reconstruction formula. All seven active freezing maps retain at least
five residual holes, where the audited PC lower bound excludes degree three.
Subset totals are evaluated by exact integer binomial coefficients within the
guarded integer range. The output compactly specifies the complete slice families
and their uniform weights; no slice members are silently omitted or sampled.

Four negative controls record the expected mismatch:

- Omit the binary singleton correction where it is needed.
- Use singleton slices alone on a quadratic cross term.
- Use the odd-field formula with the wrong target congruence.
- Apply the F3 quadratic reconstruction to a cubic monomial.

These controls concern the displayed formulas, not every possible alternative
reconstruction. The universal freezing and Hall certificate proofs are reused;
their previous finite suites were not rerun. No full PHP satisfying model or
generic cubic-rank computation is claimed.

## Reproduce

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_occupancy_slice_reconstruction.cpp -o /tmp/check_occupancy_slice_reconstruction
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_occupancy_slice_reconstruction --out PATH-TO-NEW-OUTPUT.jsonl
```

The checker refuses to overwrite output. `checks-01.jsonl` contains every
monomial check, family count, weight, residual size, and control. Compilation
and all checks passed. `provenance.json`, `timing.html`, and the archived session
retain exact sources and measured evidence. The initial outline of the next
partition-statistic step was also part of this interval.
