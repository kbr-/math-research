\\ Review falsification test of conj:cube-two-far-hook-coefficient (29 September 2026; cycle bmd-20260929-zt).
\\ Same computation as bmd_cube_two_far_h_lambda.gp ([s_nu*] H with beta_k = binom(-L, k), L formal), at new sizes
\\ r = 4 (n = 5), (n, r) = (6, 3), (7, 2), and the control (3, 2); prints the rational content C and the factorization of
\\ the primitive part. Prediction: primitive part = (L-1)^r prod over the r x r square of (L + n - 1 + content).
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
  my(ct = content(co), pr = (L - 1)^r * prod(i = 1, r, prod(j = 1, r, L + n - 1 + j - i)));
  emit(Str("n=", n, " r=", r, ": content ", ct, "; primitive part / prediction = ", co / (ct * pr), "; factors ", factor(co / ct)));
}
main() = { foreach ([[3, 2], [7, 2], [6, 3], [5, 4]], P, run(P[1], P[2])); }
main();
