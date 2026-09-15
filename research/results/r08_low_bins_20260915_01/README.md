# R08 no-retained-core low-rank specialization

Completed 15 September 2026 on formal-r-affine-removal, base
802eab1dd48ec7151a774e60ed105bcac95b3b2e. Claim
`lem:low-rank-ENS-specialization`, source `claims/LowRankENS.lean`.
Full proof is in notebook entry `entry-2026-09-15-lean-low-rank-ENS-packing`.

The rank-only theorem assumes a finite family of ordinary degree<=1 F2
polynomials in finitely many variables and rank r<=h(k+1). It supplies all
coefficient polynomials of degree<=k, exact specialization of the canonical
fresh product to Z, degree(Z)<=r, the exact common-zero indicator evaluation,
and ordinary Boolean NS witnesses for each g_i Z through r+1. Properness and
independence of the displayed family are not assumed. Empty/r=0/h=0/k=0
boundaries are covered. No positive-retained-core theorem is used at t=0.

The construction chooses a basis of the input span, mutually expresses the two
families using constants, packs basis indices into bounded bins, and uses the
library ordered-product telescoping identity. The companion certificates use
the verified Boolean vanishing theorem at the original ordinary degree ceiling.
Small binning, prefix and finite-field helpers stay local; the explicit
coefficient-degree result is public for reuse. The intermediate spanning-family
argument is more general than a basis, and the final theorem recovers the exact
rank-only source hypothesis.

`lean-verification.txt` retains exact theorem types, pinned revisions,
incremental build and transitive axiom reports: two declarations passed with
standard foundations. Reproduce with a fresh destination from repository root:

```bash
./formalization/verify.sh --target claims/LowRankENS.lean --out /tmp/low-rank-ens-check.txt
```

Recorded audit used `--session r08_low_bins_20260915_01` and the canonical
report path. Earlier checks exposed indicator-Decidable rewriting, local
abbreviation unfolding, finite-span instance and subtype-coercion issues;
all were fixed. No false mathematical claim or dependency upgrade was needed.
Full failed and successful outputs are archived under
`research/provenance/session-records/r08_low_bins_20260915_01/`, referencing the
canonical audit report without duplication. `scope.md` is the pre-proof map;
`provenance.json` hashes it, the source and report.

Printed types were reviewed against the full notebook claim. R08 is complete;
R16 must still assemble low/high cases with the complete axiom ledger and
weighted PC replay. No new mathematical gap or guidance rule was needed.
Living notebook sections and route remain coordinator-owned. Final commit
work follows the instrumented snapshot.
