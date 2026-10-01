\\ Branch values of the middle-step far polynomials (4 October 2026; cycle bmd-20261004-g).
\\ Tested statement (conj:cube-middle-far-staircase-count): for the middle far component F (blocks (1+x)^g x^b P_<cnt,
\\ [g,b,cnt] = [0,0,R_e],[-3,0,1],[0,-(R_l+2),R_l],[-7/2,0,4e],[-5/2,1/2-4l,4l],[0,-7/2+4e-4el,4el], branch point -1),
\\ the leading coefficients L_P = (pivot minors) * Vandermonde(local exponents) at P in {0,-1,oo} satisfy
\\ |W(0)/lc| = |L_0/L_oo| and |W(-1)/lc| = |L_-1/L_oo| (control), and at the collapse primes p of the Ore staircase
\\ v_p(L_-1) - v_p(L_oo) = v_p(W(-1)) = number of staircase sides, v_p(L_0) - v_p(L_oo) = 1, with the p-adic part of
\\ L_-1 / L_oo coming only from Vandermonde pairs of exponents at distance p/2 (minors p-adic units).
\\ Exponents: incremental elimination modulo q = 2^61 - 1 (first columns where the rank grows); minors exact over Q.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 4000000000);
Rn(n) = n * (2 * n - 1);
blocks(e, l) = [[0, 0, Rn(e)], [-3, 0, 1], [0, -(Rn(l) + 2), Rn(l)], [-7/2, 0, 4 * e], [-5/2, 1/2 - 4 * l, 4 * l], [0, -7/2 + 4 * e - 4 * e * l, 4 * e * l]];
localfuns(e, l, P, N) = {
  my(L = List());
  foreach (blocks(e, l), B, my(g = B[1], b = B[2]);
    for (j = 0, B[3] - 1,
      if (P == 0, listput(L, [b + j, (1 + 'u + O('u^N))^g]));
      if (P == -1, listput(L, [g, (-1 + 'u + O('u^N))^(b + j)]));
      if (P == oo, listput(L, [-(g + b + j), (1 + 'u + O('u^N))^g]))));
  Vec(L);
}
\\ pivots of the rows of M (G x C, rational) as the first columns where the rank grows, mod q
pivots(M, q) = {
  my(G = #M~, C = #M, A = M * Mod(1, q), basis = List(), piv = List());
  \\ column-by-column: maintain an echelon basis of the column space restricted to rows
  my(E = matrix(G, 0), r = 0);
  for (k = 1, C,
    my(col = A[, k], E2 = matconcat([E, col]));
    if (matrank(E2) > r, E = E2; r++; listput(piv, k); if (r == G, break)));
  Vec(piv);
}
leading(e, l, P) = {
  my(d = Rn(e) + 1 + Rn(l) + 4 * e + 4 * l + 4 * e * l, N = 3 * d + 20, F = localfuns(e, l, P, N), cls = List(), exps = List(), dets = List(), q = 2^61 - 1);
  foreach (F, f, my(c = frac(f[1])); if (!setsearch(Set(cls), c), listput(cls, c)));
  foreach (cls, c,
    my(G = select(f -> frac(f[1]) == c, F), m = vecmin(apply(f -> f[1], G)), C = N - 5, M = matrix(#G, C));
    for (i = 1, #G, my(s = G[i][2] * 'u^(G[i][1] - m)); for (k = 0, C - 1, M[i, k + 1] = polcoef(s, k, 'u)));
    my(piv = pivots(M, q));
    if (#piv < #G, error("rank deficient class"));
    listput(dets, matdet(matrix(#G, #G, i, j, M[i, piv[j]])));
    foreach (piv, k, listput(exps, m + k - 1)));
  my(ex = vecsort(Vec(exps)), V = prod(i = 1, #ex, prod(j = i + 1, #ex, ex[j] - ex[i])));
  [prod(i = 1, #dets, dets[i]), V, ex];
}
\\ SCAN mode (cycle bmd-20261004-h; conj:cube-middle-far-layer-count): from local data alone (no W needed), for each
\\ (e, l) in SCANLIST and every prime p in (d, 3d], report v_p(L_0/L_oo), v_p(L_-1/L_oo) and the valuations of the
\\ pivot-minor ratios; the prediction is a run of primes with minors units, v_p(L_0/L_oo) = 1 and v_p(L_-1/L_oo) = R_l.
SCAN = getenv("SCAN");
\\ SETS mode (cycle bmd-20261004-i; lem:cube-far-layer-count): compare the computed local exponents with the predicted
\\ sets I_0 = [-R_l-2,-3] u [0,R_e+4e], H_0 = [4e-4el-7/2, 4e+4l-9/2], I_-1 = {-3} u [0, M-1] (M = R_e+R_l+4el),
\\ H_-1 = -7/2 + [0, 4e+4l-1], I_oo = [-(R_e-1),0] u [3, R_l+4l+3], H_oo = 9/2-4e + [0, 4el+4e-1], and the predicted
\\ window max(d, 2 Q_lo + 1) < p <= 2(R_e+4el+3)+1 against the scanned valuations.
SETS = getenv("SETS");
rng(a, b) = vector(b - a + 1, i, a + i - 1);
{
if (SETS != 0 && SETS != "",
  foreach (eval(SETS), el,
    my(e = el[1], l = el[2], Re = Rn(e), Rl = Rn(l), M = Re + Rl + 4 * e * l, d = Re + 1 + Rl + 4 * e + 4 * l + 4 * e * l);
    my(P0 = vecsort(concat([rng(-Rl - 2, -3), rng(0, Re + 4 * e), rng(4 * e - 4 * e * l - 7/2, 4 * e + 4 * l - 9/2)])));
    my(P1 = vecsort(concat([[-3], rng(0, M - 1), apply(i -> -7/2 + i, rng(0, 4 * e + 4 * l - 1))])));
    my(Pi = vecsort(concat([rng(-(Re - 1), 0), rng(3, Rl + 4 * l + 3), apply(i -> 9/2 - 4 * e + i, rng(0, 4 * e * l + 4 * e - 1))])));
    my(c0 = leading(e, l, 0)[3] == P0, c1 = leading(e, l, -1)[3] == P1, ci = leading(e, l, oo)[3] == Pi);
    my(Qlo = vecmax([M + 3 - 4 * e - 4 * l, 4 * e * l + 3, Rl + 4 * l + 4 * e - 1, Re - 4 * l + 4, Re + 3 - 4 * e, 4 * e * l - 4 * e + 3]), Qhi = Re + 4 * e * l + 3);
    emit(Str("SETS e=", e, ", l=", l, ": exponents at 0, -1, oo as predicted: ", [c0, c1, ci], "; predicted window ", max(d, 2 * Qlo + 1) + 1, " <= p <= ", 2 * Qhi + 1, if (Qlo > Qhi, " (empty: Q_lo > Q_hi)", ""))));
  quit);
}
{
if (SCAN != 0 && SCAN != "",
  foreach (eval(SCAN), el,
    my(e = el[1], l = el[2], d = Rn(e) + 1 + Rn(l) + 4 * e + 4 * l + 4 * e * l, A0 = leading(e, l, 0), Am = leading(e, l, -1), Ai = leading(e, l, oo), res = List());
    forprime (p = d + 1, 3 * d, listput(res, [p, valuation(A0[1] * A0[2], p) - valuation(Ai[1] * Ai[2], p), valuation(Am[1] * Am[2], p) - valuation(Ai[1] * Ai[2], p), valuation(A0[1], p) - valuation(Ai[1], p), valuation(Am[1], p) - valuation(Ai[1], p)]));
    emit(Str("SCAN e=", e, ", l=", l, ", d=", d, ", R_l=", Rn(l), ": [p, v_p(L0/Loo), v_p(L-1/Loo), v_p(minors_0/minors_oo), v_p(minors_-1/minors_oo)]: ", Vec(res))));
  quit);
}
{
foreach ([[6, 4, [53, 59, 61, 67, 71, 73, 79, 83]], [7, 5, [67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127]], [8, 6, [97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173]]], spec,
  my(b = spec[1], k = spec[2], e = k - 1, l = b - k, W = read(Str("research/results/bmd-20261003-zzm/W_mid_b", b, "_k", k, ".gp")));
  my(A0 = leading(e, l, 0), Am = leading(e, l, -1), Ai = leading(e, l, oo));
  my(L0 = A0[1] * A0[2], Lm = Am[1] * Am[2], Li = Ai[1] * Ai[2], lc = pollead(W), w0 = polcoef(W, 0), wm = subst(W, 'x, -1));
  emit(Str("(b,k) = (", b, ",", k, "), e=", e, ", l=", l, ": control |W(0)/lc| = |L0/Loo|: ", abs(w0 / lc) == abs(L0 / Li), ", |W(-1)/lc| = |L-1/Loo|: ", abs(wm / lc) == abs(Lm / Li)));
  my(res = List());
  foreach (spec[3], p,
    listput(res, [p, valuation(wm, p) - valuation(lc, p), valuation(Am[2], p) - valuation(Ai[2], p), valuation(Am[1], p) - valuation(Ai[1], p), valuation(w0, p) - valuation(lc, p), valuation(A0[2], p) - valuation(Ai[2], p)]));
  emit(Str("  [p, v_p(W(-1)/lc), v_p(V_-1/V_oo), v_p(minors_-1/minors_oo), v_p(W(0)/lc), v_p(V_0/V_oo)]: ", Vec(res))));
}
