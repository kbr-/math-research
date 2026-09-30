\\ Collision factors of the boundary polynomial on a collision hyperplane (30 September 2026; review bmd-20260930-x).
\\ Tested statement: on H = {a_1 = a_2}, the restriction F_N|_H has no factor (A - a_k) or (a_k - a_l) with
\\ multiplicity at least two (A = a_1 = a_2), so V(F|_H) is reduced along the collision hyperplanes of H.
\\ Test: on a random line a(u) = alpha + u beta inside H over F_p, p = 2^61 - 1, interpolate
\\ G(u) = F(A(u), A(u), a_3(u), ..., a_N(u)) (degree at most lambda_N), and report the order of G at each
\\ collision parameter of H (A = a_k, a_k = a_l). The e-interpolation takes the polynomial F to H exactly.
p = 2^61 - 1;
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
beta32(m) = binomial(-3/2, m);
Hk(k, x, y) = sum(m = 0, k, beta32(m) * beta32(k - m) * x^m * y^(k - m));
prs(N) = my(v = List()); for (i = 1, N, for (j = i + 1, N, listput(v, [i, j]))); Vec(v);
\\ F(a) with the collision denominator taken over pairs of distinct labels only; on H the pair {1,2} row
\\ degenerates, so use the confluent-safe form: det divided by prod over pairs with a_i != a_j, times the
\\ appropriate limit. Here we avoid the issue by computing F at points near H: F is a polynomial, so
\\ F|_H(u) is the limit, obtained by interpolating F on the line alpha + u beta + e gamma at small e
\\ values and setting e = 0 (bivariate interpolation in (u, e)).
{
Fval(a) = my(N = #a, P = prs(N), R = #P); matdet(matrix(R, R, r, k, Hk(k - 1, a[P[r][1]], a[P[r][2]]))) / prod(r = 1, R, (a[P[r][1]] - a[P[r][2]])^(N - 2));
}
restr(N, seed) = {
  setrand(seed);
  my(lam = 3 * binomial(N, 4), al = vector(N, i, Mod(random(p), p)), be = vector(N, i, Mod(random(p), p)));
  al[2] = al[1]; be[2] = be[1]; \\ H: a_1 = a_2 on the u-line; e moves off H in direction e_2
  my(us = vector(lam + 3, t, Mod(t + 5, p)), es = vector(lam + 3, t, Mod(t + 11, p)));
  \\ G(u) = F on H: for each u, interpolate e -> F(alpha + u beta + e (e_2)) and take the value at e = 0
  my(G = vector(#us, t, my(vals = vector(lam + 1, h, my(a = al + us[t] * be); a[2] += es[h]; Fval(a)));
    subst(polinterpolate(es[1..lam + 1], vals, 'e), 'e, 0)));
  my(Gu = polinterpolate(us[1..lam + 1], G[1..lam + 1], 'u));
  if (subst(Gu, 'u, us[lam + 2]) != G[lam + 2], error("u check"));
  my(res = List());
  for (k = 3, N, my(u0 = -(al[1] - al[k]) / (be[1] - be[k])); listput(res, [Str("A=a", k), valuation(Gu, 'u - u0)]));
  for (k = 3, N, for (l = k + 1, N, my(u0 = -(al[k] - al[l]) / (be[k] - be[l])); listput(res, [Str("a", k, "=a", l), valuation(Gu, 'u - u0)])));
  emit(Str("N=", N, ": deg F|_H on the line = ", poldegree(Gu), " (lambda ", lam, "); orders at collision parameters: ", Vec(res)));
}
restr(5, 1);
restr(6, 2);
