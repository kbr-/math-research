# Fresh MOD frontiers under disjunction input assumptions

Recorded 11 September 2026. The conditional theorem, exact MP identities, and
scope are in [the notebook](https://kbr-.github.io/math-research/#entry-2026-09-11-mod-frontier-replay).
This is an application of earlier zero-replay results. Global integration of
the additional private roots has not been proved.

## Saved evidence

- `checks-01.jsonl`: the complete 23,971,645-byte partial first run. It has eleven
  complete cases and five completed traces from the twelfth case, 93 verified
  traces in total. It has no successful full-suite summary. Its last negative
  weighted baseline stopped at the shared kernel's proof-storage guard.
- `checker-first-run.cpp`: exact source for that initial run, using the unchanged
  `research/tools/pc_boundary.hpp` kernel.
- `checks-02-direct.jsonl`: targeted case 11, both scalar interfaces and their
  direct frontier replays, plus all eight residue/freshness controls. All passed.
- `degree-support.json`: 94 distinct verified traces from 97 reports, with case
  parameters, whole-trace and final-cone degrees, used axiom indices, and input
  file provenance. Three repeated reports agree exactly in their metadata.
- `provenance.json`: streamed hashes of both checker versions, kernel, metadata
  helper, both complete outputs, and the ledger.

The guard rejects proofs with 250,000 or more stored lines or more than
2,000,000 stored polynomial terms. Its error does not distinguish those two
conditions. It was not raised. The missing comparison is the negative full MP
baseline at p=5 with three argument blocks, together with its specialization.
Both direct frontier signs of that case were successfully verified separately.
No universal proof is inferred from these finite tests.

## Reproduce selected work

From the repository root, with resource controls active, use fresh session and
output paths. A direct-only run avoids reconstructing the guarded comparison:

```bash
./compute.sh start frontier_repeat
./compute.sh run frontier_repeat --threads 1 --category local_processing -- \
  c++ -std=c++17 -O2 -Wall -Wextra -Werror -pedantic \
  research/tools/check_mod_frontier_replay.cpp -o research/tmp/check_mod_frontier_replay
./compute.sh run frontier_repeat --threads 1 -- \
  research/tmp/check_mod_frontier_replay --out research/results/frontier_repeat/direct.jsonl \
  --case 11 --direct-only
```

Case IDs 0--5 are p=2,3, each with a single block of width/accuracy (3,1), (5,1),
or (2,2), in that order. Cases 6--7 use p=2 and three/five argument blocks;
8--9 use p=3 and two/four; 10--11 use p=5 and two/three. In these multiple-block
cases, each block has tuple `(x_j,1-x_j)` and accuracy one. All cases have a
positive nonzero-residue and negative zero-residue scalar interface.

The single-block old base includes `x_1-1`; multiple-block old bases contain
only Boolean domains. Both kinds are satisfiable. These are exact algebraic
inference fixtures, not PHP refutations or a primitive-Frege compiler.

To reproduce the first run, compile the saved snapshot with
`-I research/tools` and run it with `--out NEW_PATH`. Its storage-guard exit is
expected on the last baseline; preserve the generated partial file. The current
checker without selection flags also requests every comparison, but records the
primary direct construction before each expanded baseline. None of this needs
new packages or a relaxed resource limit.

To regenerate the small ledger from saved outputs:

```bash
./compute.sh run frontier_repeat --threads 1 --category local_processing -- \
  python3 research/tools/summarize_frontier_replay.py --out research/results/frontier_repeat/ledger.json \
  research/results/weighted_mod_requests_20260911_26/checks-01.jsonl \
  research/results/weighted_mod_requests_20260911_26/checks-02-direct.jsonl
```

The metadata helper streams past the polynomial lines; it does not recompute
the mathematics. Output files are never overwritten. All arithmetic in the PC
checker is exact. There is no random seed.

## Encoding and dependencies

Each case gives the prime, block products and coefficient ranges, full goal
input tuple, and companion-axiom starting indices. Proof records supply complete
axiom arrays, followed by every PC line. Polynomials use
`[coefficient, [[variable_id, exponent], ...]]`, reduced modulo the case's prime.
Rules `a`, `l`, and `m` mean axiom, two-line linear combination, and multiplication
by one variable. Index -1 denotes zero, not an additional axiom. Verified records
give the final line, degree ledger, and final-cone axiom support. Corrupting each
nonzero final line is rejected. Every cleaned line avoids the removed variables.

This cycle read the existing scalar-MP, learned-input-pruning, and positive-zero
records and their exact trace tools, as present in parent checkpoint `b1da6f9`.
It reused those hypotheses rather than claiming a new generic substitution
theorem. No source-paper download, full-text audit, or rendering suite was run.

## Timing

`timing.html` and the archive at
`research/provenance/session-records/weighted_mod_requests_20260911_26/` retain
the measured interval and complete command outputs, including the failed first
run. That command failure is a storage-guard event, not a failed mathematical
identity. Initial formulation was interleaved with targeted source/trace review;
later proof work and coding were marked separately. The preceding checkpoint's
publication and authorization retry are included in preparation. Final archival
and Git work after the snapshot are measured in the next continuous cycle.
