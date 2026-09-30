\\ Spine weights along the neck pencil chains (1 October 2026; cycle bmd-20261001-l).
\\ Setting of bmd_cube_spine_weight_general.gp (lem:cube-multicluster-spine-classes): a type (n_1..n_4) at spine
\\ points q = [mu, 1, -1, 0], limit of V_a = direct sum of the empty-pattern class, the single-root classes and one
\\ class sqrt((z-q_i)(z-q_j)) L_ij per pair of clusters of sizes (m,n) = (n_i,n_j) >= 2.  There L_ij was the flat
\\ limit along the linear eps-family.  Along arbitrary approaches, cor:cube-neck-corner-pencil-chain (conditional on
\\ the antidiagonal polygon and edge pencils) puts L_ij on the chain of pencils between the complete systems
\\ L(alpha[q_i] + (mn-1-alpha)[q_j]), m-1 <= alpha <= n(m-1) (poles bounded at q_i, q_j, bounded at infinity),
\\ transported from the frame w = (z-q_i)/(q_j-q_i).
\\ Tested, modulo p = 2^61 - 1, at one cross-ratio:
\\  (a) every vertex assembly (each neck at a vertex system; all combinations, a superset of the realizable ones):
\\      Wronskian orders at the special points and the multiplicities of the other zeros: S^2 = Q2 = W^2 prod
\\      (z-x)^(-2 ord_x); weight >= 2 at a point iff it is a root of gcd(S,S'), >= 3 iff a root of gcd(g,g'),
\\      g = gcd(S,S');
\\  (b) every pencil (one neck moved between adjacent vertices, the others fixed): the Wronskians of the members
\\      are det_a + kappa det_b (linear in the moving row), i.e. A + kappa B with A, B the polynomials S_a, S_b
\\      corrected by the special-point order differences; a member has a zero of order >= 3 at a non-special point
\\      p only if p is a root of the gcd of the 2x2 minors of [A B; A' B'; A'' B''] or a common root of A and B.
\\ Output per type: the vertex table and the pencil table with these degrees (special-point factors removed).
default(threadsizemax, 400000000); default(parisizemax, 2000000000);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
PR = 2^61 - 1;
funcs(sizes, q, al) = {
  my(u(x) = 1 / ('z - x), L = List(), s = 0, t = 0);
  listput(L, [0, 1]); listput(L, [0, 'z]);
  for (i = 1, 4, if (sizes[i] >= 2, for (k = 1, sizes[i] * (sizes[i] - 1) / 2, listput(L, [0, u(q[i])^k]))));
  for (i = 1, 4, if (sizes[i] == 1, s = i));
  if (s, for (j = 1, 4, if (j != s, if (sizes[j] == 1, listput(L, [[q[s], q[j]], 1]), for (k = 0, sizes[j] - 1, listput(L, [[q[s], q[j]], u(q[j])^k]))))));
  for (i = 1, 4, for (j = i + 1, 4, if (sizes[i] >= 2 && sizes[j] >= 2,
    t++; my(m = sizes[i], n = sizes[j], a = al[t], b = m * n - 1 - a);
    listput(L, [[q[i], q[j]], 1]);
    for (k = 1, a, listput(L, [[q[i], q[j]], u(q[i])^k]));
    for (k = 1, b, listput(L, [[q[i], q[j]], u(q[j])^k])))));
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
  foreach (Cs, key, my(d = #select(x -> Str(x) == key, Vec(C)), cl = eval(key)); fac *= Mod((z0 - cl[1]) * (z0 - cl[2]), PR)^d);
  matdet(M)^2 * fac;
}
\\ one vertex assembly: [orders at q, S with S^2 = Q2, deg Q2, check points ok]
vert(task) = {
  my(sizes = task[1], mu = task[2], al = task[3], q = [mu, 1, -1, 0], Nr = vecsum(sizes), FS = funcs(sizes, q, al), n = #FS, ords = List());
  if (n != 2 + Nr * (Nr - 1) / 2, error(Str("count ", n)));
  foreach (q, x, my(es = expset(FS, x, 90), o = vecsum(es) - n * (n - 1) / 2);
    if (#es != n, error("exponents")); listput(ords, o));
  my(DB = 1700, pts = vector(DB + 4, i, 1000 + 7 * i), vals = vector(#pts, i, my(z0 = pts[i], w = wr(FS, z0, n)); for (k = 1, 4, w *= Mod(z0 - q[k], PR)^(-2 * ords[k])); w));
  my(Q2 = polinterpolate(pts[1..DB + 1], vals[1..DB + 1], 'x), okc = prod(i = DB + 2, #pts, subst(Q2, 'x, pts[i]) == vals[i]));
  my(S = 0, sq = issquare(Q2, &S));
  if (!sq, error(Str("Q2 not a square for ", al)));
  [Vec(ords), S, poldegree(Q2), okc];
}
export(PR, funcs, ser, expset, wr, vert);
strip(P, q) = { foreach (q, x, my(xx = Mod(x, PR)); while (poldegree(P) > 0 && subst(P, 'x, xx) == 0, P = P / ('x - xx))); P; }
mult(S, q) = { my(S0 = strip(S, q), g = gcd(S0, deriv(S0, 'x)), g2 = gcd(g, deriv(g, 'x))); [poldegree(S0), poldegree(g), poldegree(g2)]; }
pencil(Sa, oa, Sb, ob, q) = {
  my(A = Sa, B = Sb);
  for (k = 1, 4, my(o = ob[k] - oa[k]);
    if (denominator(o) != 1, return("half-integral order difference"));
    if (o > 0, B *= ('x - Mod(q[k], PR))^o, A *= ('x - Mod(q[k], PR))^(-o)));
  my(A1 = deriv(A, 'x), B1 = deriv(B, 'x), A2 = deriv(A1, 'x), B2 = deriv(B1, 'x));
  my(g = gcd(gcd(A * B1 - A1 * B, A * B2 - A2 * B), A1 * B2 - A2 * B1), base = gcd(A, B));
  [poldegree(strip(g, q)), poldegree(strip(base, q))];
}
\\ Pencil discriminant (cycle bmd-20261001-q, lem:cube-discriminant-boundary-reducedness part (3)): with A, B as in
\\ pencil(), m1 = AB' - A'B off the special points; its roots are the points where some member has a double zero, at
\\ kappa = -A/B.  Returns [deg m1, deg gcd(m1, m1'), deg gcd(B, m1), d = dim F_p[x]/(m1), d minus the rank of the powers
\\ 1, phi, ..., phi^(d-1) of phi = -A/B mod m1 (0 iff the kappa values at the roots of the squarefree m1 are distinct),
\\ degree drop of the member with vanishing leading coefficient (0 if deg A != deg B)].
pdisc(tk) = {
  my(Sa = tk[1], oa = tk[2], Sb = tk[3], ob = tk[4], q = tk[5], A = Sa, B = Sb);
  for (k = 1, 4, my(o = ob[k] - oa[k]);
    if (denominator(o) != 1, return([-1]));
    if (o > 0, B *= ('x - Mod(q[k], PR))^o, A *= ('x - Mod(q[k], PR))^(-o)));
  my(m1 = strip(A * deriv(B, 'x) - deriv(A, 'x) * B, q), g1 = poldegree(gcd(m1, deriv(m1, 'x))), gb = poldegree(gcd(B, m1)), cp = 0, g2 = -1, drop = 0);
  if (gb == 0 && g1 == 0, my(d = poldegree(m1), ph = Mod(-A, m1) / Mod(B, m1), P = Mod(1, m1), M = matrix(d, d));
    for (j = 1, d, my(c = lift(P)); for (i = 1, d, M[i, j] = polcoef(c, i - 1, 'x)); P *= ph);
    cp = d; g2 = d - matrank(M));
  if (poldegree(A) == poldegree(B), my(k0 = -pollead(A) / pollead(B)); drop = poldegree(A) - poldegree(A + k0 * B));
  [poldegree(m1), g1, gb, if (cp == 0, -1, cp), g2, drop];
}
\\ Realizability: neck t = (i,j), sizes (m,n), vertex r (alpha = m-1+r) is the limit for scale weights with
\\ c_r/(mn-c_r) < w_j/w_i < c_(r+1)/(mn-c_(r+1)) (c_0 = 0, c_(M+1) = mn, antidiagonal edge parameters); a combination
\\ is realizable iff these difference constraints on log w are feasible (Bellman-Ford, strictness by a margin).
\\ Environment: TYPES selects types, REALIZABLE=1 keeps only realizable combinations.
edgeparams(m, n) = my(st = Set(vector(m + n - 2, s, sum(k = 0, m - 1, sum(l = 0, n - 1, k + l < s))))); select(c -> !setsearch(st, c), vector(m*n - 1, c, c));
feasible(pairs, sz, al) = {
  my(E = List(), ep = 1e-9);
  for (t = 1, #pairs, my(i = pairs[t][1], j = pairs[t][2], m = sz[i], n = sz[j], cs = concat(concat([0], edgeparams(m, n)), [m*n]), r = al[t] - (m - 1));
    my(lo = if (cs[r + 1] == 0, -1e9, log(cs[r + 1] / (m*n - cs[r + 1]))), hi = if (cs[r + 2] == m*n, 1e9, log(cs[r + 2] / (m*n - cs[r + 2]))));
    listput(E, [i, j, hi - ep]); listput(E, [j, i, -lo - ep]));
  my(d = vector(4));
  for (it = 1, 6, my(ch = 0); foreach (E, e, if (d[e[1]] + e[3] < d[e[2]], d[e[2]] = d[e[1]] + e[3]; ch = 1)); if (!ch, return(1)));
  0;
}
export(strip, pdisc);
{
  my(types = [[[1, 2, 2, 6], 7/3], [[1, 2, 3, 5], 7/3], [[2, 2, 2, 5], 7/3], [[2, 2, 3, 4], 7/3]], ty = getenv("TYPES"), sizing = getenv("SIZING") == "1");
  if (ty != 0 && ty != "", types = eval(ty));
  foreach (types, tp, my(sizes = tp[1], mu = tp[2], q = [mu, 1, -1, 0], nk = List());
    for (i = 1, 4, for (j = i + 1, 4, if (sizes[i] >= 2 && sizes[j] >= 2, listput(nk, [sizes[i], sizes[j]]))));
    my(ranges = apply(e -> [e[1] - 1, e[2] * (e[1] - 1)], Vec(nk)), combos = List());
    my(pairs = List()); for (i = 1, 4, for (j = i + 1, 4, if (sizes[i] >= 2 && sizes[j] >= 2, listput(pairs, [i, j]))));
    my(total = 0); forvec (v = ranges, total++; if (getenv("REALIZABLE") != "1" || feasible(pairs, sizes, v), listput(combos, v)));
    if (sizing, combos = List([combos[1], combos[#combos]]));
    my(res = parapply(vert, apply(v -> [sizes, mu, v], Vec(combos))));
    emit(Str("type ", sizes, " mu=", mu, " necks ", Vec(nk), " alpha ranges ", ranges, "; ", #combos, " vertex assemblies (of ", total, "; realizable only: ", getenv("REALIZABLE") == "1", ")"));
    my(idx = Map(), ptasks = List(), plabels = List());
    for (c = 1, #combos, mapput(idx, combos[c], c);
      my(r = res[c], mu3 = mult(r[2], q));
      emit(Str("  alphas ", combos[c], ": orders ", r[1], ", deg Q2 ", r[3], " checks ", r[4], "; off-special deg S ", mu3[1], ", deg gcd(S,S') ", mu3[2], ", deg of mult>=3 part ", mu3[3])));
    for (c = 1, #combos, for (t = 1, #nk, my(v = combos[c]); my(w = v, c2); w[t]++; if (v[t] < ranges[t][2] && mapisdefined(idx, w, &c2),
      my(pr = pencil(res[c][2], res[c][1], res[c2][2], res[c2][1], q));
      emit(Str("  pencil neck ", t, " between ", v, " and ", w, ": deg gcd of minors ", pr[1], ", deg common roots ", pr[2]));
      if (getenv("PENCILDISC") == "1", listput(ptasks, [res[c][2], res[c][1], res[c2][2], res[c2][1], q]); listput(plabels, Str(v, " -> ", w))))));
    if (getenv("PENCILDISC") == "1", my(pd = parapply(pdisc, Vec(ptasks)));
      for (i = 1, #pd, emit(Str("  pencil discriminant ", plabels[i], ": [deg m1, deg gcd(m1,m1'), deg gcd(B,m1), d, d - rank of powers, degree drop] = ", pd[i])))));
}
quit
