# Formal source cofactors and selector realization

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-source-cofactor-matrix-profile)
contains the construction, source/degree scope, realization counterexample,
and field audit. These fixtures are not complete PHP or Frege proofs.

## Reproduce

From the repository root, with the shared resource controls active:

~~~sh
./compute.sh run TURN --threads 1 --category local_processing -- \
  g++ -O2 -std=c++17 -Wall -Wextra \
  research/tools/check_source_cofactor_matrices.cpp \
  -o /tmp/math-source-cofactor-matrices
./compute.sh run TURN --threads 1 -- \
  /tmp/math-source-cofactor-matrices --out NEW_OUTPUT_PATH --nested
~~~

Omit the final option to reproduce the initial run without the nested controls.
The output must be new. Arithmetic is exact and deterministic; no dependencies
were installed. The shared header is research/tools/sparse_polynomial.hpp.

## Complete output

- matrix-checks.jsonl preserves the initial accepted run.
- matrix-checks-with-nested-controls.jsonl adds the two-level controls.
- source-audit.json records versions, access/license evidence, reading
  coverage, and the small-characteristic observation.
- source-provenance.json hashes the public CC BY 4.0 HLT2026-v1 PDF and text.
- provenance.json hashes the generating code, outputs, and audit metadata.
- timing.html and the archived session preserve measured intervals and commands.

Both runs retain two formal MP fixtures, over F2 and F3, each with 15 nodes,
14 targets, 15 factored contributions, old weights 1/2/4, and declared module
costs. These costs do not assert concrete ENS witnesses. Their certificate
budget is 10. Eighteen complete matrix programs have width 80: ordinary and
Boolean versions in three orders, plus three correction programs per field.
The ternary non-Boolean evaluation distinguishes ordinary identity from
Boolean remainder.

Three scalar selector controls use accuracy 4/6/8 and include 18 companion
NS certificates. The strengthened run adds accuracy 2/3 depth-two controls,
full cut matrices of ranks 16/512, and 18 companion certificates.
Cut width depends on order; essential source-certificate use is unproved.
Twelve Hamming-weight tables, p=2/3/5/7 and n=4/8/16, test the intermediate
subset-sum system, including small-characteristic models and a positive
unsatisfiability control. They are not FPHP models.

Polynomial records use explicit coefficients and sorted variable lists with
repetitions retained. No implicit Boolean reduction occurs in ordinary
arithmetic. Matrix programs preserve blocks, layers, nonzero entries,
initial/terminal vectors, and order. Cut matrices are complete sparse matrices:
unlisted entries are zero. Companion records preserve targets and every
nonzero cofactor/axiom pair.

## Literature scope

HLT2026-v1 is Hard CNF Instances for Ideal Proof Systems, by Tuomas Hakoniemi,
Nutan Limaye, and Iddo Tzameret, arXiv:2605.04544v1 (6 May 2026), CC BY 4.0.
The PDF is unchanged; text was converted with pdftotext -layout. Proposition 21
and its proof were visually checked on PDF pages 27–28. The main CNF lower-bound
proof was not audited. FSTW2021 and EGLT2025-v1 were screened for background and
model definitions; no PHP theorem was imported. Attribution and redistribution
details are in THIRD_PARTY_NOTICES.md and the reference policy.
