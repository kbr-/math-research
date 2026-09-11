# MOD-goal aggregate normalizers

Research cycle `mod_goal_normalizers_20260911_34`, 11 September 2026.
The complete source criteria, degree proof, residue controls, Booleanity
comparison, and accuracy argument are in the
[notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-mod-goal-normalizers).

## Complete evidence and scope

`checks-01.jsonl` contains fourteen deterministic local cases over F2/F3/F5:
linear normalizers for negative MOD children of nonzero residue, selectors for
positive MOD-zero children, and selector alternatives in two negative cases.
Four cases use independent earlier copies `R_A=P_(t), R_B=P_(t)` in one
matched input, with the actual degree-four copy proof included.

The suite saves 28 complete source/replayed PC traces, embedded normalizer
witnesses, all companion and field images, original/image degrees, selected
coefficient assignments, and the exact retained parent image. The source target
is `P+zQ`, where `Q=P_(P,z)`; the replay target is `H+z Q_image`.
Every line is checked, including multiplication by removed coefficients mapped
to nonzero constants. Every final-line corruption is rejected.

There are 56 common models and 22 missing-goal countermodels of the specialized
retained system with a nonzero selected companion image. Seven countermodels
also show a non-Boolean linear product image. The selector images remain Boolean
on all enumerated domain patterns. Source degrees range from 4 to 12, replayed
degrees from 3 to 8, and normalizer-witness degrees from 1 to 6. These are full
trace degrees, not claimed optima; replay can retain intermediate squared images.

Twelve cases use Boolean original input variables. The two F5 selector cases
instead use explicitly marked field-valued original inputs with x^5-x domain
equations. This permits nonzero zero-sum vectors at width two, keeping the
missing-goal controls nonvacuous without expanding a large proof. Boolean F3
selector fixtures use width three for the same reason. The field-domain cases
verify general ENS algebra; they are not Boolean source instances.

Ten separate invalid-residue controls use p Boolean ones, whose sum is zero.
They satisfy either a positive nonzero-residue goal or a negative-zero goal,
while every factor depending only on that homogeneous sum remains one. The
original ENS product has an explicit zero-making first-vector assignment.
This is an aggregate-only obstruction, not a general normalization lower bound.
The sharper h>=p-1 control for constant assignments over a free Boolean base is
the analytic subcube-degree proof in the notebook, not a new finite rank search.

All compilation and mathematical checks passed. Two orchestration calls failed
with `SyntaxError: missing ) after argument list` before their requested file
operations or commands ran. They produced no partial mathematical output.
Corrected quoting allowed the calls to proceed. No dependency, historical suite
rerun, or rendering check was needed.

## Encoding

The checker uses `pc_boundary.hpp`. A polynomial is a list
`[coefficient, [[variable, exponent], ...]]`, with exact field residues and
ordinary collected degrees. Zero has degree -1. Coefficient ranges are
half-open intervals. Each trace has its own axiom array and line references;
the image ledger maps the original indices into the replayed array.

The first domain slots are indexed by variable ID. Removed coefficient field
equations are replaced there by zero placeholders to preserve the domain
helper's indexing; no axiom involving a removed variable is retained. Selected
companions are replaced by their supplied proof lines, never introduced as
additional retained axioms.

Every enumerated tuple of matched input values is saved. Records marked
`common_model` were checked against both systems with the goal. Records marked
`missing_goal_countermodel` were checked against the specialized retained
system with its goal omitted. Records marked `no_nonzero_companion_image` are
candidate evaluations without that counterexample; they are not automatically
asserted to satisfy a full system.

The invalid-residue records specify the Boolean tuple, goal sign/residue, and
complete original first coefficient vector; all remaining vectors are zero.
Their formula description determines the original ENS system without expanding
an unnecessary large polynomial at those control points.

## Reproduction

From the repository root with resource controls active, choose a fresh output
path. The checker refuses to overwrite a result.

```bash
./compute.sh start mod_goal_reproduction
./compute.sh run mod_goal_reproduction --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_mod_goal_normalizers.cpp \
  -o research/tmp/check_mod_goal_normalizers
./compute.sh run mod_goal_reproduction --threads 1 --timeout 120 -- \
  research/tmp/check_mod_goal_normalizers \
  --out research/results/NEW-mod-goal-normalizers.jsonl
```

Run the executable only after compilation succeeds. These are satisfiable local
target fixtures, not PHP refutations or primitive-Frege compilations. The global
claim uses the proved occurrence invariant and its explicit matching hypotheses.

## Sources, provenance, and timing

The exact notebook field-selector and signed scalar-conversion lemmas were
read before composing them. The original normalizer, copy, and private-ancestor
mechanisms remain the dependencies; no new selector identity or literature
novelty is claimed, and no external paper was imported.

`provenance.json` hashes the complete output, checker, and reused PC kernel.
`timing.html` is embedded in the notebook. Full timing and command evidence is
archived under `research/provenance/session-records/mod_goal_normalizers_20260911_34/`.
Preparation includes the preceding checkpoint. The successful check switched
to the mathematics phase before interpretation; the quoting failures remained
in their active coding or record-writing windows, without retrospective relabeling.
