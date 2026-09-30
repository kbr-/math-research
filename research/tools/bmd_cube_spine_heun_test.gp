\\ Does the spine Weierstrass polynomial satisfy a second-order Fuchsian (Heun-type) equation? (1 October 2026;
\\ cycle bmd-20261001-e.)  If A Q'' + B Q' + C Q = 0 with A nonzero at every root of Q, every root of Q is simple
\\ (y = y' = 0 at a regular point forces y = 0): the Heine-Stieltjes mechanism behind the binary-face theorem
\\ (thm:cube-binary-face-weierstrass-points, Gegenbauer).  For the spine limit S_mu of lem:cube-fcurve-spine-limit
\\ (F-curve type (1,1,1,N-3), branch values u = 1, -1, 1/mu, cluster at u = oo), simple roots for every mu would
\\ be the spine conjecture conj:cube-fcurve-spine-weight-two in a stronger form, for every N if the equation is
\\ structural.  Test: kernel of (A, B, C) -> A Q'' + B Q' + C Q with deg A <= 3 + x, deg B <= 2 + x, deg C <= 1 + x
\\ (x = 0, 1, 2), at fixed mu, modulo q = 2^61 - 1; the system is overdetermined, so a nonzero kernel is a real
\\ signal.  Control: the binary-face polynomial Q_r (Gegenbauer) must give a nonzero kernel.
\\ Q_mu(u) is computed exactly as in bmd_cube_spine_weight3.gp (functions copied).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
nrm(e, s, k, n, u0) = {
  my(A = 1 - s * u0, r = -s / A);
  vector(n, i, my(ii = i - 1); sum(a = 0, ii, if (k - ii + a >= 0, binomial(e / 2, a) * r^a * binomial(k, ii - a) * u0^(k - ii + a), 0)));
}
nrmpair(s1, s2, n, u0) = {
  my(r1 = -s1 / (1 - s1 * u0), r2 = -s2 / (1 - s2 * u0));
  vector(n, i, my(ii = i - 1); sum(a = 0, ii, binomial(1/2, a) * r1^a * binomial(1/2, ii - a) * r2^(ii - a)));
}
Dval(N, mu, u0) = {
  my(C = binomial(N - 3, 2), s = [Mod(1, q), Mod(-1, q), mu], n = (C + 2) + 3 * (N - 3) + 3, rows = List());
  for (k = 0, C + 1, listput(rows, nrm(0, Mod(0, q), k, n, u0)));
  for (j = 1, 3, for (k = 0, N - 4, listput(rows, nrm(1, s[j], k, n, u0))));
  for (j = 1, 3, for (k = j + 1, 3, listput(rows, nrmpair(s[j], s[k], n, u0))));
  matdet(Mat(Vec(rows)~));
}
Qpoly(N, mu, E, B) = {
  my(s = [1, -1, mu], xs = vector(B + 3, i, Mod(i + 7, q)));
  my(ys = vector(B + 3, i, Dval(N, mu, xs[i]) * prod(j = 1, 3, (1 - s[j] * xs[i])^E)));
  my(P = polinterpolate(xs[1..B + 1], ys[1..B + 1], 'u));
  if (subst(P, 'u, xs[B + 2]) != ys[B + 2] || subst(P, 'u, xs[B + 3]) != ys[B + 3], error("u-interpolation"));
  foreach (s, sj, my(f = 1 - sj * 'u); while (poldegree(P) > 0 && P % f == 0, P = P / f));
  P;
}
\\ kernel dimension of (A,B,C) -> A Q'' + B Q' + C Q, degrees (da, db, dc)
odekernel(Q, da, db, dc) = {
  my(Q1 = deriv(Q, 'u), Q2 = deriv(Q1, 'u), cols = List());
  for (i = 0, da, listput(cols, 'u^i * Q2));
  for (i = 0, db, listput(cols, 'u^i * Q1));
  for (i = 0, dc, listput(cols, 'u^i * Q));
  my(D = vecmax(apply(p -> poldegree(p), Vec(cols))));
  my(M = matrix(D + 1, #cols, r, c, polcoeff(cols[c], r - 1, 'u)));
  my(K = matker(M));
  [#cols, D + 1, #K, K];
}
main() = {
  \\ control: Gegenbauer Q_r of the binary face, Q_0 = 1, Q_1 = 3T, Q_(k+1) = (2k+3) T Q_k + k(k+2)(1-T^2) Q_(k-1)
  my(Qm = Mod(1, q), Qc = Mod(3, q) * 'u);
  for (k = 1, 9, my(Qn = (2 * k + 3) * 'u * Qc + k * (k + 2) * (1 - 'u^2) * Qm); Qm = Qc; Qc = Qn);
  my(r0 = odekernel(Qc, 2, 1, 0));
  emit(Str("control: binary-face Q_10 (degree ", poldegree(Qc), "), degrees (2,1,0): unknowns ", r0[1], ", equations ", r0[2], ", kernel dimension ", r0[3]));
  foreach ([5, 6, 7], N,
    my(C = binomial(N - 3, 2), n = (C + 2) + 3 * (N - 3) + 3, E = (n - 1) * (N - 1), B = 3 * E + n * n);
    foreach ([Mod(12345, q), Mod(-7, q) / 3], mu,
      my(Q = Qpoly(N, mu, E, B), line = Str("N=", N, " mu=", lift(mu), ": deg Q = ", poldegree(Q)));
      for (x = 0, 2, my(r = odekernel(Q, 3 + x, 2 + x, 1 + x));
        line = Str(line, "; degrees (", 3 + x, ",", 2 + x, ",", 1 + x, "): unknowns ", r[1], ", equations ", r[2], ", kernel ", r[3]));
      emit(line)));
}
default(parisizemax, 2000000000);
main();
quit
