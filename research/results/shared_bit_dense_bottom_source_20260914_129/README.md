# Complete two-level shared-bit source transfer

The [notebook proof](https://kbr.is-a.dev/math-research/#entry-2026-09-14-dense-shared-bit-source)
maps bottom products on (x,y_i) to (1-x)(1-y_i), then renames the coefficients
of parents reading those products to affine cores on 1-y_i. The parent value
is x+(1-x)A. Every original NS/PC axiom image fits its original degree.

This handles arbitrary raw coefficient uses and overlapping parents. It does
not imply arbitrary later source coverage or independent parent-selector zeroes.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_shared_bit_source.cpp \
  -o /tmp/math-shared-bit-source
./compute.sh run TURN --threads 1 -- \
  /tmp/math-shared-bit-source --out NEW_OUTPUT_PATH
~~~

Use a new path and run from the repository root with the resource controls
active. Arithmetic and certificate reconstruction are exact and compiled.

## Evidence and encoding

Each F2/F3 case retains three bottom blocks and two overlapping parents,
at accuracy two. Its 37 original axiom images are certified through their
individual original degrees. Two parent-product differences and two value
Booleanity witnesses give 41 complete certificates per field, 82 in total.

Polynomial terms are [coefficient,[variable IDs with repetitions]]. Case records
give complete source/target blocks and axiom lists. Bottom coefficient variables
map to the displayed constants; parent coefficient IDs are retained for their
new affine cores. All other old variables are fixed. Source and target degree
ledgers are explicit in the certificates.

The checker evaluates all source axiom images at each of 16 canonical models
per field. It retains missing-companion models, a wrong ungated-parent-value
control, and an F3 model with coefficient value two. These finite old bases
contain only Booleanity; the tests are not numerical PHP lower bounds.

The parent profiles use original input bounds four and original value cost ten,
despite lower collected degrees after the scalar bottom map. Source images are
computed once and reused across model checks.

All checks passed. A preliminary compiler indentation warning was corrected.
Source/dependency hashes, complete command evidence, and timing are retained
with the checkpoint.
