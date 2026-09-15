# R09: matching-moment completeness

Target audit:matching-moment-completeness, exact source notebook matching-moment-completeness-audit and paper sections/03-matching-moments.tex Lemma marginals. R05 complete at953e2da; R01/R02 integrated. R04 ambient functional extension may be used to avoid strengthening the bounded-functional statement; parent has released3fbca9c, consume safely before use.

Required scope: ordinary functional-unary generators (Boolean, same-row exclusions, same-column exclusions, row sums minus1), ordinary degree bounds on each NS multiple, complete correspondence between annihilators on degreeSpace B and matching moments of size≤B satisfying every missing-row marginal. Include both constant-moment values; normalization is extra, not assumed. N≥1 and finite m. Must prove both directions, not only construct moment functionals or verify some generators.

Reusable supporting target: matching normal form, using the same nonattacking-rook predicate as Augmented.chessboardComplex. matchingBase = Boolean+all distinct-cell row/column collisions. A linear normal form maps a monomial to its squarefree support monomial when matching and zero otherwise. Prove original-degree NS error and exact generator normalization. Identify matchingBase plus row equations with existing functionalUnaryBase rather than silently replacing the encoding.

Possible cycle split: record and release the new supporting normal-form claim separately if needed, then complete existing indexed R09 in its own record. Such a helper is not completion of R09. R10 row-set filling and R14 separation remain later assigned targets. Parent alone updates notebook living sections and route; worker appends full MathJax records and maintains index. Report any discrepancy promptly.
