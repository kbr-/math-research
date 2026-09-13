# Direct multilevel row-profile certificates

Full statements and proofs are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-13-row-supported-source-normalization).
The fixture tests the simultaneous profile map and exact ordinary-degree
certificates. It does not establish a support bound for the full source family.

## Reproduce

With the shared resource controls active, from the repository root:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_row_supported_normalization.cpp \
  -o /tmp/math-row-supported-normalization
./compute.sh run TURN --threads 1 -- \
  /tmp/math-row-supported-normalization --out NEW_OUTPUT_PATH
~~~

The program refuses an existing output path. It uses exact sparse arithmetic
over F2 and F3, with no random choices or new dependencies.

## Fixture and complete output

There are three functional rows with two labels each. Column-collision axioms
are deliberately absent, so the local row-state domain is satisfiable.
The three original ENS blocks have nonlinear later inputs and tuple supports
of sizes 2, 3, and 3. Every tuple has a common zero and every listed evaluated
input is nonzero somewhere.

All coefficients are assigned simultaneously to old row-state interpolants.
The global map has degree three. The product of the support bounds, eighteen,
is recorded only to distinguish this direct map from a nested cost estimate;
neither number is asserted to be an optimum over all possible normalizers.

<code>source-certificates.jsonl</code> preserves:

- All sixteen row-state profiles across the two fields.
- Original expanded blocks and every coefficient image.
- Thirty complete ordinary NS certificates: per field, six companions, six
  coefficient fields, and three affine row equations. The largest original
  companion degree is eleven and the largest image/witness degree is nineteen,
  within the degree-three substitution ceiling of thirty-three.
- Two missing-row-equation controls, one per field.
- A ternary coefficient taking value two, which satisfies its field equation
  and fails the Boolean equation.

Polynomials are lists of coefficient/monomial pairs; each monomial is a sorted
list of variable IDs retaining repetitions. IDs 0..5 are the old row-major
incidence variables; the original fresh coefficients follow them.
No Boolean reduction is implicit in multiplication or certificate verification.
Row-state division records every Booleanity, same-row exclusion, and row
equation multiple and checks the complete sum against the original target.

The provenance manifest records hashes; timing and the session archive retain
the complete measured execution. Every compiled job used the shared limits.
