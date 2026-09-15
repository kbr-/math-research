# Full R15 assignment and dependency plan

Target: actual common ordinary restriction kernel for h=3ell,
k=ceil(sqrt(m*log(4M))), k<=m, with nonzero f in rowLinearSpace and literal
coefficients of degree<=k-1 for every high-rank block. No abstract dimension
hypothesis is a substitute for the concrete numeric argument.

Use actual variables Fin m × Fin ell and finite affine-map input tuples,
converted through finiteAffinePolynomial (matching R18/R24 and R16 inputs).
Assume m>=1, ell>=1, M>=1 as in the publication's bit-PHP regime; clarify any
stronger source-context restrictions rather than adding them silently.

Supporting work:
1. Generalize coordinate completion to arbitrary finite coordinate types, using
   existing finite affine span witnesses; this supplies the actual bit type.
2. Prove ordinary restriction zero implies literal degree-(k-1) coefficients,
   by affine polynomial coordinate changes and factoring selected variables
   from every supported monomial. Pointwise-zero alone is insufficient.
3. Prove the concrete binomial/exponential estimate. A simpler sufficient
   factorial comparison may replace the source's exact product identity, but
   must deliver the same exp(-k²/m) factor and ceil/sqrt/log bound. Handle the
   no-high-block case before dividing by dimensions or positive parameters.
4. Apply finite-dimensional joint-kernel counting to actual restriction maps;
   use rowLinearSpace dimension and convert zero restrictions to coefficients.

Each reusable dependency gets its own claim/file and full human-readable record.
No new claims of novelty. Generalizations allowed only with exact original
application recovered. R15 remains incomplete until all four obligations and
the actual final target are checked. Parent owns living sections/route.
