# Claim index and research-framework implementation checklist

This is the implementation plan for the claim index and all related proposals in
[IDEAS.md](../../IDEAS.md), including the subsequent conversation. Begin with
the index, then populate its metadata, and build the dependent workflows on it.
The full plan is not complete merely because the original table was converted.

The structured index will be authoritative for claim metadata; the notebook
remains authoritative for mathematical statements, proofs, and current research
status. Preserve the historical handoff unchanged.

Mark tasks complete only after implementation and validation. Record concrete
paths, decisions, and checkpoint references here as work proceeds. Leave partial
tasks unchecked and briefly note what remains.

## Scope and completion discipline

- Sections 1–5 record the completed **structural migration**. They do not certify
  that formalization, significance, topics, or relationships have been populated.
- Sections 6–17 are pending implementation. Nothing formerly called deferred work
  is silently outside this plan. Alternative proposals have explicit decision tasks.
- Account for every claim and entry, not just a convenient sample. Use resumable
  coverage records so batches survive compaction and newly added claims are picked up.
- `null`, an empty list, and "not reviewed" are not evidence of absence. After
  review, distinguish no applicable data from an unresolved question; retain its
  reason, evidence, and next action. An unresolved task stays open.
- A proposal may be rejected or replaced only with a recorded decision and reason;
  do not check an unimplemented feature off as if it had been delivered.
- The notebook remains the mathematical source. These tasks do not authorize
  silent changes to historical entries, public pushes, or automatic research,
  parallel-agent, or formalization runs beyond their assigned scope.

### Coverage map

| Proposal | Implementation sections |
|---|---|
| IDEAS 1: incremental Fossick | 10–11 |
| IDEAS 2: significance flags and user attention | 10–11 |
| IDEAS 3: parallel exploration and adversarial review | 13 |
| IDEAS 4: formalize the record and maintain the verified frontier | 7, 14 |
| IDEAS 5: structured index, curation, grouping, retrieval | 1–9, 12 |
| IDEAS 6: interruption notes and open-problem map | 10, 12 |
| IDEAS 7: context costs, compact views, rule consolidation | 8, 12 |
| IDEAS 8: typed claim graph and public visualization | 9, 15 |
| Conversation: complete population, not just empty schema fields | 6–10, 16 |
| Conversation: every subsequent research cycle maintains complete metadata | 17 |
| Conversation: preserve contents and fix broken Markdown table | 2–4, completed |

## 1. Inventory and schema

- [x] Pin the pre-migration Git revision and inventory every row, label, link,
      status qualification, and formalization reference in `research/CLAIM_INDEX.md`.
- [x] Identify tools and instructions that read or edit the current Markdown index.
- [x] Choose and document the structured file location and schema version.
- [x] Define claim records with stable IDs preserving existing labels, statement
      summaries, mathematical status, source links, formalization coverage, and
      optional topics. Preserve exact legacy text where structured fields alone
      would lose qualifications.
- [x] Keep mathematical status, formal verification, and significance distinct;
      represent missing or unreviewed information explicitly without guessing it.
- [x] Define graph-ready relationship records: source and target IDs, type,
      supporting source location, and review status. Support `depends_on`,
      `refines`, `corrects`, `supersedes`, and other justified relationship types.
- [x] Specify how references to historical claims and external sources are
      represented without modifying or absorbing the historical handoff index.

## 2. Complete structural migration

- [x] Implement a reproducible importer with an explicit output destination and
      diagnostics for ambiguous or unparsed rows; do not silently drop content.
- [x] Convert every existing continued-research claim into the structured source.
- [x] Preserve every original label, summary, status qualification, link, and
      formalization scope; resolve parsing ambiguities against the original row.
- [x] Preserve existing ordering and grouping where applicable, without merging,
      renaming, or reclassifying mathematical claims during conversion.
- [x] Retain citations as citations. Leave dependency edges unreviewed or absent
      unless their type is supported by the record; a hyperlink alone is not a
      proof dependency.

## 3. Generated index and compact retrieval

- [x] Generate `research/CLAIM_INDEX.md` deterministically from the structured
      source, preserving usable public links and existing reference targets.
