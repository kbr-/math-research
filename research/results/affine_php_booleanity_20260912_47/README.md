# Sharp affine Booleanity in weak PHP

The notebook entry [Classify sharp affine Booleanity](https://kbr-.github.io/math-research/#entry-2026-09-12-affine-php-Booleanity)
contains the general proofs, the exact retained-extension hypothesis, and the
characteristic-two packing consequence. This directory preserves its finite checks.

## Reproduce

From the repository root with active resource controls:

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_affine_php_booleanity.cpp -o /tmp/check_affine_php_booleanity
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_affine_php_booleanity --out PATH-TO-NEW-OUTPUT.jsonl
```

The saved run used session `affine_php_booleanity_20260912_47` and `checks-01.jsonl`
in this directory. Existing output is never replaced. No random choices are used.
The checker imports the degree-two board and exact modular basis kernel from
`check_target_annihilators.cpp`; that earlier tool's test suite is not invoked.
Its new `TARGET_ANNIHILATORS_NO_MAIN` guard leaves standalone behavior unchanged.

The initial build and full run succeeded. That build emitted a misleading-indentation
warning and a warning from renaming the imported main function. A formatting fix
and the main guard removed both; the final build is clean. These edits do not
change any matrix or polynomial operation. The completed computation was not rerun.

## Scope and records

The six bases use 3 or 4 holes and primes 2, 3, 5. Their degree-two monomials are
reduced only by Boolean and column-exclusion equations. Same-row products remain.
The normalized span of all row equations and their variable multiples has affine
part exactly the row span in every case, verifying PC closure at degree two.

For four holes, the checked affine slices are:

- All `2^9 = 512` choices on two fixed rows over F2, including the constant term.
- All `3^9 = 19,683` choices on two fixed rows over F3, including the constant term.
- All `5^5 = 3,125` choices on one fixed row over F5, including the constant term.
- All column subsets/complements with zero and one prescribed row-gauge pattern
  over F3 and F5: 1,024 further tests, some deliberately repeated.
- Two explicit negative partial-row/cross-column sums in each odd field.

Total: 24,348 tests, 1,820 positive and 22,528 negative; 282 checked dual vectors.
The general classification agrees with every tested membership decision.

`checks-01.jsonl` contains the monomial dictionaries, every original row multiple,
all echelon bases, all test polynomials, and the annihilating dual vectors.
Sparse vectors use `[coordinate, coefficient]` pairs in the board's stated field.
An affine polynomial uses coordinate zero for the constant and `1+i*n+j` for a cell.
Normal quadratic coordinates are listed explicitly in each board record.

Each negative test gives the index of a saved dual and its nonzero target value.
Every dual was checked against every original row multiple. Boolean/collision
generators vanish under the explicitly specified degree-two reduction. The output
also saves the column, subset, complement, and row gauges for each positive odd-field
classification. Complete matrix reconstruction is possible from the saved generators.

The checks are not an exhaustive enumeration of all board-wide affine polynomials.
Extra coefficient variables, arbitrary board sizes, and the general packing rule
are treated by the notebook's analytic proofs. `provenance.json`, `timing.html`,
and the archived session preserve hashes, commands, and measured intervals.
