# Side notebook workflow

Main lives in `notebook.html`. Each registered side thread lives in
`research/branches/<name>/notebook.html`, alongside `notebook.json` (identity,
parent, originating source and lifecycle status) and `context-budgets.json`.
The HTML owns the goal and mathematical state; metadata does not duplicate it.
Names survive Git branch renaming/deletion. Claims and review evidence remain in
one shared registry, with globally unique claim IDs.

## Create and select

Invoke `Branch: <goal>` in the agent conversation, optionally linking its originating
entry. The protocol is in [PROMPTS.md](../PROMPTS.md#branch). The agent reads the
actual sources before writing context; the tool does not generate mathematics.
Use a new worktree for an independent Git checkout if needed. Ordinary Git branch
and worktree commands remain available; the protocol does not automatically stash
or relocate unrelated edits.

Prepare a JSON file containing `goal` plus all six keys below. Values are reviewed
HTML contents (not section wrappers). Use MathJax delimiters for mathematics.

```json
{
  "goal": "Precisely stated new goal.",
  "before-this-notebook": "<p>Starting source and scope, with links.</p>",
  "where-we-stand": "<p>What is available and what remains unproved.</p>",
  "remaining-route": "<ol><li data-route-item=\"side-goal\">Highest-risk obligation.</li></ol>",
  "proposed-next-step": "<p>Route item: side-goal. Concrete test and stopping point.</p>",
  "working-context": "<p>Exact assumptions, conventions and linked tools.</p>",
  "formalization-gaps": "<p>Applicable recorded gaps; no formalization assigned.</p>"
}
```

```sh
python3 tools/branch.py create thread-name --title 'Readable title' \
  --context /tmp/thread-context.json --parent main \
  --origin 'https://kbr.is-a.dev/math-research/#originating-entry' --select
python3 tools/notebook_context.py --notebook thread-name
python3 tools/claim-index.py validate
```

`--origin` is optional but, when present, must resolve to an existing registered
notebook anchor. `--git-branch research/thread-name` optionally creates/switches a
Git branch in a clean worktree; otherwise setup leaves the current Git branch
alone. Commit the new thread's three files after reviewing the setup. The empty
record is intentional. Do not invent an initial research entry to fill it.

Creation validates context and budgets, then atomically renames a staging directory.
A duplicate thread is rejected. If interrupted after successful registration, inspect
it and run `select`; do not recreate it. Hidden `.creating-*` directories are ignored
and can be inspected/removed after confirming no setup process is still using them.

```sh
python3 tools/branch.py list
python3 tools/branch.py select thread-name
python3 tools/branch.py select main
python3 tools/resume.py --notebook thread-name
python3 tools/notebook-excerpt.py --notebook thread-name --current
```

Selection is stored under this worktree's Git directory, not in tracked files.
Explicit `--notebook` wins; a clone with no selection defaults to main. A missing
selected thread fails rather than silently switching mathematical context. Read
saved resume parts with the normal `--read ID --part N` commands; they retain the
original selected bundle regardless of later selection changes.

## Research and integration

Use existing research discipline for the selected notebook. Start timing with
`./compute.sh start TURN --notebook thread-name`; use unique turn names across the
repository. Finalize with `./tools/finish-turn.py TURN --notebook thread-name`.
The timing binding and unique marker check prevent accidental cross-thread writes.
`--next NEXT` inherits the selected notebook. Review/update that notebook's living
sections, keep full dated arguments there, and use the shared claim registry.

Public claim-source URLs use
`https://kbr.is-a.dev/math-research/branches/thread-name/#anchor`.
Repeated living-section anchors are local to their notebook. Qualify source links;
never infer claim independence from placement in another notebook. Bare excerpt
lookups without a saved selection reject ambiguous anchors; use `--notebook`.
Fossick inventories all registered records, qualifying side entry IDs with their
thread name while preserving the existing main ledger. Shared claim
review/impact checks still expose cross-thread corrections and stale evidence.

`tools/check-append-only.py --base REV` checks all current and base notebooks,
including deletion/unregistration. `tools/notebook_context.py --all` checks every
registered notebook. Use these and the shared registry checks at integration.
Merging distinct threads keeps both notebooks and their living sections. Same-file
conflicts still need review; automatic Git drivers belong to a separate plan.

Use `tools/branch.py status NAME completed` or `abandoned` to label a thread;
update its living assessment honestly without removing its history. A main-goal
application gets a short main integration entry linking the full side result,
not a duplicate proof or a new ID for the same claim.

## Read and publish

`python3 server.py --port 8001` serves main at `/` and side notebooks at
`/branches/<name>/`; `/math-research/`-prefixed routes also work locally. Every
page has a notebook directory and status. Live refresh watches its own source.

The Pages builder emits main and side pages under the project prefix, plus an
explicit notebook directory and public source payloads for search. It refuses
unexpected output files and copies no private/runtime files. Publish only under
the existing authorization policy; printed public URLs may not exist yet.

Search defaults to the current notebook's prose and original TeX, including
unvisited equations. Select **All notebooks** to load the other sources on demand;
results identify the source thread and navigate to its section/article. Loading
or rendering a page does not load every other notebook's record.
