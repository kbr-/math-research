# Research workspace instructions

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

- Commit research checkpoints locally, but **leave every Git push and public
  publication to the user**. Do not push branches/tags, trigger public deployments,
  publish releases, or upload research publicly. A request to research, edit, or
  commit is not permission to publish.
- Respect the user's chosen research branch. Do not switch or merge into main
  merely to publish work. The Pages workflow deploys when the user pushes main;
  local commits on any branch are only checkpoints.
- Work from the repository root; do not assume a particular absolute path, user,
  or machine. `./start-codex.sh` resumes the exact machine-local ID stored in
  `.codex-session-id`, or starts a fresh context-restoration session if absent.
- On a fresh session explicitly started by this launcher, the main assistant runs
  `./tools/remember-codex-session.py` to bind its current CODEX_THREAD_ID. Do not
  overwrite this binding from subagents or unrelated sessions. Never commit it.
  A clone restores research from files, not from another machine's chat history.
- At the end of every research turn, including an unsuccessful attempt or a turn
  with no useful mathematical result, append a Research-record entry and create
  a Git commit. Include the notebook living sections, supporting evidence,
  source provenance, code, and reproducibility data. RESUME changes only when
  navigation or workflow changes.
- Before committing, finish the timing report and run
  `./tools/archive-session.py TURN` to preserve its evidence outside ignored logs.
  Promote other essential results from scratch/runtime directories into
  `research/results/` or `research/provenance/`. Research must never exist only
  in ignored files or the chat transcript.
- Review and stage the relevant changes, then use a meaningful commit message
  describing the mathematical result or correction. Do not silently include
  unrelated user edits. If committing fails, report the blocker; do not claim
  that the result is checkpointed. Operational logs, credentials, local session
  IDs, generated binaries, virtual environments, and scratch renders stay untracked.
- Keep every commit-message line, including the subject and body, at most
  100 characters wide. Wrap prose manually and separate paragraphs with blank lines.
- Preserve complete computation outputs and reproduction metadata under
  [the output policy](COMPUTATION_RULES.md#persist-computation-outputs).
  Reference the files from the research log and relevant notebook entry, and
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
- Preserve the user's private `pre-publish` backup branch. Never publish that
  backup or use `--all`/`--mirror`. When preparing a branch for the user's
  publication, check it with `tools/verify-checkout.py --public-history BRANCH`.
  The user chooses what to publish; the current Pages workflow targets main only.

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
  mathematical status has not changed.
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
  stable HTML anchor, and explicit status (working proof, conditional result,
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
  Link corrections or retractions to their new dated entries.
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
  with `./compute.sh start TURN`; disclose work preceding instrumentation.
- Follow [the execution and timing policy](COMPUTATION_RULES.md#unified-execution-and-timing)
  for phase marking, protected commands, reports, and honest measurement scope.
- Keep full output on disk and display bounded excerpts. After compaction, read
  the restart note and load exact source passages only as needed.
- Focus routine verification on the mathematics and touched links. Run site or
  rendering checks for layout/tooling changes or a concrete rendering concern;
  ordinary research entries need no repeated builds or full-notebook audits.
- Distinguish working proofs, imported statements, conditional claims, finite
  checks, and open obligations. Match source hypotheses, encodings, and versions.
- Record exact research statements, arguments or obstructions, dependencies,
  degree/parameter accounting, actual tests, and the remaining gap. Use targeted
  falsifying tests and meaningful controls; do not rerun historical suites merely
  to import context or create an impression of verification.
