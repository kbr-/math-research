# Noemesis research workspace instructions

These are explicit user constraints. Honor later explicit user overrides.

[COMPUTATION_RULES.md](COMPUTATION_RULES.md) owns resource limits, execution,
numerical checks, timing-tool operation and result retention: read it before
computations. All substantial local jobs use `./compute.sh`, sharing at most
14 logical CPUs and 10 GB combined RAM plus swap. Never bypass failed controls,
and install no dependencies or virtual environments without explicit approval.
This file owns research workflow, notebook editing and Git/publication policy.

Keep the framework small: revise/consolidate existing guidance before adding it,
state each rule in one authoritative place and link elsewhere. Remove obsolete
history and repetition while preserving explicit constraints. Prefer actionable
rules to growing checklists or one-off setup narratives.

## Restoration and research discipline

- Restore with `python3 tools/resume.py`, then read its listed bounded parts.
  For Codex resume calls, omit `max_output_tokens` on `exec_command` and omit
  `max_output_tokens` on any enclosing `functions.exec` directive: keep their
  default output allowances for both preparation and part reads.
  The bundle includes `research/notes/RESUME.md`, required rules, notebook living sections/gaps and
  compact contents. Retry missing parts without preparing another resume or concatenating
  the full file into one tool response. Follow the guide without rereading bundled files,
  then load only relevant records. Do not load the growing record or index wholesale.
  Keep `php_codex_handoff/` immutable; its import is complete. New work belongs
  outside it, usually in `research/`. Use targeted source passages.
- On opening a research cycle, name the top-level remaining-route obligation,
  explain how the task tests/discharges it, and set a concrete stopping point.
  Prioritize an unproved obligation needed for the main goal; distinguish a
  sufficient endpoint from stronger conveniences before adding conversion steps.
- Restricted examples must test a named general hypothesis, obstruction or
  mechanism. A growing case list or equivalent reformulation leaves the general
  implication open. State that implication and test it against known obstructions,
  hard instances and allowed equivalent representations before further refinement;
  a surrogate becoming simple need not resolve the original obligation. Check preserved
  hypotheses and accumulated composition costs against the goal's budget.
  If these fail, or repeated cycles leave the same required implication untouched,
  review alternatives and address the failure before refining the same mechanism.
- Distinguish working proofs, imported statements, conditional results, finite
  checks, conjectures and refutations. Match source hypotheses, encodings and
  versions; preserve original joint degrees and exact parameter accounting.
  Record full arguments, actual tests, dependencies and remaining gaps. Use
  meaningful falsifying tests/controls; do not rerun old suites to simulate progress.
- Before proposing a next step or naming/developing a result, use
  `tools/search-claims.py WORDS` or `--show LABEL`. Unfiltered display searches also
  surface up to three historical statement matches. For a generic mechanism, follow
  relevant matches and search the immutable [historical index](php_codex_handoff/manuscript/CLAIM_INDEX.md)
  further when needed; bounded suggestions do not establish absence of prior work.
  Use
  `tools/claim-dependencies.py packet --claim ID` for bounded orientation, or
  `tools/claim-index.py list --fields id,summary --format tsv` for a complete minimal
  inventory when needed. Packets omit proof details and sometimes hypotheses:
  before reliance read the exact statement, proof and applicable corrections.
  Before committing to a direction, inspect the relevant claims' reviewed
  dependencies and correction/refinement links using `claim-index.py graph` and
  exact metadata. Check conditional premises and stronger available versions
  against the proposed argument; follow only dependencies that matter to it.
  Missing edges do not establish independence, and an impact warning is not a
  verdict that a claim is false.
  Label rediscoveries/refinements and link their original records.
- Once the question, argument and evidence are stable, make one focused correctness
  review. Reopen only for a concrete unresolved concern; defer optional extensions.
  Prepare staging paths, commit message and focused metadata checks during review.
  Then run a sequential checkpoint batch: preparation marker, checks, provenance,
  timing export/archive, staging, commit, and any authorized push. Stop on failure;
  finish the local checkpoint before developing the next result.
- Measure every research turn from as early as practical, including reading,
  failed attempts and retries: `./compute.sh start TURN --model "MODEL, reasoning setting"`.
  Disclose work before instrumentation. Follow the computation policy for phase
  markers, protected commands, honest timing scope, numerical accuracy and outputs.
  Keep full output on disk and display bounded excerpts. Focus checks on mathematics
  and touched links; run site/rendering checks only for layout/tool changes or a
  concrete rendering concern. Do not display PNG previews unless requested.

## Notebook and claim metadata

