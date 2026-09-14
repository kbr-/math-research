# Three-minute downstream companion-degree audit

Scope: the user requested a bounded audit, not a full dependency review.
The notebook entry `entry-2026-09-14-bounded-companion-degree-audit` gives the
findings, exact-degree justification, and limits.

Inspected paths:

- `mp-certificates.html`: the nearby MP ledger repeats the loose-ceiling
  expression, but the subsequent composition proof uses upper bounds only.
- `polynorm-transfer.html` and `polynorm-ns.html`: cofactor subtraction needs
  actual degree; the parent statement supplies an exact maximum input degree,
  fresh coefficients, and a polynomial ring over a field, which justify it.
- `draft-excerpts.txt`: Section 5's scalar cleanup establishes exact degree
  for proper affine blocks before its weighted-image table uses it; Section 6
  uses upper bounds in local simulations.

No invalid downstream inference was found in these passages. No conclusion is
claimed for every later compiler or the complete publication proof. No tests,
Lean proofs, or numerical computations were run for this audit. Saved excerpts
are snapshots; their provenance manifest records their hashes.
