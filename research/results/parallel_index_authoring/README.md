# Source-backed authoring proposals and acceptance fixtures

`tools/claim_authoring.py` creates an explicit questionnaire and validates a
completed proposal without writing the canonical registry. It reuses schema,
evidence hashing, source-target validation and changed-claim maintenance helpers.
It does not infer mathematical judgments, fabricate reviews or supply all-null
records that appear ready for import.

```sh
python3 tools/claim_authoring.py template lem:example --out /tmp/claim-request.json
# Fill every REQUIRED answer; add affected claim submissions and reviewed edges.
python3 tools/claim_authoring.py prepare --request /tmp/claim-request.json \
  --out /tmp/index-proposed.json --report /tmp/claim-report.json
```

The questionnaire contains the registry fingerprint, source revision/date/reviewer,
claim metadata, and five field dispositions with reasons, source locators and
pending next actions. For an existing ID it copies current metadata for editing,
but still requires explicit renewed dispositions. Reviewed empty metadata is
rejected; justified pending or not-applicable dispositions remain distinct from
completed assessment. An empty relationship list may be a reviewed conclusion
when its explicit reason and source evidence support that conclusion.

Topic definitions and relationships can be appended in the request. Changed edge
endpoints must receive the required current reviews; correction targets also need
an explicit status acknowledgment. Existing relationships/topic definitions are
not silently replaced by this authoring tool: use an ordinary reviewed edit for
such revisions. Review hashes are generated from source evidence after all
submissions have been assembled, avoiding manual hash bookkeeping.

The base fingerprint detects intervening registry edits, including interrupted
work resumed against a changed base. After reviewing the proposal, the coordinator
may import it **only against the same current base**, regenerate Markdown and
other derived views, and run the normal changed/registration/finalization gates.
The preparation tool cannot validate an unwritten future notebook article; that
article must still declare its claim inventory and pass the existing gate.
Output paths must be new and may not replace the canonical input.

Seven isolated acceptance tests cover:

- New proposal through source hashing, schema/maintenance, notebook registration,
  rendered index, actual exact-label lookup and minimal topic-filtered TSV lookup.
- Unanswered questionnaires, missing dispositions and stale bases rejected.
- Pending and not-applicable states represented honestly; missing pending action
  and broken source links rejected.
- A new dated correction preserving the old source record, requiring refreshed
  target review, and exposing a dependent claim through the impact query.
- Partial formalization scope update without upgrading mathematical status.
- Saved/resumed questionnaires and complete parallel append proposals merged
  through the existing merge helper with stable IDs and accepted records preserved.

These are fictional fixtures, not new mathematical results or a Lean verification.
They exercise component integration and actual retrieval CLI calls; existing
finalizer/CI suites remain responsible for their orchestration. The first two
test runs exposed fixture errors (empty legacy import, then incorrect assumptions
about impact-query edge types); both were corrected and retained in the timing
archive. Final seven-test run passes under protected shared resource limits.

## Coordinator integration

Expose these two commands in the registry guide and add the module/test paths to
checkout/CI tool inventories. An optional `claim-index.py author` forwarding alias
can mirror the `views` alias: forward `--registry` and remaining arguments to
`tools/claim_authoring.py`. No additional policy file is needed.

The combined fixture evidence supports the authoring and component acceptance
items in INDEX_MIGRATION sections 12–13; it does not complete metadata backfill or
prove that human judgments are correct. No shared registry/notebook/plan/CI or Git
files were changed by this worker. Timing session: `parallel_index_authoring_20260920`.
Do not add its overlapping interval to other workers' wall-clock totals.
