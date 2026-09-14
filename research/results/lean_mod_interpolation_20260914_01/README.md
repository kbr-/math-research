# First Lean formalization: MOD interpolation

The [Lean source](../../../formalization/claims/ModInterpolation.lean) formalizes
`lem:mod-interpolation` from the notebook's `mod-pruned-polynomial` section.
The full argument and scope review are recorded in the notebook entry
`entry-2026-09-14-lean-mod-interpolation`.

`MathResearch.mod_interpolation` proves the factorization and joint total-degree
bound p-3 for every natural p≥3 over any nontrivial commutative ring.
`MathResearch.mod_interpolation_two` proves the zero identity for p=2 over any
commutative ring. The two variables are independent indeterminates in
`MvPolynomial (Fin 2) R`; no Boolean or field quotient is imposed.
The surrounding MOD-axiom NS certificate and source substitution are not
formalized by this file.

## Reproduction

Restore the pinned dependencies as described in the
[Lean project guide](../../../formalization/README.md), then from the root run:

```bash
./formalization/verify.sh --out research/results/NEW_RUN/lean-verification.txt
```

For this timed turn, the identical verifier worker was invoked inside the
existing research session:

```bash
./compute.sh --session lean_mod_interpolation_20260914_01 --threads 2 --timeout 600 --category local_processing bash -c 'source "$HOME/.elan/env"; python3 formalization/verify.py --out research/results/lean_mod_interpolation_20260914_01/lean-verification-final.txt'
```

The [final output](lean-verification-final.txt) records dependency commits,
the successful build and fresh elaboration, and both axiom reports. Each lists
only `propext`, `Classical.choice`, and `Quot.sound`; no `sorryAx` or custom axiom
is present. This is universal formal proof checking, not finite numerical testing.

The initial direct check required marking abstract polynomial definitions
noncomputable and removing an unused section hypothesis. The
[first full verification](lean-verification.txt) then rejected a missing section
terminator. Both were Lean setup/syntax issues, not mathematical counterexamples.
All command output, including the initial dependency-cache download and failed
checks, is retained in the archived timing session. The cache's missing-file
warning concerned a local project module; the final local build succeeded.

The provenance manifest hashes the source, dependency configuration, verifier,
and verification records. Timing is exported into the notebook and archived
under `research/provenance/session-records/lean_mod_interpolation_20260914_01/`.
