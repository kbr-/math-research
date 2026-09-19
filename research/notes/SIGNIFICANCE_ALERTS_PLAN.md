# Per-cycle significance and user-attention plan

Plan for [IDEAS.md item 2](../../IDEAS.md). Split from the broader checklist
on 19 September 2026; existing pending tasks remain pending.

Implement ongoing significance screening, a shared candidate/attention register,
and visibility/notifications. One-time claim significance metadata population belongs
to INDEX_MIGRATION.md; periodic record mining belongs to [Fossick](FOSSICK_PLAN.md).

This plan is separate from [index migration and curation](INDEX_MIGRATION.md).
Follow the workspace rules when implementing it; planning alone does not start
research, formalization, parallel agents, installations, or publication.

## Tasks

- [ ] Consolidate candidates and user-attention flags into one authoritative
      register with pending/reviewed/actioned/dismissed states and recorded reasons.
      Resolve the original `NUGGETS.md`/`FLAGS.md` alternatives through generated
      views rather than independent editable queues.
- [ ] Provide a concise "Results of independent interest" overview linked to the
      register, without turning the living notebook into another result catalogue.
- [ ] Add a cheap per-research-turn significance question and candidate flagging;
      reserve literature audits for plausible candidates instead of every lemma.
- [ ] Make pending items visible on resume and at checkpoints, with user attention
      and acknowledgments tracked without deleting the historical assessment.
- [ ] Evaluate local notifications for the actual supported Codex and Claude
      environments, including the proposed Stop-hook approach. Implement a bounded
      optional notifier or document an explicit decision and reliable file/UI fallback.
- [ ] Integrate the shared register with Fossick and the benchmark map from
      [workflow utilities](WORKFLOW_UTILITIES_PLAN.md), keeping one editable source
      for each assessment and no independent NUGGETS/FLAGS queues.

## Acceptance and integration

- [ ] Test that a plausible independent result is surfaced during a cycle,
      acknowledgments persist, repeated scans do not repeat alerts, and corrections
      trigger reconsideration without deleting earlier assessments.
- [ ] Verify resume/checkpoint visibility and any optional local notifications in
      the supported agent environments; document limitations and maintain a fallback.
