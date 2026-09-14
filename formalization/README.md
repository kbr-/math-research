# Lean formalization

This Lake project provides the environment for formalizing selected notebook
claims. No research result has been formalized yet; `MathResearch.lean` only
imports Mathlib polynomial algebra and the ring tactic to check the installation.

## Terminal workflow

Install [elan](https://lean-lang.org/install/manual/) once. From the repository
root, follow the resource-control setup in [COMPUTATION_RULES.md](../COMPUTATION_RULES.md),
then restore dependencies and their compiled cache:

```bash
./compute.sh --threads 2 --timeout 1800 bash -c 'source "$HOME/.elan/env"; cd formalization; MATHLIB_NO_CACHE_ON_UPDATE=1 lake exe cache get MathResearch.lean'
```

Build the project:

```bash
./compute.sh --threads 2 --timeout 600 bash -c 'source "$HOME/.elan/env"; cd formalization; lake build'
```

To check an individual file, replace `lake build` with
`lake env lean MathResearch.lean`. An editor extension is optional.

## Reproducible dependencies

- `lean-toolchain` selects the Lean version required by the pinned Mathlib revision.
  Elan installs it alongside other versions without changing the global default.
- `lakefile.toml` pins Mathlib to an exact Git commit.
- `lake-manifest.json` locks its transitive dependencies. Commit this file.
- `.lake/` contains downloaded dependencies and build artifacts and is ignored.

The cache command fetches only the modules imported by the project and their
dependencies to conserve disk space. Rerun it after adding imports. The
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
