# Visible status and correction notices

`tools/claim_notices.py` provides a deterministic derived Markdown block before
the preserved four-column claim table. It displays every explicitly conditional,
retracted or refutation-status record, and every current claim targeted by a
`corrects` or `supersedes` relationship. Ordinary claims remain compact; the full
registry and lookup still own exact metadata.

Correction notices retain the relationship's exact scope, review status and
review date, and link both its source claim and all dated-record/evidence links.
The date is labelled as a relationship-review date, not a theorem date. A scoped
correction/supersession never implicitly changes mathematical status or retracts
the whole theorem. `refutation` describes a counterexample/refutation result,
not a declaration that the counterexample record is false. `conditional` retains
its hypotheses and is not described as retracted. Explicit `retracted` metadata
is highlighted separately. Pending/not-applicable status review dispositions and
unreviewed edges remain labelled as such.

## Minimal coordinator integration patch

In `tools/claim_registry.py`, import the helper:

```python
from claim_notices import render_notices, strip_notices
```

At the beginning of `legacy_rows(text)`, before checking/splitting `HEADER`:

```python
text = strip_notices(text)
```

Change the final return of `render(data)` to:

```python
return NOTICE + data['preamble'] + render_notices(data) + HEADER + '\n'.join(rows) + '\n'
```

This single import-path change covers both legacy import and reconciliation.
The helper defers its use of `claim_registry.markdown_links` until rendering, so
the import does not create an initialization cycle. The generated block uses
explicit `CLAIM-STATUS-NOTICES:START/END` markers. Removal is exact and refuses
malformed, repeated, reversed or unterminated markers; no original table cell or
preamble is rewritten. Existing table escaping and link parsing remain unchanged.

Add module/test paths to the usual CI and checkout inventories, regenerate the
primary Markdown index, and rerun registry/import/render tests after integration.
The worker did not edit those shared files or the canonical registry.

## Regression evidence and limits

Five focused tests pass: partial correction/conditional/counterexample separation,
explicit retraction and unreviewed supersession, deterministic generation without
mutation, exact stripping preserving legacy import/reconciliation, malformed
marker rejection, and absence of unnecessary notices for ordinary untouched rows.
The tests invoke existing registry importer/reconciler after stripping; coordinator
integration still needs the full real renderer/import suite.

Rendering is metadata-only and performs no silent source re-audit. It cannot
discover an omitted correction edge or prove a declared scope correct. Existing
coverage/maintenance tools remain responsible for stale review evidence. Adding
the generated block changes the generated Markdown file hash; it does not change
canonical claim text, topic/relationship values, or notebook source excerpts, so
their current evidence hashes are unaffected. A review that deliberately hashes
the generated Markdown file itself will correctly become stale and must be
reviewed/refreshed. Do not automatically refresh such evidence merely to hide it.

Timing/evidence session: `parallel_claim_notices_20260920`.
