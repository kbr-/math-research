\\ The reduced far space in u = sqrt(w) (2 October 2026; cycle bmd-20261002-y).
\\ Y(n,k) = u^(2n-3) X(n,k)|_(w = u^2) = span{ u^(2n-3) P3(u^2), u^0 * P4(u^2) } (P4 carries w^(1/2-(n-1)) = u^(3-2n)).
\\ Checks: (1) Y is a space of polynomials in u and its Wronskian in u, off u = 0 and u = +-1, is R_(n,k)(u^2) (far points pulled back);
\\ (2) Bochner test: is Y invariant under some A(u) d^2 + B(u) d with deg A <= 2, deg B <= 1, (A, B) != 0 (every classical family,
\\ Gegenbauer included, in any affine variable)?  Homogeneous system; random control of the same shape.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
strip(N, v) = { while (subst(N, v, 0) == 0, N = N / v); while (subst(N, v, 1) == 0, N = N / (v - 1)); while (subst(N, v, -1) == 0, N = N / (v + 1)); N / pollead(N); }
wr(cls) = {
  my(d = sum(i = 1, #cls, #cls[i][3]), M = matrix(d, d), row = 0);
  foreach(cls, c, my(a = c[1], b = c[2]);
    foreach (c[3], f, row++; my(g = f);
      for (m = 1, d, M[row, m] = g; g = deriv(g, 'w) + (a / 'w + b / ('w - 1)) * g)));
  strip(numerator(matdet(M)), 'w);
}
uwr(S) = { my(d = #S, M = matrix(d, d)); for (i = 1, d, my(g = S[i]); for (j = 1, d, M[i, j] = g; g = deriv(g, 'u))); strip(matdet(M), 'u); }
bochner(S) = {
  my(d = #S, D = vecmax(apply(poldegree, S)), nu = 5 + d^2, rows = List());
  for (i = 1, d, my(p = S[i], p1 = deriv(p, 'u), p2 = deriv(p1, 'u));
    my(terms = [p2, 'u * p2, 'u^2 * p2, p1, 'u * p1]);
    for (m = 0, D + 1, my(r = vector(nu));
      for (t = 1, 5, r[t] = polcoef(terms[t], m, 'u));
      for (j = 1, d, r[5 + (i - 1) * d + j] = -polcoef(S[j], m, 'u)); listput(rows, r)));
  my(M = matrix(#rows, nu, a, b, rows[a][b]), K = matker(M), ok = 0);
  for (c = 1, #K, if (K[1..5, c] != 0, ok = 1));
  if (ok, "invariant", "not invariant");
}
ctrl(S) = { my(v = apply(p -> poldegree(p), S)); setrand(11); bochner(vector(#S, i, sum(m = 0, v[i], (random(41) - 20) * 'u^m))); }
run(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); p));
  my(Y = concat(apply(p -> 'u^(2 * n - 3) * subst(p, 'w, 'u^2), P3), apply(p -> subst(p, 'w, 'u^2), P4)));
  my(g = fold(gcd, Y), Ys = apply(p -> p / g, Y));
  my(R = wr([[0, 0, P3], [1/2, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]), Ru = strip(subst(R, 'w, 'u^2), 'u), W = uwr(Ys));
  emit(Str("(n,k)=", [n, k], ": dim Y ", #Y, ", common factor ", factor(g), "; Wronskian in u off 0, +-1 equals R(u^2): ", W == Ru,
    "; Bochner test: ", bochner(Ys), " (random control: ", ctrl(Ys), ")"));
}
foreach([[2, 3], [2, 4], [3, 3], [2, 5], [3, 4], [4, 3]], v, run(v[1], v[2]));
