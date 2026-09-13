# Costed virtual OR folding

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-costed-virtual-or-folding)
contains the product closure, residual-corrected NS interface, modular source
transfer, and application to the retained code union. It preserves original
source weights and does not assert an arbitrary NS or PC substitution theorem.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_virtual_or_folding.cpp \
  -o /tmp/math-virtual-or-folding
./compute.sh run TURN --threads 1 -- \
  /tmp/math-virtual-or-folding --out NEW_OUTPUT_PATH
~~~

Run from the repository root with the resource controls active. The output must
be new. No dependencies were installed; sparse_polynomial.hpp supplies exact
ordinary F2 polynomial arithmetic.

## Complete evidence

folded-module-certificates.jsonl contains the actual old inputs, retained
blocks A/D/E, all Boolean and companion generators, the folded value and its
prefixes, and eleven complete ordinary NS certificates. Terms give generator
IDs and full cofactors; polynomials retain repeated variables.

The local fixture has h=2, five affine-side signals, four independent formal
linear-form variables, and a free modifier. Original union weight is 10;
intermediate genuine union degree is 6; folded value degree/cost is 8.
A second nontrivial comparison has a rebuilt certificate through 20, within
its original source ceiling 30. The designated comparison becomes zero, but
the tested second comparison does not.

A deliberately modified prefix creates a nonzero old Boolean residual.
The saved omission control shows that ignoring its correction breaks the
ordinary identity. The paired coefficient map realizes the folded product,
but its coefficient-field image has degree 6 rather than the original 2.
These controls distinguish modular witness reconstruction from an unsupported
degree-preserving substitution on arbitrary raw coefficients.

The four formal linear forms may be composed with the complete cycle-115
code matrix and its explicit Frobenius image certificates. That enumeration
was not repeated or copied. This is a source-shaped local system, not a
full pigeonhole refutation.

Hashes, timing, and complete command output are preserved with the checkpoint.
