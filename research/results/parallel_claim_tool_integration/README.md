# Integrated claim authoring, notices and navigable views

Integrated the previously reviewed helper modules into the shared claim workflow:

- `claim-index.py author` forwards to the source-backed questionnaire/proposal tool.
- `claim-index.py views` exposes topic/lifecycle views and duplicate suggestions.
- `views bundle --out DIR` writes a linked topic map, all/active/historical and
  unclassified pages, plus one stable-filename page per topic.
- Default canonical `render` refreshes the primary Markdown and topic bundle;
  default `validate` checks both. Alternate registries use explicit `--views-out`
  and `--views-dir` options, avoiding writes to the canonical views in fixtures.
- The real renderer emits scoped correction/status notices. Legacy import and
  reconciliation strip only the marked derived block, preserving original cells.
- Checkout verifies required tools/tests, executable helper scripts, tracked
  derived files and their freshness. CI runs the new suites and watches their
  paths, including the independently implemented article-evidence/finalizer tests.
- The registry guide links the generated topic map and explains authoring,
  proposal-base checks, scope-sensitive notices and heuristic candidate limits.

The full claim suite passed (76 tests at that snapshot), and seven existing
parallel-append tests passed. A later dedicated seven-test view suite passed with
the new CLI-alias/alternate-output/staleness regression. Real validation passed
for 869 claims, all 8,955 source references and all generated views. These counts
describe the validation snapshot; other coordinated workers continue metadata
integration. Re-run rendering after any later canonical edits.

The first full suite failed only because the old generated Markdown lacked the
new notices; regeneration resolved that expected stale-output failure. No source
JSON or notebook was modified by this worker. `test_finish_turn.py`'s copied
dependency list gained the notice helper, coordinated with the article-evidence
worker's additions. No Git operations or publication were performed.

Reproduce with protected `compute.sh run TURN --threads 1 --category
local_processing --` followed by:

```sh
python3 tools/claim-index.py render
python3 -m unittest discover -s tools/tests -p 'test_claim*.py'
python3 -m unittest discover -s tools/tests -p test_merge_formalization_appends.py
python3 tools/claim-index.py validate --out PATH
```

Timing session: `parallel_claim_tool_integration_20260920`. Do not sum this interval
with overlapping worker/coordinator elapsed time.
