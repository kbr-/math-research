# Claim-parser measurement — 9 October 2026

A finisher reported 6.6 seconds of checks against its 5-second warning threshold.
The retained profile of `tools/claim-index.py changed --base HEAD~1`, at research
commit `0ddecad5a`, found 218,610 duplicate-key object hooks and about 1.07 seconds
inside that hook. The valid path constructed an error string and called `require`
for every key. The change constructs the dictionary in C, compares lengths, and
only scans for the first duplicate when a duplicate actually exists. Nested and
escaped-key duplicates remain rejected with the original diagnostic.

The real changed comparison was pinned to `a303b71ea`. Protected unprofiled runs:

| Version | Run | Instrumented run interval |
| --- | --- | --- |
| Before | `110ba0dc25` | 5.331108562 seconds |
| After | `e1cf9fa4cb` | 4.893495904 seconds |

Both reports passed and their JSON output files were byte-identical. These are
one before/after pair, including launcher time, not a stable throughput estimate
or a measurement of the complete finisher after this change. Full reports and
the complete profile table are retained beside this note.

The required full framework run executed 555 tests in 22.0 seconds: 552 passed,
and three browser groups failed only their per-case timing assertions (7.4–7.8
seconds versus 5). No functional assertion failed; the overall 10-second limit
also failed. The complete output is retained. The host subsequently reported
load averages 16.01, 11.48, 6.46; this is possible contention evidence, not proof
that all timing excess was external. No test limit was relaxed and no timing-only
rerun was performed. Thus this checkpoint does not claim an all-green suite or a
resolved end-to-end performance limit.

All runs used the shared protected launcher under session
`binary_rank_partition_20261009`; its next research checkpoint archives the timing
journal. No benchmark helper or dependency was introduced.
