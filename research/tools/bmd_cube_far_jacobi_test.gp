\\ Jacobi test for the reduced far spaces (2 October 2026; cycle bmd-20261002-u).
\\ Hypothesis tested: each class of X(n,k) = P3 + w^(1/2-(n-1)) P4 (pure reduction, lem:cube-far-pure-reduction) is spanned by
\\ Jacobi polynomials of one family, so its polynomial part is invariant under some hypergeometric operator
\\ L = w(1-w) d^2 + (alpha + beta w) d (Jacobi families are its eigenfunctions, in the variable w or 1 - w alike).
\\ Invariance, L S subset S, is a linear system in (alpha, beta, c_ij): solvable iff the augmented matrix has a kernel vector with
\\ last coordinate nonzero.  A one-dimensional class is tested too, but is nearly always invariant (few conditions).
\\ Calibration: at n = 1 the far polynomial is Gegenbauer (binary face), but only after the operator D^2.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
thetastep(p, alpha, beta, e) = { (1 - 'w) * ('w * deriv(p, 'w) + (beta - e) * p) - alpha * 'w * p; }
inv(S) = {
  my(d = #S, D = vecmax(apply(poldegree, S)), nu = 2 + d^2, rows = List());
  \\ unknown vector: (alpha, beta, c_11..c_dd, 1) with the constant column last
  for (i = 1, d, my(p = S[i], dp = deriv(p, 'w), base = 'w * (1 - 'w) * deriv(dp, 'w));
    for (m = 0, D + 1, my(r = vector(nu + 1));
      r[1] = polcoef(dp, m, 'w); r[2] = polcoef('w * dp, m, 'w);
      for (j = 1, d, r[2 + (i - 1) * d + j] = -polcoef(S[j], m, 'w));
      r[nu + 1] = polcoef(base, m, 'w); listput(rows, r)));
  my(M = matrix(#rows, nu + 1, a, b, rows[a][b]), K = matker(M), ok = 0, sol = 0);
  for (c = 1, #K, if (K[nu + 1, c] != 0, ok = 1; sol = K[, c] / K[nu + 1, c]));
  \\ dimension of the affine solution set (unknowns minus rank of the homogeneous part), when consistent
  my(sd = nu - matrank(matrix(#rows, nu, a, b, rows[a][b])));
  if (ok, Str("invariant (alpha = ", sol[1], ", beta = ", sol[2], "; solution dimension ", sd, ")"), "not invariant");
}
\\ negative control: a random space of the same dimension and degree (a generic space must fail if the test is meaningful)
ctrl(S) = { my(D = vecmax(apply(poldegree, S))); setrand(7); inv(vector(#S, i, sum(m = 0, D, (random(41) - 20) * 'w^m))); }
run(n, k) = {
  my(C = n * (n - 1) / 2, P = (k - 1) * (k - 2) / 2, E = concat(vector(C + P + 2, t, t - 1 - C), vector((k - 1) * n, t, 1/2 - (n - 1) + t - 1)), q = #E);
  my(P3 = vector(k - 1, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 0, E[i]); al--); p));
  my(P4 = vector(n, j, my(p = 'w^(j - 1), al = 1/2); for (i = 1, q, p = thetastep(p, al, 1/2 - (n - 1), E[i]); al--); p));
  \\ also with the common factor of each class removed (a family w^a (1-w)^b Jacobi is invariant only under a conjugated operator)
  my(g3 = content(P3) * 0 + fold(gcd, P3), g4 = fold(gcd, P4), S3 = apply(p -> p / g3, P3), S4 = apply(p -> p / g4, P4));
  emit(Str("(n,k)=", [n, k], ": dim P3 ", #P3, ", P3 ", inv(P3), " | dim P4 ", #P4, ", P4 ", inv(P4),
    " || common factors removed (", factor(g3), "; ", factor(g4), "): P3 ", inv(S3), " | P4 ", inv(S4),
    " || random control of the same shape: P3 ", ctrl(S3), " | P4 ", ctrl(S4)));
}
foreach([[1, 3], [1, 4], [1, 5], [2, 3], [2, 4], [3, 3], [2, 5], [3, 4]], v, run(v[1], v[2]));
