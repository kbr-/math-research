# Joint cluster constraints: correctness review

One fresh-context Codex reviewer, explicitly set to medium reasoning, reviewed
the stable draft and three exact dependency excerpts. No second reviewer was used.

Verdict: PASS, subject to one wording correction, incorporated before registration.

- Joint cluster orders: polynomial extraction supplies nu >= alpha_M in both
  alternatives. The highest coordinate has at least that valuation. Normal-coordinate
  expansion gives ordinary-power membership; extension and relabeling preserve it.
- Control polynomial: hyperplane restriction proves absence of collision factors.
  Positivity proves exact cluster order M(M-1)-2. The ceiling estimate and displayed
  degree identity give the strict bound uniformly for M >= 5.
- Flow instability and Jack comparison: the localization statements follow from the
  invariant-prefix theorem. Radical and minimal-prime stability give the contradiction.
  The symmetric derivation descends through centering and equals delta0.
- Required correction: say "Noetherian algebra over a characteristic-zero field",
  not merely "characteristic-zero Noetherian algebra"; factorials must be invertible.

No other gaps or materially unused hypotheses were found. The review confirmed that
the control is not asserted to be an original witness and that broader Jack-based
constructions are not excluded.

Dependencies supplied in full via notebook-excerpt.py:

- cube-recursive-first-step-bound
- cube-invariant-prefix-stabilization
- cube-first-step-ext-degree

The parent also re-read cube-dimensional-restriction-defect and the relevant FJMM
source statements/proofs. The reviewer used the explicitly supplied differential
stability theorem as a premise; it did not claim an independent literature audit.
