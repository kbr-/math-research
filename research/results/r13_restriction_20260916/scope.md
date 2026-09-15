# R13/R15 assignment and dependency map

Assigned Spin-formalize targets: R13 and R15. R13 is the first release.
R01-R04 belong to the foundation worker; R07 belongs to the affine worker.
No assumed theorem may replace these dependencies for R15.

R13 extracts from the paper's row-linear dimension equation and ordinary
restriction audit: row-linear ordinary polynomial space, exact dimension
sum_{j=0}^k choose(m,j) ell^j; maximal-degree nonzero coefficient; degree
preservation under affine substitution; dimension at most choose(d+k,k)
for ordinary restriction images into d free coordinates. This is not the
larger indexed row-linear quotient injection/separation theorem.

Use Mathlib MvPolynomial and natural totalDegree, matching R01. Mathlib
restrictTotalDegree has this exact membership convention. Zero polynomial
has totalDegree zero. The polynomial space is not a Boolean quotient.

Extract separate reusable claims for row-linear space/counting and generic
ordinary polynomial restriction dimension, because the latter is independent
of row structure and useful in R15. Small cardinality and coefficient helpers
stay local. Directory claims/: project supporting interfaces adapted from the
paper's recorded argument, with no novelty claim. Existing broader claims
remain unformalized.

Boundary review: k=0 includes constants, m=0 and ell=0 leave only constant
monomial; choose(m,j)=0 for j>m. Count proof can cover arbitrary k. Affine
restriction to d=0 yields a one-dimensional constant target. Nonzero maximum
coefficient covers constants as well. R15's no-high-block case needs explicit
nonzero constant and cannot divide by ell=0; the paper context has ell>0.

Plan: index row monomials by a size-j row subset and one column per selected
row. These map injectively to ordinary exponents and monomials, giving the
basis dimension. Use a maximal supported exponent for top coefficient.
For restriction dimension, encode exponent vectors of sum<=k by degree-k
multisets on Option variables (None supplies slack); stars and bars bounds
the number of monomials. Affine substitution cannot increase total degree.

Initial rule reading preceded instrumentation. No Lean computation started
before the coordinator's dependency-cache restoration confirmation.
