# Side research notebooks and structured integration plan

Draft: 20 September 2026. Implements the proposals in
[IDEAS.md items 9 and 10](../../IDEAS.md#9-side-research-notebooks-with-shared-claim-infrastructure),
including the proposed `Branch` protocol in `PROMPTS.md`.

Status: **planned, not implemented**. Creating this plan does not start a side
investigation, install Git drivers or change the active notebook. Mark tasks
complete only after implementation and validation; record decisions, evidence
and checkpoint references here. Follow existing workspace policies rather than
introducing a second research or publication policy.

## Intended outcome

A research thread can have its own goal, bounded living context and append-only
record while sharing claims and infrastructure with the main project. Merging
its work preserves that notebook, including its living sections; it does not
replace the main goal or discard the side thread's current state.

The main notebook remains at `/math-research/`. Side notebooks are available at
`/math-research/branches/<name>/` on GitHub Pages and at the corresponding route
under the local server's configured base path. Research-thread names are stable
identifiers, independent of temporary Git branches and worktree paths.

Structured integration also supports concurrent additions to the same notebook,
claim registry and attention history. It resolves mechanically compatible edits
and leaves genuine content or review conflicts explicit.

## 1. Establish notebook identity and ownership

- [ ] Inventory assumptions of a single root `notebook.html` in server, client,
      build, restoration, excerpt, registry, review-evidence, timing and validation
      code. Record the affected interfaces before changing their defaults.
- [ ] Choose the smallest shared notebook catalogue/resolver. A proposed layout is
      `research/branches/<name>/notebook.html`, with catalogue metadata identifying
      its source path, public route, parent thread, originating entry and lifecycle
      status. Keep the main source at `notebook.html`. Final paths are an
      implementation decision, not an existing interface.
- [ ] Keep mathematical goals and current assessments in each notebook's living
      sections. Derive navigation summaries where practical; do not create another
      manually synchronized mathematical overview in catalogue metadata.
- [ ] Define safe, stable names and reject duplicate IDs, path traversal and route
      collisions. Renaming a Git branch must not rename a published notebook.
      Preserve published URLs when closing or reorganizing research threads.
- [ ] Give every notebook the familiar living sections and an independent record:
      goal/current position, remaining route, proposed next step, working context
      and applicable formalization gaps. Empty records are valid after creation.
- [ ] Preserve global claim IDs. Qualify article/source references by notebook and
      anchor; ordinary repeated section IDs are scoped to their notebook. Reject
      ambiguous legacy anchor-only lookups rather than resolving to the wrong file.

## 2. Parameterize existing tools without duplicating the framework

- [ ] Introduce one shared notebook-selection interface, with an explicit option
      such as `--notebook NAME` and the main notebook as the backward-compatible
      default. Validate the selection before modifying any file.
- [ ] Specify persistent selection per worktree/session, without committing machine
      paths or agent session IDs. Explicit selection takes precedence. Never infer
      the active research thread solely from the Git branch name; report the chosen
      notebook in restoration and finalization output.
- [ ] Extend `tools/resume.py` and bounded excerpt/context tools to load only the
      selected notebook's living sections and compact contents, followed by relevant
      cross-thread sources as needed. Preserve the bounded resume delivery contract;
      do not import the entire main notebook to initialize every side notebook.
- [ ] Extend `research/context-budgets.json` handling so each notebook has an
      explicit allocation using the established policy. Creating a thread does not
      raise the main notebook's limits or waive per-notebook hard limits.
- [ ] Pass notebook identity through timing and `tools/finish-turn.py`: insert the
      unique timing marker and producer credit into the selected record, validate
      its route/review cadence, and retain globally unambiguous evidence paths.
- [ ] Apply append-only, declaration/source-inventory and link checks to every
      touched notebook. Compare existing records against the relevant integration
      base. Detect deleted notebooks and lost records, not just edits in files that
      remain present. Preserve the historical handoff unchanged.
- [ ] Update claim source lookup, packets, citation discovery and evidence hashing
      to resolve all registered notebooks. Existing main-notebook links and review
      evidence must keep their meaning; do not blanket-refresh review hashes.
- [ ] Share claim metadata, relationships, attention history and formalization
      infrastructure. A cross-thread correction must surface affected dependencies;
      membership in another thread is not evidence of independence.

## 3. Add the `Branch` protocol and a small setup tool

- [ ] Add a `Branch` section to `PROMPTS.md` only once its tools are usable. Invocation:
      `Branch: <new goal>`, optionally with a notebook entry/claim reference where
      the goal originated. The agent resolves the reference and reads the exact
      relevant hypotheses, existing results, corrections and remaining gaps.
- [ ] Separate mechanical scaffolding from mathematical context preparation. The
      tool creates/registers a notebook; the agent supplies a faithful goal and
      initial living context. It must not infer a proof, novelty or a reviewed
      dependency merely from the requested goal or a short claim packet.
- [ ] Select a stable research-thread name and create the associated Git branch or
      isolated worktree as appropriate to the assignment and current worktree.
      Preserve unrelated edits and the user's branch. Record the association, not
      an equivalence between Git branch identity and notebook identity.
- [ ] Initialize a genuinely empty research record. Fill living sections with the
      new goal, exact starting assumptions, inherited tools and links, highest-risk
      obligations, a concrete first test/stopping point and relevant formalization
      gaps. Do not copy historical entries or claim setup itself as research progress.
- [ ] Register navigation, source resolution, budgets and active selection. Validate
      the complete proposed setup before exposing it as ready. Refuse overwriting
      an existing thread and make interrupted setup recoverable without duplicates.
- [ ] End setup with a local checkpoint and report the source path, local/public
      route, goal and next step. Distinguish a future public URL from an already
      deployed page. Creation alone starts no unbounded Spin, parallel assignment,
      Lean work or publication; subsequent research follows the selected thread.
- [ ] Revise existing root guidance that assumes a sole notebook so each notebook
      owns its thread's mathematical state while the main notebook owns the main
      goal. Link the shared policy rather than copying it into every branch.

## 4. Serve and publish multiple notebooks

- [ ] Reuse the current page shell, lazy MathJax, navigation controls and source-TeX
      search. Add clear thread identity, lifecycle status, a link to main, and a
      small branch directory. Keep the main page's existing URL and behavior.
- [ ] Resolve assets, refresh endpoints, entry anchors and cross-notebook links under
      both local serving and the GitHub Pages project prefix. Nested pages must not
      accidentally fetch the main notebook or use broken relative paths.
- [ ] Make local live refresh operate for the selected source. Build side pages
      through `tools/build_pages.py` into the minimal public artifact; never copy
      the checkout, private feedback, caches or local session metadata.
- [ ] Default search to the displayed notebook, including unrendered mathematics.
      Provide an explicit all-notebooks scope with result labels and source links.
      Load wider indexes only on demand; do not typeset other notebooks to search.
- [ ] Keep completed and abandoned notebooks accessible. Lifecycle changes update
      living status without deleting earlier records. Promotion of a useful result
      creates a concise main integration entry linking the full side proof; the
      shared claim retains its identity and original source.

## 5. Structured merge rules

Consolidate/generalize `tools/merge-formalization-appends.py`; avoid a parallel
one-off resolver. Support ordinary merges and merge-backend rebases. Document any
unsupported backend explicitly. Extra whitespace and line-based `merge=union`
are not substitutes for preserving complete structured records.

- [ ] Notebook driver: parse complete articles by stable ID, verify base records
      are preserved byte-for-byte and in order on both sides, and combine independent
      additions without splitting HTML or timing tables. Deduplicate identical
      additions; reject differing content with the same ID, altered/deleted history,
      malformed markup and incompatible ordering constraints.
- [ ] Preserve each branch's sequence of additions. Define a deterministic ordering
      for independent additions and respect explicit dependency constraints where
      available. Do not globally reorder historical entries by timestamps.
- [ ] Merge living sections and surrounding structure with ordinary three-way
      semantics. Preserve genuine competing edits as conflicts; never silently
      choose the main overview and discard a side's changes to the same notebook.
      Distinct side notebooks should survive integration intact.
- [ ] Registry driver: three-way merge claims and relationships by ID; accept
      independent additions and compatible field changes. Reject divergent same-ID
      additions, same-field competing edits and delete/edit conflicts. Treat arrays
      according to their schema rather than blindly concatenating them.
- [ ] Handle coupled review fields conservatively. Combining a statement edit on
      one branch with a review on another must not certify the combined statement.
      Existing evidence/value hashes determine staleness; require explicit review
      when needed, never fabricate a refreshed approval to make the merge pass.
- [ ] Attention driver: combine distinct events while preserving each side's history
      order. Deduplicate only identical events; equal timestamps alone are not
      identity. Conflicting dispositions without a justified ordering require review.
- [ ] Generated views: regenerate claim indexes, topic views and attention Markdown
      only after authoritative inputs are merged. Define a reliable integration
      command/checkpoint because Git does not guarantee per-file driver order.
      A clean Git merge is not a successful checkpoint while derived views are stale.
- [ ] Track code and `.gitattributes`, and provide idempotent per-clone Git driver
      registration without overwriting unrelated configuration. Fresh clones must
      detect missing setup; ensure unsupported/missing drivers cannot silently
      bypass required validation. Installation does not authorize publication.
- [ ] On driver failure, leave recoverable inputs and actionable conflicts. Test
      abort/retry/continue paths and require the existing post-merge checks before
      committing or publishing the integrated result.

## 6. Validation and rollout

- [ ] Preserve a fixture for the current single-notebook workflow. Existing commands,
      links, timing output and main-page behavior must work without new arguments.
- [ ] In disposable repositories/worktrees, exercise `Branch` setup with a prose goal
      and with an originating entry; test empty records, duplicate names, invalid
      references, unrelated edits and interrupted/repeated setup.
- [ ] Verify two threads can run independently with separate living sections/timing,
      shared claims, cross-thread dependencies and corrections, and bounded restores.
      Loading one thread must not load every other record.
- [ ] Test real merges and rebases: distinct notebooks, concurrent same-notebook
      appends, identical/divergent IDs, modified history, overview conflicts,
      independent/competing claim edits, stale review evidence, attention-event
      ordering, missing driver configuration and regeneration failures. Confirm
      both parent histories survive, and genuine conflicts remain visible.
- [ ] Run local/server and static Pages tests for nested routes, refresh, assets,
      cross-links, unrendered-TeX search, mobile controls and browser history.
      Measure startup/render/search costs with multiple growing records; record
      before/after evidence rather than assuming partitioning guarantees speed.
- [ ] Validate per-notebook budgets, all affected registry evidence, append-only
      preservation and minimal-public-artifact contents. Retain focused evidence
      and checkpoint locally; publish only with applicable user authorization.
- [ ] After infrastructure acceptance, use an explicitly assigned first side thread
      as the pilot. Odd-field double covering is a candidate, not an assignment in
      this plan. Confirm its initialized scope with the requested goal before any
      mathematical investigation.

Suggested implementation order: identity/resolution and compatibility first,
then tool parameterization, setup protocol, serving/search and end-to-end checks.
Structured merge drivers can be developed independently against fixtures and
integrated once the identity/source conventions are fixed. Do not enable a
partially wired `Branch` protocol that initializes notebooks the finisher cannot
safely maintain.

## Boundaries with other plans

[PARALLEL_RESEARCH_PLAN.md](PARALLEL_RESEARCH_PLAN.md) owns agent coordination;
this plan supplies persistent thread identity and integration, not permission to
spawn workers. [CONTEXT_BUDGET_PLAN.md](CONTEXT_BUDGET_PLAN.md) owns budget and
bounded-restoration policy. [INDEX_MIGRATION.md](INDEX_MIGRATION.md) owns the shared
claim/review schema; this plan extends its source resolution and merge support.
[CLAIM_GRAPH_PLAN.md](CLAIM_GRAPH_PLAN.md) can consume notebook-qualified sources
without becoming a prerequisite for side notebooks.
