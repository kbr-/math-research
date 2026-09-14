# Signed row trades and full old matching moments

The [notebook entry](https://kbr.is-a.dev/math-research/#entry-2026-09-15-signed-row-trades-relative-moments)
contains the full statements, proofs, finite bounds, and remaining gap.

The elementary row-trade lemma spans every zero-marginal array on r rows and
N >= 2r columns over every field. It gives a constant signed difference detecting
any nonzero class in the old functional matching quotient. Together with the
existing all-prime affine coefficient substitution and signed residual designs,
this extends one-level old-target preservation to the full transported matching
window at polylogarithmic proof degree.

The conclusion is relative to the transported matching ideal J_t. It does not
identify J_t with the compact base's own degree-t NS space, assert survival of
every Boolean-nonzero target, or extend arbitrary moments involving previously
adjoined selectors. The first rank-cutoff selector prescription failed an actual
degree-(4h+1) comparison. Multilevel compatibility remains open.

## Reproduction

Run with an active timing session and the shared resource controls:

    ./compute.sh run TURN --threads 1 --category local_processing -- \
      g++ -O2 -std=c++17 -Wall -Wextra \
      research/tools/check_signed_row_trades.cpp -o /tmp/math-signed-row-trades
    ./compute.sh run TURN --threads 1 --timeout 180 -- \
      /tmp/math-signed-row-trades --out NEW_OUTPUT_PATH

The program refuses an existing output path. No dependency was installed.
The initial compile succeeded with five misleading-indentation warnings;
formatting was cleaned up and the final compile was warning-free. The successful
exact run preceded that whitespace-only cleanup; the algorithm was unchanged
and the numerical run was not repeated.

## Complete output and encoding

`signed-row-trades.jsonl` retains seven geometries, nineteen field cases,
thirty-eight exact matrix factorizations, and twelve parameter cases.

- A geometry includes every injection tuple, marginal row label, full sparse
  marginal matrix, row-pair choice, and full sparse signed trade vector.
  Sparse entries are `[column, integer coefficient]`. Every trade's marginals
  were checked over the integers before field reduction.
- Every rank certificate gives A = C B, with basis rows B having distinct
  leading pivots. Accepted input rows give an invertible lower-triangular
  submatrix of C. Both recomposition and these independence conditions were
  checked for every matrix.
- Over F2, vectors use little-endian arrays of fixed-width hexadecimal 64-bit
  words; bit i represents column i. Over F3 and F5, vectors are ordinary
  residue arrays. Large parameter integers are decimal strings.
- The six geometries (1,3), (2,3), (2,4), (3,5), (3,6), and (3,7) use all
  three fields. The (4,8) geometry uses F2 only.
- Thin boards (2,3) and (3,5) have a nonzero zero-marginal space but no disjoint
  row-pair trades. These negative controls deliberately fail spanning.

Parameter cases use p = 2,3,5, ell = 16,32,48,64, n = 2^ell, M = n^2,
D = t = ell^3, h = 3(p-1)ell, and
k = max(2t, ceil(sqrt((n+1)(2ell+2)))).
The integer 2ell+2 exceeds ln(4M), so there is no floating-point rounding
assumption. All cases pass the row-range and packing tests; the old degree
room n >= 2k(D+1)-1 fails at ell = 16,32 and passes at 48,64.
The code checks the actual affine companion degree and t >= ell as well.
No huge board or field is instantiated for these symbolic checks.

## Dependencies and review scope

The notebook links the existing matching normal form, all-field matching
extension, row-excluded affine restriction bound, all-prime affine substitution,
compact decoder, and signed residual detector. The imported BLVZ filling theorem
is reused through the existing matching-extension record; no new literature
claim or bibliographic novelty is asserted.

The focused review checks the boundary case N = 2r in the spanning induction,
ordinary NS costs when lowering a matching representative, disjointness of the
target and multiplier rows, all coefficient field images and original degrees,
residual design room, the precise ideal in the conclusion, and the limitation
to old moments. `check-metadata.json` records touched-link and evidence checks;
`provenance.json` hashes this note, checker, full output, and metadata.
Timing and complete command output are retained under this session label in
`research/provenance/session-records/`.
