# Constant accuracy for the complete affine endpoint

The [notebook theorem](https://kbr.is-a.dev/math-research/#constant-accuracy-affine-family-exclusion)
completes the row-cap-two dimension and residual-board arguments from cycle 134.
Polynomially many complete affine-bit blocks have no polylog-degree PC
refutation at constant accuracy h=2*(p-1), for each fixed prime p.
Larger individual accuracies reduce to this one by constant restriction.

The theorem concerns refutation exclusion. It does not assert the earlier
old-target or joint-selector extension statements at the new accuracy, or
general dense-source coverage.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_constant_accuracy_affine.cpp -o /tmp/math-constant-accuracy-affine
./compute.sh run TURN --threads 1 --timeout 180 -- \
  /tmp/math-constant-accuracy-affine --out NEW_OUTPUT_PATH
~~~

Use a new output path and active resource controls. No dependency installation
is required.

## Complete evidence

The JSONL output uses ordinary polynomials encoded as
[coefficient,[variable IDs with repetitions]]. Large dimension counts are
exact decimal strings.

For each field F2 and F3, the system records ten old Boolean variables grouped
into two-bit rows, all three original blocks, and every coefficient field axiom.
The common multiplier is (b0-b3)*(b1-b2). Both high tuples have rank seven,
the exact high threshold at k=2. The low tuple has rank six and fills every
packing bin at h=2*(p-1).

All coefficient variables receive one simultaneous old-only image. The output
contains the literal product images and all NS witnesses over old Booleanity:

- F2: 20 companion images, 40 coefficient-field images, 10 old Boolean images.
- F3: 20 companion images, 80 coefficient-field images, 10 old Boolean images.

The shared verifier reconstructs each target and charges every generator
multiple. Zero field images are retained too. All 256 old Boolean points with
nonzero multiplier give complete conditional source models in each field.
An unweighted-companion countermodel and an F3 non-Boolean coefficient control
preserve the boundaries of the argument.

Five exact generating-function counts verify the row-cap-two dimension estimate
and compare it to the ordinary flat-image bound. Two fixtures show that the
same bound would not suffice for the smaller old row-linear space.
These are component checks; the combined asymptotic PHP conditions are not
numerically instantiated. Earlier matching-moment suites were not rerun.

All checks passed with a clean compilation. The complete output, source hashes,
timing, and execution evidence accompany the checkpoint. Some proof planning
remained mixed with the coding phase.
