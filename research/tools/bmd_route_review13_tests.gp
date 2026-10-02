\\ Tests of the route review of 8 October 2026 (cycle bmd-20261008-zq).
\\ (a) Continued-fraction lead for conj:cube-binomial-hankel-product: from the exact Hankel determinants
\\     H_p = det[binom(-3/2, j+k-1)] (p <= 13), the ratios lambda_p = H_(p+1) H_(p-1) / H_p^2 against the rational function
\\     (2p-3)(2p+3) / (16 (2p-1)(2p+1)) predicted by the product formula; the J-fraction of a 2F1-type series has
\\     coefficients of this shape (Gauss), so agreement points to a classical proof.
\\ (b) Shifted Hankel determinants det[binom(-3/2, j+k)] (p <= 10), the other half of the J-fraction data.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
cc(n) = binomial(-3/2, n);
{
  my(H = vector(13, p, matdet(matrix(p, p, j, k, cc(j + k - 1)))));
  emit(Str("(a) product formula holds for p <= 13: ", H == vector(13, p, -(4 * p^2 - 1) / 2^(p * (2 * p - 1)))));
  for (p = 2, 12, my(l = H[p + 1] * H[p - 1] / H[p]^2, pr = (2 * p - 3) * (2 * p + 3) / (16 * (2 * p - 1) * (2 * p + 1)));
    emit(Str("(a) p = ", p, ": lambda_p = ", l, ", predicted ", pr, ", equal: ", l == pr)));
  for (p = 1, 10, emit(Str("(b) p = ", p, ": det[c_(j+k)] = ", factor(matdet(matrix(p, p, j, k, cc(j + k)))))));
}
quit
