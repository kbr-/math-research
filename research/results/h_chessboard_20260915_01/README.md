# H08 verification evidence

Source: whitepaper sections/08-topology.tex, classical first-row star argument.
Formalized: closed stars are subcomplexes and cones (literal insertion closure), and cover (a+1)-by-b boards for a+1≤b. Shared finite-cover definitions retain empty faces and use a common vertex for nonempty nerve faces. H04 supplies homological cone exactness separately.

Commands and full results are archived with timing session h_chessboard_20260915_01. The local pinned dependency cache was restored in this isolated worktree. An attempted Mathlib.Tactic.Omega cache name does not exist in this pinned Mathlib and was skipped; no source imports it. Lean built missing pinned imports locally. Initial proof-check failures were API naming and membership/coercion errors, not mathematical counterexamples. Full verifier prints declaration types and axioms in verification.txt; only standard Lean axioms are permitted.

No new mathematical gap was found. No unproved custom proposition is assumed. All new mathematical definitions/results are indexed. Small matching-extension helper remains local to its sole use. Shared FiniteComplexCover is separate because the homology branch consumes it independently.
