# Noemesis research workspace instructions

These are explicit user constraints for this workspace and future sessions.

Read [COMPUTATION_RULES.md](COMPUTATION_RULES.md) before running computations.
It owns resource limits, execution, numerical checks, timing-tool operation,
and result retention. This file owns research workflow, notebook editing, and
Git/publication rules; reference the relevant policy rather than duplicating it.

For mathematical research, start with `research/notes/RESUME.md`, the reading
guide to the authoritative initial sections of `notebook.html`. Keep
`php_codex_handoff/` unchanged as the historical package. New research artifacts
belong in `research/` (or another appropriate directory outside the handoff).
Use targeted source excerpts rather than repeatedly importing the full manuscript.

Keep the research framework itself small and usable. Before adding guidance,
revise or consolidate existing rules; keep each rule in one authoritative place
and link to it elsewhere. Remove obsolete or repetitive instructions as the
framework evolves, while preserving explicit user constraints. Prefer a short,
actionable rule over another checklist or a record of one-off setup history.

## Portable sessions and Git checkpoints

- **While the user-authorized Spin task is active, push reviewed research and
  framework checkpoints to `origin/main` at `github.com/kbr-/math-research`.**
  On 2026-09-17 at approximately 23:10 UTC the user refreshed the action
  authorization: "You're allowed to push during Spin for the next 24 hours."
  The window runs through 2026-09-18 23:10 UTC and applies only while Spin is
  active; it replaces the expired 2026-09-12 grant.
  This later authorization covers every reviewed Spin checkpoint and its normal
  GitHub Pages update, superseding the earlier no-push instructions for Spin.
  Compaction does not revoke it: restore this grant and cite the user's actual
  authorization in approval requests. Do not ask again within this scope.
  It ends when the window closes, or earlier if the user stops Spin or revokes
  or limits the permission; honor later user instructions. Source/history
  checks and private-backup exclusions below still apply.
- Outside Spin, commit locally and leave publication to the user unless a prompt
  explicitly authorizes it. A request to research, edit, or commit alone is not
  permission to publish.
- Respect the user's chosen research branch. Do not switch or merge into main
  merely to publish work. The Pages workflow deploys when main is pushed;
  local commits on any branch are only checkpoints.
- Pin integration targets to immutable commit IDs after fetching or receiving a
  worker checkpoint; rebase and validate against those IDs, not moving branch
  names. Immediately before a fast-forward, check the destination's current
  HEAD and worktree status. If it advanced, refresh/rebase or leave it unmerged;
  never treat validation against an older target as validation of the new one.
- Work from the repository root; do not assume a particular absolute path, user,
  or machine. The repository supports Codex and Claude Code. `./start-codex.sh`
  and `./start-claude.sh` resume the exact machine-local ID stored in
  `.codex-session-id` or `.claude-session-id`, or start a fresh
  context-restoration session if absent.
- On a fresh Codex session explicitly started by its launcher, the main assistant
  runs `./tools/remember-codex-session.py` to bind its current CODEX_THREAD_ID;
  the Claude launcher binds the ID itself. Do not overwrite a binding from
  subagents or unrelated sessions. Never commit it.
  A clone restores research from files, not from another machine's chat history.
  An agent's private memory may hold user preferences only, never mathematical
  state or research progress.
- At the end of every research turn, including an unsuccessful attempt or a turn
  with no useful mathematical result, append a Research-record entry and create
  a Git commit. Include the notebook living sections, supporting evidence,
  source provenance, code, and reproducibility data. RESUME changes only when
  navigation or workflow changes.
- Before committing, run `./tools/finish-turn.py TURN`: it stops and exports timing,
  archives evidence, and fills the entry's unique `<!-- TIMING TURN -->` placeholder.
  During continuous research, add `--next NEXT` to start the next clock immediately
  after the snapshot; final checkpoint work is then measured as preparation.
  Run this small controller directly, not as a job in the session it will stop.
  Promote other essential results from scratch/runtime directories into
  `research/results/` or `research/provenance/`. Research must never exist only
  in ignored files or the chat transcript.
