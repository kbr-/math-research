# Dependency and scope map: thm:generic-affine-subspace-consequence-transfer

Assignment: Formalize prompt, 17 September 2026, second of two separate cycles.

## Target conclusions (notebook entry of 16 September 2026)

Binary field, finite variable set of size v, arbitrary old base F containing the Boolean
equations, finite complete one-level affine ENS family with accuracy h >= 1 and old-affine
inputs, a degree-D ordinary-PC refutation with D >= 2h+1, k >= 1, and a linear subspace U of
polynomials of degree at most k. With H the blocks whose input span omits one and has rank
greater than h(k+1), B = k(D+1), and R = sum over H of C(v - r_a + k, k):

1. dim(U ∩ C_B(F)) >= dim U - R, stated without natural subtraction as
   dim U <= dim(U ∩ C_B(F)) + R.
2. dim U > R gives a nonzero member of U derivable through B.
3. If U ∩ C_B(F) = {0} and dim U > R, no such refutation exists.
4. With r_* = h(k+1)+1 <= v, R <= |H| C(v - r_* + k, k); if r_* > v then H is empty.

The CNF initial-value bridge and the short-proof control in the same notebook entry are
separate remarks, not part of the indexed theorem, and are outside this assignment.

## Boundary cases inspected before proving

- H empty: R = 0 and the claim says every member of U is derivable. Consistent with the
  removal theorem, whose high-block hypothesis is then vacuous or discharged by unit spans.
- U = 0 and zero polynomials: totalDegree 0 <= k, dimensions zero, statement trivial.
- Blocks with rank at most h(k+1): handled inside the verified removal theorem by exact
  low-rank packing; they do not enter R.
- k >= 1 and h >= 1 are hypotheses of the removal theorem and are kept explicit.
- Natural subtraction in v - r_a: r_a <= v for proper blocks (affineInputRank_le), so the
  binomial argument is the intended one.

## Supporting claims, all already Lean-verified and reused

- lem:proper-affine-block-restriction: `blockRestrictionData_exists`, `affineInputRank_le`.
- lem:ordinary-restriction-dimension through `affineRestriction_image_finrank_le`.
- lem:affine-family-removal-with-unit-blocks: `affine_family_removal_with_units`.
- Mathlib: rank-nullity, finrank of finite products, finite-dimensionality of degree spaces.

## New formal work

The joint restriction map on an arbitrary U, its kernel's inclusion in U ∩ pcSpace, and the
dimension count. This abstracts the bit-variable, row-linear argument of
lem:common-affine-restriction-kernel to arbitrary finite variable types, accuracy, and U.
