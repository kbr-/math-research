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
\\ Analysis part of bmd_cube_symmetric_base.gp (appended after the row functions of bmd_cube_base_weight.gp).
symtest(Ds, sim, k) = {
  my(p = 2^61 - 1, a = #Ds, n = #sim, N = 2 * a + n, R = binomial(N, 2), E = binomial(R, 2));
  my(vals = concat(Ds, sim), rk = matrank(rowsh(Ds, sim, Mod(3, p), R)));
  my(D = (N - 2) * E + 3 * R, xs = List(), ys = List(), t = 1);
  while (#xs < D + 3, t++; my(tm = Mod(t, p)); if (prod(c = 1, #vals, 1 + vals[c] * tm) == 0, next);
    listput(xs, tm); listput(ys, matdet(rowsh(Ds, sim, tm, R)) * prod(c = 1, #vals, (1 + vals[c] * tm)^E)));
  my(P = polinterpolate(Vec(xs)[1..D+1], Vec(ys)[1..D+1], 'z));
  if (subst(P, 'z, xs[D + 2]) != ys[D + 2] || subst(P, 'z, xs[D + 3]) != ys[D + 3], error("interpolation check"));
  my(P0 = P, mult = vector(#vals));
  for (c = 1, #vals, if (vals[c] != 0, while (subst(P0, 'z, -1 / vals[c]) == 0, P0 = P0 / ('z + 1 / vals[c]); mult[c]++)));
  my(v0 = valuation(P0, 'z), Q = P0 / 'z^v0);
  my(inz = 1); for (j = 0, poldegree(Q), if (polcoef(Q, j, 'z) != 0 && j % k != 0, inz = 0));
  emit(Str("N=", N, " doubles at the ", k, "-th roots of unity", if (n, Str(", simple ", sim), ""), ": rank ", rk, " of ", R,
    "; deg P=", poldegree(P), "; branch multiplicities ", mult, "; non-branch degree ", poldegree(P0), " (T(a) ", Tcount(N, a), ")",
    "; multiplicity at the fixed point t=0: ", v0, "; rest is a polynomial in z^", k, ": ", inz,
    "; rest squarefree: ", poldegree(gcd(Q, deriv(Q))) == 0));
}
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
{
my(p = 2^61 - 1, w = Mod(1, p)); for (x = 2, 100, my(c = Mod(x, p)^((p - 1) / 3)); if (c != 1, w = c; break));
symtest([Mod(1, 2^61 - 1), w, w^2], [], 3);
symtest([Mod(1, 2^61 - 1), w, w^2], [Mod(0, 2^61 - 1)], 3);
}
