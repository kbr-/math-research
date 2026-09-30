\\ Weight test on assembled spine limits of fully clean types (30 September 2026; cycle bmd-20260930-zzd).
\\ A type (n_1..n_4) sits at spine points q = [mu, 1, -1, 0] (in the order given), with fixed rational shapes.
\\ The limit (lem:cube-multicluster-spine-classes) is the direct sum of
\\  A  1, z, u_i^k (k = 1..binom(n_i,2)) for every cluster of size >= 2        (weight-0 clusters; checked below)
\\  B  sqrt((z-q_s)(z-q_j)) u_j^k, k < n_j, for the single root s and each other point j
\\  C  sqrt((z-q_i)(z-q_j)) L_ij for clusters of sizes >= 2, with L_ij the exact flat limit of the two-cluster
\\     class, computed by valuation reduction over Q[[eps]] in the frame w = (z - q_i)/(q_j - q_i) (shapes divided
\\     by q_j - q_i) and transported back (u' = (q_j - q_i) u).  No conjecture is used.
\\ Then, modulo q = 2^61 - 1: local exponent sets at the four special points, Wronskian orders there, the remaining
\\ polynomial Q interpolated with check points, and gcd(Q, Q').  Control: (1,2,2,6) with the shapes of
\\ bmd_cube_1226_spine_weight.gp must again give deg Q = 378 and a squarefree Q (at a small rational mu here).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 4000000000);
PR = 2^61 - 1;
coords(a, c, K) = {
  my(F = 1 / ('z^a * ('z - 1)^c), v = vector(2 * K + 1));
  my(s0 = F + O('z^1)); for (k = 1, K, v[k] = polcoef(s0, -k, 'z));
  my(t = subst(F, 'z, 1 + 'y) + O('y^1)); for (k = 1, K, v[K + k] = polcoef(t, -k, 'y));
  v[2 * K + 1] = if (a + c == 0, 1, 0); v;
}
flat(b, c, K) = {
  my(n1 = #b, n2 = #c, D = 2 * K + 1, rows = List(), CO = matrix(K + 1, K + 1));
  for (a = 0, K, for (cc = 0, K - a, CO[a + 1, cc + 1] = coords(a, cc, K)));
  for (j = 1, n1, for (k = 1, n2, my(r = vector(D));
    for (a = 0, K, for (cc = 0, K - a, r += binomial(1/2, a) * (-b[j])^a * binomial(1/2, cc) * (-c[k])^cc * 'e^(a + cc) * CO[a + 1, cc + 1]));
    listput(rows, r)));
  my(R = Mat(Vec(rows)~), n = n1 * n2, vals = vector(n), iter = 0);
  while (1, iter++; if (iter > 20000, error("no convergence"));
    for (i = 1, n, vals[i] = vecmin(vector(D, t, if (R[i, t] == 0, oo, valuation(R[i, t], 'e)))));
    my(L = matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e)), ker = matker(L~));
    if (#ker == 0, break);
    my(w = ker[, 1], i0 = 0, best = -oo);
    for (i = 1, n, if (w[i] != 0 && vals[i] > best, best = vals[i]; i0 = i));
    R[i0, ] = sum(i = 1, n, w[i] * 'e^(best - vals[i]) * R[i, ]);
    for (t = 1, D, R[i0, t] = truncate(R[i0, t] + O('e^(K + 1)))));
  my(L = matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e)));
  if (matrank(L) != n, error("flat limit rank"));
  if (vecmax(vals) > K - 4, error(Str("truncation too small: max order ", vecmax(vals), ", K = ", K)));
  [vals, L];
}
weightzero(b) = {
  my(m = #b, C = m * (m - 1) / 2, K = C + 2, F = List([1 + O(x^K), x + O(x^K)]));
  for (i = 1, m, for (j = i + 1, m, listput(F, ((1 - b[i] * x) * (1 - b[j] * x) + O(x^K))^(1/2))));
  matdet(matrix(K, K, r, c, polcoef(F[r], c - 1))) != 0;
}
funcs(sizes, q, sh) = {
  my(u(x) = 1 / ('z - x), L = List(), s = 0);
  listput(L, [0, 1]); listput(L, [0, 'z]);
  for (i = 1, 4, if (sizes[i] >= 2, for (k = 1, sizes[i] * (sizes[i] - 1) / 2, listput(L, [0, u(q[i])^k]))));
  for (i = 1, 4, if (sizes[i] == 1, s = i));
  if (s, for (j = 1, 4, if (j != s, if (sizes[j] == 1, listput(L, [[q[s], q[j]], 1]), for (k = 0, sizes[j] - 1, listput(L, [[q[s], q[j]], u(q[j])^k]))))));
  for (i = 1, 4, for (j = i + 1, 4, if (sizes[i] >= 2 && sizes[j] >= 2,
    my(d = q[j] - q[i], K = max(14, 4 * (sizes[i] + sizes[j])), res = flat(sh[i] / d, sh[j] / d, K), Lm = res[2]);
    for (r = 1, matsize(Lm)[1],
      my(f = Lm[r, 2 * K + 1] + sum(k = 1, K, Lm[r, k] * (d * u(q[i]))^k + Lm[r, K + k] * (d * u(q[j]))^k));
      listput(L, [[q[i], q[j]], f])))));
  Vec(L);
}
ser(F, x0, N) = {
  my(cl = F[1], r = subst(F[2], 'z, x0 + 'T), half = 0, g = 1 + O('T^(N + 20)));
  if (cl != 0, foreach (cl, a, if (a == x0, half = 1, my(d = x0 - a); g *= (1 + 'T / d + O('T^(N + 20)))^(1/2))));
  [r * g, half];
}
expset(FS, x0, N) = {
  my(res = List());
  for (h = 0, 1, my(S = List(), lo = 0);
    for (i = 1, #FS, my(sh = ser(FS[i], Mod(x0, PR), N)); if (sh[2] == h, listput(S, sh[1]); lo = min(lo, valuation(sh[1], 'T))));
    if (#S, my(M = matrix(#S, N - lo - 6, i, j, polcoef(S[i], j - 1 + lo, 'T)), r = 0);
      for (j = 1, N - lo - 6,
        my(sub = matrix(#S, j, i, jj, M[i, jj]), rk = matrank(sub));
        if (rk > r, listput(res, (j - 1 + lo) + h / 2); r = rk));
      if (r != #S, error(Str("exponent set incomplete at ", x0, ": rank ", r, " of ", #S)))));
  vecsort(Vec(res));
}
wr(FS, z0, n) = {
  my(M = matrix(n, n, i, k, 0), fac = Mod(1, PR));
  for (i = 1, n, my(sh = ser(FS[i], Mod(z0, PR), n + 1)); for (k = 1, n, M[i, k] = polcoef(sh[1], k - 1, 'T)));
  my(C = List()); for (i = 1, #FS, if (FS[i][1] != 0, listput(C, FS[i][1])));
  my(Cs = Set(apply(x -> Str(x), Vec(C))));
  \\ squared Wronskian: det^2 * prod_classes ((z0-a)(z0-b))^d is rational for every class dimension d
  foreach (Cs, key, my(d = #select(x -> Str(x) == key, Vec(C)), cl = eval(key)); fac *= Mod((z0 - cl[1]) * (z0 - cl[2]), PR)^d);
  matdet(M)^2 * fac;
}
test(sizes, sh, mu) = {
  my(q = [mu, 1, -1, 0], Nr = vecsum(sizes), FS = funcs(sizes, q, sh), n = #FS, N = 90, ords = List());
  if (n != 2 + Nr * (Nr - 1) / 2, error(Str("count ", n)));
  for (i = 1, 4, if (sizes[i] >= 3 && !weightzero(sh[i]), error(Str("weight-zero hypothesis fails for ", sh[i]))));
  foreach (q, x, my(es = expset(FS, x, N), o = vecsum(es) - n * (n - 1) / 2);
    if (#es != n, error("exponents")); listput(ords, [x, o]));
  \\ Q2 = W^2 * prod (z - x)^(-2 ord_x) = R^2; weight <= 1 off the special points iff R is squarefree
  my(DB = 1700, pts = vector(DB + 4, i, 1000 + 7 * i), vals = vector(#pts, i, my(z0 = pts[i], w = wr(FS, z0, n)); foreach (ords, xo, w *= Mod(z0 - xo[1], PR)^(-2 * xo[2])); w));
  my(Q2 = polinterpolate(pts[1..DB + 1], vals[1..DB + 1], 'x), okc = prod(i = DB + 2, #pts, subst(Q2, 'x, pts[i]) == vals[i]));
  my(R = gcd(Q2, deriv(Q2, 'x)), sq = (R^2 * pollead(Q2) / pollead(R)^2 == Q2), g1 = gcd(R, deriv(R, 'x)));
  my(spec = select(xo -> subst(Q2, 'x, xo[1]) == 0, Vec(ords)));
  emit(Str("type ", sizes, " mu=", mu, ": ", n, " functions; Wronskian orders at ", q, ": ", apply(xo -> xo[2], Vec(ords)),
    "; deg Q^2 = ", poldegree(Q2), " (bound ", DB, ", checks ok ", okc, "); Q^2 = R^2 with R = gcd(Q^2, (Q^2)'): ", sq,
    "; deg R = ", poldegree(R), "; zero at special points: ", #spec, "; deg gcd(R, R') = ", poldegree(g1)));
}
main() = {
  my(P1 = [-1, 1], P2 = [-1, 2], P3 = [-2, 3], T3 = [-1, 0, 2], F4 = [-3, -1, 1, 4], F5 = [-4, -1, 0, 2, 5], S6 = [-5, -2, 0, 1, 2, 4]);
  foreach ([7/3, -11/5], mu,
    test([1, 2, 2, 6], [[], P1, P2, S6], mu);
    test([1, 2, 3, 5], [[], P1, T3, F5], mu);
    test([2, 2, 2, 5], [P3, P1, P2, F5], mu);
    test([2, 2, 3, 4], [P3, P1, T3, F4], mu));
}
main();
quit
