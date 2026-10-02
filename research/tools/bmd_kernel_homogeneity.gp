\\ Weighted homogeneity of the kernel determinants (cycle bmd-20261009-r, 9 October 2026).
\\ Tested identity: D_T(u, lambda y) = lambda^(delta_T) D_T(lambda u, y), delta_T - delta_{T0} = Sum T - Sum T0,
\\ for the coefficient-space determinant D_T = det[standard negative columns | K_u(z^i), i in T] (as in
\\ bmd_monomial_minimality.gp). Checked exactly over Q at random rational roots and lambda, M = 3, 4, all p,
\\ all k-sets T of [0, 4], u-orders 0..B + 4 (all, zeros included); checks the absolute delta_T and reports vacuous sets.
OUT = "research/results/bmd-20261009-r/kernel-homogeneity.txt";
Zv = varhigher("zz");
c(n) = binomial(-3/2, n);
T1(F) = { my(d = poldegree(F, Zv)); sum(i = 0, d, polcoef(F, i, Zv) * c(i + 1) / c(i) * Zv^(i + 1)) };
Dser(Y, p, T, NU) = {
  my(M = #Y, P = prod(s = 1, M, Zv - Y[s]));
  my(ncol = vector(p, n, my(r = lift(Mod(sum(m = 0, NU - n, c(m) * c(n + m) * 'u^(n + m) * Zv^m), P))); vector(M, s, polcoef(r, s - 1, Zv))));
  my(kc = vector(#T, a, my(F = P * Zv^T[a], col = vector(M));
    for (m = 1, NU, F = T1(F); my(r = lift(Mod(F, P))); for (s = 0, M - 1, col[s + 1] += c(m) * polcoef(r, s, Zv) * 'u^m)); col));
  matdet(matrix(M, M, r, j, if(j <= p, ncol[j][r], kc[j - p][r])))
};
{
  setrand(7);
  foreach([3, 4], M,
    my(Y = vector(M, s, random(97) / (random(13) + 1) + s), lam = 5 / 3);
    for (p = 1, M - 1, my(k = M - p, B = p * (p + 1) / 2 + p * (p - 1) / 2 + k, NU = B + 4, d0 = 0, worst = 0, cnt = 0, vac = 0);
      forsubset([5, k], S, my(T = Vec(S) - vector(k, a, 1));
        my(A = Dser(lam * Y, p, T, NU), Bs = Dser(Y, p, T, NU), co = vector(NU + 1, n, polcoef(A, n - 1, 'u)), cb = vector(NU + 1, n, polcoef(Bs, n - 1, 'u) * lam^(n - 1)));
        \\ exact check at every order n (zeros included) against the formula delta_T = sum (M+i) - sum N - binom(M,2)
        my(dT = vecsum(apply(i -> M + i, T)) - p * (p + 1) / 2 - M * (M - 1) / 2, nz = 0);
        for (n = 1, NU + 1, if(co[n] != lam^dT * cb[n], worst = 1); if(cb[n] != 0, nz++));
        if(nz == 0, vac++);
        cnt++);
      write(OUT, "M=", M, " p=", p, ": ", cnt, " sets T, identity with delta_T = sum(M+i) - sum N - C(M,2) holds at every order: ", worst == 0, ", sets with all coefficients zero: ", vac)));
}
