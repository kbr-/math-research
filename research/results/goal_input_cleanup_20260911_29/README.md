# Maximal goal-input cleanup and assignment-tree certificates

Research cycle `goal_input_cleanup_20260911_29`, 11 September 2026.
The complete statements, proofs, failed parameter route, and limitations are in
the [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-goal-input-cleanup).
These files preserve evidence; they are not a second current research summary.

## Structural cleanup

`checks-01.jsonl` contains 24 deterministic cases over F2 and F3, at accuracy two:
spine length 1/2/7, width 3/7, and covered/gap argument forms. Each case saves the
physical formula forest, leaf origins, parents, coefficient-family assignment,
ordinary cuts, cleanup batches, live sets, paired input comparisons, and control
points. All 2,032 cleanup roots in 376 rounds pass the structural invariants.
There are 80 nonliteral ordinary pairs and 352 nonliteral cleanup input pairs.

The formulas are excluded-middle and weakening-schema MP spines. This checks
the occurrence schedule, not primitive-Frege leaf expansion or new PC traces.
General degree bounds use the notebook's existing copy and signed-replay proofs.
The gap form retains exactly `length` outside maximal canonical classes; that is
a failure of this coverage criterion, not proof that those classes are essential.

Point assignments use original proposition values zero. A listed family assigns
one to the indicated coordinate(s) of its first coefficient vector. The field
name `vector_zero_coordinates` means vector index zero; those coordinates have
value one. All other coefficients are zero, including the second vector.
Nonliteral-pair witnesses establish distinct polynomial values; they are not
models of all companion equations. Separate controls show a changed protected
goal input and a changed retained ancestor companion under an ineligible cut.

The checker reuses `check_private_mod_frontiers.cpp` as an occurrence kernel by
renaming its CLI entry point. An explicit final `return 0` was added to that
existing entry point, preserving its behavior. The first compilation failed
without that return, and a premature dependent launch failed because no binary
existed. The corrected build and run passed. Both failed command logs remain in
the archived session. The previous version of the included kernel is tracked in
parent commit `e45aff6`; no partial mathematical output was produced by the failures.

## Assignment tree

`assignment-tree-checks-01.jsonl` contains exact NS identities and controls over
F2, F3, F5, with accuracy 1/2 and parent prefix length 0/1/2:

- 18 local splitting certificates;
- 48 satisfying models;
- 12 odd-prime countermodels when the split Boolean equation is omitted;
- six complete two-variable assignment-tree certificates, including each split,
  each leaf certificate, and the summed refutation.

Polynomials are lists `[coefficient, monomial]`; a monomial is a sorted list of
zero-based variable IDs with repetitions for exponents. Coefficients are reduced
modulo the case prime. Certificate cofactors align with the case's saved axiom
array. The reported degree is the maximum collected ordinary degree of an axiom
times its cofactor. No field reduction is used to lower that degree.

The complete small cases use four assignment-indicator equations and Boolean
axioms, not PHP. Their base is already easy. They test the certificate algebra
and degree ledger, while the notebook's general proof establishes the PHP
application with exponentially many blocks. No large assignment tree was built.
Coefficient field equations are unused in every certificate. The local controls
explicitly satisfy them along with all non-omitted equations.

## Reproduction

From the repository root, with the resource controls active, choose new output
paths if the named files already exist. The checkers refuse to replace them.

```bash
./compute.sh start cleanup_reproduction
./compute.sh run cleanup_reproduction --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_goal_input_cleanup.cpp \
  -o research/tmp/check_goal_input_cleanup
./compute.sh run cleanup_reproduction --threads 1 -- \
  research/tmp/check_goal_input_cleanup --out research/results/NEW-cleanup.jsonl

./compute.sh run cleanup_reproduction --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_assignment_tree_certificate.cpp \
  -o research/tmp/check_assignment_tree_certificate
./compute.sh run cleanup_reproduction --threads 1 -- \
  research/tmp/check_assignment_tree_certificate \
  --out research/results/NEW-assignment-tree.jsonl
```

Run each executable only after its build succeeds. Both suites are deterministic
and use exact compiled modular arithmetic. No dependency was installed.

## Sources, provenance, and measurement

The cleanup proof extends the notebook's inherited-forest, formula-copy, and
partial-MOD results. The virtual-copy calculation specializes its existing COPY
identity using the recorded weighted-prefix theorem. The pointwise design-lift
calculation is analytic and ends in an inactive companion regime.

The assignment-tree construction was compared with the historical
[`lem:prefixcertificate`](../../../php_codex_handoff/manuscript/chapters/07_elimination.md#lem-prefixcertificate),
whose pebbling base has PC degree at most three. This different exhaustive tree
uses Boolean splitting and has exponential family count. Its ordinary-PHP
corollary uses the previously audited Razborov lower bound; no new paper import
or literature novelty claim is made.

`provenance.json` records streaming SHA-256 hashes of both complete outputs and
their source dependencies. `timing.html` is the measured table embedded in the
notebook. The complete timing journal, commands, and outputs are preserved in
`research/provenance/session-records/goal_input_cleanup_20260911_29/`.
Some reading included proof formulation; preparation included the preceding
checkpoint and initial planning; coding included compaction. These windows were
not retrospectively relabeled. The two compile/launch failures are operational
failures, not mathematical counterexamples. No rendering or historical test
suite was rerun for this research entry.
