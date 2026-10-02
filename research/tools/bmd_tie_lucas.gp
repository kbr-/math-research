\\ Lucas reduction of the confluent tie window (8 October 2026; cycle bmd-20261008-c).
\\ For a prime p > d + 3m + 4, W(3/2, c) = W((3-p)/2, c) mod p entrywise: the window of binomial polynomials
\\ (1+T)^((p-5)/2) T^i, (1+cT)^((p-3)/2) T^n, (1+T)^(p-3), ((1+T)(1+cT))^((p-3)/2), T (1+T)^((p-5)/2) (1+cT)^((p-3)/2).
\\ A special value c0 (not 0, 1) of W(3/2, c) in characteristic 0 reduces to one of the window mod p for all but finitely
\\ many p.  Question: over F_p, does the gcd of the maximal minors have roots off {0, 1}, and for which (m, p)?
\\ Part 1: the reduction identity itself is checked entrywise (W(3/2) - W((3-p)/2) = 0 mod p).
\\ Part 2: for m = 2..4 and primes p from d + 3m + 5 to 150, the degree of the gcd over F_p[c] stripped of c and c - 1,
\\ and its factor degrees; primes with a nontrivial stripped gcd are listed with the factorization.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
bn(a, k) = if (k < 0, 0, binomial(a, k));
rowco(r, m, k, L) = {
  if (r <= 2 * m, return(bn(-L - 1, k - (r - 1))));
  if (r <= 3 * m, my(n = r - 2 * m - 1); return(bn(-L, k - n) * 'c^max(k - n, 0)));
  if (r == 3 * m + 1, return(bn(-2 * L, k)));
  if (r == 3 * m + 2, return(sum(a = 0, k, bn(-L, a) * bn(-L, k - a) * 'c^(k - a))));
  sum(a = 0, k - 1, bn(-L - 1, a) * bn(-L, k - 1 - a) * 'c^(k - 1 - a));
}
winmat(m, L) = { my(d = m * (m - 1) / 2); matrix(3 * m + 3, 3 * m + 5, r, j, rowco(r, m, d + j - 1, L)); }
st(q) = { q = q / 'c^valuation(q, 'c); while (subst(q, 'c, 1) == 0, q = q / ('c - 1)); q; }
{
my(ok = 1);
for (m = 2, 4, my(d = m * (m - 1) / 2); forprime(p = d + 3 * m + 5, 60,
  if ((winmat(m, 3/2) - winmat(m, (3 - p) / 2)) * Mod(1, p) != 0, ok = 0)));
emit(Str("Part 1: W(3/2) = W((3-p)/2) mod p for m = 2..4 and all primes up to 60 above the bound: ", ok));
for (m = 2, 4, my(d = m * (m - 1) / 2, W0 = winmat(m, 3/2), bad = List(), good = 0);
  forprime(p = d + 3 * m + 5, 150,
    my(W = W0 * Mod(1, p), w = #W, g = 0);
    for (i = 1, w, for (j = i + 1, w, g = gcd(g, matdet(vecextract(W, "..", select(t -> t != i && t != j, [1 .. w]))))));
    if (g == 0, listput(bad, [p, "all minors zero"]); next);
    my(s = st(g));
    if (poldegree(s, 'c) > 0, listput(bad, [p, poldegree(s, 'c), factor(s)]), good++));
  emit(Str("Part 2, m = ", m, ": primes with no root off {0,1}: ", good, "; primes with roots off {0,1}: ", Vec(bad))));
\\ Part 3 (added after review): for p < m^2 + m + 5 the first 3m rows (polynomials of degree <= (p-5)/2 + 2m - 1) have
\\ 3m unknowns against (p-5)/2 + 2m - d window conditions, forcing rank < 3m + 3 at every c.  Ranks of W_p at c = 5, 7
\\ for m = 4..6 and primes from d+3m+5 to m^2+m+15; then, at m = 5, the stripped gcd for primes from m^2+m+5 to 80.
for (m = 4, 6, my(d = m * (m - 1) / 2, W0 = winmat(m, 3/2), res = List());
  forprime(p = d + 3 * m + 5, m^2 + m + 15,
    listput(res, [p, p < m^2 + m + 5, matrank(subst(W0, 'c, 5) * Mod(1, p)), matrank(subst(W0, 'c, 7) * Mod(1, p))]));
  emit(Str("Part 3, m = ", m, " (full rank ", 3 * m + 3, "): [p, p < m^2+m+5, rank at c = 5, rank at c = 7] = ", Vec(res))));
my(m = 5, d = 10, W0 = winmat(5, 3/2), bad = List(), good = 0);
forprime(p = m^2 + m + 5, 80,
  my(W = W0 * Mod(1, p), w = #W, g = 0);
  for (i = 1, w, for (j = i + 1, w, g = gcd(g, matdet(vecextract(W, "..", select(t -> t != i && t != j, [1 .. w]))))));
  if (g == 0, listput(bad, [p, "all minors zero"]); next);
  my(s = st(g)); if (poldegree(s, 'c) > 0, listput(bad, [p, poldegree(s, 'c)]), good++));
emit(Str("Part 3, m = 5: primes from m^2+m+5 to 80 with no root off {0,1}: ", good, "; others: ", Vec(bad)));
}
quit
