# Lean formalization

This Lake project provides the environment for formalizing selected notebook
claims. Each result will have its own file under `claims/`, for example
`claims/ModInterpolation.lean`. No research result has been formalized yet.

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
./compute.sh --threads 2 --timeout 600 bash -c 'source "$HOME/.elan/env"; cd formalization; lake build'
```

To check an individual file, replace `lake build` with
`lake env lean claims/ModInterpolation.lean` once that file exists.
Build imported local modules first with `lake build`. An editor extension is optional.

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
