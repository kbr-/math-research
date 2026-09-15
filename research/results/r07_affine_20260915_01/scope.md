# R07/R08/R16 assignment

Target set: R07, R08, R16. R07 releases a complete affine-linear-algebra
supporting claim first; exact fresh-variable companion degrees and scalar PC
cleanup then receive their own proofs/record. R08/R16 await Boolean reduction
and use released substitution/reuse. No R15 work in this worktree.

R07 source: paper §5 scalar cleanup and following affine basis paragraph;
notebook affine-common-vanishing-learning and semantic-weakening-PC-degree.
Do not label the larger learning or weakening claim formalized by these helpers.

Initial representation: AffineForm K n = Option (Fin n) → K, with None the
constant coefficient and Some i the linear coefficient. Supply ordinary
polynomial and existing AffineMap bridges. Affine-form evaluation is injective
for any field (evaluate at zero and coordinate unit vectors), so this does not
identify general ordinary polynomials with functions on a finite field.

First claim conclusions: absence of unit form in span gives a common zero;
vanishing on a consistent zero flat implies membership in the input span and
explicit constant coefficients; empty zero set gives a unit combination;
linear-part projection is injective on a proper span, giving independence
for an affine basis and dimension/rank equality. Source variables finite;
empty input list, zero forms, constant and zero-dimensional cases included.

Proof plan: finite-coordinate expansion of a linear functional on forms.
Separate unit from proper span to obtain and normalize a common zero.
At a fixed zero x0, every annihilator of the input span can be rewritten as
constant multiple of evaluation at x0 plus a direction evaluation. A form
vanishing on all common zeros is killed by every annihilator and belongs to
the span by the library double-annihilator theorem. No unproved topological
or polynomial-system dependency is assumed.

Reusable affine-system statements belong in claims/ with source attribution;
no novelty claim. Small coordinate calculation lemmas remain in the same file.
Exact companion degree needs separate polynomial algebra with disjoint fresh
variables; this is not inferred from an upper bound. The coordinator owns all
living notebook sections and the route. Report intermediate release and limits.

Initial rule restoration preceded timing start; all proof work and Lean checks
are measured by r07_affine_20260915_01.

Final extraction decision: the affine coefficient/polynomial/AffineMap bridge
has its own `claims/AffineForm.lean` and claim-index entry, because it is reused
without system duality. The first release deliberately excludes complete affine
coordinate parametrization, fresh-companion degrees, and scalar PC replay;
these remain later R07 obligations, not part of the two extracted claim statements.