- When opening a research cycle, name the remaining-route obligation, explain
  how the task could discharge or test it, and state a concrete stopping point.
  Distinguish what suffices for the goal from stronger conveniences of a method.
  Select a sufficient endpoint before adding proof-conversion steps.
  Prioritize an unproved obligation required for the main goal. Use restricted
  cases to test a named hypothesis, obstruction, or candidate general mechanism.
  A growing case list or equivalent reformulation leaves the general implication
  unproved. Before further refinement, state the intended general claim and try
  to falsify it using known
  obstructions or hard instances. Check the hypotheses preserved by each step
  and the accumulated costs under composition against the budget needed for
  the goal. If those checks fail or repeated cycles leave the same required
  implication untouched, review alternative approaches and address the failure
  before refining the same mechanism. Route reviews are periodic and enforced:
  tag every entry's `<article>` with `data-kind` (`research`, `review`, or
  `formalization`) and `data-route`, a `data-route-item` slug of a top-level
  item of The remaining route (or `side-...`), never a sub-gap of the current
  line; `finish-turn.py` refuses a seventh consecutive research entry without a
  review. A review entry states the current line's general claim, what the main
  goal needs from it, a falsification attempt, an honest estimate of the chance
  that the line advances the goal (of that line only, never a verdict on the
  program as a whole), and the next step on the highest-risk item;
  Proposed next step names the route item it advances. Once the question,
  argument, and evidence are stable, make one focused correctness review;
  move optional extensions to the next cycle. Reopen the argument only
  for a concrete unresolved concern. Prepare the commit message, staging paths,
  and focused metadata check during review. Start preparation with a ready
  sequential checkpoint batch: phase marker, check, provenance, timing export,
  archival, staging, commit, and any already authorized push. Stop on failure
  and inspect it before continuing. Finish the local checkpoint before developing
  the next result.
  Review only the relevant changes; do not silently include
  unrelated user edits. If committing fails, report the blocker; do not claim
  that the result is checkpointed. Operational logs, credentials, local session
  IDs, generated binaries, virtual environments, and scratch renders stay untracked.
- Keep every commit-message line, including the subject and body, at most
  100 characters wide. Wrap prose manually and separate paragraphs with blank lines.
