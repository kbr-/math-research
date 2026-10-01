\\ Cherry window (7 October 2026; cycle bmd-20261007-i).  Tested statement: for a fixed generic cluster D of M roots
\\ scaled by x (roots x*d_i) and a cherry {1, 1+e} above it, the pair matrix of the M+2 roots, with columns 0..R+1
\\ (R = binom(M+2,2)), has a maximal minor that is a monomial x^a e^b times a unit of Q[[x,e]], and its corner (a,b)
\\ is componentwise below the support of every other maximal minor with columns in L' u {j > max L'}, where L' is that
\\ minor's column set.  This is the invariant (H) of thm:cube-single-tie-chain-avoidance for the joined cluster at
\\ every ratio of the two scales.  For each column set S the script prints the componentwise minimum (amin, bmin) of the
\\ support and whether x^amin e^bmin itself occurs.  lambda = 3/2.  Env MS (list of M), DS (list of d), OUT.
default(parisizemax, 2 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
b(k) = if (k < 0, 0, binomial(-3/2, k));
H(X, Y, k) = sum(n = 0, k, b(n) * b(k - n) * X^n * Y^(k - n));
pairmat(pts, ncol) = {
  my(rows = List());
  for (i = 1, #pts, for (j = i + 1, #pts, listput(rows, vector(ncol, c, H(pts[i], pts[j], c - 1)))));
  matrix(#rows, ncol, r, c, rows[r][c]);
}
corner(P) = {
  my(am = oo, bm = oo, has = 0, ce);
  if (P == 0, return([oo, oo, 0]));
  for (i = 0, poldegree(P, 'x),
    ce = polcoef(P, i, 'x);
    if (ce != 0, am = min(am, i); bm = min(bm, valuation(ce, 'e))));
  has = polcoef(polcoef(P, am, 'x), bm, 'e) != 0;
  [am, bm, has];
}
{
if (getenv("NEWTON") != "1" && getenv("VERTEX") != "1",
my(MS = eval(getenv("MS")), DS = eval(getenv("DS")));
foreach(MS, M,
  my(R = (M + 2) * (M + 1) / 2, ncol = R + 2, pts, A, res = List(), best);
  pts = concat(vector(M, i, 'x * DS[i]), [1, 1 + 'e]);
  A = pairmat(pts, ncol);
  forsubset([ncol, R], S,
    my(cols = Vec(S), P = matdet(vecextract(A, "..", cols)), cr = corner(P));
    listput(res, [apply(c -> c - 1, cols), cr]));
  emit(Str("M = ", M, ", R = ", R, ", columns 0..", R + 1, ", D = ", DS[1..M]));
  for (t = 1, #res, emit(Str("  S = ", res[t][1], "  corner (x^", res[t][2][1], ", e^", res[t][2][2], ") ", if (res[t][2][3], "attained", "NOT attained"))))));
}
\\ VERTEX=1: for S = {0..R_D-1} u J, J a (2M+1)-subset of the window R_D..R_D+2M+2 (R_D = binom(M,2)), compare the
\\ coefficient A_k(J) of p(S) at the conjectured vertex (C(R_D,2) + M(M-1) + k(k+1), (M-k)^2 + k) with the minor on J of
\\ U_(M-k), rows T^i (1+T)^(-3/2-(M-k)) (i < 2M) and (1+T)^(-3).  Prints the set of ratios A_k(J)/U(J) over J (one
\\ value = proportional) and whether every U-minor of the square window is nonzero.
umat(M, j, cols) = matrix(2 * M + 1, #cols, r, c, if (r <= 2 * M, polcoef((1 + 'T)^(-3/2 - j) * 'T^(r - 1) + O('T^(cols[c] + 1)), cols[c], 'T), polcoef((1 + 'T)^(-3) + O('T^(cols[c] + 1)), cols[c], 'T)));
{
if (getenv("VERTEX") == "1",
  my(MS = eval(getenv("MS")), DS = eval(getenv("DS")));
  foreach(MS, M,
    my(RD = M * (M - 1) / 2, R = (M + 2) * (M + 1) / 2, ncol = R + 2, pts, A, win = vector(2 * M + 3, i, RD + i - 1), x0, P, ratios, sq);
    pts = concat(vector(M, i, 'x * DS[i]), [1, 1 + 'e]);
    A = pairmat(pts, ncol);
    x0 = RD * (RD - 1) / 2 + M * (M - 1);
    emit(Str("VERTEX M = ", M, ", D = ", DS[1..M]));
    my(Ps = List());
    forsubset([2 * M + 3, 2 * M + 1], Jv, my(J = vector(#Jv, i, win[Jv[i]]), cols = concat(vector(RD, i, i), apply(c -> c + 1, J)));
      listput(Ps, [J, matdet(vecextract(A, "..", cols))]));
    for (k = 0, M - 1,
      ratios = List(); sq = matdet(umat(M, M - k, vector(2 * M + 1, i, RD + i - 1)));
      for (t = 1, #Ps, my(J = Ps[t][1], Ak = polcoef(polcoef(Ps[t][2], x0 + k * (k + 1), 'x), (M - k)^2 + k, 'e), U = matdet(umat(M, M - k, J)));
        listput(ratios, if (U == 0, if (Ak == 0, "0/0", "A/0"), Ak / U)));
      emit(Str("  vertex k = ", k, ": distinct ratios ", Set(Vec(ratios)), "; square U minor ", if (sq != 0, "nonzero", "ZERO"))))));
}
\\ NEWTON=1: for every column set, the vertices of the lower-left Newton polygon (faces with positive normal) and
\\ the edge polynomials in t = x^p / e^q, p/q the edge slope, factored over Q.  LIMIT=k: only the first k column sets.
lowhull(P) = {
  my(pts = List(), V = List(), cur, best);
  for (i = 0, poldegree(P, 'x), my(ce = polcoef(P, i, 'x)); if (ce != 0, listput(pts, [i, valuation(ce, 'e)])));
  pts = Vec(pts);
  cur = pts[1]; listput(V, cur);
  while (1,
    best = 0;
    for (k = 1, #pts, my(p = pts[k]); if (p[1] > cur[1] && p[2] < cur[2],
      if (best == 0 || (p[2] - cur[2]) * (best[1] - cur[1]) < (best[2] - cur[2]) * (p[1] - cur[1]) ||
          ((p[2] - cur[2]) * (best[1] - cur[1]) == (best[2] - cur[2]) * (p[1] - cur[1]) && p[1] > best[1]), best = p)));
    if (best == 0, break); cur = best; listput(V, cur));
  Vec(V);
}
edgepoly(P, v1, v2) = {
  my(dx = v2[1] - v1[1], de = v1[2] - v2[2], g = gcd(dx, de), p = dx / g, q = de / g, f = 0);
  for (s = 0, g, f += polcoef(polcoef(P, v1[1] + s * p, 'x), v1[2] - s * q, 'e) * 't^s);
  [p, q, factor(f)];
}
{
if (getenv("NEWTON") == "1",
  my(MS = eval(getenv("MS")), DS = eval(getenv("DS")));
  foreach(MS, M,
    my(R = (M + 2) * (M + 1) / 2, ncol = R + 2, pts, A);
    pts = concat(vector(M, i, 'x * DS[i]), [1, 1 + 'e]);
    A = pairmat(pts, ncol);
    emit(Str("NEWTON M = ", M, ", D = ", DS[1..M], " (vertices [x-exp, e-exp]; edges [p, q, factored poly in t = x^p/e^q])"));
    my(cnt = 0, lim = if (getenv("LIMIT") != 0 && getenv("LIMIT") != "", eval(getenv("LIMIT")), oo));
    forsubset([ncol, R], S, cnt++; if (cnt > lim, break);
      my(cols = Vec(S), P = matdet(vecextract(A, "..", cols)), V = lowhull(P));
      emit(Str("  S = ", apply(c -> c - 1, cols), " vertices ", V));
      for (k = 1, #V - 1, my(ed = edgepoly(P, V[k], V[k + 1])); emit(Str("    edge ", k, ": slope ", ed[1], "/", ed[2], ", ", ed[3]))))));
}
