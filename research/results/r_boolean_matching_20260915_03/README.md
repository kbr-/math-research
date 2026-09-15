# R09 complete: matching-moment ordinary-NS correspondence

Claim audit:matching-moment-completeness is fully covered for the source's N≥1, arbitrary natural m,B, and arbitrary constant moment. No global-functional hypothesis is substituted for the actual bounded-degree domain. The reusable supporting claim lem:functional-matching-normal-form has its own file/index entry and full proof in the same research record. R09 source: matching-moment-completeness-audit and paper sections/03-matching-moments.tex. Full new record: entry-2026-09-15-lean-matching-moment-completeness.

## Main interfaces (MathResearch.PolynomialCalculus)

Cell m N = Fin m × Fin N. IsMatching S is exactly membership in Augmented.chessboardComplex m N. RowUnused/ColUnused quantify absence of a row/column. matchingBase is BOOL plus all distinct-cell same-row/column collision equations. functionalUnaryBase_eq proves equality with matchingBase ∪ rowBase, preserving the original R01 encoding.

matchingNormal m N is a linear polynomial map replacing each monomial by its squarefree matching monomial or zero. matchingNormal_ns proves its original-degree NS error; matchingNormal_degree its nonincrease; matchingNormal_kernel identifies the bounded Boolean/exclusion kernel. matchingNormal_row_unused and matchingNormal_row_occupied are exact polynomial identities. rowEquation_degree requires N≥1 and proves actual degree1, not merely a ceiling. Pure matching normal-form facts also cover empty boards.

MatchingMarginals m N B z requires all missing-row equations for matching S with S.card<B. z is represented on all finite cell sets for convenient extension, but values at nonmatching or larger supports do not affect the bounded correspondence. momentFunctional is an explicit linear map with the exact monomial rule; momentFunctional_support recovers each matching moment and momentFunctional_one equals z empty. momentFunctional_annihilates constructs an ordinary-NS annihilator from any marginal-compatible z.

matching_marginal_completeness gives the two-way ambient functional constraint equivalence. bounded_matching_moment_completeness gives the actual target: for L:degreeSpace B→ₗF2F2, BoundedAnnihilator iff there exists marginal-compatible z whose momentFunctional restricts to L. bounded_moment_recovery recovers z(S) from each matching monomial with |S|≤B. Thus this is full existence and recovery, not only a necessary-marginal check.

## Verification and dependencies

normal-form-verification.txt audits21 public declarations; completeness-verification.txt audits12. Both use incremental protected verify.sh --target and print complete types/transitive standard axioms. R01/R02/R05 and the shared pair certificate are reused; R04 annihilator_extension is used for the bounded-to-ambient bridge. This means the actual R09 implementation depends on R04 as well as the original R01/R05 route list. Parent was asked to maintain the route accordingly. H's exact face definition is reused, not an unproved topological assertion.

Full command output and timing are archived canonically. Failures concerned pinned coefficient/monomial APIs, classical decidability elaboration and simple coordinate rewrites; no mathematical discrepancy was found. The N=0 row-generator boundary was reviewed and the original N≥1 hypothesis retained. Existing guidance permitted the broader pure kernel facts; no optional reworking of completed claims was performed.

Parent owns living notebook sections and route; this worker appended the full MathJax proof and updated only the claim index. No main change, push or extra agent was performed. R10 extension/stability/PC=NS and R14 separation remain subsequent assigned work, not completion implied by R09.
