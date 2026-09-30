\\ Two-run Rodrigues formula for the class P3 of the reduced far space (2 October 2026; cycle bmd-20261002-w).
\\ Claim (lem:cube-far-p3-rodrigues): with beta0 = 1/2 - (n-1), K = (k-1)n, C = binom(n,2), P = binom(k-1,2), q = C+P+2+K,
\\ c2 = P + 3 - beta0 - K and B3 = -P - 3/2,
\\   P3 = (1-w)^(q-1/2) w^(P+2) w^(1-c2) d^K w^(c2+K-1-P-2) d^C [ w^(P+2+C) (1-w)^B3 Pol_<(k-1) ]   (as spans).
\\ Functions g w^a (1-w)^b are carried as triples [g, a, b] with g a polynomial.  Test: the span of the formula equals the span of
\\ P3 computed by the pure reduction's thetastep (rank of the stacked coefficient matrix equals each rank, k - 1).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
dtrip(t) = { my(g = t[1], a = t[2], b = t[3]); [deriv(g, 'w) * 'w * (1 - 'w) + a * g * (1 - 'w) - b * g * 'w, a - 1, b - 1]; }
dpow(t, m) = { for (i = 1, m, t = dtrip(t)); t; }
\\ normalize a triple to a polynomial when its exponents are non-negative integers
topoly(t) = {
  if (type(t[2]) != "t_INT" || type(t[3]) != "t_INT" || t[2] < 0 || t[3] < 0, error("not a polynomial: exponents ", t[2], ", ", t[3]));
  t[1] * 'w^t[2] * (1 - 'w)^t[3];
}
run(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, K = (k - 1) * n, b0 = 1/2 - (n - 1), q = C + P + 2 + K, c2 = P + 3 - b0 - K, B3 = -P - 3/2);
  my(E = concat(vector(C + P + 2, t, t - 1 - C), vector(K, t, b0 + t - 1)));
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, #E, p = thetastep(p, al, 0, E[i]); al--); p));
  my(F = vector(k - 1, j, my(t = ['w^(j - 1), P + 2 + C, B3]);
    t = dpow(t, C); t[2] += c2 + K - 1 - P - 2; t = dpow(t, K); t[2] += (1 - c2) + (P + 2); t[3] += q - 1/2; topoly(t)));
  my(D = max(vecmax(apply(poldegree, P3)), vecmax(apply(poldegree, F))));
  my(M3 = matrix(k - 1, D + 1, i, m, polcoef(P3[i], m - 1, 'w)), MF = matrix(k - 1, D + 1, i, m, polcoef(F[i], m - 1, 'w)));
  my(r3 = matrank(M3), rF = matrank(MF), r = matrank(concat(M3~, MF~)~));
  emit(Str("(n,k)=", [n, k], ": rank P3 ", r3, ", rank formula ", rF, ", rank of both ", r, (if (r == r3 && r == rF, " (equal spans)", " (MISMATCH)"))));
}
foreach([[1, 3], [2, 3], [3, 3], [2, 4], [4, 3], [3, 4], [2, 5]], v, run(v[1], v[2]));
