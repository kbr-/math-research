\\ Support rule for the Schur expansion of two-far windows at s_2 = 0 (29 September 2026; cycle bmd-20260929-zm;
\\ conj:cube-two-far-schur-support). Version of bmd_cube_two_far_schur_support.gp that checks, over the complete
\\ support with |nu| <= H = w(nu*)/2 + 3, the rule: a_nu != 0 implies |nu| >= |nu*| and nu is dominated by
\\ nu* + (|nu| - |nu*|) (boxes added to the first row); and a_nu* != 0. Prints only violations and a summary.
\\ At s_2 = 0, P_E = sum_{K1,K2} B(K1,K2) Y_K1 Y_K2 with Y_K = +-prod_{k in K} beta_k Delta(t) s_mu(K)(t) and
\\ B(K1,K2) = +- s^(sum K1 + sum K2 - sum E) b(K1,K2), b constant. Hence P_E = s^c Delta(t)^2 sum_nu a_nu s^|nu| s_nu(t),
\\ a_nu = sum b(K1,K2) prod beta_K1 prod beta_K2 c^nu_{mu1,mu2} (Littlewood-Richardson). At weights val s = 1,
\\ val t_j = j the monomial s^|nu| s_nu has least weight |nu| + sum_j j nu_j = sum_j (j+1) nu_j.
\\ Tested prediction: among nu with a_nu != 0, the least weight is attained only at nu* = (2r, 2r-2, ..., 2) on the
\\ window [-(n-r), n-1+r]. (This version prints only the rule check below, not the support.)
\\ LR coefficients are read off as coefficients of t^(nu+delta) in a_(mu1+delta)(t) s_mu2(t), with s_mu2 by
\\ Jacobi-Trudi in complete symmetric polynomials; the sum over (K1, K2) is complete for |nu| <= H.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(k) = if (k < 0, 0, binomial(-3/2, k));
Bf(E, K1, K2) = {
  my(L = #E, A = matrix(L, L));
  for (a = 1, #K1, for (c = 1, L, A[a, c] = (K1[a] == E[c])));
  for (a = 1, #K2, for (c = 1, L, A[#K1 + a, c] = be(K2[a] - E[c])));
  matdet(A);
}
wt(nu) = sum(j = 1, #nu, (j + 1) * nu[j]);
run(n, r) = {
  my(T = vector(n, i, eval(Str("t", i))), m = n - r, E = [-m .. n - 1 + r]);
  my(nus = vector(r, i, 2 * (r + 1 - i)), ws = wt(nus), H = ws \ 2 + 3);
  \\ complete symmetric polynomials h_k(t_1..t_n), k <= H + n
  my(hv = vector(H + n + 1), cur = vector(H + n + 1, k, if (k == 1, 1, 0)));
  for (i = 1, n, my(nx = vector(H + n + 1)); for (k = 0, H + n, nx[k + 1] = sum(j = 0, k, T[i]^j * cur[k - j + 1])); cur = nx);
  hv = cur;
  my(h(k) = if (k < 0, 0, hv[k + 1]));
  my(parts = List());
  for (sz = 0, H, forpart(p = sz, my(mu = vector(n)); for (i = 1, #p, mu[i] = p[#p + 1 - i]); listput(parts, mu), , [0, n]));
  my(schur(mu) = matdet(matrix(n, n, i, j, h(mu[i] - i + j))), alt(al) = matdet(matrix(n, n, i, j, T[i]^al[j])));
  my(delta = vector(n, j, n - j), Kof(mu) = vecsort(vector(n, j, mu[j] + n - j)), pb(K) = prod(i = 1, #K, be(K[i])));
  my(acc = Map());
  for (i1 = 1, #parts, my(mu1 = parts[i1], K1 = Kof(mu1), A1 = 0);
    for (i2 = 1, #parts, my(mu2 = parts[i2]); if (vecsum(mu1) + vecsum(mu2) > H, next);
      my(K2 = Kof(mu2), b = Bf(E, K1, K2)); if (b == 0, next);
      if (A1 == 0, A1 = alt(mu1 + delta));
      my(pr = A1 * schur(mu2), c = b * pb(K1) * pb(K2), tot = vecsum(mu1) + vecsum(mu2));
      forpart(q = tot, my(nu = vector(n)); for (i = 1, #q, nu[i] = q[#q + 1 - i]);
        my(ex = nu + delta, co = pr); for (i = 1, n, co = polcoef(co, ex[i], T[i]));
        if (co != 0, my(old = 0); if (mapisdefined(acc, nu), old = mapget(acc, nu)); mapput(acc, nu, old + c * co)), , [0, n])));
  my(M = Mat(acc), cnt = 0, viol = List(), nst = 0, sz = vecsum(nus));
  my(dom(a, b) = my(pa = 0, pb = 0, ok = 1); for (i = 1, n, pa += a[i]; pb += b[i]; if (pa > pb, ok = 0)); ok);
  for (i = 1, matsize(M)[1], my(nu = M[i, 1]); if (M[i, 2] != 0, cnt++;
    my(k = vecsum(nu) - sz, top = vector(n, j, if (j <= r, nus[j], 0)));
    if (k < 0, listput(viol, nu), top[1] += k; if (!dom(nu, top), listput(viol, nu)));
    if (k == 0 && nu == top, nst = M[i, 2])));
  emit(Str("2x", n, " r=", r, ": nu* = ", nus, ", |nu| <= ", H, ": support size ", cnt, ", a_nu* = ", nst, ", violations ", Vec(viol)));
}
main() = { foreach ([[3, 0], [3, 1], [3, 2], [4, 0], [4, 1], [4, 2], [4, 3], [5, 1], [5, 2], [5, 3]], P, run(P[1], P[2])); }
main();
