\\ Weight-three points on the spine limit of the F-curve (1,1,1,N-3) (30 September 2026; cycle bmd-20260930-zq).
\\ Spine space, in u = 1/z with the collapsed cluster at u = oo and single branch points at u = 1/s_j:
\\   P_(<=C+1)(u)  +  sum_j (1 - s_j u)^(1/2) P_(<N-3)(u)  +  sum_(j<k) ((1 - s_j u)(1 - s_k u))^(1/2),
\\ C = binom(N-3,2), s = (1, -1, mu) (one modulus).  At a non-branch u0 the weight is the vanishing order of the
\\ Wronskian, equal (the factors (1 - s_j u0)^(1/2) being units there) to that of the determinant D(u0) of the
\\ Taylor coefficients (orders 0..dim-1) of the normalized functions.  Q_mu(u) = D * prod_j (1 - s_j u)^(E_j), a
\\ polynomial, with every factor (1 - s_j u) removed.  Question: is there any mu off the collisions {0, 1, -1} and a
\\ root of Q_mu of multiplicity >= 3?  Modulo q = 2^61 - 1: Q_mu by interpolation in u (checked at extra points);
\\ R1(mu) = Res(Q_mu, Q_mu'), R2(mu) = Res(Q_mu, Q_mu'') by interpolation in mu (checked); every root of
\\ gcd(R1, R2) over F_q-bar is tested directly for a triple root.  Nonzero results mod q are upper bounds for
\\ coincidences over Q; an empty candidate set mod q (with no degree drop) excludes weight three for every mu.
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
\\ polynomial Q_mu(u) with branch factors removed; E = clearing exponent, B = degree bound
Qpoly(N, mu, E, B) = {
  my(s = [1, -1, mu], xs = vector(B + 3, i, Mod(i + 7, q)));
  my(ys = vector(B + 3, i, Dval(N, mu, xs[i]) * prod(j = 1, 3, (1 - s[j] * xs[i])^E)));
  my(P = polinterpolate(xs[1..B + 1], ys[1..B + 1], 'u));
  if (subst(P, 'u, xs[B + 2]) != ys[B + 2] || subst(P, 'u, xs[B + 3]) != ys[B + 3], error("u-interpolation"));
  foreach (s, sj, my(f = 1 - sj * 'u); while (poldegree(P) > 0 && P % f == 0, P = P / f));
  P;
}
run(N) = {
  my(C = binomial(N - 3, 2), n = (C + 2) + 3 * (N - 3) + 3, E = (n - 1) * (N - 1), B = 3 * E + n * n);
  my(Q1 = Qpoly(N, Mod(12345, q), E, B), d = poldegree(Q1));
  \\ degree in mu of the (unnormalized) coefficients: interpolate the leading coefficient's growth via R-degree bound search
  my(mus = List(), r1 = List(), r2 = List(), deg = 0, stable = 0, m = 0, R1 = 0, R2 = 0);
  \\ increase the number of mu-samples until both interpolants stabilize on two extra points
  while (!stable, m += 50;
    while (#mus < m + 2, my(mu = Mod(1000 + 17 * #mus, q), Q = Qpoly(N, mu, E, B));
      listput(mus, mu); listput(r1, polresultant(Q, deriv(Q))); listput(r2, polresultant(Q, deriv(deriv(Q)))));
    R1 = polinterpolate(Vec(mus)[1..m], Vec(r1)[1..m], 'mu); R2 = polinterpolate(Vec(mus)[1..m], Vec(r2)[1..m], 'mu);
    stable = (subst(R1, 'mu, mus[m + 1]) == r1[m + 1] && subst(R1, 'mu, mus[m + 2]) == r1[m + 2]
      && subst(R2, 'mu, mus[m + 1]) == r2[m + 1] && subst(R2, 'mu, mus[m + 2]) == r2[m + 2]);
    if (m > 6000, error("mu-degree too large")));
  my(g = gcd(R1, R2));
  foreach (['mu, 'mu - 1, 'mu + 1], f, while (poldegree(g) > 0 && g % f == 0, g = g / f));
  my(cands = if (poldegree(g) > 0, factormod(lift(g), q)[, 1], []), hits = 0);
  foreach (cands, fac, my(t = ffgen(fac * Mod(1, q), 't), Qt = Qpoly(N, t, E, B), h = gcd(gcd(Qt, deriv(Qt)), deriv(deriv(Qt))));
    if (poldegree(h) > 0, hits++; emit(Str("  triple root at mu root of ", fac, ": gcd degree ", poldegree(h)))));
  emit(Str("N=", N, ": dim ", n, "; deg_u Q ", d, "; mu-samples ", m, "; deg R1 ", poldegree(R1), ", deg R2 ", poldegree(R2),
    "; gcd (collisions removed) degree ", poldegree(g), "; mu-factors with a triple root: ", hits, " of ", #cands));
}
\\ Faster variant (MODE=2): the clearing exponent from the local exponents at a branch point u = 1/s_j, assuming
\\ they are minimal there (even class 0..n-N, odd class 1/2..N-3/2; checked by the exact interpolation below):
\\ E = (N-1)/2 - alpha, alpha = sum of exponents - n(n-1)/2.  Q(u, mu) is interpolated as a bivariate polynomial
\\ (degrees found adaptively, each step checked at extra points), then R1 = Res_u(Q, Q_u), R2 = Res_u(Q, Q_uu).
Qraw(N, mu, E, B) = {
  my(s = [1, -1, mu], xs = vector(B + 3, i, Mod(i + 7, q)));
  my(ys = vector(B + 3, i, Dval(N, mu, xs[i]) * prod(j = 1, 3, (1 - s[j] * xs[i])^E)));
  my(P = polinterpolate(xs[1..B + 1], ys[1..B + 1], 'u));
  if (subst(P, 'u, xs[B + 2]) != ys[B + 2] || subst(P, 'u, xs[B + 3]) != ys[B + 3], return(0));
  P;
}
run2(N) = {
  my(C = binomial(N - 3, 2), n = (C + 2) + 3 * (N - 3) + 3);
  my(alpha = (n - N) * (n - N + 1) / 2 + (N - 1)^2 / 2 - n * (n - 1) / 2, E = (N - 1) / 2 - alpha);
  if (denominator(E) != 1, error("E not integral"));
  my(B = 2 * n, P1 = 0); while (!(P1 = Qraw(N, Mod(12345, q), E, B)), B *= 2);
  my(d = poldegree(P1));
  foreach ([1 - 'u, 1 + 'u, 1 - 12345 * 'u], f, if (P1 % (f * Mod(1, q)) == 0, emit(Str("  N=", N, ": branch factor left at ", f))));
  \\ bivariate interpolation in mu
  my(mus = List(), polys = List(), m = 0, Q = 0, ok = 0);
  while (!ok, m += 20;
    while (#mus < m + 2, my(mu = Mod(1000 + 17 * #mus, q)); listput(mus, mu); listput(polys, Qraw(N, mu, E, d + 4)));
    my(cs = vector(d + 1, i, polinterpolate(Vec(mus)[1..m], vector(m, t, polcoef(polys[t], i - 1, 'u)), 'mu)));
    Q = sum(i = 1, d + 1, cs[i] * 'u^(i - 1));
    ok = (subst(Q, 'mu, mus[m + 1]) == polys[m + 1] && subst(Q, 'mu, mus[m + 2]) == polys[m + 2]);
    if (m > 3000, error("mu-degree too large")));
  my(Qu = deriv(Q, 'u), R1 = polresultant(Q, Qu, 'u), R2 = polresultant(Q, deriv(Qu, 'u), 'u), g = gcd(R1, R2));
  my(lc = polcoef(Q, d, 'u)); g = g / gcd(g, lc^(2 * d));
  foreach (['mu, 'mu - 1, 'mu + 1], f, while (poldegree(g) > 0 && g % f == 0, g = g / f));
  my(cands = if (poldegree(g) > 0, factormod(lift(g), q)[, 1], []), hits = 0);
  foreach (cands, fac, my(t = ffgen(fac * Mod(1, q), 't), Qt = substpol(lift(Q), 'mu, t) * t^0, h = gcd(gcd(Qt, deriv(Qt, 'u)), deriv(deriv(Qt, 'u), 'u)));
    if (poldegree(h, 'u) > 0, hits++; emit(Str("  triple root at mu root of ", fac, ": gcd degree ", poldegree(h, 'u)))));
  emit(Str("N=", N, " (bivariate): dim ", n, "; clearing exponent ", E, "; deg_u Q ", d, ", deg_mu Q ", poldegree(Q, 'mu),
    "; deg R1 ", poldegree(R1, 'mu), ", deg R2 ", poldegree(R2, 'mu), "; gcd (leading coefficient and collisions removed) degree ",
    poldegree(g), "; mu-factors with a triple root: ", hits, " of ", #cands));
}
main() = { my(Ns = if (getenv("NS"), eval(getenv("NS")), [5])); foreach (Ns, N, if (getenv("MODE") == "2", run2(N), run(N))); }
default(parisizemax, 4000000000);
main();
quit
