\\ Weight-three test on the assembled spine limit of the fully clean type (1,2,2,6), N = 11 (30 September 2026;
\\ cycle bmd-20260930-zza).  Spine points: single root s = mu, pairs at q2 = 1 (shape b2) and q3 = -1 (shape b3),
\\ six-cluster at q4 = 0 (shape c).  The limit (lem:cube-pair-spine-limit) is spanned by 57 functions:
\\  A  1, z, u2, u3, u4^k (k = 1..15)                                  (empty pattern, C_i = binom(n_i, 2))
\\  B  sqrt((z-s)(z-q2)) {1, u2}; sqrt((z-s)(z-q3)) {1, u3}; sqrt((z-s)(z-q4)) {u4^k, k = 0..5}
\\  C  sqrt((z-q2)(z-q3)) {1, u2, u3, g2 u2^2 + g3 u3^2}                   (thm:cube-two-double-cross-limit)
\\  D  sqrt((z-q2)(z-q4)) {1, u2, u2^2, u2^3, u4, .., u4^7, al2 u2^4 + be2 u4^8}   (cor:cube-two-n-limit-small, n = 6)
\\  E  sqrt((z-q3)(z-q4)) {1, u3, u3^2, u3^3, u4, .., u4^7, al3 u3^4 + be3 u4^8}
\\ with u_i = 1/(z - q_i), g = (difference of the pair shape)^2/16, and (al, be) the u1^4 : u2^8 ratio of the order-10
\\ limit function of the (2,6) class, computed here exactly by valuation reduction (as in bmd_cube_two_n_extras.gp)
\\ for the pair and cluster shapes in the frame with pair at 0 and cluster at 1 (D: reflection z -> 1 - z, shapes
\\ negated; E: translation z -> z + 1).  Modulo q = 2^61 - 1, for random mu: exact local exponent sets at s, q2, q3,
\\ q4 (echelon of Laurent coefficients of the normalized functions, sqrt constants dropped per class), the Wronskian
\\ order there, W = det of Taylor coefficients times the class factors, Q = W * prod (z - x)^(-ord_x) interpolated
\\ with check points, and gcd(Q, Q', Q'').  A root of Q of multiplicity >= 3 is a non-special point of weight >= 3.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 4000000000);
PR = 2^61 - 1;
\\ ---- exact (2,n) flat limit, order-10 u1^4 : u2^8 ratio (rational arithmetic) ----
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
  while (1, iter++; if (iter > 5000, error("no convergence"));
    for (i = 1, n, vals[i] = vecmin(vector(D, t, if (R[i, t] == 0, oo, valuation(R[i, t], 'e)))));
    my(L = matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e)), ker = matker(L~));
    if (#ker == 0, break);
    my(w = ker[, 1], i0 = 0, best = -oo);
    for (i = 1, n, if (w[i] != 0 && vals[i] > best, best = vals[i]; i0 = i));
    R[i0, ] = sum(i = 1, n, w[i] * 'e^(best - vals[i]) * R[i, ]);
    for (t = 1, D, R[i0, t] = truncate(R[i0, t] + O('e^(K + 1)))));
  [vals, matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e))];
}
tieratio(b, c) = {
  my(K = 18, res = flat(b, c, K), vals = res[1], L = res[2], i = 0);
  if (vecsort(vals) != [0, 1, 1, 2, 3, 4, 4, 5, 7, 8, 9, 10], error(Str("orders ", vecsort(vals))));
  for (j = 1, #vals, if (vals[j] == 10, i = j));
  [L[i, 4], L[i, K + 8]];   \\ coefficients of u1^4 (pole 4 at 0) and u2^8 (pole 8 at 1)
}
\\ ---- the 57 functions, as [class, rational part] with class = [a, b] (sqrt((z-a)(z-b))) or 0 ----
funcs(mu, q2, q3, q4, g2, g3, t2, t3) = {
  my(u(x) = 1 / ('z - x), L = List());
  listput(L, [0, 1]); listput(L, [0, 'z]); listput(L, [0, u(q2)]); listput(L, [0, u(q3)]);
  for (k = 1, 15, listput(L, [0, u(q4)^k]));
  listput(L, [[mu, q2], 1]); listput(L, [[mu, q2], u(q2)]); listput(L, [[mu, q3], 1]); listput(L, [[mu, q3], u(q3)]);
  for (k = 0, 5, listput(L, [[mu, q4], u(q4)^k]));
  foreach ([1, u(q2), u(q3), g2 * u(q2)^2 + g3 * u(q3)^2], f, listput(L, [[q2, q3], f]));
  foreach ([[q2, t2], [q3, t3]], pt, my(x = pt[1], t = pt[2]);
    for (a = 0, 3, listput(L, [[x, q4], u(x)^a])); for (k = 1, 7, listput(L, [[x, q4], u(q4)^k]));
    listput(L, [[x, q4], t[1] * u(x)^4 + t[2] * u(q4)^8]));
  Vec(L);
}
\\ Taylor/Laurent coefficients at z = x0 (in t = z - x0), orders lo..hi, of g_c/g_c-constant * r, mod PR.
\\ At a special point x0 in the class, the factor sqrt(z - x0) is dropped (exponent shift by 1/2 recorded).
ser(F, x0, N) = {
  my(cl = F[1], r = subst(F[2], 'z, x0 + 'T), half = 0, g = 1 + O('T^(N + 20)));
  if (cl != 0, foreach (cl, a, if (a == x0, half = 1, my(d = x0 - a); g *= (1 + 'T / d + O('T^(N + 20)))^(1/2))));
  [r * g, half];
}
expset(FS, x0, N) = {
  \\ exponents at x0: separate integer and half-integer monodromy groups; echelon of Laurent coefficients
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
  \\ class factor g_c(z0)^(dim_c) = ((z0-a)(z0-b))^(dim_c/2): multiply per function by sqrt -> collect per class
  my(C = List()); for (i = 1, #FS, if (FS[i][1] != 0, listput(C, FS[i][1])));
  my(Cs = Set(apply(x -> Str(x), Vec(C))));
  foreach (Cs, key, my(d = #select(x -> Str(x) == key, Vec(C)), cl = eval(key)); if (d % 2, error("odd class")); fac *= Mod((z0 - cl[1]) * (z0 - cl[2]), PR)^(d / 2));
  matdet(M) * fac;
}
main() = {
  my(q2 = 1, q3 = -1, q4 = 0, b2 = [-1, 1], b3 = [-1, 2], c = [-5, -2, 0, 1, 2, 4]);
  my(g2 = (b2[1] - b2[2])^2 / 16, g3 = (b3[1] - b3[2])^2 / 16);
  my(t2 = tieratio(-b2, -c), t3 = tieratio(b3, c));
  emit(Str("tie ratios (u_pair^4, u_cluster^8): D ", t2, ", E ", t3));
  foreach ([987654321, 123456789012345], mu,
    my(FS = funcs(mu, q2, q3, q4, g2, g3, t2, t3), n = #FS, N = 80, ords = List());
    if (n != 57, error("count"));
    my(tot = 0);
    foreach ([mu, q2, q3, q4], x, my(es = expset(FS, x, N), o = vecsum(es) - n * (n - 1) / 2);
      if (#es != n, error("exponents")); listput(ords, [x, o]); emit(Str("mu=", mu, ": point ", x, ": exponents ", es, "; Wronskian order ", o)));
    \\ Q = W * prod (z - x)^(-ord_x); interpolate with degree bound DB, check at extra points
    my(DB = 700, pts = vector(DB + 4, i, 1000 + 7 * i), vals = vector(#pts, i, my(z0 = pts[i], w = wr(FS, z0, n)); foreach (ords, xo, w *= Mod(z0 - xo[1], PR)^(-xo[2])); w));
    my(Qp = polinterpolate(pts[1..DB + 1], vals[1..DB + 1], 'x));
    my(okc = prod(i = DB + 2, #pts, subst(Qp, 'x, pts[i]) == vals[i]));
    my(d = poldegree(Qp));
    emit(Str("mu=", mu, ": deg Q = ", d, " (bound ", DB, "), check points ok: ", okc));
    foreach (ords, xo, if (subst(Qp, 'x, xo[1]) == 0, emit(Str("  Q vanishes at special point ", xo[1]))));
    my(g1 = gcd(Qp, deriv(Qp, 'x)), g3 = gcd(g1, deriv(deriv(Qp, 'x), 'x)));
    emit(Str("mu=", mu, ": deg gcd(Q,Q') = ", poldegree(g1), ", deg gcd(Q,Q',Q'') = ", poldegree(g3))));
}
main();
quit
