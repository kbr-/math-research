# Independent correctness audit: Pang v1

Audit date: 7 October 2026. Source: Shuo Pang, [*A Degree–Size Relation for Resolution over Polynomials*, arXiv:2610.00837v1](https://arxiv.org/html/2610.00837v1).

**Verdict.** The ordinary unary PHP conclusion survives this audit. I found no fatal gap or repairable mathematical gap in the proof chain inspected. This is a substantive proof audit, not a formal verification or a claim that every theorem in the paper has been verified. The central argument was checked independently through Sections 2–6; the PHP and bit-PHP applications were checked against their imported degree theorems and their reductions. The imported general PC lower-bound machinery remains a literature dependency.

The claim audited is a lower bound for unrestricted **syntactic DAG** proofs with Boolean variables, prime-field coefficients, the displayed linear-combination and multiplication rules, and size measured by nodes. Theorem 7.2(d), specialized to degree-one equations, covers ordinary complete unary PHP with one more pigeon than holes. The optional characteristic-two comparison is separate from this conclusion.

## Findings and classification

| Item | Audit classification |
|---|---|
| Multiplicity estimate and rank specialization | Passed proof check |
| Frobenius descent over the rational-function field | Passed proof check, including coefficients of kernel vectors |
| Bounded-degree PC multiplication and base change | Passed proof check; no saturation or unrestricted-ideal inference found |
| Standard-monomial normalized-rank argument | Passed proof check |
| Approximation gain and common kernel | Passed proof check with degree ledger below |
| Syntactic rule simulation and main constants | Passed proof check |
| Graph, functional, ordinary and complete PHP transfer | Passed import-hypothesis and reduction check |
| Bit-PHP substitution and local axiom derivations | Passed proof check |
| Characteristic-two semantic weakening | Passed via the direct additional justification below |
| Other applications and their literature imports | Outside this audit; no verification claimed |

No counterexample was found. No computational enumeration was used: these are symbolic argument checks, and finite matrix samples would not settle their all-parameter obligations.

## Algebraic checks

**The truncated space really suffices.** Starting with an already derived polynomial of actual degree $j$, one can append a variable-by-variable derivation of each of its monomial multiples. Thus multiplying it by a polynomial of degree $e$ costs at most $j+e$, in addition to the degree already used to derive the starting polynomial. It does not require replaying the old derivation after multiplying all of its lines. This distinction validates the absorption property used throughout the proof.

The field-extension version is also justified. Intersecting with a fixed degree filtration commutes with extending scalars. Consequently, an extension-field polynomial of degree $j$ in the extended consequence space has an expansion using base-field consequences of degree at most $j$. This prevents cancellation among high-degree terms from invalidating the multiplication bound. At no point is the truncated consequence space treated as an unrestricted ideal.

**Specialization.** For a nonzero minor determinant, rank deficiency at a specialization is bounded by its order of vanishing there: row reduction at that point makes the requisite number of rows have zero constant terms. The determinant then has no terms below that number. The multivariate multiplicity estimate follows by choosing a lowest-degree nonzero coefficient in the shifted leading coefficient in the last variable, and applying the univariate root-multiplicity bound to that coefficient polynomial. The total-degree induction has the necessary inequality $\deg H_t+t\leq\deg H$. This proof does not require a nonvanishing evaluation of the determinant on the finite grid.

**Frobenius and kernel coefficients.** Entrywise Frobenius preserves the pivot pattern of a reduced row-echelon basis. Its rows remain independent even if the field is imperfect, because their pivot submatrix is still the identity. If the original row space is Frobenius-stable, equality of dimensions and uniqueness of reduced row-echelon form force all its entries into the prime field. Surjectivity of Frobenius is unnecessary.

For the two parameter matrices, their corresponding minors are Frobenius powers, so they have equal ranks. The assumed kernel inclusion is therefore equality. Applying Frobenius to a kernel vector raises **both** the parameters and the coordinates of that vector; kernel equality puts the resulting vector back in the original kernel. This is exactly what the row-echelon argument needs. It would be wrong to leave the vector coefficients unchanged at this step; the paper does not do that.

For the multiplication-map application, keep the extension-field polynomial $f$ unchanged while multiplying the known consequence by the $(p-1)$-st power of the parameter combination. The necessary product degrees are at most $b+k+pa$. Separately, each base-field polynomial $g_i$ satisfies the Boolean consequence $g_i^p-g_i$. Multiplying this consequence by $h_\alpha f$ has the same bound. Subtraction gives the required parameter-Frobenius kernel inclusion. This argument neither asserts $f^p=f$ nor extracts roots of its rational-function coefficients.

**Normalized rank.** The kernel spaces have the two properties actually needed: compatibility under intersection with the degree filtration, and closure under multiplication while staying within the permitted degree. With a degree-compatible order, their standard monomials therefore form a downward-closed family. Boolean consequences exclude squareful standard monomials. Counting incidences between its degree-$j$ and degree-$j+1$ layers yields decreasing layer densities in the Boolean lattice. The cumulative density decreases as well, since each added layer density is at most the previous weighted average. There is no appeal to a full Gröbner ideal or to consequences above the truncation degree here.

## Degree and dimension ledger

Write $a$ for the current approximator degree, $d$ for the degree bound on the family, and $K$ for the multiplier-domain degree. The following independent bookkeeping checks cover the delicate operations in the gain argument.

| Operation | Upper bound on degree |
|---|---:|
| Multiply an old error by one family polynomial, with input degree at most $K-d$ | $a+K+d$ |
| Turn a diagonal square error into a $p$-th-power error | $a+K+(p-1)d$ |
| Subtract the corresponding Boolean Frobenius consequence | $a+K+(p-1)d$ |
| Apply multiplication-map descent | $a+K+pd$ |
| Preserve an old kernel vector under the new approximation factor | $a+K+pd$ |
| Kill a vector of the form $qf$, using $q-q^p$ | $a+K+pd$ |

The diagonal-square step is valid also for $p=2$, when the extra multiplier has exponent zero. Conversely, the off-diagonal components follow from ordinary bounded-degree multiplication. Hence the stacked-map kernel is the old error kernel, rather than merely containing it.

The rank retained by $q$ counts the dimension of $qV_{K-d}$ modulo its intersection with the old kernel. The new kernel contains both that subspace and the old kernel. Subtracting their dimensions gives the asserted gain; possible intersections are counted correctly. Before the final iteration, substituting $a=(t-1)(p-1)d$ in the most demanding bound gives exactly the common-multiplier theorem's total degree allowance.

For the final dimension argument, all error maps kill the low-degree intersection with the consequence space. Their total rank is strictly smaller than the dimension of the resulting quotient. A common-kernel vector outside the consequence space follows. Multilinearization changes that vector by a Boolean consequence and preserves all its kernel memberships at the available degree. There is no assumption that the ordinary polynomial-space dimension equals its Boolean quotient dimension.

## Simulation and numerical constants

The identity expanding one minus an approximator has coefficient degree at most $\Delta-d$: expand each power using one factor from its defining linear combination and telescope the product. This is a polynomial identity, not merely a functional equality.

The induction is over a topological ordering, so it imposes no tree-like restriction. Input CNF clauses use their actual falsity axioms. For a premise with one distinguished equation, multiplying the expansion identity by the conclusion approximator first produces the required residual relation; removing its distinguished indicator uses its Boolean idempotence. The degree cost here is $K+2\Delta+d$.

In a binary linear-combination inference, multiplying one such residual relation by the other indicator raises this to $K+2\Delta+2d$. The remaining vanishing term and error multiple cost at most $K+\Delta+3d$, which fits because $\Delta\geq d$. Multiplication inferences use the implication that a zero factor makes the product zero; their functional identities are derivable from Boolean axioms at their displayed degrees. False constant equations have zero indicators and cause no missing summand. Contraction and weakening are covered by the expansion identity. The last empty line has approximator one, producing the contradiction with the chosen multiplier.

The constants have slack. The theorem's lower threshold gives $D\geq32(p-1)d$, hence $K\geq2d$, $t\geq1$, and $2d\leq D/16$. The chosen parameters satisfy the simulation degree bounds, and also $\Delta+K+d\leq D$, as required by the multiplier construction. The binomial-ratio estimate uses $K\leq n/3$, follows by comparing consecutive binomial coefficients, and uses $K\geq D/8$ after rounding. Finally,

\[
t\geq\frac{D}{16(p-1)d},\qquad
\eta\geq\frac{p-1}{2p}\left(\frac{D}{16n}\right)^d
\]

give a lower bound $D/(32pd)$ times the displayed power. Since $d=(p-1)r\leq pr$, this is at least the weaker coefficient in the theorem. Thus neither rounding nor the last relaxation reverses the inequality. The completeness upper bound of $n+1$ already suffices to infer $D\leq n$; the stronger CNF-specific observation is not essential.

## PHP imports and reductions

The primary imported source checked was Mikša–Nordström, [journal author version](https://jakobnordstrom.se/docs/publications/GeneralizedMethodPCdegreeJournal.pdf), especially its conventions in Section 2 and Theorems 5.4 and 5.8 with their application proofs. The corresponding older statements, Theorems 4.5 and 4.9, were also located in [arXiv:1505.01358](https://arxiv.org/pdf/1505.01358).

The source works over every field. Its truth-value convention is opposite to Pang's, but the affine involution $x\mapsto1-x$ changes one encoding to the other without increasing PC degree: a multiplication step becomes a linear combination of an old line and its variable multiple. The functional graph theorem applies with bounded **left** degree; it does not require exactly one more pigeon, which matters for bit-PHP. The onto theorem requires the one-pigeon surplus and nonisolated holes. Its matching premise follows from Pang's boundary expansion at least one: every subset of a small pigeon set has at least its size in neighbours, so Hall's theorem applies. Pang's no-isolated-holes hypothesis handles the condition explicitly present in the newer source. The older onto statement's omission of this condition is not inherited by Pang.

The functional import's application proof was checked: a variable cluster for a hole contains all variables belonging to pigeons adjacent to that hole. Setting one selected incident edge true and every other variable in the cluster false respects both collision and functionality clauses. Each variable occurs in at most the left-degree bound number of clusters. This checks the source theorem's translation, while its underlying general respectful-expansion theorem remains an imported result.

For ordinary PHP the implication direction is correct: any proof from the smaller axiom set is also a proof after functionality axioms are added. For complete PHP, restricting nonedges to zero gives the appropriate graph formula. Formal substitution preserves the syntactic algebraic rules and polynomial degree; tautological restricted input lines can be supplied using the true-equation axiom and weakening if necessary. Even allowing constant overhead for that convention leaves the claimed exponent intact. The graph formulas have linearly many variables and bounded width; the complete formulas' quadratic variable count is therefore never inserted into the degree–size bound.

The claimed expander availability is consistent with a direct first-moment check. For $N<m\leq CN$, use a fixed number of independent layers in which each hole receives either $\lfloor m/N\rfloor$ or $\lceil m/N\rceil$ pigeons, uniformly permuting those slots. Degrees on both sides stay bounded and no hole is isolated. For fixed pigeon and hole sets of sizes $a,b$, the probability all the chosen neighbours lie in the latter is at most $(C'b/N)^{\Delta a}$. After union bounding over the two sets with $b=(\Delta-2)a$, the bound has the form $[C''a/N]^a$. A sufficiently small constant upper range $a\leq\gamma N$ makes the sum tend to zero. Collapsing parallel edges preserves neighbourhoods, and the edge-counting inequality gives boundary expansion at least one for $\Delta\geq5$. Thus no problematic regularity or divisibility premise is needed.

For bit-PHP, the substitution uses the one-hot edge variables for each pigeon to represent its chosen hole's bits. Local functionality is essential here and is available. The image of a collision axiom involves the edge variables of only two pigeons; their local pigeon, functionality and collision clauses imply that image. The image of a Boolean axiom uses only one pigeon. Each image remains a clause of affine equations. The brute-force derivation fact is valid: on each assignment, either an input clause is false or one equation of the conclusion vanishes; the latter polynomial lies in the ideal generated by the assignment equations, with the required degree bound. Eliminating assignment clauses through a binary resolution tree proves the image in a constant number of nodes for fixed graph degree. Width in the original bit variables causes no hidden logarithmic factor in this node count. Substitution preserves every subsequent syntactic inference.

## Optional characteristic-two semantic rule

The cited [Itsykson–Sokolov paper](https://doi.org/10.1016/j.apal.2019.102722) gives a syntactic simulation of semantic weakening. Its explicit bound depends on clause lengths, so when size means only nodes it is helpful to justify this bridge directly instead of silently identifying size conventions.

Here is a direct check inside Pang's simulation. Over the two-element field, the truth indicators of affine equations are themselves affine polynomials. If a clause $A$ implies a clause $B$, falsifying $B$ means solving the affine system setting all its indicators to zero. If this system is consistent, every indicator of $A$ vanishes on its solution space and is a scalar linear combination of the indicators of $B$, by Gaussian elimination. Thus all the error relations needed for the weakening simulation follow by scalar linear combinations of the errors for $B$. If the system is inconsistent, a scalar linear combination of its indicators equals one; its error relations directly give $fP_B\in C_D$. Neither case raises degree or depends on the number of disjuncts. The main syntactic lower bound does not need this extra argument, and this audit makes no analogous assertion for odd-prime semantic weakening.

## Limits and evidence

This audit did not reprove the full Mikša–Nordström general degree-lower-bound theorem, audit the random-CNF/Tseitin/colouring imports, check the other applications in Section 7, or certify the historical novelty claims. It provides no probability of correctness. The surviving conclusion means that the requested critical proof chain and reductions passed this independent mathematical inspection, with the imported general theorem explicitly retained as a dependency.

No shared notebook, claim registry, Git branch, session binding, or publication state was changed. Source text downloaded for inspection remains in the assigned ignored scratch directory, not in public evidence. Timing began after reading the computation policy and making the initial source-access plan; those preparatory actions are outside the measured interval. Some web retrieval and source-reading windows remain mixed into the mathematics category; no retrospective split was invented. One protected download attempt failed because the sandbox could not access the user systemd manager; retrying the protected launcher with approved access succeeded. This was an infrastructure failure, not a failed mathematical test. The separate timing export records 533.33 seconds and confirms medium reasoning; this timing disclosure and final delivery were completed after that snapshot.
