# Signed boundaries, MOD values, and earlier-input pruning

11 September 2026. The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-11-signed-boundary-audit)
contains the complete arguments and their limitations. This cycle checks four
small algebraic derivations and proves simultaneous PC removal for blocks with
strictly earlier input proofs, including negative axiom-leaf proper copies.
It does not give a PHP refutation or eliminate arbitrary argument evaluations.

## Reproduce

From the repository root with the shared resource controls active:

```bash
mkdir -p research/tmp
./compute.sh --threads 1 c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_signed_boundaries.cpp -o research/tmp/check_signed_boundaries
./compute.sh --threads 1 research/tmp/check_signed_boundaries \
  --out research/results/signed_boundary_audit_20260911_12/checks-REPRO.jsonl
```

The checker refuses to overwrite an existing output. GCC 11.4.0, C++17, exact
ordinary finite-field arithmetic, one thread; no dependencies were installed.
The shared PC engine has 16 variable slots and guards proof storage at two
million polynomial terms. Work ran inside the shared CPU/memory limits.

## Evidence and encoding

- `checks-02.jsonl` is the complete accepted output (9,468,191 bytes): four cases,
  42 proof traces, all axiom polynomials, PC rules and parameters, final-line
  dependency supports, and the nonzero later-companion substitution controls.
- `degree-support.json` extracts the proof-size, degree, and support records for
  convenient inspection. It is not a replacement for the full traces.
- `checks-01.jsonl` preserves the partial first run. Its unit-trace assertion was
  too tight: zero substitution emitted degree-five dead intermediates although
  the final dependency cone has degree three. The corrected ledger retains both
  measures. The original theorem's degree-six ceiling was never violated.
- `replay-kernel-recheck.jsonl` is byte-identical to
  `../implication_boundary_20260911_01/checks-01.jsonl`. This one regression run
  validates extraction of the existing replay engine into `pc_boundary.hpp`;
  it is not a fresh mathematical discovery or a routine resume check.

Every line is a JSON object. A `case` starts a field/formula fixture. A `proof`
contains its ordered axiom array, final line index, total line count, and maximum
emitted degree; following `line` records store the actual PC operations.
Rules are axiom introduction (`a`), two-term linear combination (`l`), and
one-variable multiplication (`m`). Index -1 means the zero polynomial, never
an extra axiom. Polynomials are lists of
`[coefficient, [[variable_id, exponent], ...]]`, with coefficients modulo p.
`support` reports only ancestors of the final line, their degree, used axiom
indices, and variables. Every nonzero final line passes rule verification and
fails the deliberately corrupted-final check. This is an exact implementation
check, not independent formal verification of arbitrary Frege simulations.

Original variables x,y have IDs 0,1 and Boolean equations. All other variables
have field equations r^p-r, including p=3 where they are not Boolean.

| Fixture | Proper variables | Old nondomain axiom indices |
| --- | --- | --- |
| Positive | Inner OR 2,3; proper A 4,5 | Inner companions 6,7; A companions 8,9 |
| Negative | Complementary X 2,3; Y 4,5; proper W 6,7 | X companions 8,9; Y 10,11; W 12,13 |

Each case starts with its old domain equations. Private coefficients are allocated
after the proper variables and absent from the transformed proofs. Block records
give exact private ranges and companion offsets in the corresponding source
axiom arrays. Reduced systems use their own explicitly stored axiom arrays.
Proof names recur across cases; interpret them within the preceding case.

For both p=2 and p=3, the positive antecedent requires the used inner companion
and both canonical-A companions in this trace. The negative input proofs use
only their respective child block and its domains, with no canonical-W variable.
The weighted MOD construction subsequently uses canonical-W coefficient domains
but still no W companions. The alternative direct reuse trace avoids those
extra domain proofs. None of the recorded degrees is claimed optimal.

## Timing and provenance

`provenance.json` hashes the checkers, shared engine, and complete result files.
This cycle uses the precise prior notebook proofs; no new paper/source audit
or site-rendering check was needed. A metadata extraction initially failed on
the header's missing `record` key and then succeeded; it did not change the
mathematical output. Full failures and command outputs are archived with timing.

`preparation-audit.json` contains only timestamps and activity metadata for the
previous turn's final preparation window, answering the user's timing question.
It contains no message bodies, account data, or session identifiers. The full
window is about 60 min 57 s; seven tool calls include notebook/proof revisions,
and no compaction event appears. The preceding timing journal fixes the phase
boundaries. This is evidence of a mixed, poorly bounded finalization phase, not
a retrospective measurement of pure thinking or a basis for relabeling minutes.
The old table remains unchanged. The workflow correction is commit `5f1a538`.

The current clock began during completion of the preceding checkpoint and
remained active across context compaction/restoration. Initial preparation can
therefore include that interruption. The marked overhead window covers the user's
timing question, its investigation, and the small workflow correction. Proof
review and notebook mathematics remained in the mathematics phase afterward.
The final table is `timing.html`; archived evidence is under
`research/provenance/session-records/signed_boundary_audit_20260911_12/`.
