# One-block consequence transfer and implication replay — 11 September 2026

The complete working proofs are in [the notebook](../../../notebook.html),
entry `entry-2026-09-11-implication-boundary`. They preserve an old PC consequence
when one fresh ENS block is removed, and use weighted replay of the full
implication premise to preserve an MP conclusion. Other extension blocks remain;
there is no global elimination theorem or PHP lower bound in this record.

## Reproduce

From the repository root, with the established resource controls active:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic research/tools/check_boundary_replay.cpp -o research/tmp/check_boundary_replay
./compute.sh --threads 1 research/tmp/check_boundary_replay --out research/tmp/boundary-recheck.jsonl
```

The destination must not already exist. Use a new destination for each run;
the checker refuses to replace an accepted output. No dependencies were installed.
Compilation and execution used the shared 14-CPU, 10-GB combined-memory controls.
The recorded compiler was GCC 11.4.0 (Ubuntu 11.4.0-1ubuntu1~22.04.3).
Other compilers may order independent trace-building calls differently;
the mathematical conclusions and degree checks are the reproduction targets.

The measured session was `implication_boundary_20260911_01`.
The initial compilation succeeded with four indentation warnings. After those
were corrected, compilation with `-Werror` succeeded and the transformation suite
passed on its first execution. The archived command records preserve both
compilations, execution, and the later output/provenance check.

## Cases and scope

[checks-01.jsonl](checks-01.jsonl) contains the complete output: 1,935,583 bytes,
14,843 JSONL records, 96 source/transformed proofs, and 14,657 PC inference lines.
[summary.json](summary.json) preserves the full 40-case degree ledger and hashes.
There is no random seed or floating-point arithmetic.

The suite uses p = 2, 3, 5, 7 and accuracy h = 1, 2:

- Twenty-four old-consequence cases use an affine input x, a nonlinear input xy,
  or an old boundary xy² of larger degree than the input x. The old domains make
  x field-valued and y Boolean. The old axiom g² and the ENS companion give the
  source derivation g = E + U g²; the larger-boundary case then multiplies by y².
- Sixteen MP cases use atomic or disjunction conclusions. Both source premise
  proofs use the selected implication block. Their old system also contains the
  antecedent as an axiom; this is a controlled replay fixture, not a claim that
  these examples need the transformation to obtain a low-degree proof.
- Each transformed proof is checked for its exact conclusion, its proved degree
  ceiling, and absence of the removed variables. The program then independently
  replays its stored inference rules using the same polynomial implementation.
  Adding one to the final line is rejected in every case.
- Eight hypothesis controls record, for each prime, a satisfying assignment
  showing that the implication alone cannot replace the antecedent/annihilator
  hypothesis, and an explicit later companion changed by zeroing the selected
  block. The latter checks a failed freshness hypothesis, not impossibility of
  every multilevel method.

These are synthetic finite traces and controls. The general arguments are
mathematical working proofs, not formally verified theorems. No historical suite
was rerun, and none of these cases is a PHP instance. The separate univariate
degree-loss example and prefix/spread comparisons are proved in the notebook.

## Trace format

All records are JSON objects. A `case` record supplies the prime, accuracy,
family, variable counts, input/boundary degrees, and degree bounds. Proofs
following it use that field until the next case or control.

A `proof` record declares its full axiom list, number of emitted lines, final
line index, and maximum introduced line degree. An axiom may be available
without being introduced: unused high-degree axioms do not count as proof lines.
Line indices restart at zero for each proof.

Each `line` record contains:

- `rule: "a"`: introduce axiom number `a`;
- `rule: "l"`: form `ca * line[a] + cb * line[b]`, with coefficients modulo p;
- `rule: "m"`: multiply line `a` by the variable with index `variable`.

Index -1 means a zero contribution, not an additional axiom. Zero results are
omitted from the emitted proof, so every retained reference points backward.
Unused fields in a line record can be ignored.

A polynomial is a list of terms `[coefficient, [[variable, exponent], ...]]`.
Coefficients are nonzero residues modulo p; unspecified exponents are zero.
An empty term list represents zero; an empty exponent list represents a
constant. Arithmetic is ordinary polynomial arithmetic, without implicit
Boolean or field reduction. Domain reductions are themselves expanded into PC
inferences from explicit univariate domain axioms.

In old-consequence cases, variables 0 and 1 are x and y, with domain sizes
listed in `domain_sizes`; subsequent variables belong to the removed block.
In MP cases, variables 0 and 1 are Boolean x,y. Any other variable below
`old_variables` is a retained field-valued coefficient of the conclusion block.
Variables from `old_variables` through `variables - 1` belong to the removed
implication block. The explicit axiom arrays also record all domain equations.

The implementation uses sparse maps with 16 byte-sized exponent slots, checks
exponent overflow and mixed fields, and limits each polynomial to 250,000 terms.
Each proof has guards of 250,000 lines and 2,000,000 stored polynomial terms.
The fixed prime range p ≤ 7 keeps coefficient products safely inside `int`.
The external shared cgroup/watchdog limit remains authoritative.

## Provenance

The source is
[check_boundary_replay.cpp](../../tools/check_boundary_replay.cpp), SHA-256
`8a19d7467c38846cd969cdadfd592ba3f5577e1c376f3680c71e21a658a2c4f0`.
The complete output has SHA-256
`8de8d7dfc8ff84777675249a1e2d6051bb56a6b8967a3bd34e70c03bf0da3104`.
The summary also records the exact historical chapter hashes.

Targeted readings covered Chapter 1's PC reuse, weighted substitution, selectors,
and domain reduction; Chapter 7's one-block elimination and prefix controls;
Chapter 8's nested-span replay; and the prior notebook's full MP entry.
BIKPRS Definition 6.8 and the closing proof of Theorem 6.7(1) were consulted in
the already imported author-layout source, PDF pp. 28 and 31,
DOI [10.1007/BF01294258](https://doi.org/10.1007/BF01294258).
The source PDF hash is
`78fff21cb13fb81d110bcfacba57d9be5a7dbd0ab36e1e1e2e4207fbcb09f4d2`.
That PDF and its full text remain local-only; no source excerpt is bundled here.

## Timing

[timing.html](timing.html) is the measured table embedded in the notebook.
The [archived session](../../provenance/session-records/implication_boundary_20260911_01/)
preserves the journal, report, and complete command outputs.
Goal creation preceded instrumentation, and the initial source-review phase
included initial argument development. Table embedding, archival, and Git
operations follow the final measured snapshot.
