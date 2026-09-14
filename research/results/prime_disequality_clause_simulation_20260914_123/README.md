# An explicit prime-field affine-disequality calculus

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-prime-disequality-clause-simulation)
defines the calculus and proves its complete forward simulation and working
bit-PHP size bound. Its lines are disjunctions of affine disequalities. Rules
are valid on the full prime field, and Boolean domains are explicit initial
clauses. At odd primes this is not an identification with general equation-clause
Res(lin Fp).

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra research/tools/check_prime_disequality_pc.cpp \
  -o /tmp/math-prime-disequality-pc
./compute.sh run TURN --threads 1 -- \
  /tmp/math-prime-disequality-pc --out NEW_OUTPUT_PATH
~~~

Run from the repository root with resource controls active. The output path
must be new. The checker uses the existing exact ordinary-PC kernel
research/tools/pc_boundary.hpp and standard C++; no dependency installation.

## Complete evidence

PC-traces.jsonl contains 31 fully replayed traces:

- F3/F5, accuracy one/two: p-way cuts, semantic weakenings, tautological clauses,
  every non-Boolean excluded residue, and two-row compact initial clauses.
- Separate Boolean-sum pivot fixtures reach every field residue from old bits,
  checking the actual degree-p Booleanity witness used in the theorem.
- A full three-premise affine-cover simulation and its nine-point field check.
- Four composed residue-partition refutations deriving their premise values
  from actual initial equations. These artificial inconsistent systems are not PHP.

Each case states its prime, domain exponents, blocks, inputs, prefixes, products,
all proof axioms, and every primitive proof line. Polynomials use
[coefficient,[[variable,exponent],...]], with ordinary powers. Only axiom
introductions, two-term field-linear combinations, and multiplication by one
variable occur. Each final polynomial and degree ceiling is checked; corrupting
the final trace line is rejected.

Typed models include every variable and every axiom value. Omitted premises or
initial equations are explicitly listed, and every other axiom is checked at
that assignment. This distinguishes legitimate domain assumptions from
full-field inference and supplies nonvacuous missing-premise controls.

The compact initial fixtures are satisfiable two-row bit systems. Their old
collision degree is 2(p-1), not the binary degree reused over another field.
The complete output includes all models and all primitive lines; no numerical
PHP size lower bound is inferred from these local tests.

## Source scope

The Part–Tzameret ECCC TR18-117 primary report record was read for the standard
equation-clause terminology and bibliographic identity. No lower-bound proof
from that paper was imported, and no paper copy is added to the repository.
The actual rules used here are defined and proved in the notebook.

The affine-cover argument, degree ledger, and size consequence use the recorded
all-prime affine exclusion. This is an internal working derivation with explicit
scope, not external peer review.

All builds and checks passed. Source and output hashes, command evidence, and
the measured timing fragment accompany the checkpoint.
