# Scheduled architecture review: independent stage

Use .claude/agents/medium-reviewer.md. Read-only; no computations, edits, escalations or app actions.
At this stage do not read notebook living sections, latest entries or route decisions.
Consider only this goal and the bounded available statements below. The current preferred route is
intentionally withheld. A later stage will supply it and ask for correctness review.

Goal: for every fixed depth, prove a superpolynomial size lower bound for AC0[2]-Frege on one
polynomially encoded family of unsatisfiable Boolean formulas (or equivalent tautologies).
The family may depend on depth but not on the proposed polynomial proof-size exponent.
Any family is allowed; it need not be pigeonhole or Tseitin. Odd primes are a later goal.

Available proved/imported tools, at their exact scoped level:

1. Fixed bounded-degree charged-modulo-three Tseitin CNFs over coefficient field F2 have n old
Boolean variables, O(n) clauses of constant width and an ordinary PC degree barrier gamma*n
for a fixed positive gamma. Their binary one-hot quotient has a Fourier/cut-code description.
No global satisfying-assignment model exists for its proper truncated quotient.

2. The audited binary coherent genuine source compiler turns a fixed-depth, size-S Frege proof
in the recorded finite Boolean/MOD2-recursion/MP presentation into a complete product-only ENS
source refutation. At accuracy h>=clause width its PC ceiling is c*L, L<=(d+1)h^d with d fixed.
There is no proof-height factor. Source inputs are old fixed-degree predicates plus affine
combinations of strictly earlier whole ENS products; no raw earlier coefficients occur outside
products. There are O(S) blocks and safely O(S^2) flattened slots. Every companion and fresh
Boolean equation remains. Original product cost is h(delta+1); companion cost adds input degree.

3. Source theorem: on an old family with proper PC ceiling floor(gamma*n), O(n) fixed-degree
initial predicates, fixed <=ell product-only levels, <=C*n^(1+rho) blocks per nonterminal level
and arbitrary fixed polynomial terminal inventory, no original degree-B PC/NS refutation exists
for 2<=B<=n^beta(log n)^c if rho(2^(ell-1)-1)+beta<1. Accuracies are arbitrary positive integers.
Combining with item2 proves a polynomial symbol-size interval for each fixed depth, not all exponents.

4. Alternative source theorem: an old Boolean family on v variables with proper PC ceiling
D=floor(v/2-s), s=o(v/(log v)^(ell-2)) at fixed ell>=2, with fixed input width/degree, would
exclude every polynomial inventory for the audited product-only ENS grammar at sublinear original
proof degree and suitable polynomial accuracy. No qualifying near-half family is known.
Existing unary PHP barriers are measured in holes, not near half the total Boolean variable count.

5. A bounded-degree binary polynomial assignment to every source coefficient, plus one surviving
old polynomial weight, can replay complete source relations at b+T*B<=D. Algebraic-extension maps
and weights satisfying every weighted fresh field equation descend to F2 with no degree increase.
This is a conditional transfer, not a map-existence theorem.

6. Fixed Boolean-frame evaluation and PC copy/MP compilation are available when all value interfaces
are supplied over one common retained system. Factored source maps, eligible costed virtual folds,
and structured two-level sources have positive scoped normalizations. None is a universal compiler
normalization. Proof-local weighted replay only needs actual axiom leaves, copy discrepancies and
MP defects c-(1-a)b, at degW+2L<=D; all-companion removal is sufficient but not necessary.

Task: propose a materially different architecture for the stated goal using these tools or identify
why none is supported. Name the weakest genuinely missing implication, what concrete next test
would distinguish the architecture, and which hypotheses/costs must be checked. Do not invent a
complete theorem, numerical probability or a source-coverage assertion. Prefer an alternative
that changes the necessary implication over another sufficient-condition layer. If no supported
alternative was found, say so plainly. Keep the response concise. No literature search is required
in this blind stage; name unverified external suggestions as suggestions.
