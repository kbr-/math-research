\\ Test of a Wronskian identity behind conj:cube-flow-order-family-value (cycle bmd-20261009-bd, 9 October 2026).
\\ By lem:cube-cross-leading-coefficient, for family p (k = M - p, E- = 0) the least coefficient of the set with
\\ nonnegative part L+ is (nonzero constant) Vand^2 D_L, and D_L is the minor on rows L+ of the coefficient matrix of
\\ the space V_p spanned by z^j H(z) (0 <= j < M) and G_m(z) = (1/z) int_0^z w^m H(w) dw (p-1 <= m <= M-2),
\\ H = 1 / prod(1 - y_q z) = sum h_n z^n.  Candidate identity: the Wronskian W_p(z) of these M + k functions equals
\\ z^e times a unit times Hank_k(y / (1 - z y)), the flowed Hankel determinant; then the ramification weight of V_p
\\ at 0 (the least E+ with D_L != 0) equals the flow order j_p. The script computes, at rational clusters,
\\ ord_z W_p and ord_z Hank_k(y/(1 - z y)) and compares them. (A first version also tested whether the ratio is
\\ const * prod(1 - y z)^(-c); at the generic quartic the fitted c differed between p, so that form is false.)
OUT = "research/results/bmd-20261009-bd/wronskian-flow.txt";
N = 40;
hser(P) = 1 / Polrev(Vec(P), 'z) + O('z^N);
\\ flowed Hankel determinant Hank_k(y/(1 - z y)) as a series, from the polynomial P (variable z for roots)
flowhank(P, M, k) = {
  my(Q = subst(P, 'z, 'x / (1 + 'z * 'x)) * (1 + 'z * 'x)^M + O('z^N));
  Q = Q / polcoeff(Q, M, 'x);
  my(a = vector(M, j, polcoeff(Q, M - j, 'x)), pw = vector(2*k + 1));
  for (j = 1, 2*k, my(s = if (j <= M, j * a[j], 0)); for (i = 1, min(j - 1, M), s += a[i] * pw[j - i]); pw[j] = -s);
  matdet(matrix(k + 1, k + 1, i, j, if (i + j == 2, M, pw[i + j - 2])));
}
wronsk(P, M, p) = {
  my(k = M - p, H = hser(P), F = List());
  for (j = 0, M - 1, listput(F, 'z^j * H));
  for (m = p - 1, M - 2, my(hv = Vec(H)); listput(F, sum(n = 0, N - 1 - m, hv[n + 1] * 'z^(n + m) / (n + m + 1)) + O('z^(N - 1))));
  my(n = #F, W = matrix(n, n, i, j, my(f = F[j]); for (r = 1, i - 1, f = deriv(f, 'z)); f));
  matdet(W);
}
{
  my(cls = [[4, 'z^4 - 2*'z^3 + 5*'z - 3], [4, 'z^4 - 1], [4, 'z^4 + 'z + 1], [5, 'z^5 + 'z + 1], [5, 'z^5 - 'z^2 + 2*'z + 3], [5, 'z^5 - 3*'z^4 + 'z^2 - 7]]);
  foreach(cls, cl,
    my([M, P] = cl, ys = polroots(P), S = sum(q = 1, M, 0) );
    \\ sum_q y_q/(1 - y_q z) = -(d/dz) log prod(1 - y z), exact from Polrev
    my(Lg = -deriv(Polrev(Vec(P), 'z), 'z) / Polrev(Vec(P), 'z) + O('z^(N - 12)));
    for (p = 1, M - 1,
      my(k = M - p, W = wronsk(P, M, p), Fh = flowhank(P, M, k));
      my(eW = valuation(W, 'z), eF = valuation(Fh, 'z));
      write(OUT, "M = ", M, ", ", P, ", p = ", p, ", k = ", k, ": ord W = ", eW, ", flow order = ", eF, ", equal: ", eW == eF)));
}
