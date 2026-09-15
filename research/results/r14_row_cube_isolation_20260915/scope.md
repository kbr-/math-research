# R14 dependency: row-cube coefficient isolation

For row-linear P and prescribed row-monomial x with degP≤degree(x), sum arbitrary
substitutions over the binary choices on x's selected rows. On each selected
row, the images are constants from the supplied label and its flip in x's bit
direction. Outside the selected rows, images need only be choice-independent;
no degree bound, nonzero hypothesis, packing or ℓ≥2 assumption is imposed.
Prove the sum is exactly C(P.coeff(rowMonomialExponent x)).

Expand P in its actual support. Row-linearity supplies a row-monomial index y
for each term. If y misses a selected row, pair cube choices differing there
and cancel in characteristic2. Otherwise the degree bound forces exactly the
selected row set, with no outside factor. Finite product/sum distributivity
then makes each row contribute its one-bit Kronecker difference, isolating x.
Degree-zero and lower-degree cases are included. No board-specific theorem or
abstract separating-functional assumption is used.

Dependencies: checked row-monomial support/degree/injectivity API, generic cube
cancellation, and concrete flipColumn_label. Previously private R13 API facts
were exposed without proof changes in a separate authorized setup commit;
their verification is attached to this timing cycle. Initial source/API reading
preceded instrumentation. The full R14 board/PC separation remains assigned to
the matching worker and is not completed by this helper alone.