- [x] Clearly mark the Markdown as generated and document the authoritative edit path.
- [x] Adapt `tools/search-claims.py` to query the structured source and return
      bounded results containing the claim ID, concise summary, status, and source.
- [x] Add exact-label lookup that exposes the complete claim metadata and links
      to the relevant notebook statement or proof without loading the full index.
- [x] Support useful filters where metadata is available; make omitted results
      and unknown fields visible. Do not require a complete topic taxonomy first.
- [x] Provide a stable machine-readable lookup/export interface for later Fossick
      and graph tools, without building those tools in this migration.

## 4. Validation and regression coverage

- [x] Produce a migration reconciliation report against the pinned original:
      every row and label accounted for, all source text and links preserved,
      and any normalization or exception explicitly documented.
- [x] Validate unique IDs, required fields, schema versions, and relationship
      endpoints; preserve distinctions between unknown and verified metadata.
- [x] Check repository-local files and notebook anchors, and preserve external
      destinations without treating their availability as proof verification.
- [x] Verify deterministic generation and add a check that detects stale generated
      Markdown relative to the structured source.
- [x] Test meaningful retrieval and migration cases, including qualified or partial
      formalizations, multiple links, corrections, unusual table syntax, and
      malformed records. Ensure searches still find representative known claims.
- [x] Confirm graph consumers can distinguish citations from reviewed dependencies
      and that missing edges do not imply mathematical independence.

## 5. Structural workflow integration and completion

- [x] Update affected tools and concise workspace guidance to use the structured
      source; consolidate existing rules rather than adding duplicate instructions.
- [x] Update the resume reading guide only where navigation changes, keeping full
      index loading out of routine context restoration.
- [x] Document how to add or revise a claim, regenerate views, and validate changes.
- [x] Preserve conversion tooling, reconciliation evidence, and essential outputs
      in the repository. Follow the computation policy for substantial jobs.
- [x] Review and commit coherent implementation checkpoints locally, updating this
      checklist after each. Publishing remains subject to explicit authorization.
- [x] Confirm the structural migration is complete: structured source authoritative,
      Markdown generated, retrieval working, validation passing, and no unresolved
      loss of original index content.

## 6. Complete metadata inventory and review tracking

- [ ] Pin the enrichment baseline and report population of every field. The first
      migration has 866 claims, all new classifications/significance null, all
      topics empty, and zero relationships; preserve this as the starting snapshot.
- [ ] Define field-level review metadata: reviewed source revision/anchor, review
      date or checkpoint, disposition, evidence, and unresolved work. Avoid a
      single "reviewed" flag that conceals untouched fields.
- [ ] Inventory every claim against its full source, including later corrections,
      formalization records, and publication records. Extract explicit information
      first; mark interpretations requiring mathematical review separately.
- [ ] Version and migrate the schema as needed for richer formalization,
      significance, topics, relationships, and review provenance; update exporters,
      generated views, merge support, validators, and tests together.
- [ ] Add bounded commands/reports for missing fields, pending reviews, stale
      reviews, broken references, and coverage by field/topic. Include all claims
      added or corrected while the enrichment pass is in progress.
- [ ] Establish one authoritative home for each fact and queue. Generate views
      instead of duplicating editable status across registry, flags and scan files.

## 7. Populate existing formalization coverage for every claim

- [ ] Inventory all per-claim Lean files, declarations, route maps, verification
      reports and notebook formalization entries; map them to stable claim IDs.
- [ ] Populate structured formalization records wherever coverage is already
      explicit, including source links and exact scope. Do not leave known
      complete or partial coverage null merely to avoid semantic extraction.
- [ ] Distinguish full verification, partial verification, stronger hypotheses,
      statement-only specification, failed/discrepant formalization, and no
      recorded formalization; record evidence for the classification.
- [ ] Support multiple formalization artifacts/scopes for one claim and shared
      supporting files without implying that a filename verifies every conclusion.
- [ ] Resolve mixed cases such as `lem:mp-telescoping`: preserve the verified
      identity/bounds, the refuted equality, and the downstream audit limitation.
