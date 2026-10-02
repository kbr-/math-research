\\ Goal-level route review tests (8 October 2026; cycle bmd-20261008-zg), lambda = 3/2, m = 2, 3.
\\ Window of lem:cube-confluent-tie-reduction at start s: rows (1+T)^(-5/2) T^i (i < 2m), T^n (1+cT)^(-3/2) (n < m),
\\ (1+T)^(-3), ((1+T)(1+cT))^(-3/2), T (1+T)^(-5/2) (1+cT)^(-3/2); columns T^s .. T^(s+3m+4); full rank is 3m+3.
\\ Test 1 (Desnanot-Jacobi descent across starts): for s = 0 .. d+3 (d = binom(m,2)), the exceptional polynomial
\\ E_s = gcd over Q[c] of the maximal minors, with the powers of c and c-1 removed.  A descent mechanism predicts
\\ E_(s+1) | E_s (a drop at a start forces a drop at the previous start).
\\ Test 2 (singularity confinement): pure determinants S(n,c) = det of the 3m pure rows on columns n .. n+3m-1, and
\\ gcd(S(n), S(n+1)) off c(c-1) for n = d .. d+5.  Confinement predicts consecutive pure determinants are coprime.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
strip(p) = { if (p == 0, return(0)); while (subst(p, 'c, 0) == 0, p = p / 'c); while (subst(p, 'c, 1) == 0, p = p / ('c - 1)); p; }
ess(p) = { my(q = strip(p)); if (q == 0, return("identically zero")); my(f = factor(q / content(q))); if (#f~ == 0, return("constant (none)")); [poldegree(q), vector(#f~, i, [poldegree(f[i, 1]), f[i, 2]])]; }
rowsW(m, K) = {
  my(L = List(), pw(a, s) = (1 + a * 'x + O('x^(K + 1)))^s, ser(f) = vector(K + 1, k, polcoef(f, k - 1, 'x)));
  for (i = 0, 2 * m - 1, listput(L, ser('x^i * pw(1, -5/2))));
  for (n = 0, m - 1, listput(L, ser('x^n * pw('c, -3/2))));
  listput(L, ser(pw(1, -3))); listput(L, ser(pw(1, -3/2) * pw('c, -3/2))); listput(L, ser('x * pw(1, -5/2) * pw('c, -3/2)));
  matrix(#L, K + 1, i, j, L[i][j]);
}
{
  foreach([2, 3], m,
    my(d = binomial(m, 2), K = d + 3 + 3 * m + 4 + 6, P = rowsW(m, K), r = 3 * m + 3);
    for (s = 0, d + 3,
      my(g = 0, cols = [s + 1 .. s + 3 * m + 5]);
      forsubset([#cols, r], S, g = gcd(g, matdet(vecextract(P, "..", vecextract(cols, Vec(S))))));
      emit(Str("m = ", m, ", start s = ", s, (if (s == d, " (= d)", "")), ": exceptional polynomial E_s off c(c-1): [degree, [factor degree, mult]] = ", ess(g))));
    my(Pp = vecextract(P, Str("1..", 3 * m), ".."), Sv = vector(6, j, matdet(vecextract(Pp, "..", [d + j .. d + j + 3 * m - 1]))));
    for (j = 1, 5, emit(Str("m = ", m, ": gcd(S(", d + j - 1, "), S(", d + j, ")) off c(c-1): ", ess(gcd(Sv[j], Sv[j + 1]))))));
}
quit
