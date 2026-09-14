# Lean formalization

This Lake project provides the environment for formalizing selected notebook
claims. Each result has its own file under `claims/`. The
[claim index](../research/CLAIM_INDEX.md) links formalizations and records their
exact verified scope; this guide covers setup, structure, and verification.

For an assigned formalization, follow [AGENTS.md](AGENTS.md): establish the exact
statement first, prove it, then review the verified type against the notebook.

Files can depend on other claim files using imports such as
`import claims.ModInterpolation`. Lake discovers all Lean modules under
`claims/` and builds them in dependency order; no aggregate file is required.
Each file should identify its claim-index label and notebook source, and import
only the dependencies it needs. Shared definitions can be factored into a
separate module when needed.

## Terminal workflow

Install [elan](https://lean-lang.org/install/manual/) once. From the repository
root, follow the resource-control setup in [COMPUTATION_RULES.md](../COMPUTATION_RULES.md),
then restore dependencies and their compiled cache:

```bash
./compute.sh --threads 2 --timeout 1800 bash -c 'source "$HOME/.elan/env"; cd formalization; MATHLIB_NO_CACHE_ON_UPDATE=1 lake exe cache get Mathlib.Algebra.Polynomial.Div Mathlib.Tactic.Ring'
```

Build the project:

```bash
./compute.sh --threads 2 --timeout 600 --category formal_verification bash -c 'source "$HOME/.elan/env"; cd formalization; lake build'
```

To check an individual file, replace `lake build` with
`lake env lean claims/ModInterpolation.lean`.
Build imported local modules first with `lake build`. An editor extension is optional.

## Claim records and verification

Start each claim file with a header like this, filling in its exact scope and
all result declarations:

```lean
/-
Claim: lem:mod-interpolation
Source: https://kbr.is-a.dev/math-research/#mod-pruned-polynomial
Scope: State the exact coverage and any differences from the informal claim.
Declarations: MathResearch.mod_interpolation
-/
```

List every declaration offered as a verified result, using fully qualified names
separated by spaces. Explain strengthened hypotheses, missing degree bounds,
or other limitations in `Scope`; a verified special case is not the full claim.
Shared helper modules under `claims/` use the same header, identifying their
supporting role and listing the helper declarations to audit.

From the repository root, run the complete verification command:

```bash
./formalization/verify.sh
```

It builds under `compute.sh`, rechecks each claim file with warnings treated as
errors, and prints each listed declaration's type with `#check @name`, including
implicit parameters, alongside `#print axioms`.
Unfinished proofs
(`sorry` or `admit`) are not accepted. Axiom reports may contain only the standard
Lean foundations `propext`, `Classical.choice`, and `Quot.sound`; `sorryAx`, custom
axioms, and other additions fail verification. In particular, do not replace an
unproved step with a custom axiom. The command reports an empty project as setup
only, never as a verified research result.

During a research turn, attach verification to its existing timing session and
preserve the complete output in a new evidence file:

```bash
./formalization/verify.sh --session TURN --out research/results/TURN/lean-verification.txt
```

Use `./compute.sh phase TURN formalization` while designing and coding the Lean
proof, following the phase distinctions in [COMPUTATION_RULES.md](../COMPUTATION_RULES.md).
The wrapper records the command as `formal_verification` in that session without starting or stopping
the overall research clock. Without `--session`, the launcher creates an
automatic command session. Output includes dependency revisions, declaration
types, and axiom reports. Commit it with the formalization and notebook entry
under the root research protocol. The separate statement-review obligation is
defined in [AGENTS.md](AGENTS.md).

Lake builds incrementally, reusing compiled modules whose sources and
dependencies have not changed. The verifier deliberately also re-elaborates
every claim file for a full audit. Keep this behavior while it is inexpensive.
If repeated full checks become noticeably costly, add an incremental development
mode and retain the full audit for research checkpoints; this is a deferred
improvement, not a requirement to add another mode now.

## Reproducible dependencies

- `lean-toolchain` selects the Lean version required by the pinned Mathlib revision.
  Elan installs it alongside other versions without changing the global default.
- `lakefile.toml` pins Mathlib to an exact Git commit.
- `lake-manifest.json` locks its transitive dependencies. Commit this file.
- `.lake/` contains downloaded dependencies and build artifacts and is ignored.

The cache command fetches the initial polynomial algebra and ring tactic modules
and their dependencies. Once a claim file exists, pass its path to `cache get`
instead to fetch exactly its imported dependencies. The
environment variable prevents initial dependency setup on a fresh checkout
from also requesting the full Mathlib cache.

Use the checked-in versions when restoring the project. Dependency upgrades
should be deliberate changes to the toolchain, Mathlib pin, and manifest,
followed by a cache download and build. See the
[Mathlib project guide](https://leanprover-community.github.io/install/project.html).

Future formalizations belong in the `MathResearch` namespace and should link
their exact statements to the claim index and notebook record. Follow the root
research protocol when beginning that work; environment setup alone is not a
formal verification of a research claim.
