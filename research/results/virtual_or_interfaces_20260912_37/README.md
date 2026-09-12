# Unit and annihilator interfaces for local OR values

The complete theorem and proof are in the
[12 September notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-virtual-or-interfaces).
An interface supplies proofs of every input times its value, and a conditional
proof of one minus that value after adjoining its zero input assumptions.
For literally concatenated child tuples, the three interfaces yield c-ab through
C+2L when all witnesses fit C and C>=2L.

The virtual-zero specialization replays an input refutation with weight ab.
It uses a new local value definition and proof. It is not yet a transformation
of an existing expanded ENS proof or a full source compilation theorem.
The retained system and every witness must remain valid under any later changes.

## Reproduce

From the repository root, with the shared resource controls active:

    ./compute.sh start virtual_or_reproduction
    ./compute.sh run virtual_or_reproduction --threads 1 --category local_processing --timeout 120 -- g++ -std=c++17 -O2 -Wall -Wextra -pedantic research/tools/check_virtual_or_interface.cpp -o /tmp/math-check-virtual-or-interface
    ./compute.sh run virtual_or_reproduction --threads 1 --timeout 120 -- /tmp/math-check-virtual-or-interface --out research/results/virtual_or_reproduction/checks.jsonl

The output path must be new. The program uses exact C++ modular arithmetic and
the existing ordinary-PC kernel. It includes the previous small-probe checker's
formatting, evaluation, and verification helpers with that file's main renamed;
it never calls its main or its previous research suites. No dependency was added.

## Saved evidence

`checks-01.jsonl` contains eighteen complete PC derivations over F2, F3, and F5.

- Three genuine ENS fixtures on tuples (x), (y), and (x,y). Each supplies three
  PC-two conditional unit derivations and one PC-six proof of c-ab. The proof
  exercises all three terms of the interface identity. All four old Boolean
  points per field are extended to common models. Each of the two parent
  companions has a missing-axiom countermodel with c-ab=1.
- Three virtual-parent fixtures on the seven-vertex binary pebbling tree.
  The left child retains the seven positive inputs; the right retains the sink
  input. Each conditional parent refutation has degree three, uses only the
  eight extra input assumptions, and has no coefficient variable in any line.
  The composed proof of c-ab at c=0 has degree nine. Every old Boolean point,
  128 per field, has a saved extension satisfying the retained child families.
- Eight missing-child-companion controls per pebbling field, with a=b=1 and
  c-ab=-1. Each point satisfies all displayed retained axioms except the named
  missing companion. A further control in each field has tuples (x),(y), old
  values x=y=0, and a=b=1; the proposed virtual-zero parent lacks a possible
  input refutation and its OR relation fails.

Totals: twelve conditional traces, six composed OR-relation traces, 396 common
models, and 33 missing-witness controls. All ordinary PC lines are recomputed;
corrupting a final line is rejected. Both the original build and check succeeded.

The input refutation pattern is the one already recorded in cycle 36; here it is
constructed over the actual current retained system for weighted composition.
Its antichain lower bound and sharp input Booleanity certificates are reused
with their original scope, without rerunning the previous suite. Since every
old Boolean point extends to the retained system, the constant-row bound still
applies to a full-parent product depending only on old inputs. This is a generic
pebbling example, not a tuple identified in a PHP source proof.

## Format, provenance, and measurement

The JSONL metadata and proof schema match the preceding checker. Polynomials
are arrays of `[coefficient, [[variable, exponent], ...]]`; the empty array is
zero. Proof headers list the complete axioms, final line, maximum degree, and
number of following records. Rules `a`, `l`, and `m` denote axiom introduction,
linear combination, and multiplication by one variable. Index -1 denotes zero.
An unused high-degree axiom in the header is not an introduced proof line.

Case records save the exact values and, for pebbling, the full input tuple.
Point records give the full assignment, value evaluations, relation defect, and
omitted axiom index where applicable. Generic fixtures have old variables x,y
at indices 0,1. Pebbling old variables are 0 through 6; child coefficients follow
in block order. Every record is complete, with no random sampling or truncation.

`provenance.json` records hashes of both checker sources, the shared kernel,
the new complete evidence, reused cycle-36 evidence, this README, and the claim
index. The final timing is embedded in the notebook. Operational evidence is
archived under `research/provenance/session-records/virtual_or_interfaces_20260912_37/`.
Preparation includes the prior checkpoint's archival, history check, and push.
The work phase switched automatically after the awaited push and after the
mathematical check. No rendering build or resource stress test was performed.
