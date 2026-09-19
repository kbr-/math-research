# Formalization coverage and ongoing-policy plan

Plan for [IDEAS.md item 4](../../IDEAS.md). Split from the broader checklist
on 19 September 2026; existing pending tasks remain pending.

Plan the historical formalization backlog and the policy for maintaining its
verified frontier. Recording already-existing Lean coverage in the structured index
is index curation; developing new Lean proofs belongs to this separate plan.

This plan is separate from [index migration and curation](INDEX_MIGRATION.md).
Follow the workspace rules when implementing it; planning alone does not start
research, formalization, parallel agents, installations, or publication.

## Tasks

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

## Acceptance and integration

- [ ] Account for the full chosen backlog and every pending proof obligation;
      report exact verified scope rather than treating weaker substitutes as completion.
- [ ] Integrate recorded proof outcomes with index metadata and correction-impact
      review. Use [parallel research](PARALLEL_RESEARCH_PLAN.md) infrastructure where
      asynchronous work is explicitly assigned.
- [ ] Update the applicable formalization prompts/instructions for the chosen
      policy and demonstrate recovery across interruptions and integration checkpoints.
