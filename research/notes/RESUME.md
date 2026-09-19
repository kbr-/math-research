# Resume here after compaction

Read this guide fully. **The notebook is the single source of truth for current
mathematics.** This file is a stable reading map, not a second status summary.
The handoff import is complete: **do not read HANDOFF.md or the compendium PDF**
on resume, even in a fresh clone. “Before this notebook” is historical context.

## Restart checklist

1. Restore the current user task and root/scoped AGENTS instructions. If asked only
   to restore context, read and report readiness; do not start research, timing or
   verification. If authorized work is underway, continue it after restoration.
   For coordinated work, restore assignments, immutable integration checkpoints
   and worker status before editing. Restore any actual publication grant and its
   expiry; compaction neither revokes nor renews authorization. Only an explicitly
   bootstrapped main Codex session binds its local session ID; never bind a worker.
2. For an active research cycle, restore/start timing as early as practical under
   [COMPUTATION_RULES.md](../../COMPUTATION_RULES.md), including required reading;
   do not invent time for earlier restoration. Before computations check
   `./compute.sh --status` and initialize controls after reboot if needed. Work
   from the repository root; no dependency installation without authorization.
3. Read **all content before Research record**, including formalization gaps:

   ```bash
   ./tools/notebook-excerpt.py --current
   ```

   This supplies the goal, highest-risk route, next step, exact working conventions
   and active warnings. Its summaries orient; they do not replace proof reading.
4. Scan compact record titles, then read relevant entries, not the whole record:

   ```bash
   ./tools/notebook-excerpt.py --toc
   ./tools/notebook-excerpt.py --toc --tail 20 --since 2026-09-01
   ./tools/notebook-excerpt.py ANCHOR
   ```

   TOC defaults to the latest ten entries and reports omissions. Dates come from
   stable entry IDs; undated entries remain visible. Exact heading excerpts stop
   at the next peer/enclosing boundary; articles include their full record.
   `--until END_ANCHOR` validates both boundaries; `--out PATH` saves a new file.
   Recency alone does not make administrative entries necessary reading.
5. Before mathematical reliance, read exact hypotheses, proof, encoding, original
   degree conventions and applicable corrections. Before proposing/naming a result,
   search for existing versions. Reuse saved verification evidence without calling
   that a fresh verification. Do not rerun old suites solely to restore context.
6. Follow the root research-turn, index-maintenance and local-checkpoint rules.
   Keep every research turn's full record and evidence; consolidate living sections
   yourself under the shared hard budgets. `python3 tools/notebook_context.py`
   reports counts. Preserve essential mathematics via exact links, not by dropping
   qualifications. Change this guide only when navigation/workflow changes.

## Bounded claim and source navigation

- `tools/search-claims.py WORDS` ranks bounded results; `--show LABEL` exposes
  complete metadata and links. `tools/claim-dependencies.py packet --claim ID`
  gives selected evidence and limitations, **not proof readiness**.
- If all claims are needed, use `tools/claim-index.py list --fields id,summary
  --format tsv`; never load the whole registry by default. The generated
  [topic map](../claims/views/topics.md) groups claims. `claim-index.py graph`
  offers dependencies/citations/impact; impact is review scope, not invalidity.
- `claim-index.py coverage` exposes pending/stale reviews; `changed --base REV`
  checks changed scope. The [registry workflow](../claims/README.md) explains
  authoring templates, five-field dispositions, typed edges and explicit article
  inventories. Edit structured metadata, then `claim-index.py render`; Markdown
  and topic views are generated. Unknowns need specific questions and next actions.
- Historical claims: use selected local Markdown passages via the immutable
  [historical claim index](../../php_codex_handoff/manuscript/CLAIM_INDEX.md).
  [SOURCE_AUDIT.md](SOURCE_AUDIT.md) and [IMPORT_LOG.md](IMPORT_LOG.md) preserve
  provenance and limitations. Check [reference availability](../references/README.md)
  and redistribution policy; private full text does not travel with a public clone.
- Formalization: only when explicitly assigned, read the [Lean guide](../../formalization/README.md)
  and [formalization rules](../../formalization/AGENTS.md). Ordinary research still
  reads notebook formalization gaps. Preserve exact verified scope, not just links.
- Supporting evidence lives in `research/results/` and `research/provenance/`.
  Older checkpoint notes and Git revisions are historical snapshots, not current
  summaries. Resolve conflicts against exact records; do not silently rewrite them.
  Use the assigned plan's durable progress/evidence for interrupted work; the
  [workflow-utilities plan](WORKFLOW_UTILITIES_PLAN.md) owns any future generic
  interruption-note mechanism. This guide creates no competing recovery store.
- [README.md](../../README.md) owns portable setup. A clone restores research from
  files, not machine-local chat history or private agent memory. Private memory
  may hold preferences only, never mathematical state or progress.
