# Dense column-witness elimination

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-dense-column-requests)
contains the occupied matching argument, empty-column freezing argument, combined
residual-board bound, NS/PC degree ledger, and precise scope limitations.

## Finite fixture

Over F2, take 25 rows and 24 columns. The two occupied witness sets are the even
and odd values of row+column, each containing 300 cells. The two empty witness
sets are the twelve even or twelve odd columns. Indices start at zero.

A deterministic search with rows 0,1,2 rejects columns 0,1,2 and accepts 0,1,3.
The five designated empty columns are 2,4,5,6,7. The additional matching prefix
is row 3 to column 8. Five copies of a residual 4-by-3 board plus one complementary
row give the recorded affine map. The residual board has N=3 holes.

The exact sufficient union bounds are 54/64 and 2048/16807. No Monte Carlo
probabilities or universal theorem are inferred from this finite fixture.
An all-even empty-set control misses the odd empty family; the failed matching
candidate misses the odd occupied family. These only test designated coverage.

The four accuracy-one blocks lie at levels 1,1,2,3. Occupied inputs are sums of
parity-selected cells in individual columns; empty inputs are one minus the full
column sum. Each block also has an extra input whose image remains y_00. For
the later blocks this input includes a strictly earlier chosen coefficient.
The extras are chosen to exercise this scope after the map is fixed; the density
data used for selecting the map are fixed independently of those extras.

The output preserves all 600 cell images, 76 input images, original companion
degrees, and coefficient assignments. It verifies 24 column sums and all 76
companion plus 76 coefficient-field images. Complete source polynomials are
specified compactly by the input descriptions and the block product formula.
Polynomial images use the existing kernel format: coefficient/exponent pairs,
with residual y_i_j at variable index 3*i+j. The empty list is the zero polynomial.

The preceding universal freezing proof supplies the base-image certificates;
its full finite suite was not rerun. No full PHP satisfying model is claimed.
The four nonconstant extra images show why a literal unit suffices even when
the rest of a block has not become constant.

## Reproduce

```bash
./compute.sh run CHECK --threads 1 --category local_processing --timeout 90 -- \
  g++ -O2 -std=c++17 -Wall -Wextra -pedantic \
  research/tools/check_dense_column_requests.cpp -o /tmp/check_dense_column_requests
./compute.sh run CHECK --threads 1 --category computation --timeout 90 -- \
  /tmp/check_dense_column_requests --out PATH-TO-NEW-OUTPUT.jsonl
```

The checker refuses to overwrite output. The saved run is `checks-01.jsonl` in
this directory; compilation and all checks passed. `provenance.json`, the timing
fragment, and the archived session preserve sources, full output, and timing.

The theorem assumes designated base-only single-column inputs and positive
density bounds. Other inputs may use earlier coefficients. It does not establish
the coverage condition for every source family or solve the general lower-bound
problem. The full statement and proof remain authoritative in the notebook.
