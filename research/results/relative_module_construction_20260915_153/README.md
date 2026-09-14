# Functional route audit for the source module representation

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-source-module-functional-barrier)
records the argument. No new simultaneous module design or source-level
compression was obtained.

## Source and inspection scope

Tal Elbaz, Nashlen Govindasamy, Jiaqi Lu, and Iddo Tzameret,
*Lower Bounds against the Ideal Proof System in Finite Fields*,
arXiv:2506.17210v1, 20 June 2025.

- Versioned abstract: https://arxiv.org/abs/2506.17210v1
- Versioned HTML: https://arxiv.org/html/2506.17210v1
- Inspected: Sections 1.3, 1.4.2, and 5.4, especially Fact 47,
  Proposition 48, and Theorem 49.
- Purpose: check whether finite-field functional ROABP lower bounds can be
  applied to the small formal source modules already obtained in the notebook.
- The page identifies the arXiv non-exclusive license. No PDF, full text,
  or source-containing diagnostic is copied into this public checkpoint.

The notebook applies the fixed-field inverse limitation to a distinguished
source module, retaining the common variable order and distinguishing an easy
semantic inverse from the unresolved cost of certifying its residual.
No knapsack theorem or hard-instance reduction is imported. The broader search
also screened abstracts on bounded-depth algebraic proofs; none is used as a
proof dependency.

## Repository dependencies

- `source-outer-linear-factor-normal-form`;
- `source-formal-roabp-certificate`;
- `linear-factor-subset-matrix-program`;
- `selector-old-target-module-interface`;
- `mixed-selector-extension-quantifiers`;
- `shallow-ENS-query-obstruction`.

The literal-family restriction theorem was also reread as a scope check.
It requires literal input supports and does not apply to the complete
affine-in-selector source.

## Review and evidence

The review checks matrix product closure in one common variable order,
multilinearization at matrix entries, the binary inverse-one case,
constant-width affine OR targets, and the distinction between semantic
residual vanishing and a costed joint certificate.

No numerical test was necessary for these identities. One redundant local
excerpt request used the same start/end anchor and failed safely; it was not a
failed mathematical computation. Timing includes the targeted source search
and interpretation. `check-metadata.json` records focused checks;
`provenance.json` hashes this note and metadata. Complete local command outputs
are retained in the archived session.
