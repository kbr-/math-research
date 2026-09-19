# Fossick implementation plan

Plan for [IDEAS.md item 1](../../IDEAS.md). Split from the broader checklist
on 19 September 2026; existing pending tasks remain pending.

Implement and run a resumable search of the Research record for results of
independent interest. Consume the curated index and the candidate register owned
by [significance alerts](SIGNIFICANCE_ALERTS_PLAN.md); do not duplicate their metadata.
Candidate decisions now live in `research/claims/attention.json`; use
`tools/claim-attention.py decide` and existing claim significance metadata.
Use [the benchmark map](../OPEN_PROBLEMS.md) and its maintenance procedure for
literature comparisons; link benchmark anchors from candidate assessments.

This plan is separate from [index migration and curation](INDEX_MIGRATION.md).
Follow the workspace rules when implementing it; planning alone does not start
research, formalization, parallel agents, installations, or publication.

## Reuse existing features

- [ ] Build on `claim-index.py list`, `search-claims.py`, dependency packets and
      `notebook-excerpt.py`; reuse their parsers and evidence normalization rather
      than creating another notebook parser or loading the full record by default.
- [ ] Use claim `significance` and its evidence-backed reviews for assessments.
      Follow the [cheap-check workflow](../claims/README.md#significance-check-and-attention):
      candidate decisions belong only in `claims/attention.json`, with the generated
      `ATTENTION.md` overview. Reuse its sync/decision API and reopening behavior;
      do not create NUGGETS, FLAGS or another candidate queue.
- [ ] Use relevant [benchmark-map entries](../OPEN_PROBLEMS.md) to guide targeted
      literature checks. Triage is not proof verification or novelty certification;
      unknown novelty can remain a pending question with a concrete next action.

## Durable progress and repeated invocations

- [ ] Store portable progress in tracked `research/notes/FOSSICK_STATE.json`.
      Include a schema version, a pinned scan revision, its last in-scope article,
      and an explicit **`ended_at` article anchor**: the last contiguous article
      whose screening is durably recorded. Use stable anchors, not line numbers,
      wall-clock dates or a numeric cycle counter. Null means no completed prefix.
- [ ] Preserve a compact per-article screening ledger in that same state: normalized
      source fingerprint, relevant claim/relationship fingerprints, disposition
      (`no_candidate`, `candidate_linked`, or `already_assessed`), and references
      to existing reviews/attention items or a short no-candidate reason. Store no
      duplicate statements, proofs or significance assessments. A pending candidate
      audit does not prevent its source article from being marked screened.
- [ ] Keep selection separate from completion. Proposed commands:
      `tools/fossick.py next --limit N` emits a bounded batch without advancing;
      `tools/fossick.py complete --batch FILE --out REPORT` validates saved
      dispositions and expected fingerprints before atomically advancing state.
      Preserve unfinished batch identity/progress so an interruption resumes the
      same batch. Reading a packet alone never counts as screening.
- [ ] Pin each scan pass to an immutable Git revision and terminal article so the
      scan cannot chase its own new checkpoint entries indefinitely. After reaching
      that endpoint, report completion; the next invocation adds the later suffix.
      Unchanged, already screened articles produce no repeated review requirement.
- [ ] Revisit changed items behind `ended_at` using per-item fingerprints, not the
      last Git revision alone. Include changed assessments, significance, relevant
      source evidence and new/changed incident relationships. Use existing normalized
      article evidence so generated timing/producer decoration does not retrigger
      screening. Newly recognized dependencies identify review scope, not automatic
      invalidation. Derive the revisit worklist from the ledger; do not maintain a
      second competing cursor or candidate register.
- [ ] Reconcile stable IDs after merges or branch changes. Detect insertions behind
      the frontier, missing anchors, changed sources and divergent history; never
      silently mark them covered or reset all progress. Previously screened content
      with matching fingerprints can be reused, regardless of its new position.
      Only the contiguous completed prefix determines `ended_at`.
- [ ] Make batch completion idempotent and reject stale/concurrent writes by checking
      the expected state digest. Validate all required dispositions and persisted
      candidate references before advancing. Commit the state, metadata/attention
      updates, batch report and normal measured notebook checkpoint together. If
      committing fails, finish that checkpoint before starting another batch; do not
      discard uncommitted progress or claim it is safely checkpointed.

## Screening workflow and integration

- [ ] Add a `Fossick` prompt to PROMPTS.md and the bounded scan tool. Cover the full
      new-research record, including entries with no registered claim, obstructions,
      failed attempts and formalization corrections. Start with article titles,
      status lines and minimal claim summaries. Use packets and exact source excerpts
      for plausible candidates or ambiguous scope; do not mechanically dismiss
      no-claim entries or negative results. Historical handoff import remains excluded.
- [ ] Reuse current significance reviews when their scope/evidence remains applicable;
      do not repeat the completed index-curation audit. If a previously unregistered
      result is found, follow ordinary claim registration and source-review rules.
      Link refinements/rediscoveries instead of inventing a second candidate identity.
- [ ] Expose only a short progress summary in ordinary resume: screened frontier,
      unfinished batch and remaining/revisit counts. Keep candidate visibility in
      the existing attention summary. Load detailed Fossick state only when assigned.
      Preserve bounded output and verify the ordinary resume still fits three calls
      at the current payload size.
- [ ] Run the initial complete scan through its pinned historical endpoint in measured
      bounded cycles. Preserve every screening disposition, candidate handoff and
      unresolved audit; a completed scan means screened, not all candidate audits
      finished. Tool implementation alone does not complete this plan.

## Acceptance tests

- [ ] Two consecutive runs without changes: the second has zero new/revisit items,
      no duplicate attention events and the same `ended_at` marker.
- [ ] Appended articles: only the unscreened suffix is selected; prior reviews remain.
- [ ] Interruption before completion, partial completion and retry: no skipped
      articles, no false frontier advance and no duplicated candidate decisions.
- [ ] A changed/corrected old claim, new dependency or inserted earlier article is
      revisited; unchanged neighbors are not. Relevant attention items reopen while
      earlier decisions survive. Timing-only decoration does not cause a revisit.
- [ ] Stale batch input, concurrent completion, missing IDs and a branch switch fail
      safely or reconcile by content identity; none silently certify missing work.
- [ ] Show an independently interesting candidate and a useful negative result
      reaching the existing attention mechanism with source evidence, and a no-result
      article receiving a justified screening disposition without inventing a lemma.
- [ ] Document commands, state recovery, initial scan coverage and remaining candidate
      audits. Mark this plan complete only after the initial scan and tests pass.
