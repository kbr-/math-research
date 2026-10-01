\\ Far route review tests (3 October 2026; cycle bmd-20261003-x).
\\ (1) Stieltjes order test in u: does W(u) = R_(n,k)(u^2) satisfy a Fuchsian equation of order r <= 3 whose only
\\     singular points are u = 0, 1, -1, infinity?  Form: sum_{j=0}^{r} q_j(u) (u(u^2-1))^(r-j) W^(r-j) = 0 with q_0 = 1
\\     ... written as sum_j A_j W^(j), A_r = (u(u^2-1))^r * c, A_(r-j) = (u(u^2-1))^(r-j) q_j, deg q_j <= 2j.
\\     A nonzero solution with A_r != 0 at a root forces multiplicity < r there: r = 3 would exclude triple roots.
\\     Reports the kernel dimension of the linear system in (c, q_1..q_r) for r = 2, 3.  A trivial kernel falsifies
\\     the lead in this form.  Positive control: a Gegenbauer polynomial in u (Fuchsian order 2, singular at +-1, inf).
\\ (2) Unit-circle test for the Klein tau form: number of roots of R_(n,k) in the real interval [0,1] (w in [0,1] iff
\\     the Klein-tau variable t lies on the unit circle, where the trigonometric Calogero-Moser flow is collision-free).
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
farR(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); p));
  wr([[0, 0, P3], [1/2, 0, apply(p -> p * 'w^(-(n - 1)), P4)]]);
}
fuchs(W, r) = {
  my(s = 'u * ('u^2 - 1), D = vector(r + 1), nv = 1 + sum(j = 1, r, 2 * j + 1), cols = List());
  D[1] = W; for (j = 2, r + 1, D[j] = deriv(D[j - 1], 'u));
  listput(cols, s^r * D[r + 1]);
  for (j = 1, r, for (t = 0, 2 * j, listput(cols, s^(r - j) * 'u^t * D[r - j + 1])));
  my(dm = vecmax(apply(poldegree, Vec(cols))), M = matrix(dm + 1, #cols, a, b, polcoef(cols[b], a - 1, 'u)), K = matker(M));
  my(lead = 0); for (c = 1, #K, if (K[1, c] != 0, lead = 1));
  [#K, lead];
}
main() = {
  my(g = pollegendre(6, 'u));
  emit(Str("control Legendre P6(u): order 2 kernel ", fuchs(g, 2), ", order 3 kernel ", fuchs(g, 3)));
  foreach([[2, 3], [3, 3], [2, 4], [2, 5]], v,
    my(R = farR(v[1], v[2]), W = subst(R, 'w, 'u^2));
    emit(Str("(n,k)=", v, ": deg R ", poldegree(R), "; Fuchs u order 2 [kernel dim, leading coefficient free] ", fuchs(W, 2),
      ", order 3 ", fuchs(W, 3), "; roots of R in [0,1]: ", #polrootsreal(R, [0, 1]), " of ", poldegree(R),
      " (real roots ", #polrootsreal(R), ")")));
}
main();
