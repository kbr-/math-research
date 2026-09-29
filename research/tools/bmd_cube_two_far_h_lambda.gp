\\ [s_nu*] H as a rational function of a formal lambda (29 September 2026; cycle bmd-20260929-zs;
\\ lem:cube-two-far-leading-reduction). H = det[gamma_(b,e+1) - gamma_(b-1,e) - gamma_(b,n) gamma_(n-1,e)],
\\ b = m..n-1, e = n..n+r-1, gamma_(b,k) = (-1)^(n-1-b) (beta_k / beta_b) s_(k-n+1, 1^(n-1-b))(t), beta_k = binom(-L, k).
\\ The coefficient of s_nu*, nu* = (2r, ..., 2), is read as the coefficient of t^(nu*+delta) in H Delta(t).
\\ Prints its factorization over Q[L], to look for a product formula nonvanishing for L not an integer.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
be(k) = binomial(-L, k);
run(n, r) = {
  my(T = vector(n, j, eval(Str("t", j))), m = n - r, D = r * (r + 3) + 2);
  my(cur = vector(D + 1, k, if (k == 1, 1, 0)));
  for (i = 1, n, my(nx = vector(D + 1)); for (k = 0, D, nx[k + 1] = sum(j = 0, k, T[i]^j * cur[k - j + 1])); cur = nx);
  my(h(k) = if (k < 0, 0, cur[k + 1]), sch(la) = my(l = #la); if (l == 0, 1, matdet(matrix(l, l, i, j, h(la[i] - i + j)))));
  my(hook(a, l) = sch(concat([a + 1], vector(l, i, 1))));
  my(ga(b, k) = if (b < 0, 0, if (k == b, 1, if (k < n, 0, (-1)^(n - 1 - b) * be(k) / be(b) * hook(k - n, n - 1 - b)))));
  my(H = matdet(matrix(r, r, i, j, my(b = m - 1 + i, e = n - 1 + j); ga(b, e + 1) - ga(b - 1, e) - ga(b, n) * ga(n - 1, e))));
  my(A = H * prod(i = 1, n, prod(j = i + 1, n, T[i] - T[j])), dl = vector(n, j, n - j), nus = vector(n, j, if (j <= r, 2 * (r + 1 - j), 0)));
  my(co = A); for (j = 1, n, co = polcoef(co, nus[j] + dl[j], T[j]));
  co = factor(co);
  emit(Str("n=", n, " r=", r, ": [s_nu*]H = ", co));
}
main() = { foreach ([[2, 1], [3, 1], [3, 2], [4, 2], [5, 2], [6, 2], [4, 3], [5, 3]], P, run(P[1], P[2])); }
main();
