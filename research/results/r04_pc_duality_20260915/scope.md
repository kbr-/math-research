# R04: finite-dimensional separation and annihilator extension

Target: full historical lem:duality, including its NS≤PC assertion already
proved in R02. Designs/annihilators must be linear functionals on the actual
ordinary degree≤B subspace, normalized at one. They carry neither positivity
nor multiplicativity assumptions. Separation is proved more generally without
finite-dimensional hypotheses using Mathlib algebraic basis extension.

New reusable supporting interface: given U,S⊆M and l:U→K vanishing on U∩S,
there exists an ambient L:M→K extending l and annihilating S. This standard
linear-algebra result is not claimed as project novelty. Put it in a separate
third-party-claims file for matching and restriction consumers; prove it by
gluing l and zero on U+S and applying Mathlib exists_extend. The same file
exposes separation normalized to one using exists_extend_of_notMem.

Dependencies: R01/R02 and pinned Mathlib Basis.VectorSpace, LinearPMap.
No matching filtration, restriction dimension inequality, or source-specific
extension hypothesis is proved here. Brief pre-cycle API reading is disclosed.
