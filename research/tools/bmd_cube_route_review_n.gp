\\ Route review tests (29 September 2026).
\\ (1) Falsification attempt for conj:cube-pair-degeneration-simplicity on the next pattern of the
\\     double-root induction, (2,2,1^(N-4)), N = 5, 6: double roots A = 1, B = 2, simple roots -1 and
\\     (N=6) 3. Exact cleared Wronskian numerator P(t) = det[rho_r(t,X)] prod_c (1+ct)^E by exact
\\     interpolation (degree bound (N-2)E + 2N, checked at an extra point); strip the branch factors;
\\     report the non-branch degree and squarefreeness (the (A,B) block uses the directional limit).
\\ (2) Absurd-bridge translation test: are the zeros of Q_r (the binary-face Weierstrass points,
\\     D^r (1-T^2)^(-3/2) = (1-T^2)^(-3/2-r) Q_r) real and simple for r <= 12?
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
serpow(u, al, L) = vector(L, m, binomial(al, m - 1) * u^(m - 1));
mul(A, B, L) = vector(L, n, sum(m = 1, n, A[m] * B[n + 1 - m]));
tx(B, t, L) = vector(L, n, t * B[n] + if (n > 1, B[n - 1], 0));  \\ multiply by (t + X)
rows22(dbl, sim, t, L, naive = 0) = {
  my(u(c) = c / (1 + c * t), R = List(), A = dbl[1], B = dbl[2]);
  my(p(c, e) = serpow(u(c), e, L));
  for (i = 1, #sim, for (k = i + 1, #sim, listput(R, mul(p(sim[i], -3/2), p(sim[k], -3/2), L))));
  foreach (dbl, D, foreach (sim, k,
    listput(R, mul(p(D, -3/2), p(k, -3/2), L));
    listput(R, tx(mul(p(D, -5/2), p(k, -3/2), L), t, L))));
  \\ (A,B) block: phi_A phi_B, phi_A' phi_B, phi_A phi_B' and, since phi_A' phi_B' is a combination of
  \\ the previous two, the second-order limit (phi_A' - g phi_A) phi_B'', g = -3/(2(A-B)), of an exact
  \\ double A and a double B approached by B, B+eta. Up to constants that row is
  \\ (1+AT)^(-5/2) (1+BT)^(-7/2) T^2 (-(3/2) T - g (1+AT)).
  listput(R, mul(p(A, -3/2), p(B, -3/2), L));
  listput(R, tx(mul(p(A, -5/2), p(B, -3/2), L), t, L));
  listput(R, tx(mul(p(A, -3/2), p(B, -5/2), L), t, L));
  my(g = -3 / (2 * (A - B)), q = mul(p(A, -5/2), p(B, -7/2), L));
  my(lin = vector(L, n, if (n == 1, -(3/2) * t - g * (1 + A * t), if (n == 2, -(3/2) - g * A, 0))));
  listput(R, if (naive, tx(tx(mul(p(A, -5/2), p(B, -5/2), L), t, L), t, L), tx(tx(mul(lin, q, L), t, L), t, L)));
  listput(R, p(A, -3)); listput(R, p(B, -3));
  if (#R != L, error("row count"));
  matrix(L, L, r, j, R[r][j]);
}
\\ Both candidate row lists are rank deficient, so the interpolation below (main1) cannot run;
\\ main0 reports the ranks at one point instead (the Wronskian is then identically zero).
main0() = {
  foreach ([5, 6], N,
    my(R = binomial(N, 2), sim = if (N == 5, [-1], [-1, 3]));
    emit(Str("(2,2,1^", N - 4, ") N=", N, " rank of the ", R, " rows at t=3: naive derivative rows ",
      matrank(rows22([1, 2], sim, 3, R, 1)), ", second-order directional row ", matrank(rows22([1, 2], sim, 3, R, 0)))));
}
main1() = {
  foreach ([5, 6], N,
    my(R = binomial(N, 2), E = binomial(R, 2), dbl = [1, 2], sim = if (N == 5, [-1], [-1, 3]), vals = concat(dbl, sim));
    \\ modulo p = 2^61-1 (exact rational interpolation timed out at 600 s); generous interpolation
    \\ degree (N-2)E+3R, checked at two extra points. The reduction mod p of the rational numerator
    \\ has at most its degree; if the degrees agree, squarefree mod p implies squarefree over Q.
    \\ T22 below is the bound for the naive derivative rows, printed for comparison only.
    my(p = 2^61 - 1, D = (N - 2) * E + 3 * R, xs = List(), ys = List(), t = 1);
    while (#xs < D + 3, t++; if (prod(c = 1, #vals, 1 + vals[c] * t) % p == 0, next);
      my(tm = Mod(t, p)); listput(xs, tm); listput(ys, matdet(rows22(dbl, sim, tm, R)) * prod(c = 1, #vals, (1 + vals[c] * tm)^E)));
    my(P = polinterpolate(Vec(xs)[1..D+1], Vec(ys)[1..D+1], 'z));
    if (subst(P, 'z, xs[D + 2]) != ys[D + 2] || subst(P, 'z, xs[D + 3]) != ys[D + 3], error("interpolation check"));
    if (P == 0, error("zero Wronskian: dependent rows"));
    my(P0 = P); foreach (vals, c, while (subst(P0, 'z, Mod(-1, p) / c) == 0, P0 = P0 / ('z + Mod(1, p) / c)));
    my(ms = binomial(N - 1, 2) + binomial(R - N + 1, 2));
    my(md = -5 * (N - 2) + binomial(2 * N - 4, 2) - 3 + binomial(binomial(N - 2, 2), 2) + 4 * N - 5);
    my(T22 = (N - 4) * E + 2 * N - 4 - 2 * md - (N - 4) * ms);
    emit(Str("(2,2,1^", N - 4, ") N=", N, ": deg P=", poldegree(P), " (bound ", (N - 4) * E + 2 * N - 4,
      "), non-branch degree ", poldegree(P0), " (naive-row T22 ", T22, "), squarefree ", poldegree(gcd(P0, deriv(P0))) == 0,
      ", zero at 0: ", subst(P0, 'z, 0) == 0)));
}
Qr(n) = { my(a = 1, b = 3*'T, c); if (n == 0, return(a)); for (k = 1, n - 1, c = (2*k+3)*'T*b + k*(k+2)*(1-'T^2)*a; a = b; b = c); b; };
main2() = {
  my(res = vector(12, r, my(q = Qr(r), n = polsturm(q)); [r, poldegree(q), n, poldegree(gcd(q, deriv(q))) == 0]));
  emit(Str("Q_r [r, degree, real zeros (Sturm), squarefree]: ", res));
}
main2();
main0();