- [ ] Populate the Res(⊕) bit-PHP publication theorem, exponential corollary and
      dependency route from their existing records, retaining both rule conventions
      and exact parameter/encoding scope.
- [ ] Audit consistency between informal scope, structured coverage, Lean links
      and recorded verification evidence. Distinguish inspecting existing evidence
      from performing a fresh kernel replay.
- [ ] Complete a coverage report for the entire index: every claim has a reviewed
      formalization disposition or a specifically recorded unresolved item.

## 8. Mathematical status, topics, compression and deduplication

- [ ] Populate mathematical status independently of formalization and significance:
      working proof, established/imported result, conditional result, conjecture,
      finite check, refutation, correction/retraction, or contextual record as appropriate.
- [ ] Define a small reusable topic taxonomy with descriptions and stable IDs;
      allow multiple topics per claim. Separate topic, object/proof system, and
      current-route membership where those distinctions are useful.
- [ ] Assign topics across all claims, resolving ambiguous and uncategorized cases
      explicitly rather than leaving an unexamined tail.
- [ ] Generate a compact topic map and topic-specific index views; choose their
      layout without creating a second editable source or breaking existing links.
- [ ] Run similarity-based duplicate discovery as a review aid. Check hypotheses,
      encodings, quantifiers and costs before classifying any pair.
- [ ] Record true duplicates, rediscoveries, refinements, supersessions and
      corrections with stable-label relationships. Do not delete or conflate claims
      because their wording is similar.
- [ ] Provide active and historical/retracted views, retaining lookup of every old
      label and visible correction warnings. A parked result remains discoverable.
- [ ] Compress generated display text and links where useful while retaining full
      exact scope through lookup. Ensure links work on GitHub, locally and on Pages;
      a bare notebook anchor in a Markdown file is not automatically a valid link.

## 9. Populate and audit the relationship graph

- [ ] Extract candidate citations from the entire Research record and claim source
      passages, mapping entry anchors to claims without assigning an entry's every
      citation to every claim in that entry.
- [ ] Review every claim's direct proof dependencies from the actual argument;
      do not populate only the publication or active frontier and call the graph complete.
- [ ] Populate `depends_on`, `cites`, `refines`, `supersedes`, `corrects`,
      `rediscovers`, `formalizes`, `applies`, and `obstructs` wherever justified;
      define direction and meaning consistently and preserve evidence locators.
- [ ] Distinguish required dependencies from alternative proofs, contextual
      citations, tests and counterexamples. Record scope/conditions where an edge
      applies to only part of a claim or one proof.
- [ ] Resolve historical and external endpoints through stable identities and
      locators, leaving the immutable handoff untouched. Decide how entry, method,
      Lean-artifact and publication nodes are represented when they are not claims.
- [ ] Seed reviewed edges with the documented publication dependency route and
      active tools, then continue through the complete index with coverage tracking.
- [ ] Mark pending edge reviews and claims whose dependencies have been inspected
      but found empty. Do not conflate either case with unexplored dependencies.
- [ ] Validate endpoints, duplicate/conflicting edges, self-links, and cycles;
      distinguish genuine circular proof dependencies from harmless cycles of citation.
- [ ] Add predecessor/successor, ancestor/descendant, "what cites this", and
      correction-impact queries. Report that impact is an audit scope, not a proof
      that every descendant is invalidated.

## 10. Significance, publication candidates and field benchmarks

- [ ] Define structured significance assessments with rationale, exact scope,
      novelty status, source evidence, review date and suggested action. Keep
      independent interest, novelty, correctness and publication readiness separate.
- [ ] Populate the known Res(⊕) publication result and its corollaries first, using
      the recorded literature/dependency audits and current external-review status;
      do not leave them null or promote an internal assessment to external confirmation.
- [ ] Screen every remaining claim for independent interest, reusable tools,
      meaningful negative results and corrected published claims. Include finite
      checks and failed attempts that expose valuable counterexamples.
- [ ] Perform targeted literature checks for plausible candidates, preserving
      exact formulations, encodings, versions, dates, uncertainty and source links.
- [ ] Create a maintained open-problem/benchmark map, including the systems and
      formulations named in IDEAS.md. Record last verification and link candidates
      to it; it guides searches rather than replacing current literature review.
