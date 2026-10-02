\\ Confluent tie window: minors through the pure block (7 October 2026; cycle bmd-20261007-zc).
\\ W^c(c) = (3m+3) x (3m+5) window of lem:cube-confluent-tie-reduction.  For each 3-subset K of its last five columns,
\\ the maximal minor on (first 3m columns) u K equals Delta * (3x3 minor of the Schur complement), Delta the pure
\\ block determinant = kappa c^(m binom(m,2)) (c-1)^(m(m+1)) H_m (conj:cube-two-point-window-factorization).
\\ Prints, for m = 1..5 and each K, the factorization of the minor divided by Delta (the Schur minor, a polynomial
\\ or rational function in c), and the gcd of the ten numerators stripped of c and c-1.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(str) = print(str); if (OUT != 0 && OUT != "", write(OUT, str));
bn(x, k) = if (k < 0, 0, binomial(x, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(nn = r - 2 * m - 1); return(bn(-3/2, k - nn) * 'c^max(k - nn, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(aa = 0, k, bn(-3/2, aa) * bn(-3/2, k - aa) * 'c^(k - aa))));
  sum(aa = 0, k - 1, bn(-5/2, aa) * bn(-3/2, k - 1 - aa) * 'c^(k - 1 - aa));
}
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
for (m = 1, 5,
  my(d = m * (m - 1) / 2, W = matrix(3*m + 3, 3*m + 5, r, j, rowco(r, m, d + j - 1)));
  my(Delta = matdet(matrix(3*m, 3*m, r, j, W[r, j])), g = 0);
  forsubset([5, 3], K, my(cols = concat([1 .. 3*m], apply(u -> 3*m + u, Vec(K))));
    my(D = matdet(vecextract(W, "..", cols)), q = D / Delta, nq = strip01(numerator(q)));
    g = gcd(g, nq);
    emit(Str("m = ", m, ", K = ", Vec(K), ": minor/Delta has c^", valuation(numerator(q), 'c) - valuation(denominator(q), 'c),
      " (c-1)^", valuation(numerator(q), 'c - 1) - valuation(denominator(q), 'c - 1), ", other numerator factor degrees ",
      if (nq == 0, "zero", Str(apply(poldegree, factor(nq)[, 1]~), " with multiplicities ", factor(nq)[, 2]~)), ", denominator stripped degree ", poldegree(strip01(denominator(q))))));
  emit(Str("m = ", m, ": gcd of the ten stripped numerators = ", g)));
}
