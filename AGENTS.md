# Computation rules

These are explicit user constraints for this workspace and future sessions.

Read [COMPUTATION_RULES.md](COMPUTATION_RULES.md) before running computations.
It is the authoritative computation policy; the rules below summarize it.
When updating the policy, keep this summary consistent with that document.

For mathematical research, start with `research/notes/RESUME.md`, the reading
guide to the authoritative initial sections of `notebook.html`. Keep
`php_codex_handoff/` unchanged as the historical package. New research artifacts
belong in `research/` (or another appropriate directory outside the handoff).
Use targeted source excerpts rather than repeatedly importing the full manuscript.

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
- Computation scripts should provide `--out PATH` (or an equivalent explicit
  output destination) for substantial results. Save complete tables, enumerations,
  certificates, and other research data under `research/results/` or another
  tracked directory. Large output is acceptable; never discard or truncate
  important results just to keep logs or commits small.
- Reference each result file from the research log and, where relevant, the
  notebook entry. Record how it was produced: command, parameters, seed if used,
  encoding/schema, and relevant verification. Commit the output with the result.
  Stream/chunk large computations and file I/O within the shared memory limit;
  bounded terminal previews do not replace complete persisted output.

- Maximum CPU use: 14 of this machine's 16 logical CPUs, shared across jobs.
- Maximum memory budget: 10 GB TOTAL across all simultaneous computation
  processes and their children, never per process. Swap is allowed by the user;
  do not disable system-wide swap. Count RAM plus swap toward the budget.
- Run local computations, numerical checks, builds, and other potentially
  substantial workloads through `./compute.sh COMMAND ...`. All such jobs
  share `mathcompute.slice`. Never bypass a failed resource-limit check.
- The user explicitly requires an arbitrary RAM/swap split. Do NOT set separate
  fixed shares such as 9 GB RAM plus 0.5 GB swap. Cgroup v2 has no native combined
  cap: the installed C watchdog polls workload RAM + swap + watchdog RAM + swap
  every 2 ms and writes cgroup.kill when the total exceeds 10,000,000,000 bytes.
  Separate 10 GB RAM and 10 GB swap caps are only backstops; the watchdog is
  required to enforce the combined budget. Brief overshoot is acceptable to the
  user (they explicitly mentioned 10.5 GB); monitoring has no strict latency or
  overshoot guarantee. Plan allocations below the limit, including temporaries.
- Each job's CPU affinity is restricted to CPUs 0-13 and verified before execution.
  This host delegates memory/pids only; slice CPUQuota/AllowedCPUs are NOT enforced
  here. The control shell/Codex/browser are outside the computation group.
- `./compute.sh --status` verifies the active limits. If initialization is
  needed, run `python3 resource-controls/setup.py` (or the setup.sh shim) with the
  necessary system access. This self-contained, idempotent script recreates all
  units, compiles the embedded watchdog using the existing C compiler, starts it,
  and verifies readiness. Rerun after reboot/login; it refuses to reconfigure
  while computation jobs are running. Respect tool escalation requirements:
  the user systemd manager is inaccessible inside the Codex sandbox.
- Jobs require the watchdog service. On watchdog failure/stop, systemd stops its
  dependent jobs and ExecStopPost kills the whole computation group. Never bypass
  these dependencies. Do not run numerical work if the watchdog is unavailable.
- Use compiled numerical implementations (NumPy, SciPy, BLAS, etc.) for heavy
  computation. No Python inner loops or heavy numerical logic in pure Python.
  Vectorize where appropriate, but chunk operations when full vectorization
  would create large temporaries. Python orchestration is fine.
- Avoid process/thread oversubscription. For 14 worker processes, use
  `./compute.sh --threads 1 ...`; otherwise budget worker count times BLAS
  threads within 14. All concurrent launcher invocations share the same cap.
  Do not change CPU affinity or escape the cgroup from within a workload.
- Install no libraries or dependencies without the user's explicit approval.
  Inform the user when something needed is missing. No virtual environment or
  package installation has yet been authorized/created.
- Publish substantial new mathematics in the live notebook, following the rules below.

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
  current definitions, reusable bounds, controls, source matches, and obligations.
  Keep the overview concise and accurate; do not invent progress when the
  mathematical status has not changed.
- Append an entry for **every research turn** to the notebook's final **Research
  record**, even if it produces no useful result, only an obstruction, or a failed
  proof attempt. Describe the question/approach, actual outcome, and remaining gap
  honestly; do not manufacture a lemma to justify an entry. Publish all substantial
  new mathematics there in full. Supporting notes or chat alone are insufficient.
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
- Mark phases using `./compute.sh phase TURN reading` or the appropriate category.
  Bracket external browsing/tool windows with phase changes.
- Run commands with `./compute.sh run TURN --threads N -- COMMAND ...` to enforce
  limits and log execution together. There is no unprotected timed-run mode.
  `./compute.sh COMMAND ...` also records timing in a standalone session.
- End with `./compute.sh report TURN --stop`; report measured elapsed time,
  relevant categories, and failures. Count overlapping worker intervals once.
  Reading includes interpretation; tool windows include orchestration. Never
  claim pure reasoning time, pure network latency, or unmeasured end-to-end time.
- Keep full output on disk and display bounded excerpts. After compaction, read
  the restart note and load exact source passages only as needed.
- Distinguish working proofs, imported statements, conditional claims, finite
  checks, and open obligations. Match source hypotheses, encodings, and versions.
- Record exact research statements, arguments or obstructions, dependencies,
  degree/parameter accounting, actual tests, and the remaining gap. Use targeted
  falsifying tests and meaningful controls; do not rerun historical suites merely
  to import context or create an impression of verification.
