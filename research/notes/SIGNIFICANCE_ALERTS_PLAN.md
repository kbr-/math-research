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

- [x] Consolidate candidates and user-attention flags into one authoritative
      register with pending/reviewed/actioned/dismissed states and recorded reasons.
      Resolve the original `NUGGETS.md`/`FLAGS.md` alternatives through generated
      views rather than independent editable queues.
- [x] Provide a concise "Results of independent interest" overview linked to the
      register, without turning the living notebook into another result catalogue.
- [x] Add a cheap per-research-turn significance question and candidate flagging;
      reserve literature audits for plausible candidates instead of every lemma.
- [x] Make pending items visible on resume and at checkpoints, with user attention
      and acknowledgments tracked without deleting the historical assessment.
- [x] Evaluate local notifications for the actual supported Codex and Claude
      environments, including the proposed Stop-hook approach. Implement a bounded
      optional notifier or document an explicit decision and reliable file/UI fallback.
- [x] Integrate the shared register with Fossick and the benchmark map from
      [workflow utilities](WORKFLOW_UTILITIES_PLAN.md), keeping one editable source
      for each assessment and no independent NUGGETS/FLAGS queues.

## Acceptance and integration

- [x] Test that a plausible independent result is surfaced during a cycle,
      acknowledgments persist, repeated scans do not repeat alerts, and corrections
      trigger reconsideration without deleting earlier assessments.
- [x] Verify resume/checkpoint visibility and any optional local notifications in
      the supported agent environments; document limitations and maintain a fallback.

Implementation (19 September 2026): existing per-claim significance dispositions
plus the finalizer gate; `claims/attention.json` is the single decision history,
`ATTENTION.md` its generated overview. Resume/checkpoint summaries are bounded.
Recorded changes reopen decisions; unchanged scans preserve acknowledgments.
File/console notifications are the chosen cross-agent fallback; no desktop hook
or notifier dependency was added. Initial metadata seeding is not the separate
Fossick historical scan. See [operation](../claims/README.md#significance-check-and-attention).
