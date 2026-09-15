# Common moment densities and a failed projection recipe

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-moment-density-projection-audit)
contains the full characteristic-two determinant argument, density-representation
statement, exact projection counterexample, and remaining source-feasibility gap.

## Mathematical scope

Old matching stability through 2t permits arbitrary diagonals in a normalized
degree-t Gram matrix. In characteristic two, the squarefree product of those
diagonal parameters has coefficient one in its determinant. A sufficiently
large finite extension field therefore supplies one normalized old design with
a nondegenerate pairing. Every old functional through t has a unique density
class through t against that pairing; shorter active components first extend.

This is a representation result. It does not choose densities satisfying the
source equations. Only functional values use the extension field; original
binary coefficient domains remain r^2-r.

The projection counterexample uses r Boolean bits, t=r-1, and GF(4) point weights
theta at zero, theta+1 at e_1, and one elsewhere. All three required Gram
restrictions are nonsingular. Nevertheless the orthogonal-unit densities for
the first r-1 inputs and all r inputs give a nonzero mixed OR-port value.

At r=6, t=D=5 covers the actual mixed port's original NS cost. Rescaling the
second density matches every correct old query through t, but multiplying that
density as a Boolean value then gives a nonzero Booleanity error. Densities
represent support-indexed components and need not be multiplicative.

These are satisfiable Boolean-source controls, not PHP instances. Complete
source models provide a genuine joint functional, so existence is not in doubt
for the control. The counterexample rejects automatic projection, not every
PHP-specific construction.

## Reproduction

Use a fresh output path and the shared computation controls:

    ./compute.sh run TURN --threads 1 --category local_processing -- \
      g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_moment_density.cpp \
      -o /tmp/math-moment-density
    ./compute.sh run TURN --threads 1 -- \
      /tmp/math-moment-density --out NEW_OUTPUT_PATH

The checker refuses to replace an existing output. No dependency was installed.
The first compile and run passed.

`density-controls.jsonl` stores complete point weights, all old monomial moments,
full Gram matrices, ideal Gram matrices, projections, corrected densities, and
genuine source models for r=3 and r=6. Elements 0,1,2,3 encode 0,1,theta,theta+1,
with theta^2+theta+1=0. Polynomial vectors use the listed squarefree monomial
bit masks; source products remain defined by their original factored ENS recipe.

There are six nonsingular matrices, 72 complete source models, and three one-bit
field-size controls. Both projection cases have the expected mixed-port value
theta+1, corrected value zero, and density-squaring Booleanity error one. The
three-bit illustration does not meet t>=D; the six-bit case does. All source
assignments are Boolean, including every coefficient; GF(4) values appear as
functional weights, not as non-Boolean source coefficient assignments.

`check-metadata.json` records the proof review and saved-output checks;
`provenance.json` hashes this note, checker, output, and metadata. Timing and
complete command output are archived with the research checkpoint.
