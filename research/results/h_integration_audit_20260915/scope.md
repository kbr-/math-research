# Integrated H01–H11 audit

This checkpoint integrates the four workers through sequential rebases and
fast-forwards on `formal`. Every research article from both sides was preserved
byte-for-byte during conflict resolution; subsequent file relocations repair
Lean hyperlinks without changing historical statements, proofs, or timing.
The preceding coordination was not instrumented in this audit session.

The audit concerns statement provenance, claim-index coverage, module integration,
and fresh Lean verification. It is not an independent mathematical review of
the publication or a proof of H12/H13. Every worker supplied full mathematical
arguments and declaration/axiom audits in its own research records.

## Directory decisions

- Move `AugmentedChains`, `AugmentedChainMaps`, and
  `ChessboardParameterArithmetic` to `claims/`: these are project-formulated
  concrete interfaces, combining standard algebra/arithmetic with the selected
  representation and degree conventions. Their increased interface scope is not
  evidence of mathematical novelty. Keep historical labels and declaration
  namespaces stable, including their original `third-party` prefixes; the
  provenance description and directory now give the classification.
- Retain `AugmentedBoundarySquared`, `SimplexBoundary`, `HomologicalCover`, and
  the three `ChessboardStar*` files in `third-party-claims/`: these formalize
  standard attributable identities and the classical star-cover argument.
  The alternate finite-chain proof of the cover lemma does not transfer theorem
  authorship. The H proposition remains there as a statement-only external target.
- Retain the already separate project helpers `AugmentedCone`,
  `FiniteComplexCover`, `CoverDoubleComplex`, and
  `AugmentedSubcomplexRelabeling` in `claims/`.
- Keep the short closed-star definitions/closure facts with the star-cover
  development; their present consumers are that development, and extracting
  another indexed module has no demonstrated benefit. Likewise the small
  parameter bookkeeping lemmas remain with the H11 interface. This does not
  prevent later extraction when an independent use warrants it.

## Index and evidence

`claim-inventory.json` records all 19 module headers: 18 proof modules and the
statement-only H module, each linked in the index. The 13 new proof modules
cover H01–H11 and two separately extracted cover/relabeling interfaces. No
missing indexed claim was found. Keep the stable IDs and existing full proofs.
Refresh the H08–H10 route rows with the completed interfaces and consolidate
the living overview; the main Frege route and formalization gap list are unchanged.

Reproduce the combined check from this checkout:

```sh
./formalization/verify.sh --session h_integration_audit_20260915 --out research/results/h_integration_audit_20260915/lean-verification.txt
```

The output path must be new for a repeat run. Historical per-worker audit outputs
and source manifests remain unchanged; they describe their original checkpoints.
The fresh report and manifest describe this integrated source layout.

The user also requested promotion of the temporary append-conflict helper into
repository tooling. Six tests, including a real disposable Git rebase, passed
under this session. The tool rejects changed historical articles, unrelated
living sections, edited/conflicting index rows, and ambiguous overview merging.
It neither stages files nor continues rebases. That framework change is committed
separately after this audit checkpoint.