- `notebook.html` owns the main goal; each registered side notebook owns its
  thread's current mathematical state and full record. Select the thread via
  [the side-notebook workflow](tools/SIDE_NOTEBOOKS.md); never replace main
  living sections with a side goal. Edit the selected notebook directly;
  `python3 server.py` serves the live notebook on localhost:8000
  with automatic refresh. `index.html` owns layout. `research/notes/RESUME.md`
  is navigation only: change it for workflow/navigation, not new findings.
  Supporting notes hold evidence, proofs and dated audits, not duplicate living
  summaries. Label historical snapshots; Git already preserves prior overviews.
- After every research turn, review/update **Where we stand**, **The remaining
  route** (highest risk first), **Proposed next step**, and **Working mathematical
  context**. Lead with the selected thread's goal, keep the route/next step on
  its path, and
  mention side publications briefly. Do not invent progress. Keep exact setup,
  degree conventions, linked hypotheses/proofs and unresolved dependencies needed
  next; consolidate by topic/purpose, not by adding a subsection every turn.
- All pre-record regions have [configured budgets](research/context-budgets.json).
  Run `python3 tools/notebook_context.py` while drafting; see
  [counting/enforcement](research/notes/CONTEXT_BUDGET_PLAN.md#budget-operation).
  Soft excess requires your editorial review; any section or aggregate hard excess
  blocks finalization and CI. New sections need budget allocation. Only an explicit
  user override authorizes raising/waiving hard limits; record it transparently.
  Consolidate yourself without asking the user to edit. Preserve essential
  hypotheses/warnings and link full arguments/history in the unlimited record;
  preserve unique substance durably before shortening. Do not duplicate Git snapshots.
- Append a dated Research-record entry for **every research turn**, including
  unsuccessful attempts, obstructions and turns with no useful result. State the
  question/approach, actual outcome and remaining gap honestly; invent no lemma to
  justify an entry. All substantial new mathematics belongs there **in full**;
  supporting notes/chat alone are insufficient. The record has no size limit.
  Routine setup/admin turns need no mathematical entry.
- Use MathJax for inline mathematical notation as well as displayed equations;
  reserve code formatting for program identifiers and source references.
- Give each article a stable anchor, descriptive title/date and explicit status
  (working proof, conditional result, conjecture, finite check, refutation, etc.).
  Include assumptions, precise claim, complete argument, dependencies, parameter/
  degree costs and checks. Keep `<p class="entry-meta">` at most 300 characters
  before the producer credit added from the timing session. Do not number cycles;
  use anchors, and route IDs for parallel formalization entries.
- Tag articles with `data-kind="research|review|formalization"` and `data-route`,
  naming a top-level remaining-route `data-route-item` slug (or `side-...`), never
  a sub-gap. The finisher rejects a seventh consecutive research entry without a
  review. A review states the line's general claim, what the main goal needs,
  a falsification attempt, an evidence-based qualitative assessment of **that line only**, and
  the next step on the highest-risk item. Proposed next step names its route item.
  Explain progress, obstructions and remaining uncertainty; do not invent numerical
  probabilities for research prospects. A probability requires a stated quantitative
  method and evidence, not an uncalibrated impression.
- Keep entries chronological and append-only, including opinions/assessments even
  when the user objects. Withdraw/correct/retract in a new dated entry linking the
  old anchor; update living status and correction metadata. Never silently rewrite
  prior mathematics to match later results. Link repairs alone are allowed.
  `tools/check-append-only.py` checks HEAD at finalization and must pass against
  `origin/main` before a push, unless the user explicitly overrides the check.
- Historical labels link directly to Markdown statement/proof anchors using
  `php_codex_handoff/manuscript/CLAIM_INDEX.md`. Use public GitHub file URLs in the
  notebook so links work locally and on Pages; verify file/anchor locally and read
  local excerpts when available. Mathematical corrections require new entries.
- [research/claims/index.json](research/claims/index.json) owns claim metadata;
  [research/CLAIM_INDEX.md](research/CLAIM_INDEX.md) and topic views are generated.
  Follow the [registry workflow](research/claims/README.md); regenerate with
  `tools/claim-index.py render`. Preserve labels, exact scope and full-record links.
- **Index maintenance:** each new or substantively revised claim needs current
  evidence-backed mathematical status, topics, formalization scope/disposition,
  significance and relationship review. Use the [cheap significance/attention workflow](research/claims/README.md#significance-check-and-attention)
  at each checkpoint; surface new/reopened candidates to the user. Unknowns need a specific pending question
  and next action; do not invent metadata to pass. Record applicable dependencies,
  refinements, corrections and obstructions; refresh affected existing claims.
  `claim-index.py changed --base REV` checks changed scope (HEAD at finalization,
  integration base in CI); untouched backlog remains visible separately.
  New articles declare `data-claims="ID ..."` matching claims sourced there, or
  `data-claims="none"` with a specific `data-claim-note`. Unregistered explicit
  labels and source/inventory mismatches block finalization. Preserve stable IDs
  and dated records; follow the registry editing contract for metadata-only work.
- Read **Gaps identified by formalization** on ordinary restoration too. Its concise
  living list links discrepancies and audit status; full corrections stay in dated
  records. Begin Lean work only under explicit assignment, including an assigned
  parallel formalizer. Then read [formalization/AGENTS.md](formalization/AGENTS.md)
  and its README, not as routine research/Spin reading. Record exact per-claim Lean
  scope and file links, distinguishing partial coverage/stronger hypotheses from
  complete verification. Absence of Lean is not mathematical incompleteness; a
  verified special case does not verify the full informal claim. Use normal research
  evidence, timing and checkpoint rules for formalization.
- During coordinated parallel formalization the coordinator alone edits **all**
  living sections, including formalization gaps, at integration checkpoints.
  Workers review them, append full records, maintain claim metadata and promptly
  send proposed overview changes/discrepancies; do not wait for all workers to finish.
- Draft the entry and overview before the final snapshot. Run the small controller
  `./tools/finish-turn.py TURN` directly, not in the session it stops: it exports
  timing, archives evidence and fills the unique `<!-- TIMING TURN -->` marker.
  For continuous research add `--next NEXT` to start the next clock immediately;
  subsequent checkpoint work is preparation. Each entry ends with a generated
  two-column **Measured category / Elapsed** table and bold total instrumented
  interval (`compute.sh report TURN --stop --html-out PATH`). Use actual measured
  categories, count overlap once, and distinguish tool failures/timeouts from failed
  mathematics. Keep its footnote one short sentence plus exceptional limitations;
  do not repeat the methodology or backfill unmeasured time. Commit the entry,
  fragment, archive and supporting results together.

## Portable sessions, Git and publication

- Work from the repository root without assuming a machine/user/absolute path.
  `start-codex.sh` starts the remote-control daemon; `start-session.sh` and
  `start-claude.sh` resume exact machine-local IDs in `.codex-session-id` or
  `.claude-session-id`, or start context restoration when absent. Only the main
  Codex session explicitly bootstrapped by its launcher runs
  `./tools/remember-codex-session.py`; never overwrite a binding from a worker or
  unrelated session. Claude's launcher binds its own ID. Never commit IDs.
  Clones restore files, not chat history. Private agent memory may hold preferences
  only, never mathematics or research progress.
- Every research turn ends in a local Git commit, including failures/no results.
  Include living sections, full record, sources/provenance, code, reproducibility
  data and complete important outputs per the computation policy. Promote essential
  scratch/runtime results into `research/results/` or `research/provenance/`;
  research must not exist only in ignored files/chat. Do not include unrelated user
  edits; review relevant changes and report commit blockers honestly. Logs,
  credentials, session IDs, binaries, environments and scratch renders stay untracked.
  Every commit-message line must be at most 100 characters; wrap prose and separate
  paragraphs with blank lines.
- Publish only under explicit user authorization, including a still-active scoped/
  time-limited grant. Research/edit/commit requests alone do not authorize it.
  Restore the actual grant after compaction, honor expiry/later overrides and do
  not ask again within authorized scope. Current grant (20 September 2026):
  "You are authorized to git push origin main after each reviewed research or
  framework checkpoint for the full duration of this Spin run, including after
  compaction or session restart." It ends when the user stops Spin or revokes
  permission; restore it with the active assignment. Earlier expired grants are
  preserved in Git, not standing permission.
- Respect the user's branch; do not switch/merge into main just to publish. Pin
  integration targets to immutable commits after fetching/receiving workers, rebase
  and validate against those IDs. Immediately before fast-forwarding check the
  destination HEAD and worktree: if advanced, refresh/rebase or leave unmerged;
  validation against an old target is not validation of a new one.
- Preserve private `pre-publish`; never publish it or use `--all`/`--mirror`.
  Before authorized publication run `tools/verify-checkout.py --public-history BRANCH`
  and the append-only check, unless explicitly overridden by the user. Pages targets
  main only; local commits are checkpoints. The Pages workflow builds HTML/site-tool
  changes with `tools/build_pages.py --out _site`: upload only that minimal artifact,
  never the checkout/private sources. Preserve live mode and project-relative
  published revision URLs.
- Follow LICENSE: original software MIT, original research CC BY 4.0. Preserve
  attribution, cite upstream mathematics and distinguish working from established
  results. Third-party papers are not ours to relicense: follow THIRD_PARTY_NOTICES.md
  and research/references/redistribution.json. Keep uncleared PDFs/full text and
  source-containing diagnostics out of public commits/reachable history; preserve
  needed personal copies locally, never publish private/backups. If retrieval fails
  after an honest attempt, create/update Git-ignored `user_requests` with citation,
  attempted links and purpose; continue independent work while awaiting the user.
