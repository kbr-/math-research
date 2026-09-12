# Functional auxiliary base and signed-literal restrictions

The [notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-functional-literal-restrictions)
contains the full statements and proofs. An explicit functional auxiliary base
retains Razborov's PC degree lower bound. Matching-switch and negative-survival
counts give simultaneous coverage of every polynomial-size literal collection
at logarithmic accuracy, on a square-root residual. Affine star normalizers
preserve completed PC degree D>=max(2h+1,p).

This covers a source subclass. General MOD inputs and a multilevel invariant
remain unresolved. The weak source endpoint is unchanged; row exclusions are
adjoined explicitly, not derived from it. No literature-wide novelty claim is made.

## Exact finite evidence

The accepted complete output is counting-checks.jsonl, with all graph edge lists,
bad-event counts, exact survival counts, and rational bounds.

| n | Residual N | Matching size q | All matchings enumerated |
| -: | -: | -: | -: |
| 6 | 1 | 5 | 15,120 |
| 8 | 2 | 6 | 1,693,440 |

Each board tests six positive graphs: empty, complete, diagonal, cyclic pairs,
one-row star, and checkerboard. The positive bad event is counted directly,
independently of the injection's encoding; multiple cases have nonzero counts.
Fixed negative matchings of sizes one, two, and three test the exact formula.
All twelve positive inequalities and six negative equalities passed.
The matching enumeration is exhaustive for these fixtures, not for every graph.
Graph edges are zero-based. No randomness or seed is used.

Reproduce from the repository root, with a new output path:

~~~bash
./compute.sh --threads 1 --category local_processing \
  g++ -std=c++17 -O2 -Wall -Wextra -Werror \
  research/tools/check_literal_matching_restrictions.cpp \
  -o /tmp/math-literal-matching-check
./compute.sh --threads 1 /tmp/math-literal-matching-check \
  --out research/results/literal-matching-recheck.jsonl
~~~

## Sources and measurement

The local published Razborov 1998 extraction was reread at lines 130-164 and
214-251: Definitions 2.1 and 2.4 and Theorem 3.1. Lines 1-24 identify the title
and version. SOURCE_AUDIT.md records the earlier visual inspection of printed
pages 296-297; this cycle did not repeat it or read the whole paper.
The local-only PDF and extraction are fingerprinted, not copied into public
evidence. One-star certificates extend the recorded one-column literal formulas
using the explicit row exclusions. Provenance hashes identify these dependencies.

The initial preparation interval includes the preceding checkpoint; reading
includes a short user status exchange. Mathematics includes initial test-design
discussion before the coding marker, without retrospective splitting. Coding,
compilation, and the exact run are measured separately. Proof review and writing
remain in mathematics. Complete protected command outputs are archived.

Two source lookups included nonexistent guessed filenames and were corrected.
One patch submission had a quoting error and made no edits before its correction.
These were utility errors; the strict-warning build and single compiled check
both passed. No dependency was installed.

The process improvement clarifies the existing encoding guidance: preserve the
default weak source system while permitting explicitly justified auxiliary
systems with their actual transfer and lower-bound hypotheses.
