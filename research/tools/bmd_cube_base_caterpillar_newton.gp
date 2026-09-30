\\ Scale-separated (caterpillar) degeneration of the base space (30 September 2026; cycle bmd-20260930-za).
\\ Base V^(b), N = 2b even (b doubles, no simple root), rows as in bmd_cube_base_weight.gp, with the doubles at
\\ separated scales D_k = CS[k] e^(b-k), CS = (2, -3, 5, -7, ..., 1) (the first listed is the hierarchy's first).
\\ Question: as e -> 0, at which scales |t| ~ e^(-slope) do the T(b) non-branch Weierstrass points sit, how many
\\ at each scale, and is each edge polynomial squarefree with no root at 0 (simple points)?
\\ Method: Q(e, t) = det(rows) * prod (1 + D_k t)^(E - m_k) mod p = 2^61 - 1, with m_k the base script's minimal
\\ multiplicities, a polynomial of t-degree T(b); interpolated in t (T(b)+1 points, two checks) at KE values of
\\ e, then each t-coefficient in e (two checks). Exactness in e: the t^d coefficient of Q is homogeneous in D of
\\ degree d + K0, K0 = R(R-1)/2 - 6 binom(b,2) (entries of column m scale as lambda^m, rows shifted by T^j scale
\\ down by j, and 1 + D t is invariant under D -> lambda D, t -> t/lambda), so its e-degree is at most
\\ (b-1)(d + K0); the script checks KE > (b-1)(T(b) + K0). Branch nonvanishing: Q(e, -1/D_k) is not identically
\\ zero; for interior k the slope-(b-k) edge polynomial must not vanish at x = -1/CS[k], for the outer k there
\\ must be no edge at slopes 0 and b-1; both are checked.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
serpow(u, al, L) = vector(L, m, binomial(al, m - 1) * u^(m - 1));
mul(A, B, L) = vector(L, n, sum(m = 1, n, A[m] * B[n + 1 - m]));
tx(B, t, L) = vector(L, n, t * B[n] + if (n > 1, B[n - 1], 0));
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
\\ Parameters: N (even) from the environment, default 6; b = N/2 doubles CS[k] e^(b-k), k = 1..b, CS = (2, -3, 5, -7, ...,
\\ last 1); DT = (N-b-2) E + 12 binom(b,2), the degree bound of the base script.
N = if (getenv("N"), eval(getenv("N")), 6); BB = N / 2; RR = binomial(N, 2); EE = binomial(RR, 2);
DT = (N - BB - 2) * EE + 12 * binomial(BB, 2);
CS = concat([2, -3, 5, -7, 11, -13][1..BB - 1], [1]);
\\ Minimal branch multiplicities of the base script (md as there; no simple roots, n = 0); dividing them out
\\ leaves the non-branch part Q(e, t) of t-degree T(b), a polynomial because the minimal multiplicities are
\\ lower bounds at every configuration.
md(N, c) = my(K = 2 * N - 4); -c * K + binomial(K, 2) - 3 + binomial(binomial(N - 2, 2), 2);
MM = vector(BB, c, my(e = c - 1, l = BB - c); md(N, if (e, 7/2, 5/2)) + 3 + 10 * l + 14 * e);
TB = DT - vecsum(MM);
g(e, t) = my(Ds = vector(BB, k, CS[k] * e^(BB - k))); matdet(rowsh(Ds, [], t, RR)) * prod(c = 1, #Ds, (1 + Ds[c] * t)^(EE - MM[c]));
DT = TB;
export(serpow, mul, tx, rowsh, g, RR, EE, DT, BB, CS, MM);
main() = {
  my(q = 2^61 - 1, KE = if (getenv("KE"), eval(getenv("KE")), 400));
  my(K0 = RR * (RR - 1) / 2 - 6 * binomial(BB, 2), ebound = (BB - 1) * (DT + K0));
  emit(Str("N=", N, " b=", BB, " CS=", CS, " T(b)=", DT, " KE=", KE, "; e-degree bound (b-1)(T(b)+K0) = ", ebound));
  if (KE <= ebound, error("KE below the e-degree bound"));
  my(ts = vector(DT + 3, j, Mod(j + 1, q)), es = vector(KE + 2, i, Mod(i + 1, q)));
  my(Y = parvector(KE + 2, i, vector(DT + 3, j, g(es[i], ts[j]))));
  my(C = matrix(KE + 2, DT + 1));
  for (i = 1, KE + 2,
    my(P = polinterpolate(ts[1..DT + 1], Y[i][1..DT + 1], 'z));
    if (subst(P, 'z, ts[DT + 2]) != Y[i][DT + 2] || subst(P, 'z, ts[DT + 3]) != Y[i][DT + 3], error("t check"));
    for (d = 0, DT, C[i, d + 1] = polcoef(P, d, 'z)));
  my(v = vector(DT + 1), cs = vector(DT + 1), degs = vector(DT + 1));
  for (d = 0, DT,
    my(c = polinterpolate(es[1..KE], C[1..KE, d + 1]~, 'e));
    if (subst(c, 'e, es[KE + 1]) != C[KE + 1, d + 1] || subst(c, 'e, es[KE + 2]) != C[KE + 2, d + 1], error("e check"));
    cs[d + 1] = c; v[d + 1] = if (c == 0, oo, valuation(c, 'e)); degs[d + 1] = poldegree(c));
  emit(Str("max e-degree of a t-coefficient: ", vecmax(degs), " (", KE, " points)"));
  my(pts = List());
  for (d = 0, DT, if (v[d + 1] != oo, listput(pts, [d, v[d + 1]])));
  my(H = List([pts[1]]));
  for (k = 2, #pts,
    while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (pts[k][1] - H[#H][1]) >= (pts[k][2] - H[#H][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H));
    listput(H, pts[k]));
  emit(Str("hull vertices: ", Vec(H)));
  \\ edge polynomials: for each hull edge, the leading forms sum over points on the edge
  for (k = 2, #H,
    my(d0 = H[k - 1][1], d1 = H[k][1], sl = (H[k][2] - H[k - 1][2]) / (d1 - d0), ep = 0);
    for (d = d0, d1, if (v[d + 1] != oo && v[d + 1] == H[k - 1][2] + sl * (d - d0),
      ep += polcoef(cs[d + 1], v[d + 1], 'e) * 'x^(d - d0)));
    my(f = factormod(lift(ep), q), br = "");
    if (denominator(sl) == 1 && sl >= 1 && sl <= BB - 2,
      br = Str("; at the branch value x = -1/CS[", BB - sl, "]: ", if (subst(ep, 'x, Mod(-1, q) / CS[BB - sl]) != 0, "nonzero", "ZERO")));
    if (sl == 0 || sl == BB - 1, br = "; OUTER BRANCH SCALE");
    emit(Str("edge slope ", -sl, " length ", d1 - d0, ": edge polynomial factor degrees and exponents ",
      vector(#f~, j, [poldegree(f[j, 1]), f[j, 2]]), br)));
}
default(nbthreads, 12);
default(parisizemax, 3000000000);
default(threadsizemax, 150000000);
main();
