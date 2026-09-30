\\ Base of the Wronskian descent at N = 11 (30 September 2026; cycle bmd-20260930-zzl): the header and
\\ functions of bmd_cube_base_weight.gp unchanged, applied to V^(5) with doubles 1, 2, -3, 5, -7 and
\\ simple root 11.  env SIZE=9 runs the recorded N = 9 case (doubles 1, 2, -3, 5, simple 7) for sizing.
\\ Original header (N = 8, 9 there):
\\ Tested statement (the hypothesis of cor:cube-collision-half-reduction at the base, b = floor(N/2)):
\\ at some configuration where the base space V^(b) attains its count T(b), every finite
\\ non-branch Weierstrass point has weight at most two. Sufficient here: rows independent, degree and
\\ every branch multiplicity equal to the bound (attainment) and the non-branch part squarefree.
\\ N = 8: V^(4), doubles 1, 2, -3, 5; N = 9: V^(4), doubles 1, 2, -3, 5 and simple root 7.
\\ Functions copied unchanged from bmd_cube_hierarchical_attainment.gp (rows of V^(a), minimal
\\ multiplicities, T(a)); computation mod p = 2^61-1 by interpolation, checked at two extra
\\ points. Equality of degree and multiplicities mod p gives equality over Q (multiplicities can only
\\ rise mod p and are bounded below by the minimal ones), and squarefree mod p at equal degree gives
\\ squarefree over Q, so a passing line is a characteristic-zero certificate for that N.
OUT = getenv("OUT");
default(parisizemax, 4000000000);
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
if (getenv("SIZE") == "9", test([1, 2, -3, 5], [7]), test([1, 2, -3, 5, -7], [11]));
