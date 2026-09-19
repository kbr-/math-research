# Preserve new article reviews across finalizer decoration

The real finalizer passes metadata validation, then inserts producer credit and
the timing fragment. Legacy whole-article byte hashes therefore become stale
immediately after a successful checkpoint. `reproduction.json` demonstrates all
five fields changing from reviewed to stale in an isolated Git repository.

## Minimal backward-compatible proposal

- New `tools/claim_evidence.py` implements version `notebook-article-v1`.
- Apply `integration.patch` after inspecting against current files. It proposes
  changes to `claim_reviews.py`, schema v2, `finish-turn.py`, and its existing test
  fixture. No shared implementation file was edited by this worker.
- New article reviews created by `make_review` carry an optional `normalization`
  key. Existing items without that key retain raw-byte semantics and every stored
  legacy hash stays untouched. Direct `Evidence.sha256(target)` calls also remain
  raw, so dependency-candidate/source fingerprints do not change silently.
- Normalized article evidence omits the exact direct-child TIMING placeholder,
  machine-marked timing block and machine-marked terminal producer span in the
  article's status paragraph. Ordinary/unmarked text, unmarked historical timing,
  status wording, formulas and source attributes remain evidence. Existing
  historical entries are never rewritten to add markers.
- The finalizer wraps only newly produced metadata with versioned markers.
  The separate timing artifact remains unchanged. Old producer/timing markup is
  not globally erased; a new review of an old article simply includes that
  historical raw decoration in its source material.
- TeX angle brackets are masked with length-preserving characters only during
  markup parsing; they remain unchanged in hashed mathematical content.

## Actual checks

`tools/tests/test_claim_article_evidence.py`: three focused tests pass. They
check decoration stability, changes to mathematics/status/article ID, unmarked
credits/timing, malformed producer-like content and raw TeX inequalities.

`reproduce.py` runs real `finish-turn.py` metadata/archival flows in disposable
Git repositories with a new fully populated claim whose evidence is the whole
article. Before the proposal all five reviews become stale; with the proposal
all remain reviewed. Subsequent mathematical or status changes still make all
five stale. The real finalizer and shared protected launcher run in both cases;
no mock replacement claims successful finalization. The output is retained in
`reproduction.json`. The small fake theorem is a software fixture, not research.

The proposal also adjusts the existing finalizer test's copied-module list and
expected generated markup. The coordinator should include the new helper/test
in CI and checkout inventories, run the existing finalizer suite after applying
the proposal, and use a permanent complete-new-claim finalizer regression
alongside these isolated reproduction artifacts. No dependency installation or
canonical-registry changes are needed. This is a normalization format addition,
not a migration that rehashes existing claims.

One limitation is explicit: machine-generated markers identify excluded
presentation content. They are not a semantic proof that a human could never
mislabel mathematical prose as generated decoration. The normal path writes
those markers only around the tool's own producer credit and timing fragment;
mathematical/status prose outside them is always fingerprinted.

## Implemented integration and final-heading extension

The coordinator authorized applying the shared edits, and they are now installed.
`integration.patch` preserves the initial proposal, not a command to reapply over
the implemented code. The existing finalizer fixture retains the concurrent
`claim_notices.py` addition. New `test_claim_article_finalizer.py` runs actual
successful finalization with complete new metadata in both whole-article and
final-H4 source configurations. The final-H4 case uses optional version
`notebook-fragment-v1`, restoring an enclosing parsing scope only while stripping
recognized decoration. Its mathematics remains fingerprinted. Earlier status
text outside an H4 source is deliberately not part of that source; whole-article
reviews cover it. Both modes preserve absent-version raw semantics.

The permanent regression additionally checks the raw digest against the actual
excerpt bytes, verifies that finalization never rewrites stored metadata, and
shows a decoration-only change stales raw legacy reviews while leaving newly
normalized reviews current. Changes to covered mathematics or status still stale
new reviews. The isolated reproduction now obtains unpatched shared files from
immutable baseline `4747534a8c0b68d3eeb7d4e8f199c9d355febd1f`, so it remains
reproducible after integration. No historical claim metadata was rehashed.

An initial patch application stopped on a concurrent finalizer-fixture change;
no partial shared patch was applied. The patch was regenerated preserving that
change, checked and applied. This was an integration conflict, not a test or
mathematical failure.

## Legacy refresh guard

Coordinator integration exposed a historical free-form markup fragment at
`#local-zero-cofactor-pruning` that the stricter decoration parser rejected.
Automatic normalization now activates only when an excerpt contains a TIMING
placeholder or an explicit finish-turn-generated producer/timing marker.
Untouched historical sources stay on exact raw hashing, including when a new
metadata review is recorded. The actual source is covered by a regression test;
all six focused article/fragment/legacy tests pass. The current article and final
H4 flows still opt in before finalization because their TIMING placeholder is
present. No source content or stored old hash was rewritten.
