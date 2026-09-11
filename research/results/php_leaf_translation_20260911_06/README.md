# Ordinary-PHP simulation bridge and clause blocks

11 September 2026. Timing session: `php_leaf_translation_20260911_06`.
The full general proofs, assumptions, and remaining gap are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-ordinary-php-transfer).

## Mathematical scope

The transfer proof first derives ordinary row clauses from MOD-one rows in
polynomial symbol length and constant formula depth. BIKPRS Theorem 6.7(1)
then applies with constant effective assumption degree. Its TRUE-by-zero
convention requires q = 1-x. The translated modular-row polynomials are powers
of the exact base row axioms, so their NS replacement preserves degree.
No same-row exclusions are added.

The clause-block identities and affine substitutions are separate explicit
ordinary-ring identities. All retained later inputs and cofactors are specialized.
The resulting remaining extension system is valid ENS, with no increase in degree,
levels, or companion count. The global elimination problem remains open.

## Complete check output

`checks-01.jsonl` contains:

- 33 clause cases over primes 2, 3, 5, 7, accuracies h = 1, 2, 3, and distinct
  row widths in {2, 3, p+1};
- exact translated MOD-row and collision polynomials;
- every row and collision block product, all original companions, their
  coefficient-variable maps, and the specialized products;
- degree ledgers and 180 verified companion images;
- 66 nonzero controls omitting a necessary base row or collision contribution;
- 384 Boolean row evaluations checking the truth convention, including one
  accepted p+1-ones row for each prime;
- four later-block cases, with both original and specialized companions;
- the 32-assignment check of the fixed Boolean induction template.

In the later-block cases, n = 2 and the row and collision blocks each have one
factor. The later inputs are P-Q and 1-PQ; the later block has two factors.
Original companion degrees 12 and 14 decrease to 10 and 11. Leaving the later
inputs unchanged fails all eight corresponding controls.

These finite checks support the general written proofs. They do not constitute
a formalized Frege derivation or a verification of the full external simulation.

## Reproduction and data encoding

From the repository root, with the documented resource controls active:

```bash
mkdir -p .resource-runtime/bin
./compute.sh --threads 1 c++ -std=c++17 -O3 -Wall -Wextra -Werror \
  research/tools/check_php_leaf_translation.cpp \
  -o .resource-runtime/bin/check_php_leaf_translation
./compute.sh --threads 1 --timeout 240 \
  .resource-runtime/bin/check_php_leaf_translation \
  --out research/results/php_leaf_translation_20260911_06/checks-REPRO.jsonl
```

Choose a new output path; existing results are not overwritten.
The accepted computation used GCC 11.4.0, C++17, and the shared
`sparse_polynomial.hpp` kernel. No dependencies or floating-point arithmetic
are involved.

JSONL schema 1. Polynomial terms are `[coefficient, [variable_ids]]).
The sorted list retains repeated variable IDs as powers; these are ordinary
polynomials, before Boolean or field reduction.

Old variable IDs are row-major: i*n+j, with zero-based indices. All n(n+1)
incidence-variable IDs are reserved, even when a check uses only one row and
the cell x_(1,0). Fresh coefficient IDs start after that range. Each block
records its coefficient-variable array by factor and input position.

For the row substitution, first-factor coefficients are one and all other
coefficients are zero. For collision inputs (1-x_(0,0), 1-x_(1,0)), first-factor
coefficients are (1, x_(0,0)) and the others are zero. A later block retains
its own coefficient IDs while all its input polynomials are specialized.

The Boolean induction template has placeholders A, B, C, z, m. Its premises are
A implies not B, A implies not z, and
m iff ((B and not z) or (C and z)); its conclusion is A implies not m.
The fixed template has a constant-size proof in the chosen complete Frege basis;
the notebook gives its instantiation at each row-prefix step.

## Source provenance and timing

The mathematical source is the locally supplied author-layout BIKPRS paper,
DOI [10.1007/BF01294258](https://doi.org/10.1007/BF01294258), particularly
Definition 1.1, Section 2's translation, Definitions 6.1 and 6.3–6.8, and
Theorem 6.7(1). Source identification and targeted reading coverage are recorded
in [SOURCE_AUDIT.md](../../notes/SOURCE_AUDIT.md).
Krajicek [arXiv:2301.10617v3](https://arxiv.org/abs/2301.10617) records the
linear dependence of the simulation exponent on the fixed formula depth.

`provenance.json` records the accepted checker, shared kernel, complete output,
and the source PDF's path, size, and hash. The reproduction of these finite
checks does not require the source PDF.
`timing.html` is the measured table embedded in the notebook. The session
archive retains complete command output and timing events.
