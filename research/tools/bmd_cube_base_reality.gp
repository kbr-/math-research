\\ Reality of the base's Weierstrass points (30 September 2026), the smallest test of an
\\ electrostatic (Stieltjes / Heine) bridge for the base weight bound.
\\ Tested statement: at a real configuration of distinct real entries, the non-branch part of the
\\ cleared Wronskian numerator of the base space V^(b) (N = 6: doubles 1, 2, -3; N = 7: doubles
\\ 1, 2, -3 and simple 5) has only real roots. An equilibrium mechanism of Stieltjes type would make
\\ all Weierstrass points real at real data; a count of real roots well below the degree falsifies
\\ that form of the bridge. Exact computation over Q: interpolation of the cleared numerator from
\\ exact determinants, branch factors removed, real roots counted with polsturm.
\\ Row construction copied unchanged from bmd_cube_hierarchical_attainment.gp.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
serpow(u, al, L) = vector(L, m, binomial(al, m - 1) * u^(m - 1));
mul(A, B, L) = vector(L, n, sum(m = 1, n, A[m] * B[n + 1 - m]));
tx(B, t, L) = vector(L, n, t * B[n] + if (n > 1, B[n - 1], 0));  \\ multiply by (t + X)
rowsh(Ds, sim, t, L) = {
  my(R = List(), p(c, e) = serpow(c / (1 + c * t), e, L));
  for (i = 1, #sim, for (k = i + 1, #sim, listput(R, mul(p(sim[i], -3/2), p(sim[k], -3/2), L))));
  foreach (Ds, D, foreach (sim, k,
    listput(R, mul(p(D, -3/2), p(k, -3/2), L));
    listput(R, tx(mul(p(D, -5/2), p(k, -3/2), L), t, L))));
  foreach (Ds, D, listput(R, p(D, -3)));
  for (r = 1, #Ds, for (s = r + 1, #Ds,
    my(v = mul(p(Ds[r], -5/2), p(Ds[s], -7/2), L));
    for (j = 0, 3, listput(R, v); v = tx(v, t, L))));
  if (#R != L, error("row count"));
  matrix(L, L, r, j, R[r][j]);
}
ms(N) = my(R = binomial(N, 2)); -3/2 * (N - 1) + binomial(N - 1, 2) + binomial(R - N + 1, 2);
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
Tcount(N, a) = {
  my(R = binomial(N, 2), E = binomial(R, 2), n = N - 2 * a);
  (N - a - 2) * E - 3 * R - n * ms(N) - if (a >= 1, md(N, 5/2) + (a - 1) * md(N, 7/2), 0);
}
realtest(Ds, sim) = {
  my(a = #Ds, n = #sim, N = 2 * a + n, R = binomial(N, 2), E = binomial(R, 2));
  my(vals = concat(Ds, sim), D = (N - 2) * E + 3 * R, xs = vector(D + 1, i, i), ys);
  ys = vector(D + 1, i, my(t = xs[i]); matdet(rowsh(Ds, sim, t, R)) * prod(c = 1, #vals, (1 + vals[c] * t)^E));
  my(P = polinterpolate(xs, ys, 'z), t2 = D + 5);
  if (subst(P, 'z, t2) != matdet(rowsh(Ds, sim, t2, R)) * prod(c = 1, #vals, (1 + vals[c] * t2)^E), error("interpolation check"));
  my(P0 = P);
  for (c = 1, #vals, while (subst(P0, 'z, -1 / vals[c]) == 0, P0 = P0 / ('z + 1 / vals[c])));
  emit(Str("N=", N, " base doubles ", Ds, " simple ", sim, ": non-branch degree ", poldegree(P0),
    " (T ", Tcount(N, a), "); real roots ", polsturm(P0), "; squarefree ", poldegree(gcd(P0, deriv(P0))) == 0));
}
realtest([1, 2, -3], []);
realtest([1, 2, -3], [5]);
