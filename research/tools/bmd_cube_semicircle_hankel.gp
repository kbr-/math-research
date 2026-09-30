\\ Check for thm:cube-two-n-cost-bounds (30 September 2026; cycle bmd-20260930-zx).
\\ (1) X = v1/S^2 for the centred pair (+-b) equals the Catalan series sum Cat_k g1^k v1^(2k+1), g1 = b^2/4, to order 21;
\\ (2) the Hankel determinants det[x_(i+j+1)]_(0<=i,j<m) of its coefficients x_1, x_2, ... (the moments of the
\\ semicircle law of variance g1) equal g1^(m(m-1)/2) for m = 1..10 (symbolic g1).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
main() = {
  my(K = 21, S = ((1 - 'b * x + O(x^(K + 2)))^(1/2) + (1 + 'b * x + O(x^(K + 2)))^(1/2)) / 2, X = x / S^2, g = 'b^2 / 4);
  my(cat = sum(k = 0, (K - 1) / 2, binomial(2 * k, k) / (k + 1) * g^k * x^(2 * k + 1)) + O(x^(K + 1)));
  emit(Str("X = Catalan series in v1 to order ", K, ": ", X - cat == 0));
  my(xs(k) = if (k % 2, my(j = (k - 1) / 2); binomial(2 * j, j) / (j + 1) * 'g^j, 0));
  for (m = 1, 10, my(H = matrix(m, m, i, j, xs(i + j - 1)));
    emit(Str("m=", m, ": Hankel determinant = g1^(m(m-1)/2): ", matdet(H) == 'g^(m * (m - 1) / 2))));
}
main();
quit
