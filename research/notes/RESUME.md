# Resume here after compaction

**Read this guide fully, then read the initial sections of
[notebook.html](../../notebook.html).** The notebook is the single source of truth
for the current mathematical state. This file is a stable reading map, not a
second research summary. Change it only when navigation or workflow changes.

**The handoff import is complete.** The notebook's **Before this notebook**
section is historical context only, not a reading assignment. Do not open or
follow `php_codex_handoff/HANDOFF.md` during resume, including on a fresh clone,
and do not repeat its one-off bootstrap/import instructions. Read selected
historical mathematical sources only when the current research task needs them.

## Restart checklist

1. Read the current user request and the root and `research/AGENTS.md` rules.
   If the request is only to restore context, complete the reading below, report
   readiness, and stop. Do not begin a research attempt, create a timing session
   or notebook entry, or rerun verification merely for context restoration.
   If research is requested or already underway, restore context and continue it;
   compaction alone is not a reason to stop an authorized task.
   For active Spin, also restore the standing publication authorization recorded
   in the root AGENTS.md Git policy, subject to any later user changes.
   Before computations, read [COMPUTATION_RULES.md](../../COMPUTATION_RULES.md),
   verify `./compute.sh --status`, and initialize the controls after reboot if
   needed. For research turns, start timing as early as practical, including
   necessary context reading; follow the policy for phases, protected jobs,
   evidence, and timing tables. Do not backfill a separate restoration turn's time.
2. Read the notebook from its beginning up to the **Research record**:
   **Where we stand**, **The remaining route**, **Proposed next step**, and
   **Working mathematical context**. The last section is an orientation map of
   the exact setup and degree conventions, active tools with linked hypotheses
   and proofs, and unresolved dependencies. It is organized by topic, not as a
   catalogue of every past turn. From the repository root:

   ```bash
   sed -n '1,/<section id="research-record">/p' notebook.html
   ```

3. Scan record titles and stable anchors, then read mathematical entries relevant
   to the current task or needed to understand the latest mathematical status.
   Skip administrative/workflow entries unless the task needs them; recency alone
   does not make an entry necessary. Do not load the entire growing record:

   ```bash
   rg -n '<article|<h3>|class="entry-meta"' notebook.html | tail -n 30
   ```

   Select line ranges with `sed -n 'START,ENDp' notebook.html`. Follow explicit
   correction/retraction links before relying on an earlier result.
4. Distinguish orientation from proof readiness. The notebook restores enough
   context to identify the next action; its summaries do not replace exact proofs.
   Before extending or composing a theorem, read its precise hypotheses and the
   relevant argument, including degree conventions and dependencies. Load only
   the passages needed for that task using the source map below. Do not repeat
   the full manuscript/reference import or rerun historical suites merely to
   establish context. Restoring an audit summary is not a new source verification.
5. After each research turn, update the notebook's living sections and append
   the complete result or failed attempt, with its measured timing table. Archive
   evidence and commit the related checkpoint locally under the root rules.
   Follow the root publication policy, including explicit user overrides. Routine setup/admin
   turns do not require a mathematical entry. Do not maintain a duplicate current
   mathematical summary in this file or the supporting notes.
   Revise and consolidate **Working mathematical context** rather than adding a
   subsection there for every turn. Review it yourself against a soft target of
   roughly 1,000 prose words, with no user review or approval needed for routine
   consolidation. Link to full records for arguments, failed approaches, testing,
   and reading history. Preserve necessary definitions, hypotheses, degree bounds,
   and gaps even if they need more space. Every research turn still gets its full
   append-only Research-record entry, with no word limit. Condensing working
   context must never erase the underlying result or evidence.

## Source and evidence map

- New claims: [continued-research index](../CLAIM_INDEX.md) locates full notebook
  statements, proofs, and obstructions by stable label. Use it for targeted lookup.

- Historical proofs: [claim index](../../php_codex_handoff/manuscript/CLAIM_INDEX.md)
  and selected records of `php_codex_handoff/manuscript/claims.json` locate the
  original chapters and TeX. Preserve the handoff unchanged; new work belongs
  outside it. Do not read the separately supplied compendium PDF.
- Source verification: [SOURCE_AUDIT.md](SOURCE_AUDIT.md) and
  [IMPORT_LOG.md](IMPORT_LOG.md) preserve exact locators, coverage, and limitations.
  Check [reference availability](../references/README.md) and redistribution
  metadata before access: some PDFs/full text do not travel with a public clone.
- Supporting evidence: [RESEARCH_LOG.md](RESEARCH_LOG.md),
  `research/results/`, and `research/provenance/`. Historical import snapshots
  [MATHEMATICAL_CHECKPOINT.md](MATHEMATICAL_CHECKPOINT.md) and
  [STATUS_AND_AUDIT.md](STATUS_AND_AUDIT.md) are not live status summaries.
  Consult their dated audit details as needed; the notebook carries current status
  and later corrections. A conflict is an audit issue to resolve from the exact
  evidence, not permission to silently rewrite history.
- Setup and portable sessions: [README.md](../../README.md). Work from the
  checkout root using relative paths. Only a main session explicitly bootstrapped
  by the launcher should bind its local session ID; never bind an unrelated chat
  or subagent. Durable research must remain in committed files, not chat history
  or ignored runtime directories.
