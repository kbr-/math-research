# Fossick implementation plan

Plan for [IDEAS.md item 1](../../IDEAS.md). Split from the broader checklist
on 19 September 2026; existing pending tasks remain pending.

Implement and run a resumable search of the Research record for results of
independent interest. Consume the curated index and the candidate register owned
by [significance alerts](SIGNIFICANCE_ALERTS_PLAN.md); do not duplicate their metadata.
Use [the benchmark map](../OPEN_PROBLEMS.md) and its maintenance procedure for
literature comparisons; link benchmark anchors from candidate assessments.

This plan is separate from [index migration and curation](INDEX_MIGRATION.md).
Follow the workspace rules when implementing it; planning alone does not start
research, formalization, parallel agents, installations, or publication.

## Tasks

- [ ] Add a Fossick prompt and bounded scan command using the structured index and
      compact notebook navigation; open full arguments for candidate assessment.
- [ ] Persist a portable scan cursor and review revision. Track "screened through"
      separately from unresolved candidates, and revisit corrections, changed claims
      and newly recognized dependencies behind the cursor.
- [ ] Run the initial complete historical scan, recording dispositions and pending
      audits. Do not stop at implementing the command without using it on the backlog.
- [ ] Test interrupted scans, repeated scans, cursor drift, newly corrected old
      entries and duplicate candidate detection. Preserve pending audits separately
      from the cursor and route alerts through the shared significance register.

## Acceptance and integration

- [ ] Demonstrate that a new candidate and a corrected previously scanned claim
      reach the shared register with evidence and a visible pending disposition.
- [ ] Document the prompt, scan command, state recovery and remaining audits;
      preserve complete scan evidence and commit coherent checkpoints locally.
