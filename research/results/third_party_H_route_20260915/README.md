# Third-party H interface and proposed proof route

The user prioritized the BLVZ boundary before the project-side publication
claims. The [formal statement](../../../formalization/third-party-claims/ChessboardFilling.lean)
is indexed as `third-party:BLVZ-chessboard-filling`. The
[route](../../../formalization/BIT_PHP_FORMALIZATION_ROUTE.md#third-party-boundary)
contains thirteen ordered planning steps, H01–H13, ending with this statement.

## Exact interface and status

Faces are finite cell sets with injective row and column projections. A k-cell
chain is an F₂ coefficient function on the finite set of k-cell faces; its
simplicial degree is k−1. Boundary is the unsigned codimension-one incidence
sum (correct in characteristic two). Empty faces are included, the vertex
boundary is augmentation, and the outgoing boundary at k=0 is zero.

`MathResearch.ThirdParty.ChessboardFilling` is a **definition of a proposition**:
for s≥2 and N≥2s−1, every cycle on (s−1)-cell faces is a boundary of a chain on
s-cell faces. It is not a proof, custom axiom, or `sorry`. In particular,
compilation does not discharge external dependency H.

The route follows the current paper appendix's homological star-cover argument.
It uses a broader ν(a,b)-acyclicity induction because the smaller intersection
boards do not stay in H's narrow range. Cone contractions, simplex-boundary
acyclicity, finite cover comparison, intersection identities, and induction
arithmetic are planned building blocks, not newly claimed formal proofs.

## Tooling and checks

- Lake builds both `claims/` and `third-party-claims/`. The configuration moved
  from TOML to `lakefile.lean` because the installed TOML glob parser rejected
  the quoted hyphenated name. Dependency revisions were not changed.
- Either directory can import from the other, using for example
  `import «third-party-claims».ChessboardFilling`. Temporary cross-directory
  imports and empty-face/vertex-augmentation checks passed and were removed.
- The verifier scans both directories, quotes module path components as needed,
  and supports `Status: statement-only`. It prints statement definitions as
  well as their types and axioms, and explicitly separates them from proof files.
- [Interface verification](interface-verification.txt) passed: five existing
  proof files and one statement-only file. Standard foundational axioms in a
  proposition's definition do not constitute a proof of that proposition.
- Initial setup errors were the TOML glob and a missing finite-instance
  reduction, fixed by using a transparent face-type abbreviation. Full logs are
  archived; no new mathematical proof or numerical experiment is claimed.

Reproduce from the repository root:

```bash
./formalization/verify.sh --out research/results/NEW_RUN/interface-verification.txt
```

The recorded timed command used `--session third_party_H_route_20260915`.
The provenance manifest records the source, build configuration, verifier,
route, paper appendix, and verification output. The notebook entry
`entry-2026-09-15-third-party-H-interface` contains the full interface review.
