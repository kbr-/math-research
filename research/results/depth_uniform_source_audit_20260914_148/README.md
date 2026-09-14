# Depth-uniform source audit

The [full notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-14-depth-uniform-source-audit)
records the goal quantifiers, the complete binary source interface, a working
extension of the adapted-basis profile construction to every selector rank,
and the resulting degree-budget audit. It answers the user's question about
whether checking further individual depths leads to the full theorem.

The new profile bound charges the maximum product of
max(1,ceil(rank/(accuracy-1))) along a source dependency path. Its proof retains
all original-input prefix, companion, and Booleanity witnesses in one complete
affine system. This construction is uniform in depth; its cost is not proved
small enough for the general Frege source. It is a source-specific logical
compiler statement, not a map of arbitrary raw coefficient uses.

The audit also separates three endpoints: normalization to one affine family,
repeated degree-multiplying deletion, and one simultaneous weighted old-only
map. It states their different quantitative requirements. No new unrestricted
Frege bound or new next-depth theorem is claimed.

## Exact sources used

The prior notebook state is commit
`68ab6243dfd8288e68188da905304ccc86b88c2c`.
The following existing anchors supply the relevant statements and proofs:

| Purpose | Notebook anchors |
| --- | --- |
| Ordinary-to-compact bridge and source boundary | `ordinary-PHP-to-compact-bit-source`, `compact-virtual-zero-clause-source` |
| Original rank and degree-ordered basis | `source-dependent-selector-rank`, `rank-adapted-original-source-prefixes` |
| Complete profile definition and existing induction | `costed-ns-value-profile`, `costed-profile-product-closure`, `dependent-rank-source-collapse` |
| Logical degree compiler | `costed-profile-unbalanced-PC-compiler` |
| Final affine budget and accuracy tradeoff | `accuracy-dependent-affine-exclusion`, `compact-source-polynomial-rank-obstruction` |
| Actual first-removal output and conditioned barrier | `conditioned-bottom-level-removal`, `second-level-affine-flat-indicator-inputs`, `conditioned-compact-bit-filtration` |
| Other endpoint scopes checked | `bounded-affine-probe-source-exclusion`, `unit-accuracy-affine-family-exclusion` |

These are repository proofs with their recorded working status; this cycle did
not repeat their literature audits. The product-profile identity was read during
the final focused proof review. No third-party full text is reproduced here.

## Review and reproducibility

This is a symbolic audit. No new finite numerical computation was required.
The notebook supplies the full proof of the inflation recurrence and checks its
original-input inequalities. Existing finite fixtures were not rerun.

`check-metadata.json` preserves the focused source-anchor and evidence review,
the prior-record comparison, and the exact source revision. `provenance.json`
hashes this note and that metadata. The notebook entry, timing fragment, and
archived session journal preserve the research checkpoint. The complete timing
and command outputs are under this session in `research/provenance/session-records/`.
