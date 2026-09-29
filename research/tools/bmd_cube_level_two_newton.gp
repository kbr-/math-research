\\ Scales of the Weierstrass points in the cluster degeneration of the level-two space (29 Sept 2026).
\\ Level-two space V^(2) at N = 7: doubles A = 3e (first), B = -2e (second, block
\\ T^j (1+AT)^(-5/2) (1+BT)^(-7/2)), simple roots 5e, 1, -1; e -> 0 clusters M = 5 positions
\\ (5e, A, A, B, B) with the far pair +-1 outside.
\\ Question: where are the T(2) = 120 non-branch points for small e? The count identity
\\ T(2) - T(3) = binom(M,2) + 2M(M-2) = 40 (bmd_cube_hierarchical_counts.gp) against face 10,
\\ neck rings 2M per slope j/M, bubble T(3) = 80 at slope 1 (level-three attainment,
\\ bmd_cube_hierarchical_attainment.gp) leaves 2M = 10 points unplaced if the neck has only the
\\ two rings j = 1, 2 that the multi-double window ranks allow.
\\ Method: the cleared numerator P(e,T) mod p = 2^61-1, by interpolation in T (degree 648, two
\\ checks) at each e, then in e (two checks); the lower Newton polygon of the e-valuations of the
\\ T-coefficients gives the scales |T| ~ e^(-slope) with multiplicity. Branch roots are known:
\\ slope 0 at T = -+1 (minimal multiplicity 120 each), slope 1 at the cluster values
\\ (87 at A, 81 at B, 120 at 5e), all minimal at generic e by the attainment test.
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
g(e, t) = {
  my(Ds = [3 * e, -2 * e], sim = [5 * e, 1, -1], vals = concat(Ds, sim));
  matdet(rowsh(Ds, sim, t, 21)) * prod(c = 1, #vals, (1 + vals[c] * t)^210);
}
export(serpow, mul, tx, rowsh, g);
main() = {
  my(q = 2^61 - 1, DT = 648, KE = if (getenv("KE"), eval(getenv("KE")), 700));
  my(ts = vector(DT + 3, j, Mod(j + 1, q)), es = vector(KE + 2, i, Mod(i + 1, q)));
  my(Y = parvector(KE + 2, i, vector(DT + 3, j, g(es[i], ts[j]))));
  my(C = matrix(KE + 2, DT + 1));
  for (i = 1, KE + 2,
    my(P = polinterpolate(ts[1..DT + 1], Y[i][1..DT + 1], 'z));
    if (subst(P, 'z, ts[DT + 2]) != Y[i][DT + 2] || subst(P, 'z, ts[DT + 3]) != Y[i][DT + 3], error("T check"));
    for (d = 0, DT, C[i, d + 1] = polcoef(P, d, 'z)));
  my(v = vector(DT + 1), degs = vector(DT + 1));
  for (d = 0, DT,
    my(c = polinterpolate(es[1..KE], C[1..KE, d + 1]~, 'e));
    if (subst(c, 'e, es[KE + 1]) != C[KE + 1, d + 1] || subst(c, 'e, es[KE + 2]) != C[KE + 2, d + 1], error("e check"));
    v[d + 1] = if (c == 0, oo, valuation(c, 'e)); degs[d + 1] = poldegree(c));
  emit(Str("max e-degree of a T-coefficient: ", vecmax(degs), " (", KE, " points)"));
  \\ lower convex hull of (d, v_d)
  my(pts = List());
  for (d = 0, DT, if (v[d + 1] != oo, listput(pts, [d, v[d + 1]])));
  my(H = List([pts[1]]));
  for (k = 2, #pts,
    while (#H >= 2 && (H[#H][2] - H[#H - 1][2]) * (pts[k][1] - H[#H][1]) >= (pts[k][2] - H[#H][2]) * (H[#H][1] - H[#H - 1][1]), listpop(H));
    listput(H, pts[k]));
  emit(Str("hull vertices: ", Vec(H)));
  my(edges = List());
  for (k = 2, #H, listput(edges, [(H[k][2] - H[k - 1][2]) / (H[k][1] - H[k - 1][1]), H[k][1] - H[k - 1][1]]));
  emit(Str("edges [slope, length]: ", Vec(edges)));
  emit("expected without escape: slope 0: 10 face + 240 far branch = 250; slopes 1/5, 2/5: 10 each; slope 1: 80 bubble + 288 cluster branch = 368; total 648 = 638 + 10 unplaced");
}
default(nbthreads, 12);
main();
