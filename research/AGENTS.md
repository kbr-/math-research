# Current research workspace

- Follow the root AGENTS.md Git/publication policy on the user's chosen branch,
  including any explicit publication override for the active task.
- Start with `notes/RESUME.md`, then read the initial sections of
  `../notebook.html`, including Working mathematical context. The notebook is the
  single source of truth for current mathematical status; RESUME is navigation
  only. Do not reimport the manuscript or dump large source outputs into context.
- `../php_codex_handoff/` is the immutable historical package. Read selected
  proofs there as needed. All new notes, corrections, tools, logs, reference
  acquisitions, and experiments belong here or elsewhere outside that package.
- Obey `../COMPUTATION_RULES.md`; substantial workloads use `../compute.sh`.
  Use exact finite-field arithmetic and compiled numerical kernels. No package
  installation without explicit user approval.
- Preserve ordinary designs versus PC consequences, original joint-variable
  degree, and the weaker Boolean linear-row PHP encoding without row exclusions.
- Read the notebook for the status of the goal and elimination route. Separate
  working proofs, checked source statements, finite tests, and conjectures.
- Use `../compute.sh` for each research turn, including failed commands.
  Report measured intervals honestly; reading includes interpretation.
- Add supporting evidence or dated audits when needed; do not maintain duplicate
  current-state summaries in notes. Preserve historical reports and snapshots;
  do not rerun archived suites simply to claim verification.
- Record all substantial new mathematics in `../notebook.html`. Keep its three
  overview sections and Working mathematical context current after each research
  turn, and append dated, anchored results/proofs/corrections to its final Research
  record. Consolidate working context by topic instead of adding a subsection
  for every turn; keep exact setup, active tools, and current dependencies there.
  Review it yourself against the root rules' soft target of roughly 1,000 prose
  words, retaining essential mathematical detail even if the target is exceeded.
  The full Research record has no length limit and still gets every research
  turn. Internal notes are supporting records, not a substitute for the notebook.
- Every research turn, including failed attempts and turns with no useful result,
  gets a dated Research-record entry and a measured timing table. Generate the
  table with `../compute.sh report TURN --stop --html-out PATH`; never invent
  categories or elapsed times. Commit the complete checkpoint under the root
  AGENTS.md rules. Archive timing
  and essential output into provenance; ignored scratch files and chat history
  must not be the only copies of research progress.
