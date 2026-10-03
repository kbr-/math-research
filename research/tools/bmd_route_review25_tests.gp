\\ Route review tests (cycle bmd-20261009-bl, 9 October 2026).
\\ (1) Falsification attempt for hypothesis (F) (cor:cube-fixed-cluster-breakpoints): on fixed-cluster arcs, the least
\\     value of family p over ALL coordinates (full P_Lambda, so higher u-coefficients included) should be
\\     f_p = b_p + w_x j_(M-p) with the unique minimizer [-p,-1] u O_p. Exact h-determinant valuations at M = 6 clusters
\\     with long Hankel blocks (z^6 + z + 1: block k0 = 0, N = 5; z^6 + z^3 - 2: two blocks), rates (1,1) and (3,2),
\\     all 12-sets with E+ <= j_max + 2, E- <= 1. Reports violations (value < f_p), ties at f_p other than the pivot set,
\\     and whether the family minimum equals f_p.
\\ (2) Lee-Yang-type bridge test: for random real clusters with distinct coordinates, are the flowed Hankel
\\     polynomials Hhat_k(t) = sum_S Vand(y_S)^2 prod_(i not in S)(1 - t y_i)^(2k) real-rooted?
OUT = "research/results/bmd-20261009-bl/review-tests.txt";
default(parisizemax, 2 * 10^9);
default(threadsizemax, 4 * 10^8);
default(nbthreads, 12);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
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
hank(p, M, k) = matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, p[i + j - 2])));
\\ Hankel pivot set of C_k from power sums (exact): greedy row rank
hpivots(sv, k, T) = {
  my(A = matrix(T, k + 1, r, c, sv[r + c - 1]), ords = List(), prev = 0);
  for (i = 1, T, my(ri = matrank(A[1..i, ])); if (ri > prev, listput(ords, i - 1); prev = ri));
  Vec(ords);
}
{
  my(NSv = 80);
  foreach([[6, 'z^6 + 'z + 1], [6, 'z^6 + 'z^3 - 2]], cl,
    my([M, P] = cl, pi = Polrev(Vec(P), 'z), hv = Vec(1 / pi + O('z^NSv)), sv = Vec(-'z * deriv(pi, 'z) / pi + M + O('z^NSv)));
    my(jk = vector(M, p, my(k = M - p, O = hpivots(sv, k, 40)); vecsum(O) - k * (k + 1) / 2));  \\ j_(M-p) = weight of Hankel pivots
    my(Emax = vecmax(jk) + 2);
    write(OUT, "(1) ", P, ": flow orders by p (j_(M-p)) = ", jk);
    foreach([[1, 1], [3, 2]], w,
      \\ (a first run used a fixed h-series length 80, too short for the valuation precision)
      my(NS = vecmax(vector(M, p, bwin(M, p, w[1], w[2]))) + (Emax + 4) * max(w[1], w[2]) + 6, hv = Vec(1 / pi + O('z^(2 * NS + 4 * M))));
      for (p = 1, M,
        my(F = famsets(M, p, Emax, 1), Vs = parapply(c -> valh(hv, M, c[1], w[1], w[2], NS), F), fp = bwin(M, p, w[1], w[2]) + w[1] * jk[p]);
        my(k = M - p, O = hpivots(sv, k, 40), piv = concat([-p .. -1], concat([0 .. M - 2], apply(x -> x + M - 1, O))));
        my(viol = select(i -> Vs[i] < fp, [1 .. #F]), ties = select(i -> Vs[i] == fp, [1 .. #F]));
        my(tieok = (#ties == 1 && F[ties[1]][1] == piv));
        write(OUT, "   rate ", w, ", p = ", p, ": f_p = ", fp, ", family min ", vecmin(Vs), ", violations ", #viol, ", minimizer unique and = pivot set: ", tieok))));
  \\ (2) Lee-Yang test
  setrand(7);
  for (M = 4, 6, for (trial = 1, 3,
    my(y = vector(M, i, random(41) - 20)); while (#Set(y) < M, y = vector(M, i, random(41) - 20));
    my(res = List());
    for (k = 1, M - 2,
      my(Hh = 0);
      forsubset([M, k + 1], S, my(v = prod(a = 1, k + 1, prod(b = a + 1, k + 1, y[S[b]] - y[S[a]])), inS = vector(M));
        for (a = 1, k + 1, inS[S[a]] = 1);
        Hh += v^2 * prod(i = 1, M, if (inS[i], 1, (1 - 't * y[i])^(2 * k))));
      my(d = poldegree(Hh, 't), nr = #polrootsreal(Hh));
      listput(res, [k, d, nr]));
    write(OUT, "(2) M = ", M, ", y = ", y, ": [k, degree of Hhat_k, number of real roots] = ", Vec(res))));
}
