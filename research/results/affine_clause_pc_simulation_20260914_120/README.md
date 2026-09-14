# Direct affine-clause PC simulation

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-affine-clause-PC-simulation)
contains the complete resolution, weakening, binary-semantic, initial-clause,
and global DAG arguments, plus the working bit-PHP lower-bound corollary.
The asymptotic conclusion relies on the explicitly linked internal one-level
theorem; finite traces verify the simulation, not that lower-bound theorem.

## Reproduce

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_affine_clause_pc.cpp \
  -o /tmp/math-affine-clause-pc
./compute.sh run TURN --threads 1 -- \
  /tmp/math-affine-clause-pc --out NEW_OUTPUT_PATH --semantic
~~~

Run from the repository root with the resource controls active. Omit the final
option to reproduce the initial ten-trace run. The output must be new. No
dependencies were installed; the existing pc_boundary.hpp kernel generates
and independently replays primitive ordinary-PC operations over F2.

## Complete output

- pc-traces.jsonl: the accepted initial ten-trace run.
- pc-traces-with-semantic-inference.jsonl: twelve traces, adding the genuinely
  binary semantic-inference convention identified in the second primary source.
- source-audit.json: exact rule conventions, encoding, and reading coverage.
- provenance.json: code and complete output hashes.
- timing.html and the archived session: measured windows and complete commands.

Each proof record contains all axioms, its final-line index, actual maximum
degree, and line count. The following line records retain the complete
polynomial and the actual primitive rule:

- a: axiom introduction, with an index in that proof's axiom table;
- l: two-term linear combination, with earlier line references and scalars;
- m: multiplication of an earlier line by one variable.

Reference -1 is a zero contribution, not an additional axiom. Polynomials are
lists of coefficients and sparse variable/exponent pairs. No implicit Boolean
reduction is used. A block record also preserves its true-indicator inputs,
fresh coefficient interval, product, and all prefix polynomials.

The strengthened run has 3,172 primitive PC lines in twelve traces at h=1,2.
It includes full satisfying/missing-premise assignments for the local rule
systems, invalid-weakening controls, and rejection of corrupted final lines.
The two-row ell=2 initial-clause systems are satisfiable. The composed two-hole
traces have ell=1, outside the ell>=2 lower-bound theorem; their old base already
refutes in degree one. They test composition only.

## Scope

The simulation uses one fresh affine-input ENS block per proof clause and
constant additional inventory for binary semantic inferences. It preserves
degree max(2h+ell,4h+1), with no proof-height factor. Conditional premise-value
lines are replaced by actual earlier derivations in the global proof.

The working size lower bound for DAG-like Res(parity) on bit PHP follows from
this simulation and the internal polynomial-inventory one-level exclusion.
Its dependency chain is the next audit target. No unrestricted Frege,
odd-prime, or automatic unary-encoding lower bound is asserted.
