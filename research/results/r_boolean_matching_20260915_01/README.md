# R05: binary degree-controlled Boolean reduction

Completed claim: lem:binary-degree-controlled-Boolean-reduction. Full MathJax statement and proof: notebook entry entry-2026-09-15-lean-boolean-reduction, anchor lean-binary-degree-controlled-Boolean-reduction. This is the route's extracted binary helper, not the broader all-prime mixed-domain historical claim.

The implementation proves squarefree individual and total degree bounds, pointwise equality, original-degree NS remainder certificate, zero-grid certificate and q²−q through2degq, with supplied-ceiling variants. It includes zero/constant/empty-variable cases. Natural totalDegree assigns zero to zero. Finite types live in Lean Type, matching all route encodings; no mathematical hypothesis beyond finite variables is imposed. Standard finite-field interpolation in pinned Mathlib supplies grid injectivity, with its dimension/indicator proof explained in the notebook.

Dependencies: parent R01 release76cc94b and R02 release866df1edc4a6f693447c49d125496136b13ebc6e consumed via clean stash/rebase/pop before dependent work. Uses nsSpace_mul from R02, so the implementation dependency map is R01+R02, slightly larger than the initial route's R01 list. Parent was asked to update the route accordingly. No duplicate foundations or custom axioms.

Verification command:
./formalization/verify.sh --target claims/BooleanReduction.lean --session r_boolean_matching_20260915_01 --out research/results/r_boolean_matching_20260915_01/verification.txt

PASS:12 audited declarations with only propext,Classical.choice,Quot.sound. Incremental verification checks this module and all its transitive axioms, not unrelated claims. All command outputs are archived; verification.txt is canonical under the current archival policy. The first180-second build timed out while compiling missing finite-field Mathlib imports, before checking the draft. A300-second incremental retry completed setup and reported proof API errors; later checks fixed them. These were setup/type/API issues, not mathematical counterexamples.

The certificate helpers are local to this claim; no independently reusable mathematical theorem needed splitting beyond the existing R01/R02 interfaces. The public supportMonomial and squarefreePart interfaces support R09. Initial policy/restart-guide reading preceded timing; a labeled coordination-wait phase separates cache/foundation waiting. Parent alone owns living notebook sections and route; neither was edited here. No new mathematical gap was found.
