\\ Closed form of the Euler-operator images in the pure reduction (5 October 2026; cycle bmd-20261005-k).
\\ Lemma tested: for phi(x) = prod_(e in E) (x - e) of degree q and any exponent s,
\\   (1-w)^(q-1/2) phi(theta)[(1-w)^(1/2) w^s] = sum_(r=0..q) Delta^r phi(s) * binom(1/2,r) (-1)^r * w^(s+r) (1-w)^(q-r),
\\ with Delta the forward difference.  Compared with the iterated theta-steps of research/tools/bmd_cube_far_pure_reduction.gp
\\ for P3 (s = j) and P4 (s = 1/2 - (n-1) + j, with the factor w^s removed as in that tool).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
closed(E, s) = {
  my(q = #E, phi = x -> prod(i = 1, q, x - E[i]));
  sum(r = 0, q, sum(i = 0, r, (-1)^(r - i) * binomial(r, i) * phi(s + i)) * binomial(1/2, r) * (-1)^r * 'w^r * (1 - 'w)^(q - r));
}
{
foreach([[2, 3], [3, 3], [2, 4], [4, 3]], v,
  my(n = v[1], k = v[2], C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2);
  my(E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E, ok = 1);
  for (j = 0, k - 2, my(p = 'w^j, al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); if (p != 'w^j * closed(E, j), ok = 0));
  for (j = 0, n - 1, my(p = 'w^j, al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); if (p != 'w^j * closed(E, 1/2 - (n - 1) + j), ok = 0));
  emit(Str("(n,k) = ", [n, k], ", q = ", q, ": closed form equals the iterated theta-steps for all P3 and P4 generators: ", ok == 1)));
}
quit;
