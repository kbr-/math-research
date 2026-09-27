# Consolidated correctness review — 28 September 2026

One fresh-context Codex reviewer, explicitly medium reasoning, reviewed the stable
draft, integer driver and retained output, with exact dependency excerpts.
No computations were rerun and no second reviewer was used.

Verdict: Pass, with no blocking mathematical issues or unused substantive hypotheses.

- The t-regular upper quotient gives genuine fibre injection and Hilbert subtraction.
- Deflation gives weights 4,5,6,6,7,8; universal cyclic columns give 60 > 54.
- PID decomposition forces actual source vertex torsion, with dim(T6/tT6) >= 6.
- Spectator extension gives depth N-6, below dimension N-5, for every N >= 6.
- The four-action graph Koszul resolution correctly excludes A_N-freeness.

The review's gradedness clarification is incorporated: a polynomial g(t) with
nonzero constant term acts injectively by the lowest homogeneous component.
All polynomial torsion is consequently t-primary, and homogeneous localization
shows that the torsion submodule is graded.

Dependencies read in full for the proof:
- cube-marked-ore-deflation
- cube-triple-double-normalization-quotient and its closed verification gate in
  entry-2026-09-27-cube-bounded-residual-source
- cube-normalization-koszul-resolutions
- entry-2026-09-27-cube-residual-kernel-support
- cube-triple-triple-transverse-residual
- cube-simple-spectator-formal-stability

Root novelty check distinguished earlier non-CM of the full defect and torsion
in a quotient detector image from the present actual residual-source assertion.
No literature novelty is claimed.
