\\ Export of the reduced triple window's maximal minors for exact elimination (cycle bmd-20261009-cb, 9 October 2026).
\\ For m = 2..8, writes research/results/bmd-20261009-cb/triple-minors-mM.sing (a Singular ring Q[x, y] and the ideal
\\ of the ten 3 x 3 minors of U_3(x, y, 1) from lem:cube-level-window-gegenbauer-form) and triple-minors-mM.ms (msolve
\\ input with the Rabinowitsch generator). The rows have the nonzero factors Pi_m (a_i a_j)^m and the constant Gamma
\\ normalization of rho^(-m) removed, which does not change the minors' common zero set off the excluded loci;
\\ denominators are cleared by content.
default(parisizemax, 4 * 10^9);
lam = 3/2;
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
cc(n) = binomial(-lam, n);
{
  for (m = 2, 8, my(a = ['x, 'y, 1], d = m * (m - 1) / 2, N0 = d + m, U = matrix(3, 5), F = Str("research/results/bmd-20261009-cb/triple-minors-m", m, ".sing"));
    my(prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
    for (r = 1, 3, my([i, j, k] = prs[r], top = N0 + 4);
      my(e = vector(top + 1, n, sum(t = 0, n - 1, cc(t) * cc(n - 1 - t) * a[i]^t * a[j]^(n - 1 - t))));
      for (col = 1, 5, my(n = N0 + col - 1);
        U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rq(-m, n - l) * e[n - l + 1], 0))));
    my(gens = List());
    forsubset([5, 3], S, my(Sv = Vec(S), D = matdet(matrix(3, 3, r, t, U[r, Sv[t]]))); if (D != 0, listput(gens, D / content(D))));
    write(F, "ring r = 0, (x, y), dp;");
    write(F, "ideal I = ");
    for (g = 1, #gens, write(F, "  ", gens[g], if (g < #gens, ",", ";")));
    write(F, "poly Bad = x * y * (x - 1) * (y - 1) * (x - y);");
    \\ msolve input with the Rabinowitsch variable t: the system is inconsistent iff no common zero off Bad = 0
    my(G = Str("research/results/bmd-20261009-cb/triple-minors-m", m, ".ms"));
    write(G, "x,y,t"); write(G, "0");
    for (g = 1, #gens, write(G, gens[g], ","));
    write(G, "t*x*y*(x-1)*(y-1)*(x-y)-1"));
}
