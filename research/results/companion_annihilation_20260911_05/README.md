# Direct companion annihilation

11 September 2026. Timing session: `companion_annihilation_20260911_05`.
Full statements and proofs:
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-companion-annihilation).

## Accepted results

All computations use exact binary arithmetic and the ordinary Boolean,
linear-row PHP base, with no same-row exclusions.

- `base-pc3-01.txt` certifies the degree-three PC space for n = 7, m = 8.
  There are 19,321 normal monomials and 9,276 independent consequences.
  The lower-degree part has dimension 420, equal to the degree-two space.
  The affine part has dimension eight.
- The query program replays every basis derivation, verifies all 11,208
  original generators, and checks all 23,520 allowed products of lower-degree
  basis rows. Thus the queried space is PC-closed, not merely an NS span.
- `checks-02.jsonl` contains the accepted expanded computation. In each of
  the seven saved spread spaces, the first three inputs give an injective
  multiplication map from the 981-dimensional quadratic quotient into three
  copies of the 10,045-dimensional cubic quotient.
- In saved space zero, the corresponding first-input and first-two-input
  kernels have dimensions 48 and one. All 49 kernel vectors are retained.
  Nine nonsingular minors certify the image ranks.
- Every full 24-input tuple excludes affine coefficients satisfying even the
  first three companion equations through base PC degree three. Each system
  has 1,368 parameters and rank 876. Seven tuples of three functionals certify
  inconsistency by direct polynomial-coordinate checks.
- A two-input block passes as a positive control, with explicit coefficients.
  Every obstruction tuple has a perturbation rejected by a specified parameter
  equation while preserving annihilation of the base space.

The earlier `pilot-01.jsonl` is preserved as an exploratory output for space
zero. It predates the added kernel/minor reporting and corruption controls;
all accepted mathematical cases from it are repeated in the expanded result.
The reproduction commands below generate the final expanded format.

These are finite results for the specified board and inputs. They do not assert
a universal PC/NS equality or exclude larger degree budgets, several nontrivial
ENS factors, nonlinear substitutions, or certificate-dependent transformations.

## Reproduction

From the repository root, with the shared resource controls active:

```bash
mkdir -p .resource-runtime/bin
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/build_php_degree3.cpp \
  -o .resource-runtime/bin/build_php_degree3
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/check_companion_annihilation.cpp \
  -o .resource-runtime/bin/check_companion_annihilation
./compute.sh --threads 1 --timeout 240 \
  .resource-runtime/bin/build_php_degree3 --holes 7 \
  --out research/results/companion_annihilation_20260911_05/base-pc3-REPRO.txt
./compute.sh --threads 1 --timeout 240 \
  .resource-runtime/bin/check_companion_annihilation \
  --base research/results/companion_annihilation_20260911_05/base-pc3-REPRO.txt \
  --inputs research/results/restriction_resistant_spread_20260911_03/certificate-01.jsonl \
  --first-targets 3 \
  --out research/results/companion_annihilation_20260911_05/checks-REPRO.jsonl
```

Both programs refuse to replace existing output. The builder currently supports
binary boards up to seven holes. The query uses the fixed seven-hole spread
producer schema. It increases the number of tested companion targets by three
if a prefix is feasible, while keeping all inputs available to the coefficients.
All seven accepted cases were already excluded at the first three targets.

The accepted run used GCC 11.4.0, C++17, one thread, and the protected launcher.
No dependencies were installed. Both programs share `binary_php.hpp`; the
query consumes the saved base derivations so future queries can reuse them.
Sparse and dense binary row operations are selected within the compiled kernel.

## Base proof format

The text proof is a tokenized, versioned format:

- `BINARY_PHP_PC 1 n 3 variables low width` declares the schema and dimensions.
- `MONOMIAL id mask` gives every normal monomial. Mask bit v denotes variable v,
  with v = row*n + column. The constant has mask zero. Coordinates are ordered
  by degree and then increasing variable tuples. Same-row products are retained.
- `BASIS pivot kind a b count old_pivots... count terms...` records a new basis
  row. Kind `A` starts from row axiom a times monomial b. Kind `P` starts from
  the previously derived low-degree row at pivot a times variable b.
  The listed old pivot rows are added in the given order over F2; the final
  sorted term list gives the claimed new row.
- `INITIAL rank low_rank` marks the original-axiom span.
- `FINAL rank low_rank affine_rank products` records closure dimensions.
- `BASE_DUAL count terms...` gives a normalized functional annihilating the
  completed space; `REFUTATION 0` is the alternative for a refuted small board.
- `END` terminates the file.

Normal-form reduction only uses Boolean and column axioms and preserves degree.
The reader checks every derivation and dimension record, then separately verifies
original-generator coverage and all permitted PC products.

## Query format

JSONL schema 1. Polynomial and functional vectors are sorted lists of nonzero
monomial-coordinate IDs over F2. The monomial map is in the base proof.

Affine input and coefficient words are hexadecimal strings, with bit 0 for the
constant and bit 1+v for old variable v. Input coefficients use every old variable,
not just the 48 coordinates used to store the original spread.

`quadratic_annihilator_map` records use the listed `domain_monomials` as a basis
of the quadratic quotient. Kernel coordinate vectors refer to indices in this
list. They represent polynomials annihilated by every tested input.

The rank minor uses `minor_input_columns` from that domain basis and
`minor_output_coordinates` from the direct sum of cubic quotients.
Cubic quotient coordinates are the increasing nonpivot monomial IDs of the
certified base space. Blocks are concatenated in target-input order, each with
width 10,045. `minor_rows` give all entries in the selected-column order.
The stored nonsingular minor and the independent kernel vectors jointly certify
the reported rank and nullity.

`companion_system` records retain all old inputs and, when feasible, the affine
coefficient vector and its quadratic H. An inconsistent system instead stores
one full cubic functional per tested companion. These annihilate the PC base;
their weighted target value is one, and every coefficient-parameter value is zero.
Parameters are indexed j*57+k, with k = 0 for the constant coefficient and
k = 1+v for variable v. The corruption record uses a coordinate of the packed
cubic quotient dual and identifies a parameter equation that rejects the change.

## Provenance and measurement

`provenance.json` records the exact accepted source files, shared header, input
spread, base proof, and expanded result. The earlier spread is the certificate
recorded at notebook anchor `resistant-finite-certificate` in commit `97d5acd`.
`timing.html` is the measured table embedded in the notebook; the session archive
preserves complete command output and the timing journal.
