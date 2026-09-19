# Context restoration and framework-consolidation plan

Plan for [IDEAS.md item 7](../../IDEAS.md). Split from the broader checklist
on 19 September 2026; implemented and validated in the context-budget cycle.

Reduce routine restoration and instruction overhead while preserving necessary
mathematics and the complete append-only record. Compact claim listing and topic
views are owned by INDEX_MIGRATION.md and reused here.

This plan is separate from [index migration and curation](INDEX_MIGRATION.md).
Follow the workspace rules when implementing it; planning alone does not start
research, formalization, parallel agents, installations, or publication.

## Completion — 19 September 2026

Implemented as the explicitly requested research cycle. All tasks below are
complete; the [measurement and recovery report](../results/context_budget_20260919/restoration-accepted.json)
records a **49.14% reduction in the prescribed restoration output bytes**
(103,822 to 52,803), not a token-usage claim. All pre-record regions fit the
unchanged proposed budgets. Historical entries remain byte-identical; previous
overview versions are referenced by immutable Git revision, not copied.

The [evidence guide](../results/context_budget_20260919/README.md) maps retained
constraints and six recovery scenarios to exact sources. Twelve budget/TOC tests,
eight finalizer tests, 79 claim tests and six page tests pass. The same hard-limit
checker runs in local finalization, context CI and the Pages build. Resume and
root/scoped guidance use it and the bounded TOC; future interruption-note tooling
remains in its owning plan. No mathematical route, claim status, computation
resource enforcement or publication permission was changed.

## Tasks

- [x] Measure actual mandatory restoration output and representative claim lookups;
      distinguish byte/word counts, token estimates and measured token accounting.
- [x] Extend the existing notebook excerpt tool with compact TOC output, default
      bounded tail, `--tail N` and `--since DATE`; avoid a second notebook parser.
- [x] Consolidate every section before **Research record**, including **Proposed
      next step**, historical orientation and formalization gaps, by its purpose
      rather than chronology. Preserve exact hypotheses, costs, unresolved gaps
      and links to complete records; do not turn orientation into a second history.
- [x] Consolidate AGENTS and related instructions: retain every current user
      constraint once, remove duplication, and move expired authorization history
      out of mandatory context without accidentally renewing permission.
- [x] Update Resume to use the compact overview, TOC, topic map and exact claim
      lookup, loading full entries only as needed and retaining the gaps section.
- [x] Implement the per-section budget policy below, replacing the existing late
      finisher warning with a shared checker and pre-finalization enforcement.
      Keep historical entries append-only and unabridged.
- [x] Validate restoration on representative paused tasks and compare its output
      cost and ability to recover the needed definitions/dependencies with the baseline.

## Machine-enforced living-section budgets

User addition, 19 September 2026: soft warnings alone are insufficient. Every
updated-in-place notebook section before Research record must have a hard limit,
initially **1.5 times its soft target**. The limits apply to the notebook overview,
not to full proofs, evidence files or the append-only Research record.

Budget design used for implementation (the machine-readable configuration is
authoritative; this table records the agreed starting allocation):

| Region | Soft target | Hard limit |
| --- | ---: | ---: |
| Title and introductory text outside sections | 100 | 150 |
| Before this notebook | 150 | 225 |
| Where we stand | 400 | 600 |
| The remaining route | 500 | 750 |
| Proposed next step | 250 | 375 |
| Working mathematical context | 1,000 | 1,500 |
| Gaps identified by formalization | 300 | 450 |
| **Total pre-record content** | **2,700** | **4,050** |

## Budget operation

The authoritative values live in [context-budgets.json](../context-budgets.json).
Run `python3 tools/notebook_context.py` while drafting; `--out PATH` preserves the
complete report without suppressing its failure status. There is no automatic
waiver. Hard limits are the soft allocation multiplied by 1.5, rounded down.

Counting uses whitespace-delimited HTML text, including headings, lists, tables
and literal TeX. Tags, attributes and comments are excluded; entities are decoded,
whitespace normalized, and inline formatting does not split a word. A second
limit allows 12 normalized text characters per allocated word (at both soft and
hard levels). Thus one long unspaced formula still consumes the character budget.
This is a deterministic size guard, **not measured tokens**. Actual raw restoration
bytes/words are reported separately because agents also receive markup and URLs.
Nested configured sections own their text exclusively; the aggregate counts each
region once. Introductory/outside-section text belongs to `@intro`.

Every pre-record section must have one unique, configured ID. Unknown, missing or
duplicate sections fail closed. Soft excess warns; hard word/character excess
fails. The finisher checks before timing stop, archival or notebook mutation;
context CI uses the same checker, and the Pages build checks before publication.
The Research record has no budget. Consolidate by linking exact sources; preserve
unique substantive content before shortening. Previous overview versions are
already in Git history and must not be copied into a second snapshot file.
Budget changes/waivers require an explicit user override recorded in the change,
not an agent silently increasing a cap to pass validation.

- [x] Store section IDs and budgets in one small machine-readable configuration;
      derive hard limits from the multiplier and generate reports from that source.
      Match stable IDs, not headings or line numbers. Include introductory content
      and an aggregate budget so adding sections cannot silently expand restoration.
- [x] Define and test deterministic counting of visible text, lists, tables,
      headings and mathematics, excluding HTML attributes/comments. Document how
      TeX is charged; add a character guard if word counts undercount dense or
      unspaced mathematics. Never describe word counts as actual token accounting.
- [x] Reuse the existing notebook parser to discover every pre-record section.
      Reject unbudgeted, missing or duplicate sections and account for nested
      content exactly once. New sections require an explicit budget allocation.
- [x] Warn above each soft target and fail above any hard limit, including the
      aggregate limit. Report the section, actual count, target, limit and excess.
      Provide a cheap standalone report/check command usable while drafting.
- [x] Run the shared check in `finish-turn.py` **before** stopping the clock,
      archiving or modifying the notebook; run the same check in CI for notebook,
      configuration and checker changes. Cover direct/admin notebook edits in CI,
      not just turns that happen to invoke the finalizer.
- [x] Consolidate existing oversized sections before enabling the blocking gate;
      do not grandfather their excess or silently enlarge budgets to make CI pass.
      Keep essential assumptions and active warnings in the overview, with exact
      links to detailed arguments. Move unique material to durable records before
      shortening it; never discard substance merely to meet the cap.
- [x] Reconcile root/scoped guidance and Resume with hard enforcement, replacing
      the current soft-only exception and warning rather than adding a competing
      rule. Agents may not waive or raise hard limits on their own; an explicit
      user override remains authoritative and must be recorded transparently.
- [x] Test exact boundaries, soft-only warnings, hard failures, aggregate overflow,
      unknown sections, nested markup and math counting. Verify a failed finalizer
      leaves timing active and notebook/evidence untouched. Confirm that arbitrarily
      long Research-record entries are outside these limits.

## Acceptance and integration

- [x] Use the minimal listing, field projection and topic views from the
      index plan; do not introduce another index source or retrieval parser.
- [x] Test representative restored tasks, including mathematical dependencies and
      formalization gaps, against the pre-change reading baseline.
- [x] Preserve all current user constraints and historical entries; document
      measured savings, final budget choices and any explicit user overrides.
- [x] Verify all pre-record regions meet their hard limits and demonstrate that
      both local finalization and CI reject a deliberately oversized fixture.
- [x] Coordinate interruption-note integration with [workflow utilities](WORKFLOW_UTILITIES_PLAN.md)
      rather than maintaining a second task-recovery mechanism.
