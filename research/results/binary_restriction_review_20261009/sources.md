# Restriction-transfer review — source scopes

All source references below are primary research or authoritative statements.
No third-party paper text is committed.

- Smolensky, Algebraic methods in the theory of lower bounds for Boolean circuit complexity (1987), Theorem2 and its surrounding prime/field definitions and proof were read at https://people.cs.umass.edu/~immerman/cs601/Smolensky.pdf . Used only for the established fixed-depth AC0[2] MOD3 circuit lower bound, not as a new proof-complexity theorem.
- Elsheikh–Giesbrecht, arXiv1401.1773v4, Section1 Smith decomposition/determinantal divisors and the local-ring definition in Section3.1: https://arxiv.org/html/1401.1773 . Only the standard invariant-factor/rank framework is used; no typical-eigenvalue or random-density theorem is imported.
- Stacks Project, Lemma10.32.6, both proofs: https://stacks.math.columbia.edu/tag/00J9 . The second proof gives the explicit cubic correction and squared defect. This source was already queued in the preceding review; its scalar characteristic-two test is not rediscovered as a new source theorem.
- Mahler's interpolation statement was read in the official reprint abstract: https://ems.press/books/dms/252/4989 . The original scan is available at https://carmamaths.org/resources/mahler/docs/139.pdf but has no extracted text; the EMS chapter-PDF fetch failed. The erratum introduction at https://carmamaths.org/resources/mahler/docs/145.pdf identifies a correction to differentiability Theorem2, which is not used. The review's discontinuity and finite Newton calculation are elementary and supplied independently; no full-paper verification is claimed.
- Håstad, On the correlation of parity and small-depth circuits, definitions2.1–2.3, Lemmas3.3–3.8 and their proof: https://www.csc.kth.se/~johanh/paritycorr.pdf . The source has binary coordinate restrictions, AND/OR circuits and downward-closed conditioning; no categorical/MOD2 extension is assumed.
- Gao, Quantum union bounds for sequential projective measurements, Theorem1, its density/projector setup and corollary: https://arxiv.org/html/1410.5688 . Only the proposed bridge is tested; no positivity theorem is transported to characteristic two.
- Fernández–Procacci, Cluster expansion for abstract polymer models: new bounds from an old approach, Section2 definitions, self-incompatibility convention and Kotecky–Preiss conditions(2.12)–(2.15): https://arxiv.org/html/math-ph/0605041 . Its exact self-exclusion product is the calibration. This does not verify a graded or matrix-valued source expansion.

Internal records reread include the full categorical restriction proof, the affine-flow review,
defect-slice representation and later conditional-slice limits, the arbitrary-charge and Fourier
PC barriers, the binary compiler, and the preceding scheduled review's nilpotent lead.
The six completed cycle records supply their own correctness evidence; they are not rerun.

The only new computation is the constant counter-transition encoding control: all8192 Boolean
assignments, six true premises, no violations, and12 failures after dropping predecessor equality.
All other listed cheap tests are exact analytic calculations.

The sole medium reviewer first received blind-brief.md and returned blind-review.txt.
The same reviewer handles the stable route comparison and correctness gate.

Correction-stage sources: Cook–Reckhow, The Relative Efficiency of Propositional
Proof Systems, Definitions2.1–2.2 and the fixed-rule substitution argument in
Theorem2.3 were read at https://www.cs.toronto.edu/~sacook/homepage/cook_reckhow.pdf .
The counter control uses completeness only for one fixed local tautology; it
asserts some absolute bounded depth, not the same numerical depth as any chosen
presentation. The existing weighted-cofactor-Booleanization record was reread;
it concerns ordinary Boolean remainder and costed corrections, not finite
2-adic source replay.

The living summaries were consolidated under their soft targets where possible.
Removed detail remains in its linked full records; no context budget was raised.
