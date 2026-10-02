\\ Zero locations of maximal minors of the confluent tie window (7 October 2026; cycle bmd-20261007-zj).
\\ Question: do two maximal minors of W^c(c) have their zeros (other than 0 and 1) in disjoint regions of the c-plane,
\\ for instance separated by a line?  Then localizing each would prove conj:cube-confluent-tie-window-full-rank.
\\ For m = 2..5 and each pair of dropped columns {p, q} (0-based offsets), prints the number of zeros outside {0, 1}, the
\\ ranges of their real parts and arguments, and the number on the real axis by interval.
default(realprecision, 50);
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
winmat(m) = { my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1)); }
strip01(f) = { if (f == 0, return(0)); while (subst(f, 'c, 0) == 0, f /= 'c); while (subst(f, 'c, 1) == 0, f /= ('c - 1)); f / content(f); }
{
for (m = 2, 5,
  my(A = winmat(m), w = 3 * m + 5);
  for (p = 1, w, for (q = p + 1, w,
    my(D = strip01(matdet(vecextract(A, "..", select(j -> j != p && j != q, [1 .. w])))));
    if (poldegree(D, 'c) == 0, emit(Str("m = ", m, ", drop ", [p - 1, q - 1], ": no zeros off {0,1}")); next);
    my(R = polroots(D), re = apply(real, R), ar = apply(z -> arg(z), R), nr = polsturm(D));
    emit(Str("m = ", m, ", drop ", [p - 1, q - 1], ": ", #R, " zeros, Re in [", precision(vecmin(re), 5), ", ", precision(vecmax(re), 5),
      "], |arg| in [", precision(vecmin(apply(abs, ar)), 5), ", ", precision(vecmax(apply(abs, ar)), 5), "], real zeros ", nr)))));
}
quit
