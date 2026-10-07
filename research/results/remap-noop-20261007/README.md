# No-op revision remapping — 7 October 2026

`remap-revisions.py` now skips claim hashing, attention scanning, writes and rendering
when no revision field changes. It still checks for old hashes outside revision
fields before returning. Real remaps retain their existing validation and update path.

Two adjacent real rebase checkpoints each matched one rewritten commit and changed
zero revision fields, review hashes or attention fingerprints. Protected launcher
wall intervals were 33.799782488 seconds before the change (run `54b9502170`) and
1.549990913 seconds after it (run `e09d962bae`), both in
`bmd-exception-precision-lift-20261007`. These were adjacent repository snapshots,
not an identical-input benchmark. Both complete command outputs are retained here;
the timing events are archived with the owning research cycle.

All 547 framework tests passed in 7.9 seconds. Regression tests verify that the
no-op path skips claim hashing and attention/render work, preserves registry bytes,
and still rejects mapped hashes outside revision fields. Existing tests retain
coverage of real revision/hash changes and attention fingerprint updates.
