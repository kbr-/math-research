# Adaptive old-query attempt

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-adaptive-query-attempt)
records the unsuccessful attempt and its exact old-query degree budget.

The case-split argument combines refutations of q=a over all a in F_p by
Lagrange factors. It incurs at most (p-1) deg(q) additional ordinary NS degree.
Applied to a height-H old-polynomial query tree and its leaf pair, this gives
a favorable degree-D design when the old barrier exceeds ((p-1)H+p)D.

This favorable design may depend on the entire tree. The recorded ENS rate
bridge instead fixes a distribution before choosing the scalar specialization
and the query tree, and requires a quantitative non-conflict probability.
The case-split argument supplies neither that quantifier order nor that rate.
The distinction was already explicit in the earlier bridge audit.

Scalar specialization does make the source queries old and degree-bounded.
That was verified from the exact source record. Committing entire input spaces
in advance leads back to an uncontrolled rank-times-degree cost.

No active source functional or new main-route bound was constructed.
The elementary case-split proof is preserved without a novelty assertion.

## Reused sources and review

- `all-prime-affine-family-exclusion`: ordinary Boolean Frobenius cost;
- `pseudo-ENS-rate-bridge`: fixed distribution, adaptive scalar choice,
  source query height, and required probability;
- `source-conflict-query-inventory`: degrees after scalar specialization;
- `shallow-ENS-query-obstruction`: failure of the coarse query guarantee;
- `full-binary-source-active-window-application`: the current construction gap.

The earlier assignment-tree split was read as a scope comparison; its ENS
family construction is different from the old-query argument here.
No new external paper or numerical run was needed.

The review checks Lagrange degrees, the Frobenius residual, the degree reserved
for the leaf factors, preservation of earlier answers, and the failed
quantifier exchange. `check-metadata.json` and `provenance.json` retain the
focused review and hashes; timing and full local command outputs are archived.
