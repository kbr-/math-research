# R11: two-row state interpolation

Target: complete indexed lem:two-functional-row-state-interpolation over F2 in
its compact-bit context. Represent the two distinct rows by Fin2 and each
column by Fin n. The local base contains Booleanity, same-row exclusions,
and row sums minus one, but no cross-row collision axioms. For every ordinary
polynomial P, prove P−Σjk P(ej,ek)X0jX1k ∈ NS_max(degP,2).

Dependencies: R01/R02 NS interfaces; R05 degree-controlled squarefree reduction;
a generic pair-divisibility helper being extracted by the matching worker.
Reduce actual-support monomials: a repeated row kills the squarefree monomial
within its own degree; otherwise at most two variables remain. Constants and
linear terms homogenize with row sums at degree2. Their one-hot evaluations
identify the bilinear coefficients. Do not use the stronger full matching
marginal theorem R09 or add cross-row equations. R12 embeds this local identity
into the global decoder; that separate claim is outside this cycle.