- [ ] Consolidate candidates and user-attention flags into one authoritative
      register with pending/reviewed/actioned/dismissed states and recorded reasons.
      Resolve the original `NUGGETS.md`/`FLAGS.md` alternatives through generated
      views rather than independent editable queues.
- [ ] Provide a concise "Results of independent interest" overview linked to the
      register, without turning the living notebook into another result catalogue.
- [ ] Complete significance coverage for all claims: a reasoned disposition or an
      explicit pending novelty/audit question, not unexplained nulls.

## 11. Fossick, per-turn significance checks and notifications

- [ ] Add a Fossick prompt and bounded scan command using the structured index and
      compact notebook navigation; open full arguments for candidate assessment.
- [ ] Persist a portable scan cursor and review revision. Track "screened through"
      separately from unresolved candidates, and revisit corrections, changed claims
      and newly recognized dependencies behind the cursor.
- [ ] Run the initial complete historical scan, recording dispositions and pending
      audits. Do not stop at implementing the command without using it on the backlog.
- [ ] Add a cheap per-research-turn significance question and candidate flagging;
      reserve literature audits for plausible candidates instead of every lemma.
- [ ] Make pending items visible on resume and at checkpoints, with user attention
      and acknowledgments tracked without deleting the historical assessment.
- [ ] Evaluate local notifications for the actual supported Codex and Claude
      environments, including the proposed Stop-hook approach. Implement a bounded
      optional notifier or document an explicit decision and reliable file/UI fallback.
- [ ] Test interrupted scans, repeated scans, cursor drift, newly corrected old
      entries, duplicate candidate detection, and avoidance of repeated alerts.

## 12. Context restoration, retrieval and interruption recovery

- [ ] Measure actual mandatory restoration output and representative claim lookups;
      distinguish byte/word counts, token estimates and measured token accounting.
- [ ] Extend the existing notebook excerpt tool with compact TOC output, default
      bounded tail, `--tail N` and `--since DATE`; avoid a second notebook parser.
- [ ] Consolidate **Where we stand**, **The remaining route**, and **Working
      mathematical context** by current obligation rather than chronology, preserving
      exact hypotheses, costs, unresolved gaps and links to complete records.
- [ ] Consolidate AGENTS and related instructions: retain every current user
      constraint once, remove duplication, and move expired authorization history
      out of mandatory context without accidentally renewing permission.
- [ ] Update Resume to use the compact overview, TOC, topic map and exact claim
      lookup, loading full entries only as needed and retaining the gaps section.
- [ ] Settle and implement a lightweight maintenance trigger for living-section
      growth, revising the existing finisher warning rather than adding competing
      checklists. Keep historical entries append-only and unabridged.
- [ ] Provide a small durable work-in-progress note for long/interrupted tasks:
      exact question, completed steps, unresolved concern, evidence paths and next
      action. Define its checkpoint incorporation/retirement so it is not a second
      live mathematical summary or private memory store.
- [ ] Validate restoration on representative paused tasks and compare its output
      cost and ability to recover the needed definitions/dependencies with the baseline.

## 13. Bounded parallel exploration and adversarial review

- [ ] Define an Explore prompt with distinct obligations/mechanisms, shared
      interfaces, concrete stopping points and an explicit coordinator role.
- [ ] Define an Adversary prompt giving a reviewer the precise statement and
      assumptions without relying on the author's persuasive narrative.
- [ ] Reuse isolated worktrees, pinned integration revisions, shared resource
      controls and append-only merging; extend integration where the new claim
      metadata/edge updates require reviewed conflict resolution.
- [ ] Specify coordinator-only living-section ownership and worker ownership of
      source records/evidence, with prompt communication of discrepancies.
- [ ] Preserve all branches' useful results, failures and obstructions; select
      the next research action without discarding the other records.
- [ ] Budget aggregate memory, CPUs, token use and duplicated restoration work.
      Choose concurrency from current headroom and workload, not historical estimates.
- [ ] When parallel research is explicitly assigned, pilot two bounded workers,
      record integration and context costs, and adjust before scaling up.

## 14. Formalization backlog and ongoing policy

