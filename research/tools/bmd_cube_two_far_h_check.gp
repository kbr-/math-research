\\ Check of the reduction of c_(kappa*, nu*) to the hook determinant H (29 September 2026; cycle bmd-20260929-zr;
\\ lem:cube-two-far-leading-reduction). Claim: the s_1^(m(m-1)) coefficient T_kappa*(t) = sum_nu c_(kappa*, nu) s_nu(t)
\\ of a two-far window [-m, n-1+r] is a nonzero constant times
\\   H = det[ gamma_(b,e+1) - gamma_(b-1,e) - gamma_(b,n) gamma_(n-1,e) ], b = m..n-1, e = n..n+r-1,
\\ with gamma_(b,k) = (-1)^(n-1-b) (beta_k / beta_b) s_(k-n+1, 1^(n-1-b))(t), beta_k = binom(-3/2, k), gamma_(-1,.) = 0.
\\ Prints the Schur expansion of H (up to a common factor, normalized at nu*), its support against nu* dominance, and
\\ [s_nu*] H. The ratios can be compared with the c_(kappa*, nu) of bmd-20260929-zp/double-schur.txt.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(k) = binomial(-3/2, k);
run(n, r) = {
  my(T = vector(n, j, eval(Str("t", j))), m = n - r, D = r * (r + 3) + 2);
  my(cur = vector(D + 1, k, if (k == 1, 1, 0)));
  for (i = 1, n, my(nx = vector(D + 1)); for (k = 0, D, nx[k + 1] = sum(j = 0, k, T[i]^j * cur[k - j + 1])); cur = nx);
  my(h(k) = if (k < 0, 0, cur[k + 1]), sch(la) = my(l = #la); if (l == 0, 1, matdet(matrix(l, l, i, j, h(la[i] - i + j)))));
  my(hook(a, l) = sch(concat([a + 1], vector(l, i, 1))));
  my(ga(b, k) = if (b < 0, 0, if (k == b, 1, if (k < n, 0, (-1)^(n - 1 - b) * be(k) / be(b) * hook(k - n, n - 1 - b)))));
  my(H = matdet(matrix(r, r, i, j, my(b = m - 1 + i, e = n - 1 + j); ga(b, e + 1) - ga(b - 1, e) - ga(b, n) * ga(n - 1, e))));
  my(Dl = prod(i = 1, n, prod(j = i + 1, n, T[i] - T[j])), A = H * Dl, dl = vector(n, j, n - j), res = List(), sz = r * (r + 1));
  my(nus = vector(n, j, if (j <= r, 2 * (r + 1 - j), 0)), cst = 0);
  forpart(p = sz, my(nu = vector(n)); for (i = 1, #p, nu[i] = p[#p + 1 - i]);
    my(co = A); for (j = 1, n, co = polcoef(co, nu[j] + dl[j], T[j])); if (co != 0, listput(res, [nu, co])); if (nu == nus, cst = co), , [0, n]);
  my(dom(a, b) = my(pa = 0, pb = 0, ok = 1); for (i = 1, n, pa += a[i]; pb += b[i]; if (pa > pb, ok = 0)); ok);
  my(bad = select(z -> !dom(z[1], nus), Vec(res)));
  emit(Str("2x", n, " r=", r, ": [s_nu*]H = ", cst, ", support size ", #res, ", not dominated by nu*: ", #bad));
  if (cst != 0, emit(Str("    normalized expansion: ", apply(z -> [z[1], z[2] / cst], Vec(res)))));
}
main() = { foreach ([[3, 1], [3, 2], [4, 1], [4, 2], [4, 3], [5, 2], [5, 3], [6, 3]], P, run(P[1], P[2])); }
main();
