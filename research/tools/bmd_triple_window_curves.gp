\\ Triple window along curves, from the closed form (cycle bmd-20261009-ca, 9 October 2026).
\\ Tested statement (conj:cube-triple-window-full-rank): for distinct c1, c2 not in {0, 1}, U_3(c1, c2, 1) has rank 3.
\\ By lem:cube-level-window-gegenbauer-form, the (ij) row of U_3 is, up to the nonzero factor Pi_m (a_i a_j)^m, the
\\ sequence (1 + a_k E^-1)^m h^(ij) at indices n = M - 2m, M = d+3m..d+3m+4, h^(ij)_n = rho^(-m)_n e^(ij)_n. With
\\ a = (c1, c2, 1), c2 fixed rational and c1 = 'x symbolic, the gcd of the ten 3 x 3 minors (stripped of x, x - 1,
\\ x - c2 and the row factors) must have no root. m = 2..8, c2 in {-5/3, 4, 1/3}.
OUT = "research/results/bmd-20261009-ca/triple-window-curves.txt";
default(parisizemax, 4 * 10^9);
lam = 3/2;
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
cc(n) = binomial(-lam, n);
strip(f, c2) = { my(g = f); if (g == 0, return(0)); foreach(['x, 'x - 1, 'x - c2], u, while (polresultant(g, u) == 0 && poldegree(g) > 0, g = g / u)); g / content(g); }
{
  foreach([-5/3, 4, 1/3], c2,
    for (m = 2, 8, my(a = ['x, c2, 1], d = m * (m - 1) / 2, N0 = d + m, U = matrix(3, 5));
      my(prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
      for (r = 1, 3, my([i, j, k] = prs[r], top = N0 + 4);
        my(e = vector(top + 1, n, sum(t = 0, n - 1, cc(t) * cc(n - 1 - t) * a[i]^t * a[j]^(n - 1 - t))));
        my(hseq = vector(top + 1, n, rq(-m, n - 1) * e[n]));
        for (col = 1, 5, my(n = N0 + col - 1);
          U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, hseq[n - l + 1], 0))));
      my(g = 0);
      forsubset([5, 3], S, my(Sv = Vec(S), D = matdet(matrix(3, 3, r, t, U[r, Sv[t]]))); g = gcd(g, D));
      my(gs = strip(g, c2));
      write(OUT, "c2 = ", c2, ", m = ", m, ": gcd of the maximal minors of U_3 after stripping x, x-1, x-c2 has degree ", poldegree(gs),
            if (poldegree(gs) > 0, Str(" = ", factor(gs)), " (rank 3 for every c1 off {0, 1, c2})"))));
}
