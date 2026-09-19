# Existing formalization mappings: route-map reconciliation

This is an exhaustive source-relative reconciliation of the **75 currently mapped
claims and 77 scoped artifacts**, not new Lean development or a fresh kernel replay.
The authoritative index was not edited. `report.json` is the complete per-claim
inventory; `reconcile.py` reproduces the mechanical comparisons, fingerprints and
proposed wording changes.

## Coverage and result

- **68 claims** map to the publication formalization route. Every one of its
  **38 planning obligations (R01–R25, H01–H13)** has explicit claim coverage.
- **Six claims** map to all four later dependency/scope maps: exponential bit-PHP,
  generic subspace consequence, generic CNF bridge/criterion, and density/control.
- **One claim**, MOD interpolation, is explicitly outside the publication route.
  Its existing general-ring interpolation/degree proof remains independently mapped.
- Every mapped Lean source is unchanged from the earlier audited formalization
  inventory. Every declaration actually claimed by each artifact occurs in its
  existing successful named-axiom evidence, with only the accepted foundations.
- The import-only `BitPHPPreprintRevision1.lean` aggregate has no mathematical
  claim to index and is explicitly accounted for separately.

**No completion-status, formalization-ownership or theorem-scope mismatch was
found.** Four harmless historically prospective scope phrases say that the actual
common-kernel assembly “remains R15”, although R15 is now complete. The proposed
changes replace that wording with a link-by-label to the separately verified
`lem:common-affine-restriction-kernel`. They do not expand the helper claims.
Exact before/after fields are in `proposed-corrections.json`; applying them requires
the coordinator to refresh those formalization review fingerprints.

## Scope checks that matter

The complete route and all four later maps were read, together with all 75 current
structured scope dispositions. The report records the exact route rows and source
headers beside every artifact so coverage is reviewable without rereading proofs.

- R06 keeps the loose-ceiling companion equality **refuted**, with identity and
  upper bounds complete. R07's fresh genuine degree-one setup supplies the separate
  exact companion degree. A counterexample artifact is not a proof of the false claim.
- H's definition-only module is **statement-only**; the separate proof module
  establishes the full original filling proposition, including augmentation.
  H12 is binary homological vanishing, not homotopical connectivity.
- R10 preserves the verified arbitrary-row generalization and explicitly removes
  the unnecessary `m >= B` source assumption. Stable PC=NS is not attributed to R01.
- R05 is the binary Boolean result, not the historical full all-prime mixed-domain
  statement. R08 is no-retained-core packing, not the larger retained-core optimum.
- R11 covers local two-row interpolation, not the full column normalizer. R12
  distinguishes coordinate injectivity for all bit lengths from actual PC transfer
  requiring bit length at least two; no whole transported-filtration package inferred.
- R13 is ordinary polynomial dimension/top-coefficient data, not quotient injection.
  Four extra header-listed elementary helpers lack individual printouts in the chosen
  report; the artifact correctly claims only its four reported principal declarations.
  Their checked transitive proofs use the helper code. No fresh helper verification
  is asserted or needed for the artifact's stated route obligations.
- R15 uses **ordinary** zero restriction and literal coefficients, not merely zero
  evaluation over the finite field. R16's later unit-span alternative is separately
  recorded while its literal-only wrapper remains available.
- R19/R20 import sharing is not a theorem dependency on the semantic separator.
  R21's local semantic derivation is separate from R22/R23 concrete PC certificates
  and R24's complete shared DAG assembly. Existing scope wording preserves this.
- Later shared `GenericCNFSubspaceCriterion.lean` ownership is split: three bridge
  declarations versus two DAG/criterion declarations. The generic subspace claim
  does not absorb those later results. Density has explicit `r <= v`, no formal
  asymptotic claim; short-proof control is not a general audit of short refutations.
- The exponential bound retains the concrete `ell >= 32` threshold and both rule
  conventions. The publication theorem is eventual for every positive real exponent.
  This reconciliation makes no new publication-readiness or novelty determination.

## Evidence and limits

`report.json` includes source/map/report SHA-256 values, each artifact's exact
scope and declaration list, all mapped route rows, the live registry fingerprint
and the baseline commit. Both mechanical passes reported zero errors. These
checks establish consistency with the existing recorded verification and route
boundaries; they do not replace mathematical statement review or rerun Lean.

A short formalization-policy read preceded instrumentation. Session
`parallel_formalization_route_reconcile` is exported and archived. The coordinator
owns final notebook integration, canonical metadata changes and the Git checkpoint.
