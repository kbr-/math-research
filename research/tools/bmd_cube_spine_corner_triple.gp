\\ Weight-three limits on two-wall strata of neck chains (1 October 2026; cycle bmd-20261001-l).
\\ Setting of bmd_cube_spine_chain_weights.gp.  When two necks t, t' sit on walls of their chains at once (scale
\\ ratios on edge normals), cor:cube-neck-corner-pencil-chain puts both neck classes on pencils, so the limits of
\\ V_a form the two-parameter family V(k1,k2) = V_00 + <f0 + k1 f1> + <f0' + k2 f1'>, and the Wronskian is bilinear:
\\   det(k1,k2) = d00 + k1 d10 + k2 d01 + k1 k2 d11,
\\ with the four determinants computed with the same row order and the same normalization (exact signs; no squares).
\\ A member has a zero of order >= 3 at a non-special point p iff (1,k1,k2,k1k2) spans the kernel of the 3x4 jet
\\ matrix J(p) = [D; D'; D''], D = (d00,d10,d01,d11), i.e. (generically) iff the kernel vector x(p) of 3x3 minors
\\ satisfies Seg(p) = x0 x3 - x1 x2 = 0 with x0 != 0.  By dimension count such p are expected unless structure
\\ prevents them; a root gives a limit of weight >= 3 over an interior point of the F-curve, which puts that point
\\ in the closure of the weight-three locus (the hypothesis of lem:cube-contact-fcurve-criterion (3) fails there).
\\ Computed modulo p = 2^61 - 1 at one cross-ratio: the polynomials P_ab = d_ab prod (z - q_k)^(E_k) (common E_k
\\ clearing all poles at the special points), Seg, the gcd of the x_k, and the degree of Seg off the special points.
default(threadsizemax, 400000000); default(parisizemax, 2000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
PR = 2^61 - 1;
\\ mv[t] = [0] vertex al[t]; mv[t] = [1, ch] pencil with base al[t]: rows 1, u_i^(1..a), u_j^(1..b-1), then u_i^(a+1) (ch 0) or u_j^b (ch 1)
funcs(sizes, q, al, mv) = {
  my(u(x) = 1 / ('z - x), L = List(), s = 0, t = 0);
  listput(L, [0, 1]); listput(L, [0, 'z]);
  for (i = 1, 4, if (sizes[i] >= 2, for (k = 1, sizes[i] * (sizes[i] - 1) / 2, listput(L, [0, u(q[i])^k]))));
  for (i = 1, 4, if (sizes[i] == 1, s = i));
  if (s, for (j = 1, 4, if (j != s, if (sizes[j] == 1, listput(L, [[q[s], q[j]], 1]), for (k = 0, sizes[j] - 1, listput(L, [[q[s], q[j]], u(q[j])^k]))))));
  for (i = 1, 4, for (j = i + 1, 4, if (sizes[i] >= 2 && sizes[j] >= 2,
    t++; my(m = sizes[i], n = sizes[j], a = al[t], b = m * n - 1 - a, cl = [q[i], q[j]]);
    listput(L, [cl, 1]);
    for (k = 1, a, listput(L, [cl, u(q[i])^k]));
    if (mv[t][1] == 0,
      for (k = 1, b, listput(L, [cl, u(q[j])^k])),
      for (k = 1, b - 1, listput(L, [cl, u(q[j])^k]));
      listput(L, [cl, if (mv[t][2] == 0, u(q[i])^(a + 1), u(q[j])^b)])))));
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
rawdet(FS, z0, n) = {
  my(M = matrix(n, n));
  for (i = 1, n, my(sh = ser(FS[i], Mod(z0, PR), n + 1)); for (k = 1, n, M[i, k] = polcoef(sh[1], k - 1, 'T)));
  matdet(M);
}
\\ task = [sizes, mu, al, mv, pts]: returns [Wronskian orders at q, phi at q, raw det values at pts]
job(task) = {
  my(sizes = task[1], mu = task[2], q = [mu, 1, -1, 0], FS = funcs(sizes, q, task[3], task[4]), n = #FS, ords = vector(4), phi = vector(4));
  if (n != 2 + vecsum(sizes) * (vecsum(sizes) - 1) / 2, error(Str("count ", n)));
  for (k = 1, 4, my(es = expset(FS, q[k], 90)); if (#es != n, error("exponents")); ords[k] = vecsum(es) - n * (n - 1) / 2;
    phi[k] = sum(i = 1, n, if (FS[i][1] != 0 && (FS[i][1][1] == q[k] || FS[i][1][2] == q[k]), 1/2, 0)));
  [ords, phi, vector(#task[5], i, rawdet(FS, task[5][i], n))];
}
export(PR, funcs, ser, expset, rawdet, job);
dn(P, k) = { for (i = 1, k, P = deriv(P, 'x)); P; }
strip(P, q) = { foreach (q, x, my(xx = Mod(x, PR)); while (poldegree(P) > 0 && subst(P, 'x, xx) == 0, P = P / ('x - xx))); P; }
stratum(sizes, mu, al, t1, t2) = {
  my(q = [mu, 1, -1, 0], DB = 2600, pts = vector(DB + 4, i, 1000 + 7 * i), tasks = List(), keys = [[0, 0], [1, 0], [0, 1], [1, 1]]);
  foreach (keys, kk, my(mv = vector(#al, t, [0])); mv[t1] = [1, kk[1]]; mv[t2] = [1, kk[2]]; listput(tasks, [sizes, mu, al, mv, pts]));
  my(res = parapply(job, Vec(tasks)), E = vector(4, k, vecmax(vector(4, a, res[a][2][k] - res[a][1][k]))), P = vector(4), ok = 1);
  for (a = 1, 4, my(v = vector(#pts, i, res[a][3][i] * prod(k = 1, 4, Mod(pts[i] - q[k], PR)^E[k])));
    P[a] = polinterpolate(pts[1..DB + 1], v[1..DB + 1], 'x);
    ok = ok && prod(i = DB + 2, #pts, subst(P[a], 'x, pts[i]) == v[i]));
  my(J = matrix(3, 4, r, c, dn(P[c], r - 1)), x = vector(4, c, (-1)^(c - 1) * matdet(vecextract(J, [1, 2, 3], setminus([1, 2, 3, 4], [c])))));
  my(Seg = x[1] * x[4] - x[2] * x[3], gx = gcd(gcd(x[1], x[2]), gcd(x[3], x[4])));
  my(S0 = strip(Seg, q), g0 = strip(gx, q), Sr = S0);
  if (poldegree(g0) > 0, Sr = S0 / gcd(S0, g0^poldegree(S0)));
  my(rts = polrootsmod(Sr, PR));
  my(fin = select(r -> subst(x[1], 'x, r) != 0, rts));
  emit(Str("type ", sizes, " mu=", mu, " alphas ", al, " pencils on necks ", t1, ", ", t2, ": orders ", apply(r -> r[1], res),
    "; E = ", E, "; deg P = ", apply(poldegree, P), " (bound ", DB, ", checks ok ", ok, "); deg Seg = ", poldegree(Seg),
    ", off special points ", poldegree(S0), ", after removing common kernel degeneracy ", poldegree(Sr),
    "; roots in F_p: ", #rts, ", with x0 != 0: ", #fin));
  foreach (fin, r, my(xv = vector(4, c, subst(x[c], 'x, r)), k1 = xv[2] / xv[1], k2 = xv[3] / xv[1],
      F = P[1] + k1 * P[2] + k2 * P[3] + k1 * k2 * P[4], ord = 0, G = F);
    while (subst(G, 'x, r) == 0 && poldegree(G) > 0, ord++; G = G / ('x - r));
    emit(Str("   root z = ", lift(r), ": k1 = ", lift(k1), ", k2 = ", lift(k2), ", order of the member's Wronskian there: ", ord)));
}
{
  stratum([1, 2, 2, 6], 7/3, [1, 2, 3], 2, 3);
  stratum([1, 2, 2, 6], 7/3, [2, 4, 1], 2, 3);
}
quit
