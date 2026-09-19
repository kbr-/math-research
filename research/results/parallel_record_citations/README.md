# Complete Research-record citation inventory

The reusable scanner inventories every href-bearing HTML anchor and recognized
claim-label token in research-article text nodes, including unindexed articles.
It excludes living sections, comments, attributes (including data-claims), scripts
and styles. Both links and explicit labels are retained when the same citation
uses both forms. This is occurrence accounting, not automatic proof dependencies
or a replacement for semantic omitted-claim adjudication.

```bash
./compute.sh --threads 1 --category local_processing python3 tools/claim-dependencies.py \
  record-scan --out /tmp/record-citations.json
./tools/claim-dependencies.py record-show --input /tmp/record-citations.json \
  --ownership unowned -n 10 --out /tmp/unowned-citations.json
./tools/claim-dependencies.py record-show --input /tmp/record-citations.json \
  --article entry-2026-09-15-lean-chessboard-star-intersections -n 10
```

`record-show` also filters by `--claim ID` (direct source/target candidate),
`--kind hyperlink|explicit_claim_label`, and ownership. Its output is bounded;
`--out` saves every matching occurrence. Notebook and registry changes since the
scan are both reported. Rescan after integration to refresh candidate ownership.

Each occurrence records its article, line, exact target, nearest heading including
unanchored siblings, bounded clean context, direct/enclosing/article source-claim
candidates, target candidates and ambiguity/unowned disposition. Nonheading
source anchors own only their actual element. Broad article indexing is not
silently treated as ownership of every internal claim. Historical/current labels
remain distinguishable, including a label present in both namespaces. No graph
edge or candidate acceptance is created.

`citations.json` preserves the initial snapshot. `citations-final.json` is the later
snapshot after concurrent root updates: **315 articles, 2,490 links, 77 label
occurrences**, totaling **2,567**. Of those, 645 are unowned, 144 have ambiguous
candidate owners, 59 have only broad article ownership and 1,719 have one candidate.
Unowned does not mean missing mathematical claim: references in introductions,
proofs and procedural sections can legitimately have no exact indexed owner.

`acceptance.json` verifies unique occurrence IDs and exact per-article accounting.
It records the independent heading-inventory snapshot hash, which differs because
root editing continued; both snapshots contain 315 articles. The source inventory
worker was notified and its 91 semantic candidate adjudications were not duplicated.
The earlier lookup examples deliberately preserve observed staleness reports.

Seven new tests cover complete/unindexed traversal, comments/attributes exclusion,
shared and broad ownership, unanchored siblings, exact paragraph ownership,
historical/current ambiguity, arbitrary registry prefixes and stable IDs under
living-section edits. The existing 11 dependency-tool tests also pass. The scanner
finds recognized explicit labels within individual text nodes; implicit prose
references and labels split across nodes remain outside token discovery. It
preserves all hyperlinks independently of label-token recognition.

Touched tools: `tools/record_citations.py`, `tools/claim-dependencies.py`, and
`tools/tests/test_record_citations.py`. The coordinator should include the new test
in CI and expose the two commands in the registry workflow documentation. No
canonical registry, notebook or Git state was edited by this worker. Full command
outputs and measured overlapping worker timing are archived as
`parallel_record_citations`.
