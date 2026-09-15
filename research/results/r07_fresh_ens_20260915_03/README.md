# Canonical fresh ENS block degrees

Completed 15 September 2026 on formal-r-affine-removal, base
6a21b1743c4535850567f84a46b16e13a30d032a. Extracted claim
`lem:fresh-ENS-block-degree`; full proof in notebook
`entry-2026-09-15-lean-fresh-ENS-degrees`.

`claims/FreshENSBlock.lean` defines variables `σ ⊕ (Fin h × ι)`, factors,
product and companions. Eight audited results prove factor/product/companion
upper bounds, exact degrees under an actual degree-one selected input,
injective rename degree preservation, and the whole-product renaming identity.
The latter supports a global dependent-sum coefficient registry without a
second block definition. All degree statements use ordinary total degree;
h=0 and zero/empty-input upper-bound cases are included. All hold over any field.

The product equality needs some actual degree-one input, and the companion
equality needs that companion's input to have actual degree one. The previous
proper-span theorem supplies this condition for each retained nonzero affine
input. No equality is inferred from a loose degree ceiling.

`lean-verification.txt` preserves exact theorem types, pinned dependency
revisions, the incremental build and transitive axioms. All eight declarations
pass with standard foundations only. Reproduce with a new output path:

```bash
./formalization/verify.sh --target claims/FreshENSBlock.lean --out /tmp/fresh-ens-check.txt
```

The recorded audit adds `--session r07_fresh_ens_20260915_03` and uses the
canonical evidence report. Its imported PC substitution/reuse modules were
built in dependency order after the initial direct check reported their absent
local .olean. Some pinned Mathlib dependencies also built locally. Subsequent
checks fixed classical decision instances, explicit rename equalities and
unused-section-variable warnings. Full failed and successful outputs are kept;
no false mathematical statement was found. No dependency version was changed.

`scope.md` records the initial plan, including scalar cleanup as the next
remaining R07 task. This release is only the exact fresh-degree component;
zero/unit scalar substitution and its PC replay are not yet claimed complete.
`provenance.json` hashes source, scope and canonical report. The archived session
under `research/provenance/session-records/r07_fresh_ens_20260915_03/` references
that report instead of duplicating it.

Printed theorem types were checked against the full notebook statement.
Coefficient selection plus degree-preserving substitution avoids expanding
large products; small supporting rename/product helpers stay local. This uses
existing guidance without adding another rule. The coordinator owns the living
notebook overview and route. Final commit work follows the timing snapshot.
