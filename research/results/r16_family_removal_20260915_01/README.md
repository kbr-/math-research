# R16 simultaneous weighted affine family removal

Completed 15 September 2026, base3141ed001d8a5ce79950baee9ae9e07c97ee5251.
Claim `lem:simultaneous-affine-family-removal`; source
`claims/AffineFamilyRemoval.lean`; full proof in notebook
`entry-2026-09-15-lean-affine-family-removal`.

## Exact verified interface

`ENSFamilyVars σ κ ι h := σ ⊕ (Σ b:κ, Fin h × ι b)`. Family values embed canonical
fresh ENS products, and the system is `(rename Sum.inl '' F ∪ booleanBase) ∪
{all companions}`. This matches the existing clause registry representation;
its `registry_fresh_value` identity supplies the specialized value bridge.
No product equations are included.

`affine_family_removal` takes old Boolean-containing F, degree<=1 inputs,
h,k>=1, D>=2h+1, target f with degree<=k, and a literal coefficient witness
of degree<=k-1 for each block with rank>h(k+1). From the actual ordinary PC
refutation through D it constructs a derivation of f through k(D+1).
Each input family is finite; the block index type need not be finite. The
original finite-family theorem is recovered directly. Neither properness nor
multilinearity of f is required. All polynomials and domains are over ZMod2.
The high-witness existence obligation itself remains R15, not assumed proved.

## Proof and dependency review

Local low-rank certificates come from R08; high coefficients go into one row.
The full weighted ledger is established at the sufficient tighter ceiling
W=kD+degree(f), then lifted to k(D+1). Every Boolean variable equation, all
companions, and each active old axiom are handled before R03 weighted replay.
The source predecessor bound uses its actual original ordinary degree.

Relative to the provisional route, proper-span cleanup, coordinate completion
and exact companion-degree theorems are not proof dependencies of this more
general removal theorem: its D>=2h+1 assumption is explicit. R08 uses Mathlib's
ordered product identity rather than the separate ENS telescoping theorem.
Those previously verified results remain for other consumers. No missing
proof was replaced by an axiom or a hidden strengthened hypothesis.

## Evidence and reproduction

`lean-verification.txt` contains the incremental build, exact full theorem type,
pinned dependencies and transitive axioms. It passes with standard foundations.
Reproduce from repository root with a fresh output path:

```bash
./formalization/verify.sh --target claims/AffineFamilyRemoval.lean --out /tmp/affine-family-removal-check.txt
```

The recorded audit adds `--session r16_family_removal_20260915_01` and uses the
canonical report path. Initial checks fixed dependent registry embedding/type
inference and the explicit NS-to-PC API; no mathematical failure or dependency
upgrade occurred. Full outputs/timing are under
`research/provenance/session-records/r16_family_removal_20260915_01/`, whose
manifest references the canonical report. `scope.md` records the initial map;
`provenance.json` hashes source, scope and report.

The printed type was reviewed against the full notebook statement. Reusing
weighted replay at its native bound avoided extra PC machinery. No new rule or
mathematical gap was introduced. R16 is complete; R15/R17 remain separate.
Coordinator-owned living notebook sections and route are unchanged. Final
commit work follows the instrumented snapshot.