- [ ] Inventory formalizable statements across the whole record, including
      negative results, supporting lemmas and finite certificates. Distinguish them
      from conjectures, abandoned arguments and prose that cannot be treated as proofs.
- [ ] Build the dependency-and-scope backlog using the populated registry, including
      prerequisites absent from the current index. Prioritize publication dependencies,
      frequently used tools, and uncertain claims with large downstream impact.
- [ ] Resolve the policy alternatives explicitly: the original full historical
      sweep and per-cycle requirement, active-frontier prioritization, statement-first
      specification, and asynchronous formalization. Record the chosen policy and
      completion criteria; do not silently drop the full-coverage proposal.
- [ ] Specify isolation and labelling for statement-only modules: unproved
      interfaces must not make dependent claims appear formally verified.
- [ ] When formalization is assigned, execute the chosen historical backlog in
      dependency order, recording exact Lean scope, evidence and remaining obligations.
      An unproved or false claim cannot be checked off through a weaker substitute.
- [ ] Implement the chosen ongoing policy and formalization-debt view without
      conflating mathematically reviewed work with formal verification.
- [ ] For asynchronous work, define discrepancy notifications and pause/review
      behavior for affected dependents; integrate through the existing correction
      and formalization-gaps protocol and shared resource controls.
- [ ] Demonstrate that a discovered scope discrepancy updates claim metadata,
      relationship audit tasks, the dated record and the visible verified frontier.

## 15. Interactive claim graph, locally and on GitHub Pages

- [ ] Design the graph around the populated, reviewed data; start with a selected
      claim and its neighborhood, and keep complete-graph views readable.
- [ ] Select the visualization implementation and obtain any dependency approval
      required by COMPUTATION_RULES.md. Treat CDN libraries as dependencies too;
      document licensing and pin/vendor assets if offline use is supported.
- [ ] Implement zoom/pan, selection, a statement/scope/source side panel, notebook
      and Lean links, and distinct visual treatment of claims, obstructions and
      finite checks. Display review and partial-formalization status accurately.
- [ ] Implement topic/status/date/formalization filters, ancestor/descendant
      highlighting, current-working-context route view, and correction-impact views.
- [ ] Provide grouping/collapsing or an alternative date/topic layout to avoid a
      whole-graph tangle. Treat degree/citation counts as navigation signals, not
      automatic measures of significance or formalization priority.
- [ ] Show edge types, evidence, uncertainty and incomplete coverage; disconnected
      branches are not automatically worthless or dead research.
- [ ] Provide accessible textual navigation and a useful empty/partial-data state.
- [ ] Add GraphML or DOT export for external tools, with stable IDs and documented
      direction/type semantics, alongside the existing JSON export.
- [ ] Integrate the graph and permitted data/assets into the minimal Pages build
      and local live mode, preserving project-relative links and update behavior.
- [ ] Test navigation, filtering, source links, rendering performance and offline
      behavior where promised; publish only under a separate valid push authorization.

## 16. End-to-end acceptance and maintenance

- [ ] Publish a coverage report for all baseline and subsequently added claims:
      populated metadata, reviewed dispositions, pending questions and stale evidence.
- [ ] Demonstrate a new result travelling through index registration, exact lookup,
      dependency recording, significance screening, formalization tracking and graph
      navigation without duplicated manual bookkeeping.
- [ ] Demonstrate a correction propagating to historical links, dependency-impact
      review, Fossick reconsideration and the living overview without rewriting history.
- [ ] Exercise interrupted/resumed work and parallel integration against the same
      structured source, preserving stable IDs and every accepted research record.
- [ ] Run appropriate schema, generation, retrieval, graph, workflow and portability
      checks; preserve complete evidence and reproduction metadata at checkpoints.
- [ ] Document the resulting minimal operating workflow and remove superseded
      instructions/tools after compatibility is accounted for.
- [ ] Review this plan against every item in IDEAS.md and the conversation. Record
      each proposal as implemented, explicitly superseded/rejected with a reason,
      or still open. Leave open work visible; do not declare the overall plan complete
      while known metadata or workflow gaps remain.

## 17. Enforce metadata maintenance in every subsequent research cycle

