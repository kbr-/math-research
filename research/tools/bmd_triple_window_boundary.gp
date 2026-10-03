\\ Boundary behaviour of the reduced triple window (cycle bmd-20261009-cd, 9 October 2026).
\\ Question (Hilbert-Mumford/properness bridge of the window cores review): as c1 -> 0, c1 -> 1 and c1 -> c2 (c2 = y
\\ symbolic, c1 = edge + eps), do the ten maximal minors of U_3 (closed form of lem:cube-level-window-gegenbauer-form)
\\ keep a common nonvanishing leading term? Reports, per edge and m = 2..5, the least eps-valuation over the minors and
\\ the gcd in Q[y] of the minors' coefficients at that valuation, stripped of y, y-1 (a constant gcd means U_3 has rank 3
\\ for all small eps at every admissible y).
OUT = "research/results/bmd-20261009-cd/triple-window-boundary.txt";
default(parisizemax, 4 * 10^9);
lam = 3/2;
rq(j, k) = prod(i = 1, k, i / (i + lam - j));
cc(n) = binomial(-lam, n);
stripy(f) = { my(g = f); if (g == 0, return(0)); foreach(['y, 'y - 1], u, while (subst(g, 'y, polcoef(-u, 0, 'y)) == 0 && poldegree(g, 'y) > 0, g = g / u)); g / content(g); }
{
  foreach([["c1 -> 0", 'e], ["c1 -> 1", 1 + 'e], ["c1 -> c2", 'y + 'e]], E,
    for (m = 2, 5, my(a = [E[2], 'y, 1], d = m * (m - 1) / 2, N0 = d + m, U = matrix(3, 5));
      my(prs = [[1, 2, 3], [1, 3, 2], [2, 3, 1]]);
      for (r = 1, 3, my([i, j, k] = prs[r], top = N0 + 4);
        my(ev = vector(top + 1, n, sum(t = 0, n - 1, cc(t) * cc(n - 1 - t) * a[i]^t * a[j]^(n - 1 - t))));
        for (col = 1, 5, my(n = N0 + col - 1);
          U[r, col] = sum(l = 0, m, binomial(m, l) * a[k]^l * if (n - l >= 0, rq(-m, n - l) * ev[n - l + 1], 0))));
      my(Ds = List());
      forsubset([5, 3], S, my(Sv = Vec(S), D = matdet(matrix(3, 3, r, t, U[r, Sv[t]]))); if (D != 0, listput(Ds, D)));
      my(v = vecmin(apply(D -> valuation(D, 'e), Vec(Ds))), g = 0);
      foreach(Ds, D, if (valuation(D, 'e) == v, g = gcd(g, polcoef(D, v, 'e))));
      my(gs = stripy(g));
      write(OUT, E[1], ", m = ", m, ": least eps-valuation of the minors ", v, "; gcd of leading coefficients in y (stripped) has degree ", poldegree(gs, 'y),
            if (poldegree(gs, 'y) > 0, Str(" = ", factor(gs)), ""))));
}
