\\ Attainment of the hierarchical counts T(a) (29 September 2026).
\\ Space V^(a) (see bmd_cube_hierarchical_counts.gp): doubles D_1..D_a in collision order, simple
\\ roots k. Rows: phi_k phi_l; phi_D phi_k, phi_D' phi_k; phi_D^2; for r < s the block
\\ T^j (1+D_r T)^(-5/2) (1+D_s T)^(-7/2), j = 0..3.
\\ Tested statements, at N = 7, a = 2 (doubles 1, 2; simple -1, 3, 5), N = 6, a = 3 (doubles
\\ 1, 2, -3) and N = 7, a = 3 (doubles 1, 2, -3; simple 5):
\\  (1) the rows are independent;
\\  (2) the cleared numerator P has degree <= (N-a-2)E + na + 12 binom(a,2);
\\  (3) the multiplicity at each branch value is >= the minimal one, minimal exponent sum plus
\\      pole orders: simple m_s; double with e earlier and l later doubles
\\      md(c) + 4n + 3 + 10 l + 14 e, c = 5/2 if e = 0 and 7/2 otherwise;
\\  (4) the non-branch degree is <= T(a), with equality iff (2) and (3) are equalities;
\\  (5) squarefreeness of the non-branch part is reported.
\\ Computation mod p = 2^61-1 by interpolation, checked at two extra points; as in
\\ bmd_cube_directional_two_double.gp, equality of degree and multiplicities mod p gives equality
\\ over Q, and squarefree mod p at equal degree gives squarefree over Q.
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
test(Ds, sim) = {
  my(p = 2^61 - 1, a = #Ds, n = #sim, N = 2 * a + n, R = binomial(N, 2), E = binomial(R, 2));
  my(vals = concat(Ds, sim), rk = matrank(rowsh(Ds, sim, 3, R)));
  my(D = (N - 2) * E + 3 * R, xs = List(), ys = List(), t = 1);
  while (#xs < D + 3, t++; if (prod(c = 1, #vals, 1 + vals[c] * t) % p == 0, next);
    my(tm = Mod(t, p)); listput(xs, tm); listput(ys, matdet(rowsh(Ds, sim, tm, R)) * prod(c = 1, #vals, (1 + vals[c] * tm)^E)));
  my(P = polinterpolate(Vec(xs)[1..D+1], Vec(ys)[1..D+1], 'z));
  if (subst(P, 'z, xs[D + 2]) != ys[D + 2] || subst(P, 'z, xs[D + 3]) != ys[D + 3], error("interpolation check"));
  if (P == 0, emit(Str("N=", N, " a=", a, ": Wronskian identically zero")); return);
  my(P0 = P, mult = vector(#vals));
  for (c = 1, #vals, while (subst(P0, 'z, Mod(-1, p) / vals[c]) == 0, P0 = P0 / ('z + Mod(1, p) / vals[c]); mult[c]++));
  my(minm = vector(#vals, c, if (c <= a, my(e = c - 1, l = a - c); md(N, if (e, 7/2, 5/2)) + 4 * n + 3 + 10 * l + 14 * e,
    ms(N) + 3/2 * (N - 1))));
  emit(Str("N=", N, " a=", a, " doubles ", Ds, " simple ", sim, ": rank ", rk, " of ", R,
    "; deg P=", poldegree(P), " (bound ", (N - a - 2) * E + n * a + 12 * binomial(a, 2), ")",
    "; multiplicities ", mult, " (minimal ", minm, ")",
    "; non-branch degree ", poldegree(P0), " (T(a) ", Tcount(N, a), "); squarefree ", poldegree(gcd(P0, deriv(P0))) == 0));
}
test([1, 2], [-1, 3, 5]);
test([1, 2, -3], []);
test([1, 2, -3], [5]);
