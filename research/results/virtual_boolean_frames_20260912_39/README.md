# Conditional Boolean-frame compilation from PC interfaces

This is an analytic cycle. The complete statements and proofs appear in the
[12 September notebook entry](https://kbr-.github.io/math-research/#entry-2026-09-12-virtual-boolean-frames).
No new mathematical computation or numerical suite was needed.

## Exact scope

For current values of degree at most L, let A* bound the supplied OR annihilator
proofs and U* the supplied conditional unit proofs, all over one actual retained
system Gamma. The cycle establishes:

- PC Booleanity and copy ceiling B=max(A*,U*+L,2L).
- OR-relation ceiling R=max(A*,U*+2L,3L), including singleton interfaces for
  non-OR children using their independently derived PC Booleanity.
- A fixed Boolean tautology frame with m leaf occurrences has a current root
  value proof through max(R,mL). Repeated placeholders use the copy proofs.
- One MP step composes premise value proofs through max(Da,Dc,R). A fixed
  finite Boolean axiom basis therefore has a common ceiling independent of
  proof height while all these retained-system witnesses remain available.

The formal Boolean frame has an NS identity over its abstract placeholder
domains, obtained by degree-preserving multilinear reduction. After substitution,
the source's Booleanity and copy witnesses are reused as PC proofs; they are
not flattened into same-degree NS certificates. The proof counts occurrences
in the fixed frame, not the lengths of the substituted formulas.

The frame may have MOD-containing substituted formulas, whose values are Boolean.
A MOD-specific axiom relating different MOD gates is a separate obligation and
is not a Boolean tautology on independent placeholders for those gates. The
conditional compiler also does not supply strict earlier-level leaf witnesses,
choose a useful retained family, or justify repeated highest-layer omission.

## Evidence and dependencies

The notebook includes the exact frame certificates for excluded middle and
A implies (B implies A), plus three analytic countermodels when Booleanity,
the root gate relation, or repeated-placeholder agreement is omitted. These
are direct algebraic arguments, not results of an unreported finite search.

The earlier weighted-interface and copy checkers already exercise the replay
and final-line reuse used here. Their complete cycle-37 and cycle-38 results
are reused, without rerunning the suites. The older augmented-PC MP observation
is linked to distinguish the new interface generalization from that known fact.

`provenance.json` hashes the shared PC kernel, the two reused complete result
files, this README, and the claim index. The notebook's exact proof and final
timing are preserved by the Git checkpoint. Command and timing evidence is
archived under `research/provenance/session-records/virtual_boolean_frames_20260912_39/`.
Preparation includes the preceding checkpoint's archival, public-history check,
and push. No dependency, rendering audit, resource stress test, or additional
framework rule was introduced.
