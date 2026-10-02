\\ Route review tests (7 October 2026; cycle bmd-20261007-zu).
\\ (L1) Generic perfectness of the pure two-family system: for 1 <= p <= 8, 1 <= q <= 4 and offsets 0 <= e <= 6, the square
\\      determinant of the coefficients of T^e..T^(e+p+q-1) of T^i (1+T)^(-5/2) (i < p) and T^n (1+cT)^(-3/2) (n < q) is
\\      a nonzero polynomial in c.  Counts the zero ones.
\\ (L3) Sign pattern on real c < 0: for m = 1..4 and c in {-1/2, -1, -2, -5}, the signs of all maximal minors of W^c(c);
\\      reports how many are positive, negative and zero, and whether the pattern is the same at all four values.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k) = {
  if (r <= 2 * m, return(bn(-5/2, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-3/2, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-3, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-3/2, a) * bn(-3/2, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-5/2, a) * bn(-3/2, k - 1 - a) * 'c^(k - 1 - a));
}
{
my(zero = List(), tot = 0);
for (p = 1, 8, for (q = 1, 4, for (e = 0, 6, tot++;
  my(n = p + q, A = matrix(n, n, r, j, my(k = e + j - 1); if (r <= p, bn(-5/2, k - (r - 1)), my(t = r - p - 1); bn(-3/2, k - t) * 'c^max(k - t, 0))));
  if (matdet(A) == 0, listput(zero, [p, q, e])))));
emit(Str("(L1) pure square windows tested ", tot, "; identically zero: ", #zero, " ", Vec(zero)));
}
{
for (m = 1, 4,
  my(d = m * (m - 1) / 2, w = 3 * m + 5, W = matrix(3 * m + 3, w, r, j, rowco(r, m, d + j - 1)), pats = List());
  foreach([-1/2, -1, -2, -5], c0, my(N = substvec(W, ['c], [c0]), sg = List());
    forsubset([w, 3 * m + 3], S, listput(sg, sign(matdet(vecextract(N, "..", Vec(S))))));
    listput(pats, Vec(sg)));
  my(P1 = pats[1]);
  emit(Str("(L3) m = ", m, ": at c = -1/2: ", #select(x -> x > 0, P1), " positive, ", #select(x -> x < 0, P1), " negative, ", #select(x -> x == 0, P1),
    " zero; same sign pattern at c = -1, -2, -5: ", pats[2] == P1 && pats[3] == P1 && pats[4] == P1)));
}
quit
