# Resume here after compaction

**Read this guide fully, then read the initial sections of
[notebook.html](../../notebook.html).** The notebook is the single source of truth
for the current mathematical state. This file is a stable reading map, not a
second research summary. Change it only when navigation or workflow changes.

## Restart checklist

1. Read the current user request and the root and `research/AGENTS.md` rules.
   Before computations, read [COMPUTATION_RULES.md](../../COMPUTATION_RULES.md),
   verify `./compute.sh --status`, and initialize the controls after reboot if
   needed. Start research timing as early as practical, including context reading;
   follow the policy for phases, protected jobs, evidence, and timing tables.
2. Read the notebook from its beginning up to the **Research record**:
   **Where we stand**, **The remaining route**, **Proposed next step**, and
   **Working mathematical context**. The last section contains the exact objects,
   working degree bounds, controls, source matches, and unresolved obligations
   formerly stored here. From the repository root:

   ```bash
   sed -n '1,/<section id="research-record">/p' notebook.html
   ```

3. Scan record titles and stable anchors, then read only the latest or relevant
   entries. Do not load the entire growing record:

   ```bash
   rg -n '<article|<h3>|class="entry-meta"' notebook.html | tail -n 30
   ```

   Select line ranges with `sed -n 'START,ENDp' notebook.html`. Follow explicit
   correction/retraction links before relying on an earlier result.
4. Load exact definitions, hypotheses, proofs, or source passages only as needed.
   Use the source map below; do not repeat the full manuscript/reference import
   or rerun historical suites merely to establish context.
5. After each research turn, update the notebook's living sections and append
   the complete result or failed attempt, with its measured timing table. Archive
   evidence and commit the related checkpoint locally under the root rules.
   **All pushes and public publication belong to the user.** Routine setup/admin
   turns do not require a mathematical entry. Do not maintain a duplicate current
   mathematical summary in this file or the supporting notes.

## Source and evidence map

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
