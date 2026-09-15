# Boolean/matching branch scope

Assigned Spin-formalize set: R05, R09, R10, R14 of BIT_PHP_FORMALIZATION_ROUTE.md. Exclusive worktree boolean-matching, branch formal-r-boolean-matching, initial pin3c0a92f. Parent owns all notebook living sections and route; this worker appends full per-claim records, indexes new claims, reports proposed living changes/gaps, and releases clean checkpoints for coordinated integration. No pushes or uncoordinated rebases.

R05: extract the binary degree-controlled Boolean reduction helper from historical lem:fieldreduction and whitepaper Lemma boolean. For a polynomial P over F2, define squarefree remainder red(P), prove its individual degrees≤1 and total degree≤degP, with P−red(P) in the ordinary NS space through degP. Prove Boolean-grid vanishing implies NS membership, and q²−q has an NS certificate through2degq. This does not claim the historical all-prime mixed-domain lemma is fully formalized. Include zero/constant polynomials and empty variable sets.

R01/R02 foundations are owned by r_foundations: namespace MathResearch.PolynomialCalculus, Poly K V=MvPolynomial V K, nsSpace F B=span{q*f | f∈F, degree(q*f)≤B}; booleanBase={Xv²−Xv}. No quotient degree is substituted for ordinary degree. Pinned Mathlib's MvPolynomial.eq_zero_of_eval_eq_zero on restrictDegree(card(F2)−1) can supply grid injectivity, with exact finite-variable hypotheses checked.

R09: existing audit:matching-moment-completeness, full normal-form/every-row-marginal equivalence for ordinary bounded-degree linear annihilators, all constant-moment values. R01+R05 required.
R10: existing audit:matching-extension-arbitrary-row-count, arbitrary m≥B,N≥1,N≥2B−1, k≤B, cycle/filling row-set construction, prescribed constant preserved, stability and PC=NS. R02/R04+R09+proved H required. It is not enough merely to restate the already proved H.
R14: existing lem:cube-residual-dual-separation, actual cube/residual design construction and separator for decoded nonzero row-linear f, including all parameter conditions. Depends R09/R10 and R12/R13 released by other workers.

Initial policy and restart-guide reading preceded timing; all subsequent review is instrumented. Parent restores private .lake; no Lean before readiness confirmation.
