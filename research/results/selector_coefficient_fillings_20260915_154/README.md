# Selector coefficients and conditioning-compatible filling

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-selector-coefficient-filling-obstruction)
contains the exact coupled marginal equations, proof, and scope.

The positive old filling theorem extends to a fixed vector coefficient space.
This does not automatically preserve source relations whose coefficients
multiply old variables. A proposed universal repair would choose linear
sections of old moment restriction that commute with row conditioning.

Such sections cannot exist in the stated stable range. Summing the required
commutation identities over one row makes restriction injective, while a signed
top row trade lies in its nonzero kernel. Individual linear sections still
exist. The result does not assert that the actual source requires universal
commutation or exclude jointly chosen source-dependent corrections.

The exact binary source-module presentation retains every original witness
ceiling. Row marginals and source relations must hold together. Kernel
corrections by row trades require N >= 2r on an r-row set, one more column
than the minimal filling theorem.

## Reproduction

With an active session and the shared resource controls:

    ./compute.sh run TURN --threads 1 --category local_processing -- \
      g++ -O2 -std=c++17 -Wall -Wextra \
      research/tools/check_conditioning_extension.cpp \
      -o /tmp/math-conditioning-extension
    ./compute.sh run TURN --threads 1 -- \
      /tmp/math-conditioning-extension --out NEW_OUTPUT_PATH

The output path must not already exist. No dependency was installed.
Compilation and the exact run succeeded.

## Complete output

`conditioning-controls.jsonl` uses row-major, zero-based variable indices.
The multiplier index -1 means the constant one. It contains every first and
second moment, so it specifies each entire degree-two functional.

For each prime p = 2,3,5:

- A normalized functional-PHP design on four rows and three labels gives all
  rows first moments (1,0,0). Every row pair uses the displayed signed 3-by-3
  matrix, with transpose when the row order reverses.
- All 94 degree-two old NS generator multiples are checked: 52 row-equation
  multiples, 12 Boolean equations, 12 same-row exclusions, and 18 same-column
  exclusions. Every constraint evaluation is retained.
- The same-column joint moment is zero while the product of its means is one.
- Replacing the negative sign by a positive one violates a row marginal for
  p = 3,5 and leaves p = 2 unchanged.
- A three-row, three-label actual injection supplies a satisfiable point
  control, with 57 constraints and factorized moments.

In total, six moment systems and 453 ordinary NS constraints passed.
The point control concerns its one-dimensional point-functional subspace;
it does not give commuting sections on the full moment spaces.

## Review and provenance

The proof review checks the unnormalized conditioning domains, the row-sum
identity, both section identities, the nonzero top trade in the restriction
kernel, all field signs, and the distinction between a universal splitting
rule and the actual source obligation.

The notebook reuses the existing old normal form, old extension theorem,
row-trade spanning proof, and genuine flat-comparison witness. No new external
paper was needed. `check-metadata.json` records focused checks;
`provenance.json` hashes this note, checker, full output, and metadata.
Timing and complete command output are archived under the session label.
