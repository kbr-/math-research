# Occurrence-separated MP interfaces

11 September 2026. The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-occurrence-mp-interfaces)
contains the full occurrence-copy leaf construction, freshness argument, and
subtree-local PC transfer. The remaining proper family is not eliminated.

## Reproduce

With the shared resource controls active, from the repository root:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_occurrence_mp.cpp -o research/tmp/check_occurrence_mp
./compute.sh --threads 1 research/tmp/check_occurrence_mp \
  --out research/results/occurrence_mp_replay_20260911_17/checks-REPRO.jsonl
```

Use a new output path. The accepted run used GCC 11.4.0, C++17, exact modular
arithmetic over F2 and F3, accuracy one, and one thread. No dependencies were
installed. The existing `pc_boundary.hpp` engine was reused without modification.

## Complete evidence

`checks-01.jsonl` is 2,136,162 bytes. It records two cases with five full PC traces
each, all axioms and line polynomials, actual and allowed degrees, and corruption
and freshness controls. Every mathematical check passed. This is a local MP
pattern with supplied premise proofs, not a compiler for arbitrary Frege proofs.

The formula pattern is A = NOT X OR X and B = A AND TRUE, using the source
negation/OR expansion of conjunction. Original variable 0 is Boolean x. Variables
1 and 2 are the right A coefficients, 3 and 4 are the independent left A
coefficients, and 5 and 6 are the inner B coefficients. All coefficients have
their field equations r^p-r. The inner B block has inputs (right_A, 0); its
zero-input companion is retained in the axiom array too.

The old boundary engine's polynomial encoding is
`[coefficient, [[variable_id, exponent], ...]]` for each nonzero monomial.
This differs from the repeated-variable encoding of `sparse_polynomial.hpp`.
Trace rules are `a` (axiom), `l` (linear combination), and `m` (variable
multiplication). Line -1 denotes zero; coefficients are reduced modulo p.

The five actual degree sequences are (4,4,6,8,9) over F2 and (4,4,6,10,11)
over F3. The final ceilings from the two successive one-block transfers are
10 and 12. No minimality is claimed. The checker verifies the axiom permutation
between transfers, rejects each corrupted final line, and confirms that all
removed coefficients are absent from the final proof. The right A copy remains
in the satisfiable old system. A control that shares it with the selected left
copy violates both retained-axiom and target freshness, as intended.

## Provenance and timing

`provenance.json` hashes the code, reused engine, and complete output. The
analytic proof extends the precise notebook copy-agreement and strict-leaf
arguments; their entries retain the source provenance. No new source paper was
downloaded or redistributed in this cycle.

`timing.html` is embedded in the notebook. Initial preparation includes the
previous checkpoint. Marked overhead and network windows include the user's
publication-policy request, resolved in the separately committed AGENTS/Spin
edit. Mathematics includes proof review and drafting, plus an unseparated
compaction interval before restoration was marked as reading. Coding was marked
for the short checker implementation and ended when mathematical review resumed.
No retrospective split is estimated.

A large notebook patch initially failed its context match without changing
files. A subsequent protected draft-recovery utility failed an assertion; this
is the one recorded failed local command, not a mathematical failure. The entry
was subsequently written in smaller patches. No rendering build or unrelated
mathematical suite was run. Complete timing and command evidence is preserved
under `research/provenance/session-records/occurrence_mp_replay_20260911_17/`.
