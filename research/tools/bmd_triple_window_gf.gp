\\ Triple-window functionals as generating functions (9 October 2026; cycle bmd-20261009-c).
\\ Question: for the reduced triple window U_3 of lem:cube-level-window-reduction (lambda = 3/2, h = 3), the values
\\ f_M(pair_ij) = sum_(i <= hm) p_i rho_(M-i) e_(M-i), rho_k = Gamma(k+1)/Gamma(k+lambda-m+1), are the coefficients of
\\ G_ij(T) = prod_l (1 + a_l T)^m * sum_k rho_k e_k T^k, e = coefficients of ((1+a_i T)(1+a_j T))^(-lambda).
\\ Which kind of function is G_ij: rational (constant-coefficient recurrence), or holonomic of what order?
\\ Tests: Pade/recurrence detection on 80 coefficients at a rational point, for m = 2, 3, 4.
OUT = "research/results/bmd-20261009-c/triple-window-gf.txt";
lam = 3/2;
\\ rho_k up to the common nonzero factor 1/Gamma(lam - m + 1): rho_k / rho_(k-1) = k / (k + lam - m)
rhoq(k, m) = prod(i = 1, k, i / (i + lam - m));
cc(n) = binomial(-lam, n);
seqG(a, i, j, m, L) = {
  my(e = vector(L, k, sum(r = 0, k - 1, cc(r) * cc(k - 1 - r) * a[i]^r * a[j]^(k - 1 - r))), s = sum(k = 0, L - 1, rhoq(k, m) * e[k + 1] * 'T^k) + O('T^L));
  Vec(prod(l = 1, #a, (1 + a[l]*'T)^m) * s);
};
\\ minimal constant-coefficient recurrence order via Berlekamp-Massey style: rank test on Hankel matrices
crec(v) = { my(n = #v \ 2 - 1); for (d = 1, n, my(H = matrix(n - d + 1, d + 1, r, c, v[r + c - 1])); if(matrank(H) <= d, return(d))); -1 };
\\ holonomic order test: find minimal (r, deg) such that sum_{t<=r} P_t(n) v[n+t] = 0 with deg P_t <= dd
hol(v, r, dd) = { my(N = #v - r, cols = (r + 1) * (dd + 1), A = matrix(N - 1, cols, n, c, my(t = (c - 1) \ (dd + 1), d = (c - 1) % (dd + 1)); n^d * v[n + t]));
  cols - matrank(A) };
{
  my(a = [2/7, -5/3, 1], L = 90);
  for (m = 2, 4, my(d = m * (m - 1) / 2);
    for (pr = 1, 3, my(ij = [[1,2],[1,3],[2,3]][pr], v = seqG(a, ij[1], ij[2], m, L));
      my(cr = crec(v[d + 1 .. L]), h1 = hol(v[d + 1 .. L], 1, 3), h2 = hol(v[d + 1 .. L], 2, 3));
      write(OUT, "m=", m, " pair ", ij, ": constant-coefficient recurrence order ", cr, "; kernel dim for (order 1, deg 3) ", h1,
        ", (order 2, deg 3) ", h2, "; first terms from d: ", v[d + 1 .. d + 4])));
}
