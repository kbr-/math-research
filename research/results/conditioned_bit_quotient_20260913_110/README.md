# Independent targets after conditioning

Full statements and proofs appear in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-conditioned-bit-quotient).
The checks cover Boolean multiplication, bounded-row-degree coefficient duals,
an actual compact-PHP relation outside the sufficient range, and exact formulas.
They do not construct a large PHP quotient, the earlier existential weight, or
a second-level elimination.

## Reproduce

From the repository root, with shared resource controls active:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_conditioned_bit_quotient.cpp \
  -o /tmp/math-conditioned-bit-quotient
./compute.sh run TURN --threads 1 -- \
  /tmp/math-conditioned-bit-quotient --out NEW_OUTPUT_PATH
~~~

Existing output paths are refused. The seed is 202609130110. Arithmetic is
exact over F2, with the existing Boost compiled integer implementation for
dimension formulas.

## Complete output

<code>quotient-checks.jsonl</code> retains:

- All 2,047 nonzero affine weights on five two-bit rows and 128 seeded mixed
  row-linear weights, followed by every product, pivot, reduction, and residual.
  All 69,361 multiplier columns are independent. This component is a Boolean
  algebra check independent of the PHP degree-range hypotheses.
- 160 seeded coordinate-axis families of degree eight at bit width seven.
  Their cube points and complete missing-row parities cover 40,960 legal tuples.
- Three old equalities on n=8 and their nonzero sum of degree three and row
  degree two. The sufficient cube inequality fails on this actual old relation.
- Four exact dimension ledgers: an active case, separate inactive-condition
  controls, and n=2^22 with weight/target degree 9216 and budget 1843200.
  Large integers are complete decimal strings. A candidate dimension is
  asserted to inject only under the corresponding mathematical hypotheses.

Polynomials are arrays of squarefree monomial bit masks over F2. Bit order is
row-major, low-order bit first within each row. Repeated monomials cancel;
multiplication takes mask unions followed by parity collection.
The multiplication test orders monomials first by total degree, then by mask.
Gaussian pivots separately use numerical mask order; all reductions are saved.

The provenance manifest records source/output hashes. The timing fragment and
session archive retain measured work and complete command output. No packages
were installed, and compiled jobs used the shared computation limits.
