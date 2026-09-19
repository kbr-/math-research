# Parallel metadata review: claims 680–865

This worker reviewed the 186 assigned claims at zero-based positions 680–865 of
`dc1d95b4cb6a463436256b830afd69029c1dc3ed`. The exponential bit-PHP publication
corollary already had reviewed metadata and is preserved. `patch.json` proposes
mathematical status, topics and significance for the other 185 claims (555 field
reviews). It does not modify original text, formalization or relationships.

Evidence: `extract.py` creates bounded packets, saved in `packets.json`. The review
uses exact existing assessment text and selected source excerpts for orientation,
not a fresh proof audit, Lean run or novelty search. `build_patch.py` encodes the
per-claim decisions. `validate_patch.py` applies them in memory, hashes source
evidence through the existing review API, and validates the complete resulting
schema without writing the registry. Its result is `validation.json`.

Integration must pin the baseline and preserve any intervening reviewed changes.
For each proposed field use `make_review` with its evidence targets, state, note
and next action. No new topic IDs are needed. The coordinator owns canonical
integration, generated Markdown, the plan, notebook entry and Git checkpoint.

## Points requiring explicit preservation

- The adaptive-heavy-query rule is classified as a refutation of its original
  rule; corrected hole-only and both-endpoints rules are separate valid claims.
- Early switching claims retain their conditional composition scope where their
  indexed assessment still qualifies it. Round bounds are not thereby refuted.
  Later restorations remain attached to their precise tree/pinning/light-range
  hypotheses; no global blanket restoration is inferred.
- Old decoder obstructions remain historical method limitations even when a
  later decoder resolves them. Superseded valid tools are not retracted.
- Finite rank-loss examples, spectra and closure computations remain finite
  checks; they do not establish asymptotic hardness or an untested rank range.
- The conjectures and open questions remain conjectural. The all-degree HW goal
  is not implied by the degree-two parity results.
- `not_claimed` for novelty records the scope of this metadata pass, not evidence
  that the claim is known or has no publication value. Imported Beame and
  literature entries, and explicit rediscoveries, carry `known` provenance.

No canonical files, mathematical statements, Git state or user files were edited.
Initial policy reading preceded instrumentation by a short unmeasured interval.
The failed unprivileged resource-status check was followed by a successful
escalated check; no computation bypassed enforcement.
