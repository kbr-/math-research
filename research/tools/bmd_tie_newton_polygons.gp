\\ p-adic Newton polygons of two maximal minors of the confluent tie window (7 October 2026; cycle bmd-20261007-zk).
\\ P_m = first-columns minor (drop the last two columns), Q_m = last-columns minor (drop the first two), both stripped of
\\ c and c-1.  If, at some prime p, the multisets of p-adic valuations of the roots of P_m and Q_m (the slopes of the
\\ Newton polygons) are disjoint, then gcd(P_m, Q_m) = 1, hence Z^W_m is contained in {0, 1}.  Prints the root
\\ valuations (with multiplicity counts) for p = 2, 3, 5, 7, m = 2..6, and whether they are disjoint.
default(parisizemax, 4 * 10^9);
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
\\ root valuations: newtonpoly gives the slopes; root valuations are their negatives in PARI's convention
rv(f, p) = { my(s = newtonpoly(f, p)); Set(s); }
cnt(f, p) = { my(s = newtonpoly(f, p), u = Set(s)); vector(#u, i, [u[i], #select(x -> x == u[i], s)]); }
{
for (m = 2, 6,
  my(A = winmat(m), w = 3 * m + 5, P = strip01(matdet(vecextract(A, "..", [1 .. w - 2]))), Q = strip01(matdet(vecextract(A, "..", [3 .. w]))));
  foreach([2, 3, 5, 7], p,
    my(a = rv(P, p), b = rv(Q, p));
    emit(Str("m = ", m, ", p = ", p, ": P slopes ", cnt(P, p), "; Q slopes ", cnt(Q, p), "; disjoint: ", #setintersect(a, b) == 0))));
}
quit
