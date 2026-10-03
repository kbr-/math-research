\\ Test of the flow-order prediction (cycle bmd-20261009-bc, 9 October 2026).
\\ Prediction (conj:cube-flow-order-family-value): on fixed-cluster arcs with distinct roots y0, the least value of
\\ family p (k = M - p) is b_p + w_x j_p(y0), where j_p is the order at t = 0 of
\\ F_k(t) = prod_i (1 - t y_i)^(-2k) Hank_k(y / (1 - t y)) at y0 (first-order term (D + 2k e1) Hank_k, the top-up).
\\ Also reports j for multipliers prod (1 - t y)^c with c = 0, +2k, to see whether the multiplier matters.
\\ Per family: least value among all 10-sets (M = 5; 8-sets at M = 4) with E+ <= 7, E- <= 1, at rate (1,1) and
\\ (3,2), via the h-determinant (see bmd_quintic_sigma_leaders.gp). Clusters given by e-vectors (e1..eM):
\\ M = 5: z^5 - 1, z^5 + z + 1, z^5 + 3z - 2, a non-centred translate of z^5 + z + 1 (shift 1), generic z^5 - z^2 + 2z + 3;
\\ M = 4: square z^4 - 1 and z^4 + z + 1 (generic).
OUT = "research/results/bmd-20261009-bc/flow-order-families.txt";
default(parisizemax, 2 * 10^9);
default(threadsizemax, 4 * 10^8);
default(nbthreads, 12);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
\\ h_n from the monic polynomial P (coefficients in z): sum h_n z^n = 1 / (z^M P(1/z))
hvecP(P, N) = Vec(1 / Polrev(Vec(P), 'z) + O('z^(N + 1)));
valh(hv, M, L, wa, wb, NS) = {
  my(G = matrix(2*M, 2*M), xx = 2 * 's^wa + O('s^NS), ep = 3 * 's^wb + O('s^NS), R = NS \ wb + 1, h = (n -> if (n < 0, 0, hv[n + 1])));
  for (t = 0, M - 1,
    for (u = 1, 2*M, my(i = L[u]);
      G[t + 1, u] = if (i >= 0, cc(i) * xx^i * h(t + i - M + 1), 0);
      G[M + t + 1, u] = sum(r = max(1, -i), R, cc(r) * cc(i + r) * ep^r * xx^(i + r) * h(t + i + r - M + 1))));
  my(d = matdet(G));
  if (d == 0, oo, valuation(d, 's));
}
export(lam, cc, valh);
famsets(M, p, E, F) = {
  my(res = List());
  forsubset([2*M - p + E, 2*M - p], Sp, my(plus = apply(u -> u - 1, Vec(Sp)), Ep = vecsum(plus) - (2*M - p) * (2*M - p - 1) / 2);
    if (Ep <= E, forsubset([p + F, p], Sm, my(minus = vecsort(apply(u -> -u, Vec(Sm))), Em = -vecsum(minus) - p * (p + 1) / 2);
      if (Em <= F, listput(res, [concat(minus, plus), Ep, Em])))));
  Vec(res);
}
bwin(M, p, a, b) = a * (2*M^2 - 2*M*p + p^2 - p) + b * (p^2 - p + M);
\\ order at t = 0 of prod(1 - t y)^c * Hank_k(y / (1 - t y)), from the polynomial P, as a power series in t (precision T)
floword(P, M, k, c, T) = {
  my(Q = subst(P, 'z, 'z / (1 + 'tt * 'z)) * (1 + 'tt * 'z)^M);
  Q = Q + O('tt^T);
  my(lc = polcoeff(Q, M, 'z));
  Q = Q / lc;  \\ monic in z, coefficients series in tt
  my(a = vector(M, j, polcoeff(Q, M - j, 'z)), pw = vector(2*k + 1));  \\ z^M + a1 z^(M-1) + ...
  \\ Newton: p_j + a1 p_(j-1) + ... + a_(j-1) p_1 + j a_j = 0 (a_j = 0 for j > M)
  for (j = 1, 2*k, my(s = if (j <= M, j * a[j], 0)); for (i = 1, min(j - 1, M), s += a[i] * pw[j - i]); pw[j] = -s);
  my(H = matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, pw[i + j - 2]))));
  my(Pt = Polrev(Vec(P), 'z));  \\ prod(1 - t y) = t^M P(1/t) = Polrev(P) in t
  my(F = subst(Pt, 'z, 'tt)^c * H + O('tt^T));
  if (F == 0, oo, valuation(F, 'tt));
}
{
  my(cls = [[5, 'z^5 - 1], [5, 'z^5 + 'z + 1], [5, 'z^5 + 3*'z - 2], [5, subst('z^5 + 'z + 1, 'z, 'z - 1)], [5, 'z^5 - 'z^2 + 2*'z + 3],
            [4, 'z^4 - 1], [4, 'z^4 + 'z + 1]]);
  foreach(cls, cl,
    my([M, P] = cl, fam = vector(M, p, famsets(M, p, 7, 1)));
    write(OUT, "cluster ", P, " (M = ", M, ", disc ", poldisc(P), ")");
    my(jj = vector(M, p, my(k = M - p); [floword(P, M, k, -2*k, 30), floword(P, M, k, 0, 30), floword(P, M, k, 2*k, 30)]));
    foreach([[1, 1], [3, 2]], w,
      my(NS = vecmax(vector(M, p, bwin(M, p, w[1], w[2]))) + 12 * max(w[1], w[2]) + 6, hv = hvecP(P, 2 * NS + 4 * M));
      for (p = 1, M,
        my(F = fam[p], Vs = parapply(c -> valh(hv, M, c[1], w[1], w[2], NS), F), m = vecmin(Vs));
        my(arg = select(i -> Vs[i] == m, [1 .. #F]), b0 = bwin(M, p, w[1], w[2]));
        write(OUT, "  rate ", w, ", p = ", p, ": family min ", m, " = b_p + ", m - b0, "; predicted shifts w_x j for c = -2k, 0, 2k: ",
              apply(j -> w[1] * j, jj[p]), "; argmin [E+, E-]: ", apply(i -> [F[i][2], F[i][3]], arg)))));
}
