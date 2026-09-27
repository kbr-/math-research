# Connection selection reviews — 27 September 2026

Both native reviewers explicitly used medium reasoning and fresh contexts. Reviews
were read-only, with no computer-algebra run.

## Pre-proof scope review

Reviewer: extension_connection_novelty.

Verdict: setup valid; uniqueness remained to be proved. The reviewer checked the
endpoint coefficient derivations, the free-cover matrix, and the quotient values
giving the lower density coefficient -25/2. The degree gap gives a unique cover lift
and excludes a degree-one cross term. Invariance of pushout relations is necessary
and sufficient and is linear in the extension coordinates.

The reviewer required an explicit proof that vertex torsion is connection-stable,
so the actual quotient provides a nonzero compatible extension. It also required
scope restricted to the quintic family with these prescribed endpoint connections,
without extrapolation to higher dimensions or the remaining vertex extension.
Both requirements are included in the full proof.

## Fresh correctness review

Reviewer: connection_selection_correctness.

Verdict: pass; no algebra error, missing assumption or scope overclaim.

Verified the coefficient derivation, both endpoint connections, vertex-torsion
stability, and preservation of the dimension-one layer. Verified the free-cover
matrix, all six columns of the polynomial relation matrix, and all four connection
relation identities directly by polynomial algebra.

Verified the four linear equations, elimination with the cocycle equation, the
resulting one-dimensional line, and both nonzero and rejected-point controls. The
weight gaps justify unique lifts and uniqueness of a compatible connection.

The actual nonzero compatible quotient supplies existence on the necessary line;
linearity supplies every scalar multiple. Thus the two unused relation equations
need no independent assumption. The result concerns the full stated quintic family
over characteristic-zero fields, not all-dimensional or vertex reconstruction.
