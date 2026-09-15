# PHP row-state density correction

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-PHP-row-density-correction)
contains the prescribed-row Gram refinement, full input-ideal argument,
complete PHP-based source correction, original-degree accounting, and scope.

## Mathematical result and reuse

For the old functional-unary matching base in the stable range, prescribe
nonzero masses summing to one on one row. A characteristic-two determinant
argument gives a normalized old design over a finite extension whose full
degree-t pairing and the specified row-predicate ideal restrictions are
nonsingular. The corresponding orthogonal-unit densities are the old row-state
indicators.

For 65 pigeons and 64 holes, take t=5, old pairing degree ten, and source degree
six. The selected row has masses theta at label zero, theta+1 at label one, and
one at every other label. Complete accuracy-one blocks on the first five and
all six affine label-bit predicates have densities X_0+X_32 and X_0. Their mixed
port is corrected at its original cost, with every source companion and field
preserved by the degree-one coefficient map.

This is a correction in a PHP-based source, not a satisfying PHP assignment.
The global old design and full old Gram matrix are established mathematically;
they were not constructed numerically. Finite checks cover local row states
and complete original-degree source images. The earlier row-local normalization
theorem already covers this source class. This checkpoint does not add general
multirow coverage or merge the unary and conditioned-compact presentations.

## Reproduction and complete output

With a fresh output path and active shared controls:

    ./compute.sh run TURN --threads 1 --category local_processing -- \
      g++ -O2 -std=c++17 -Wall -Wextra \
      research/tools/check_php_density_completion.cpp \
      -o /tmp/math-php-density-completion
    ./compute.sh run TURN --threads 1 -- \
      /tmp/math-php-density-completion --out NEW_OUTPUT_PATH

The checker refuses an existing output path. It uses the existing compiled
sparse-polynomial and NS-witness helpers. The initial compile called the
polynomial substitution method incorrectly; this was fixed, and the second
compile and first execution passed. No dependency was installed.

`php-density-completion.jsonl` preserves the original blocks, all coefficient
domains, decoder and coefficient maps, full local old axiom table, every NS
target and cofactor, and all 64 row states. There are 34 ordinary NS certificates:
six bit-domain images, eleven companion images, eleven own-field images,
two product/value comparisons, two canonical-value Booleanities, and two
mixed-port certificates. Product comparisons cost at most two, companions
at most three, and fields at most two; the actual mixed port fits its original
ceiling five. All eleven source coefficient fields are included.

NS polynomial coefficients are in F2. GF(4) elements 0,1,2,3 encode functional
values 0,1,theta,theta+1, with theta^2+theta+1=0. They are not non-Boolean source
coefficient assignments. Polynomial records use sorted repeated variable IDs;
old row variables have IDs 1000 through 1063. The local row Gram is diagonal
with the listed nonzero masses. The missing-query controls have exact values
one and theta+1, while the corrected mixed port is zero.

Metadata records the source revision, proof scope, and saved-output checks.
Provenance hashes the checker, shared helpers, full output, note, and metadata.
The measured timing and all command outputs are archived with the checkpoint.
