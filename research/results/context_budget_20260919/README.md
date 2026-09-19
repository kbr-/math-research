# Context-budget implementation and restoration audit

Baseline: `33047a41d10f2c1f01735ffbb23320293cc183ad`. The prior notebook and
instructions are preserved in Git; no duplicate overview snapshot is kept.
The user explicitly requested this implementation as a measured research cycle.
A brief initial Resume/plan read preceded instrumentation; it is not backfilled.

`restoration-accepted.json` is the final measurement: 103,822 to 52,803 bytes
(49.14% smaller). Earlier measurement reports record intermediate consolidation
states; none contains a copied overview. The final review made the existing
functional-board scope and degree window explicit, without changing any theorem.

## Reproduction and measurement

Run through `compute.sh`, with a fresh output path:

```bash
python3 research/results/context_budget_20260919/measure.py --out /tmp/context-measurement.json
python3 tools/notebook_context.py --out /tmp/context-budgets.json
./tools/notebook-excerpt.py --toc --tail 10
```

The report measures actual bytes/whitespace words of root/scoped instructions,
computation policy, Resume, the `--current` output and the default title scan.
The baseline title scan is the previously prescribed bounded grep/tail command,
not an inflated unbounded scan. Representative exact claim lookup outputs are
measured as well. No tokenizer, model usage counter or token estimate is claimed;
harness prompts, optional model-specific instructions and follow-up proofs are
outside the reported restoration total.

The budget itself counts normalized HTML text words and characters, retaining
literal TeX. It excludes tags, attributes/comments and the entire Research record.
The character guard prevents long unspaced mathematics from evading word counts.
Configuration is authoritative; documentation records its initial allocation.

## Preservation review

The six recovery cases in the measurement report check exact navigation plus
distinguishing conditions for source-module review, profile endpoints, probability
repair, formalization gaps, publication scope and parked routes. This is an
orientation/interface review against the baseline, not a new proof verification
or simulated model benchmark. Exact proof reading remains required on reliance.
The old Research record is checked byte-for-byte; all current internal links resolve.
Removed chronological examples remain in their existing dated entries and Git.

Instruction consolidation was reviewed by policy group:

| Before-state constraint group | Retained authoritative location |
| --- | --- |
| Resource caps, no bypass, installations, numerical/timing/output rules | COMPUTATION_RULES.md, linked at root |
| Resume/compaction, immutable handoff, targeted sources, no private math memory | Root restoration/portable rules and concise Resume |
| Main-goal prioritization, sufficient endpoints, falsification, accumulated costs | Root research discipline |
| Periodic route reviews and line-specific chance estimates | Root notebook entry rules; existing finisher enforcement |
| Full failed/successful research records, exact hypotheses/degrees, no history rewriting | Root notebook rules; unchanged append-only checker |
| Living-section ownership, formalization gaps and parallel coordinator/worker roles | Root notebook/formalization rules |
| Stable claim IDs, all five dispositions, exact evidence and registration | Root index contract plus registry guide |
| Timing phases, snapshots, archival, next-cycle clock, short footnotes | Root checkpoint rules plus computation policy |
| Chosen branch, immutable integration targets, commit wrapping, unrelated edits | Root portable/Git rules |
| Explicit publication scope/expiry, protected backup, public-history checks | Root Git rules; PROMPTS no longer refers to an expired standing grant |
| Licenses, attribution, uncleared third-party sources, ignored user_requests | Root publication rules |
| Local/public rendering, minimal Pages artifact, no unsolicited PNGs | Root notebook/research/publication rules |

Only the user-requested hard-limit rule supersedes the earlier soft-only overview
exception. The expired grant's original wording remains in baseline Git history;
no permission is renewed. Claude-specific verification requirements and launchers
are unchanged. Root/scoped references were checked after heading consolidation.

## Enforcement and evidence limits

The finisher checks budgets before stopping timing, archiving or changing the
notebook. Tests verify overflow leaves the journal and notebook byte-identical and
creates no results/provenance. The same CLI fails in CI; the Pages build also gates
publication. Unknown/missing/duplicate sections fail, nested content counts once,
and both per-section and aggregate word/character caps are checked. New sections
must be explicitly budgeted. No automatic waiver is provided.

Tests cover exact boundaries, soft warnings, dense math, nested/unknown sections,
unlimited records, compact TOC filtering, and compatibility with claim evidence.
The existing shared finalizer fixture uses its CI-portable tiny archive launcher;
production computation enforcement is unchanged.

Interruption recovery reuses the assigned plan/evidence and Resume. Any future
generic work-note mechanism remains owned by WORKFLOW_UTILITIES_PLAN.md. No second
recovery store, live mathematical summary, or research-record snapshot is introduced.
