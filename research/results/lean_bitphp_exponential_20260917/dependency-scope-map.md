# Dependency and scope map: cor:bit-PHP-exponential-parameter-bound

Assignment: Formalize prompt, 17 September 2026, first of two separate cycles. The second
target, `thm:generic-affine-subspace-consequence-transfer`, has its own cycle and record.

## Target conclusions

For n = 2^ell holes and n+1 pigeons, every refutation of the usual bit-PHP CNF in the finite
affine DAG calculus (both recorded rule conventions) with S nodes satisfies
S > exp(n / (32768 ell^2)), for all sufficiently large ell. The notebook states "sufficiently
large"; the Lean statement makes the threshold explicit (ell >= 32), which implies it.

## Required supporting claims (all already Lean-verified; reused, not new results)

- `MathResearch.affine_family_exclusion_of_square` (claims/AffineFamilyExclusion.lean): finite
  exclusion under the square condition m log(4M) <= k^2, with proper-high count at most M.
- `MathResearch.PolynomialCalculus.usual_bitPHP_PC_transfer` and
  `registry_system_eq_ensFamily` (claims/BitPHPClauseTransfer.lean): at most 3S + C(m,2) slots,
  PC refutation through max(2h+ell, 4h+1).
- `MathResearch.proper_high_count_le_proper_count` is not needed; the high index is a subtype of
  the N registry slots directly.
- Mathlib: Real.exp, Real.log monotonicity and `Real.add_one_le_exp`.

## New arithmetic needed

- 32768 (2 ell + 4) ell^2 <= 2^ell for ell >= 32 (natural-number induction).
- exp(x) >= 16 n^2 when x >= 2 ell + 4, hence 4(3S + C(n+1,2)) <= exp(2x) when S <= exp(x).
- k = floor(n/(32 ell)) satisfies n <= 64 ell k, the board conditions, and the square condition.

## Outside the assignment

The preprint text, the generic subspace theorem, and any optimization of the constant.