- Preserve complete computation outputs and reproduction metadata under
  [the output policy](COMPUTATION_RULES.md#persist-computation-outputs).
  Reference the files from the relevant notebook Research-record entry, and
  commit them with the result.

## Computation policy

- Before computations, read and follow [COMPUTATION_RULES.md](COMPUTATION_RULES.md).
  All substantial local jobs use `./compute.sh` and share at most 14 logical CPUs
  and 10 GB combined RAM plus swap. Never bypass a failed resource-limit check.
- Use compiled numerical implementations for heavy work; install no dependencies
  or virtual environments without explicit user approval. See the computation
  policy for setup, enforcement, numerical accuracy, timing, and result retention.

## Live research notebook

- Follow the root LICENSE: original software uses MIT; original research material
  uses CC BY 4.0. Preserve attribution, cite upstream mathematics appropriately,
  and keep working results distinct from established theorems.
- Third-party papers are not ours to relicense. Follow THIRD_PARTY_NOTICES.md and
  research/references/redistribution.json. Keep uncleared PDFs, full-text copies,
  and source-containing diagnostics out of public commits and reachable history.
  Preserve needed personal copies locally; do not publish private/ backups.
  If a needed paper remains unavailable after an honest retrieval attempt, add
  its citation, attempted links, and purpose to Git-ignored `user_requests` at
  the repository root. Create the file only when needed; continue independent
  work while the user obtains the paper and reports back.
- Preserve the user's private `pre-publish` backup branch. Never publish that
  backup or use `--all`/`--mirror`. Before an authorized publication, check the
  branch with `tools/verify-checkout.py --public-history BRANCH`.
  The current Pages workflow targets main only.

- `notebook.html` at the workspace root is the authoritative current mathematical
  state and user-facing research record,
  served by `python3 server.py` at http://localhost:8000. Edit its content directly;
  the browser refreshes automatically. `index.html` supplies the page layout.
- `.github/workflows/pages.yml` builds the published notebook from pushes to
  `main` that change the HTML or site tooling. `tools/build_pages.py --out _site`
  creates the minimal Pages artifact; never upload the whole checkout or private
  sources. Preserve local live mode and published project-relative revision URLs.
- After every research turn, review and refresh the three living sections:
  **Where we stand**, **The remaining route** (highest risk first), and
  **Proposed next step**. Also maintain **Working mathematical context** for
  the exact setup and degree conventions, active tools with linked hypotheses
  and proofs, and unresolved dependencies affecting the next step.
  Keep the overview concise and accurate; do not invent progress when the
  mathematical status has not changed. Lead with the main research goal and
  keep the route and next step on that path; mention side results and their
  publication briefly in the overview.
  During coordinated parallel formalization, the coordinator alone edits all
  living sections, including the formalization-gaps list, at integration checkpoints.
  Workers still review them, append their own full records, maintain claim-index
  entries, and send proposed overview changes or discrepancies to the coordinator.
  Flag a discrepancy promptly; do not wait for every branch to finish.
- Revise and consolidate Working mathematical context by topic; do not append
  a subsection there automatically for every turn. Keep full arguments, failed
  approaches, test details, and reading history in the Research record or linked
  supporting evidence. A result need not stay in working context to be preserved
  or available for future work; retain a precise source link when condensing it.
- Use roughly 1,000 prose words as a soft target for Working mathematical context
  only. Review it yourself after each research turn, especially when it grows
  beyond that target: remove duplication, consolidate related results, and link
  to full records. Do not ask the user to perform or approve routine editorial
  review. Exceed the target when essential definitions, hypotheses, degree bounds,
  or unresolved assumptions need the space; never truncate necessary mathematics
  or discard its durable record to meet a word count.
- Append an entry for **every research turn** to the notebook's final **Research
  record**, even if it produces no useful result, only an obstruction, or a failed
  proof attempt. Describe the question/approach, actual outcome, and remaining gap
  honestly; do not manufacture a lemma to justify an entry. Publish all substantial
  new mathematics there in full. Supporting notes or chat alone are insufficient.
  This full Research record has no word limit and is never consolidated away to
  satisfy the separate working-context target.
- Entries are chronological and append-only. Give each a date, descriptive title,
  stable HTML anchor, the route tags above, and a short `<p class="entry-meta">`
  status line (`finish-turn.py` rejects more than 300 characters), to which
  `finish-turn.py` appends the agent and model recorded by the timing session.
  Do not number cycles: branches and parallel worktrees cannot share a counter.
  Refer to an entry by its anchor; label parallel formalization entries by route ID.
  State an explicit status (working proof, conditional result,
  conjecture, finite check, or refutation). State assumptions and the precise
  claim, provide the mathematical argument, and include relevant dependencies,
  degree/parameter accounting, checks, and the remaining gap.
- Link historical claim references (such as `lem:prefixcertificate`) directly
  to the relevant manuscript Markdown statement/proof anchor, using the mapping
  in `php_codex_handoff/manuscript/CLAIM_INDEX.md`. In the notebook, use public
  GitHub file URLs so links work both locally and on Pages. Verify the file and
  anchor locally; agents should still read local source excerpts when available.
  Adding or repairing links in earlier entries is allowed if their statements
  and proofs remain unchanged; mathematical corrections require a new dated entry.
- Maintain [research/CLAIM_INDEX.md](research/CLAIM_INDEX.md) as concise navigation
  to new claims and obstructions: stable labels, status, and full-record links.
  Before proposing a next step or developing or naming a result, search the index
  for the same object or template and read the relevant claims. Label rediscoveries and refinements and link the
  original record; link corrections or retractions to their new dated entries.
- Read **Gaps identified by formalization** during context restoration, including
  ordinary research sessions. This concise section precedes Research record and
  links to discrepancies and their audit status. The formalization agent maintains
  it in place under [formalization/AGENTS.md](formalization/AGENTS.md); full arguments
  and mathematical corrections remain in dated research entries.
- Lean formalizations live in [formalization/](formalization/README.md). Begin
  formalization only under an explicit user assignment, including an explicitly
  assigned parallel formalization agent; ordinary research and Spin do not
  require formalizing results. Read [formalization/AGENTS.md](formalization/AGENTS.md)
  when assigned, not as mandatory reading for every research cycle. For each formalized claim,
  update its entry in research/CLAIM_INDEX.md with a link to the per-claim Lean
  file and the exact verified scope, identifying partial coverage or stronger
  hypotheses. Keep formalization status distinct from mathematical status:
  absence of a formalization does not make a result incomplete, and a verified
  special case does not verify the full informal claim. Record formalization
  work and its verification evidence under the usual research-turn protocol.
- End every research-turn entry with a two-column **Measured category / Elapsed**
  timing table, headed by the bold total instrumented interval. Generate it from
  actual timing data with `./compute.sh report TURN --stop --html-out PATH` and
  embed the fragment in the entry. Use measured categories only, count overlap
  once, and report command failures/timeouts without conflating them with failed
  mathematical attempts. Keep the per-entry footnote to one short sentence,
  adding only exceptional failures/limitations when needed. The detailed timing
  methodology lives in COMPUTATION_RULES.md; do not repeat the long disclaimer.
- Draft the entry and update the overview before the final timing snapshot;
  then export/embed the table, archive the session, and commit the entry, timing
  fragment, and supporting artifacts. Do not invent or backfill unmeasured times.
- Preserve earlier entries. Correct or retract mathematics in a new dated entry
  referencing the earlier anchor, and update the living overview accordingly.
  Do not silently rewrite prior claims or proofs to agree with a later result.
- Keep current mathematical status in the notebook only. `research/notes/RESUME.md`
  is a stable reading guide; update it only when navigation or workflow changes.
  Supporting notes preserve proofs, provenance, and dated audit evidence, not
  duplicate live summaries. Historical checkpoints remain labeled snapshots.
  After compaction, read all notebook sections before **Research record**, then
  only the latest or relevant entries; do not load the entire growing record.
  Routine setup/admin turns need no mathematical entry.

## Timing and research discipline

- Measure every research turn, including reading/review, preparation, writing,
  tools, computations, failed attempts, and retries. Start as early as practical
  with `./compute.sh start TURN --model "MODEL, reasoning setting"`; disclose
  work preceding instrumentation.
- Follow [the execution and timing policy](COMPUTATION_RULES.md#unified-execution-and-timing)
  for phase marking, protected commands, reports, and honest measurement scope.
- Keep full output on disk and display bounded excerpts. After compaction, read
  the restart note and load exact source passages only as needed.
- Focus routine verification on the mathematics and touched links. Run site or
  rendering checks for layout/tooling changes or a concrete rendering concern;
  ordinary research entries need no repeated builds or full-notebook audits.
- Keep PNG previews and contact sheets local; do not display or attach them in
  the conversation unless the user asks.
- Distinguish working proofs, imported statements, conditional claims, finite
  checks, and open obligations. Match source hypotheses, encodings, and versions.
- Record exact research statements, arguments or obstructions, dependencies,
  degree/parameter accounting, actual tests, and the remaining gap. Use targeted
  falsifying tests and meaningful controls; do not rerun historical suites merely
  to import context or create an impression of verification.