This is an ongoing requirement, not only a one-time enrichment pass. Update the
workflow during implementation of this phase; this plan update alone does not
change the active prompts or instructions.

- [ ] Define the per-claim completion contract for all new or substantively revised
      claims: precise mathematical status, topics, formalization disposition and
      scope, significance assessment, source references, applicable relationships,
      and field-level review provenance. Require explicit justified dispositions
      for genuinely unknown or inapplicable information, not unchecked placeholders.
- [ ] Require the research cycle to identify and record dependencies, refinements,
      corrections, rediscoveries, tests and obstructions introduced by its work.
      Distinguish a reviewed absence of relationships from missing review; do not
      invent edges or significance merely to satisfy a completeness check.
- [ ] Make each cycle update affected existing claims and relationships as well
      as new ones, including formalization-scope changes, correction impact and
      significance/candidate state. Preserve historical records and stable IDs.
- [ ] Update root AGENTS.md as the authoritative ongoing rule, and align scoped
      research/formalization instructions and Codex/Claude entry points by linking
      to that rule rather than duplicating it.
- [ ] Update `research/notes/RESUME.md` to restore the populated index, taxonomy,
      relationship semantics, pending reviews and the maintenance contract through
      bounded tools. Restoration must not silently revert to Markdown-only editing
      or import the entire index into context.
- [ ] Update `PROMPTS.md`: Spin, ordinary research guidance, Formalize,
      Spin-formalize, parallel variants and future Fossick/Explore/Adversary prompts
      must apply the same maintenance contract within their assigned scope.
- [ ] Update the registry guide, authoring tools and templates so a new claim is
      created with the required metadata and relationship review, rather than
      inheriting the initial migration's all-null defaults.
- [ ] Add changed-claim/relationship completeness checks to cycle finalization
      and CI, with useful diagnostics. Track historical backlog separately so the
      checks neither excuse incomplete new work nor repeatedly demand a full audit
      of the whole registry on every turn.
- [ ] Regenerate human, topic and graph views consistently at checkpoints; ensure
      pending significance flags and formalization debt remain visible to the next
      agent after compaction, branch integration or migration to another machine.
- [ ] Test a fresh cycle, a correction, a formalization update and parallel branch
      integration end to end. Verify that incomplete new metadata is caught and
      that justified unknown/not-applicable states are represented honestly.
- [ ] Include this ongoing-maintenance phase in the overall acceptance review;
      a fully backfilled index is insufficient if subsequent cycles leave its new
      fields empty again.

## Implementation notes

Completed structural implementation session: `index_migration_20260919`.
Local checkpoint: `c53b032`, "Migrate the complete claim index to a structured registry".

- Baseline: `21603c76b82afcc8d91014fa752e61e5cab690ac`.
- Imported all 866 claims to `research/claims/index.json`, schema version 1.
- `summary`, `assessment`, and `record` preserve the original three text cells
  verbatim. Machine-readable references are derived from those fields, avoiding
  a second editable copy. Classification fields remain explicitly unknown.
- Relationships have namespaced endpoints and evidence/review state; none was inferred.
- Initial reconciliation preserves every label, text field, link and row order.
  All 1,242 references (including the preamble) resolve locally.
- Rendering repairs: remove table-internal blank lines, including the break before
  `third-party:chessboard-star-nerve`, and escape bare math pipes in 22 rows.
  Entry contents are unchanged. Evidence: `research/results/index_migration_20260919/`.
- Affected consumers: ranked search, parallel append merger, checkout verification,
  root guidance, resume navigation, and public documentation.

The structural migration's completion criterion was met. Metadata enrichment and
all subsequent framework features above remain part of this expanded plan.

- Generated view and compact lookup are implemented; the complete export and
  qualified/ranked lookup examples are preserved with the evidence.
- Parallel append merges operate on JSON and regenerate Markdown; existing-record
  changes remain manual. Turn finalization, checkout validation and CI detect stale views.
- Focused suites pass: 14 registry, seven append-merge and six finalization tests.
- The user confirmed the repaired table renders correctly. No mathematical entries
  or original claim text were edited. Semantic curation and visualization remain pending.
