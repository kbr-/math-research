\\ Surviving least coefficients at the square cluster (cycle bmd-20261009-ay, 9 October 2026); conventions of
\\ bmd_topup_identity_large.gp. M = 4, cluster (1, i, -1, -i) (Hank_1 = Hank_2 = 0 = D Hank_1 = D Hank_2), exact over
\\ Q(i). For every family p = 1..4 and every 8-set L with p negatives, excess E+ <= 3 and E- <= 3
\\ (lem:cube-window-bound-excess), the least term is x^(A_p + E+) eps^(B_p + E-); report its coefficient divided by
\\ Vand^2, and list the sets where it is nonzero. Control: the cluster (1, 2, 4, 7).
OUT = "research/results/bmd-20261009-ay/square-survivors.txt";
default(parisizemax, 2 * 10^9);
lam = 3/2;
cc(n) = if (n < 0, 0, binomial(-lam, n));
coefat(ys, L, A, B) = {
  my(M = #ys, G = matrix(2*M, 2*M));
  for (s = 1, M, for (u = 1, 2*M, my(t = L[u]);
    G[s, u] = if (t >= 0, cc(t) * ('x * ys[s])^t, 0);
    G[M + s, u] = sum(r = max(1, -t), B, cc(r) * cc(t + r) * 'eps^r * ('x * ys[s])^(t + r))));
  polcoef(polcoef(matdet(G), B, 'eps), A, 'x);
}
vand(Y) = prod(i = 1, #Y, prod(j = i + 1, #Y, Y[j] - Y[i]));
{
  \\ the number-field variable must have lower priority than x and eps (a first run with 'z gave all zeros)
  my(E0 = 'eps, tt = varlower("tt"), M = 4, ii = Mod(tt, tt^2 + 1));
  foreach([[[1, ii, -1, -ii], "square"], [[1, 2, 4, 7], "control (1,2,4,7)"]], cas,
    my(ys = cas[1], V2 = vand(ys)^2);
    for (p = 1, M,
      my(A = 2*M^2 - 2*M*p + p^2 - p, B = p^2 - p + M, surv = List(), dead = 0);
      forsubset([2*M - p + 3, 2*M - p], Sp, my(plus = apply(u -> u - 1, Vec(Sp)), Ep = vecsum(plus) - (2*M - p) * (2*M - p - 1) / 2);
        if (Ep <= 3, forsubset([p + 3, p], Sm, my(minus = vecsort(apply(u -> -u, Vec(Sm))), Em = -vecsum(minus) - p * (p + 1) / 2);
          if (Em <= 3,
            my(L = concat(minus, plus), c = coefat(ys, L, A + Ep, B + Em) / V2);
            if (c != 0, listput(surv, [Ep, Em, L]), dead++)))));
      write(OUT, cas[2], ", p = ", p, ": ", #surv, " surviving sets, ", dead, " with vanishing least coefficient; surviving (E+, E-): ",
            apply(r -> [r[1], r[2]], Vec(surv)));
      foreach(surv, r, if (r[1] + r[2] <= 1, write(OUT, "     ", r)))));
}
