# Derived topic views and duplicate discovery

This worker implements the topic-map/view and heuristic duplicate-discovery
tooling in INDEX_MIGRATION section 8. It does not complete the underlying topic
curation or semantic duplicate review. No canonical metadata was changed.

Commands (from repository root):

```sh
python3 tools/claim_views.py topics --out /tmp/topics.json
python3 tools/claim_views.py topics --format markdown --out /tmp/topics.md
python3 tools/claim_views.py view --topic bit-php --format markdown --out /tmp/bit-php.md
python3 tools/claim_views.py view --topic @unclassified --out /tmp/unclassified.json
python3 tools/claim_views.py view --lifecycle historical --out /tmp/historical.json
python3 tools/claim_views.py duplicates --threshold 0.6 --out /tmp/duplicates.json
```

All outputs are complete, derived reports with deterministic ordering; JSON
records the input fingerprint. Topic membership can overlap. Unclassified claims
remain explicit, and the all-claims view retains every label and exact metadata.
Markdown links are resolved against their original registry Markdown location and
converted to public repository links so moving the generated view does not break
them. Summaries are never rewritten or compressed semantically.

Historical means explicitly retracted or superseded by a reviewed relationship;
active means only the complement of that definition, not validity or current-route
membership. Both views retain correction/supersession notices with review status.
Parked claims are retained; no parked/active inference is made from prose.

Duplicate discovery uses sparse summary-token Jaccard overlap. Scores suggest
lexical similarity, not mathematical equivalence. The report preserves every
input ID plus all pairs above the explicit threshold, without an implicit top-N
cutoff. Candidate records say `unreviewed_candidate` and
`accepted_relationship: false`; no claim is merged, removed or reclassified.
Check hypotheses, encodings, quantifiers and costs before recording relationships.

Five focused tests cover ID preservation, explicit unclassified output,
determinism, no mutation, review-sensitive lifecycle partition, visible correction
warnings, portable Markdown links and candidate-only duplicate dispositions.
All passed under the shared computation limits. The first invocation could not
access user systemd in the sandbox; the authorized protected retry passed. No
unprotected fallback was used. Samples here were generated from the working
registry and are dated evidence, not additional editable sources.

## Coordinator integration

Optional `claim-index.py` forwarding alias: add a subparser named `views` with
`add_help=False`; before normal `rest` rejection, forward to
`[sys.executable, str(ROOT/'tools/claim_views.py'), '--registry', str(args.registry), *rest]`.
The self-contained CLI already works without that alias. Add `claim_views.py` and
its test to relevant checkout/CI tracked-tool inventories and add a brief command
reference to `research/claims/README.md`. Keep the prose definitions here or in
that authoritative guide; avoid copying the whole description to multiple rules.

The tools discharge generation/discovery capabilities. Remaining acceptance work
includes semantic review of candidates, topic assignment across all records and
any needed curated historical/supersession relationships. Do not mark those done
on the strength of these reports.

Timing is exported separately by worker session `parallel_index_views_20260920`.
The controller's initial policy/source read preceded instrumentation; do not sum
this worker interval with overlapping coordinator/worker intervals.
