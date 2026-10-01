\\ Far route review test (3 October 2026; cycle bmd-20261003-zc).
\\ Certificate for "no triple roots": if p does not divide the leading coefficient of the primitive far polynomial R in Z[w],
\\ a root of multiplicity m over Q reduces to a root of multiplicity >= m of R mod p.  So max multiplicity of R mod p <= 2
\\ at one such p proves R has no triple root.  Question: is there a small prime p, the same for every size, at which the
\\ multiplicities stay <= 2 (a candidate uniform mod-p mechanism)?  Prints, for p <= 23, the degree drop and the multiplicity
\\ profile of R mod p, at the sizes (n,k) = (2,3),(3,3),(2,4),(2,5),(3,4),(4,3).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
strip(N, v) = { while (subst(N, v, 0) == 0, N = N / v); while (subst(N, v, 1) == 0, N = N / (v - 1)); N / pollead(N); }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  strip(numerator(matdet(M)), 'w);
}
farR(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); p));
  wr([[0, 0, P3], [1/2, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]);
}
main() = {
  foreach([[2, 3], [3, 3], [2, 4], [2, 5], [3, 4], [4, 3]], v,
    my(R = farR(v[1], v[2]), Z0 = R * denominator(content(R)), Z = Z0 / content(Z0), d = poldegree(Z), line = Str("(n,k)=", v, " deg ", d, ":"));
    forprime (p = 3, 23,
      my(lc = pollead(Z) % p, F, mx = 0, pr);
      if (lc == 0, line = Str(line, " p=", p, " lc0;"); next);
      F = factormod(Z, p); mx = vecmax(F[, 2]);
      pr = vecsort(F[, 2]~); line = Str(line, " p=", p, " max ", mx, ";"));
    emit(line));
}
main();
