# Current research workspace

- Start with `notes/RESUME.md`; it is the compact restart map. Do not reimport
  the entire manuscript or dump large reference/search outputs into context.
- `../php_codex_handoff/` is the immutable historical package. Read selected
  proofs there as needed. All new notes, corrections, tools, logs, reference
  acquisitions, and experiments belong here or elsewhere outside that package.
- Obey `../COMPUTATION_RULES.md`; substantial workloads use `../compute.sh`.
  Use exact finite-field arithmetic and compiled numerical kernels. No package
  installation without explicit user approval.
- Preserve ordinary designs versus PC consequences, original joint-variable
  degree, and the weaker Boolean linear-row PHP encoding without row exclusions.
- The final Frege lower bound and affordable global elimination remain open.
  Separate working proofs, checked source statements, finite tests, and conjectures.
- Use `../compute.sh` for each research turn, including failed commands.
  Report measured intervals honestly; reading includes interpretation.
- Update the current notes and status ledger. Do not rewrite historical reports
  or rerun the archived suites simply to claim verification.
- Publish all substantial new mathematics in `../notebook.html`. Keep its three
  overview sections current after every research turn, and append dated, anchored
  results/proofs/corrections to its final Research record. Follow the root
  AGENTS.md notebook rules; internal notes are supporting records, not a substitute.
- Every research turn, including failed attempts and turns with no useful result,
  gets a dated Research-record entry and a measured timing table. Generate the
  table with `../compute.sh report TURN --stop --html-out PATH`; never invent
  categories or elapsed times. Commit the complete checkpoint under the root
  AGENTS.md rules. Archive timing
  and essential output into provenance; ignored scratch files and chat history
  must not be the only copies of research progress.
