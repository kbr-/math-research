# Interruption recovery and benchmark-map plan

Plan for [IDEAS.md item 6](../../IDEAS.md). Split from the broader checklist
on 19 September 2026; existing pending tasks remain pending.

Measure interruption recovery before deciding whether work-in-progress notes
justify their overhead; separately maintain a field benchmark/open-problem map.
Neither is required to complete the claim-index migration and curation.

This plan is separate from [index migration and curation](INDEX_MIGRATION.md).
Follow the workspace rules when implementing it; planning alone does not start
research, formalization, parallel agents, installations, or publication.

## Tasks

- [x] Embed silent recovery-proxy collection into existing retrieval and timing
      tools, with automatic archival in timing summaries. See
      [the mechanism and limitations](../../tools/RECOVERY_EVIDENCE.md).
- [x] Use explicit resume preparation as the marker, not ordinary notebook
      overview reads. Deliver the cached bundle in bounded, retryable parts without
      extra resume events. Reuse the existing parser and add a restoration phase to an
      active cycle's timing table; do not create a research cycle just to restore.
- [ ] Evaluate several actual recovery candidates: observed delays, repeated
      unchanged outputs and possible computation repeats. Separate necessary
      orientation, idle time and deliberate verification from avoidable recovery.
- [ ] Only if evidence warrants it, trial narrowly scoped interruption notes and
      compare maintenance cost against recovery savings. Prefer existing plans;
      do not introduce a mandatory per-turn note or duplicate living summary.
- [ ] Create a maintained open-problem/benchmark map, including the systems and
      formulations named in IDEAS.md. Record last verification and link candidates
      to it; it guides searches rather than replacing current literature review.

## Acceptance and integration

- [x] Test silent collection, existing-command integration, identity isolation,
      missing/censored observations and archival without changing historical data.
- [ ] If notes are trialled, demonstrate recovery and checkpoint retirement;
      otherwise record why the observed benefit does not justify them.
- [ ] Populate the benchmark map with precise formulations, dated source checks
      and links to relevant claims; distinguish it from authoritative current status.
- [ ] Connect the map to significance assessment and Fossick without duplicating
      candidate queues or treating old citations as a permanent novelty verdict.
- [ ] Document the small workflow and evidence locations, linking guidance from
      the appropriate resume and research prompts.
