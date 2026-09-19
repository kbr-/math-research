# Parallel exploration and adversarial review plan

Plan for [IDEAS.md item 3](../../IDEAS.md). Split from the broader checklist
on 19 September 2026; existing pending tasks remain pending.

Design and validate bounded multi-agent exploration and adversarial review,
using the existing worktree, shared-resource and integration infrastructure.

This plan is separate from [index migration and curation](INDEX_MIGRATION.md).
Follow the workspace rules when implementing it; planning alone does not start
research, formalization, parallel agents, installations, or publication.

## Tasks

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

## Acceptance and integration

- [ ] Exercise interruption, pinned-target rebasing and integration without
      losing either branch's records or duplicating metadata ownership.
- [ ] Verify the pilot produces distinct useful assessments, preserves unsuccessful
      attempts, and records aggregate resource/context costs before expanding concurrency.
- [ ] Update the relevant prompts and coordination guidance once the workflow is
      implemented; reuse the index maintenance contract rather than copying it.
