\\ The one-double-root discriminant D^conf at N = 6 on a random line of its moduli (30 Sept 2026).
\\ Space V^(1): double root A = 1, simple roots -1, 3, k3(s) = c0 + c1 s, k4(s) = d0 + d1 s.
\\ Up to Moebius maps (which act covariantly) the one-double-root configurations at N = 6 form a
\\ plane, with coordinates (k3, k4) after fixing A, -1, 3; a random line in it tests reducedness
\\ of D^conf (Bertini).
\\ Question (restriction lead, descent review): the six-root exponent-four factor of Delta_W^nc
\\ enters the descent at level zero or one. Is D^conf at N = 6 squarefree away from the special
\\ values (collisions among the roots, k3 or k4 = 0 where the T-variable degree drops)?
\\ Method (mod p = 2^61-1): for each s, the cleared numerator P_s(T) (degree <= 3E + 4 = 319) by
\\ interpolation with two checks; the minimal branch factors (1+AT)^mA prod_k (1+kT)^ms are
\\ divided out exactly (remainder checked), leaving W_s of degree T_conf(6) = 60; D(s) = disc W_s,
\\ interpolated in s with two checks; special factors removed; squarefree decomposition reported.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
q = 2^61 - 1;
serpow(u, al, L) = vector(L, m, binomial(al, m - 1) * u^(m - 1));
mul(A, B, L) = vector(L, n, sum(m = 1, n, A[m] * B[n + 1 - m]));
tx(B, t, L) = vector(L, n, t * B[n] + if (n > 1, B[n - 1], 0));
rows1(A, sim, t, L) = {
  my(R = List(), p(c, e) = serpow(c / (1 + c * t), e, L));
  for (i = 1, #sim, for (k = i + 1, #sim, listput(R, mul(p(sim[i], -3/2), p(sim[k], -3/2), L))));
  foreach (sim, k,
    listput(R, mul(p(A, -3/2), p(k, -3/2), L));
    listput(R, tx(mul(p(A, -5/2), p(k, -3/2), L), t, L)));
  listput(R, p(A, -3));
  if (#R != L, error("row count"));
  matrix(L, L, r, j, R[r][j]);
}
N = 6; RR = 15; EE = 105;
msv = -3/2 * (N - 1) + binomial(N - 1, 2) + binomial(RR - N + 1, 2) + 3/2 * (N - 1);
mdv = -5/2 * (2 * N - 4) + binomial(2 * N - 4, 2) - 3 + binomial(binomial(N - 2, 2), 2) + 4 * (N - 2) + 3;
c0 = Mod(7, q) / 5; c1 = Mod(11, q) / 3; d0 = Mod(-13, q) / 4; d1 = Mod(2, q) / 9;
Dval(s) = {
  my(A = Mod(1, q), sim = [Mod(-1, q), Mod(3, q), c0 + c1 * s, d0 + d1 * s], vals = concat([A], sim), DT = 3 * EE + 4);
  my(ts = vector(DT + 3, j, Mod(j + 7, q)));
  my(ys = vector(DT + 3, j, matdet(rows1(A, sim, ts[j], RR)) * prod(c = 1, 5, (1 + vals[c] * ts[j])^EE)));
  my(P = polinterpolate(ts[1..DT + 1], ys[1..DT + 1], 'z));
  if (subst(P, 'z, ts[DT + 2]) != ys[DT + 2] || subst(P, 'z, ts[DT + 3]) != ys[DT + 3], error("z check"));
  my(B = (1 + A * 'z)^mdv * prod(k = 1, 4, (1 + sim[k] * 'z)^msv));
  my(dv = divrem(P, B));
  if (dv[2] != 0, return([0, -1]));
  [poldisc(dv[1]), poldegree(dv[1])];
}
export(q, serpow, mul, tx, rows1, Dval, N, RR, EE, msv, mdv, c0, c1, d0, d1);
factorsqrfree(f) = {
  my(res = List(), k = 0, c = gcd(f, deriv(f)), w = f / c);
  while (poldegree(w) > 0, k++; my(y = gcd(w, c)); my(z = w / y); if (poldegree(z) > 0, listput(res, [z, k])); w = y; c = c / y);
  Vec(res);
}
main() = {
  my(K = if (getenv("K"), eval(getenv("K")), 12000));
  emit(Str("minimal multiplicities: double ", mdv, ", simple ", msv, "; expected W degree 60"));
  my(ss = vector(K + 2, i, Mod(i + 10, q)));
  my(V = parvector(K + 2, i, Dval(ss[i])));
  my(bad = select(v -> v[2] != 60, V));
  emit(Str("s-values: ", K + 2, "; values with W degree != 60 or inexact division: ", #bad));
  if (#bad, return);
  my(vals = vector(K + 2, i, V[i][1]));
  my(Dp = polinterpolate(ss[1..K], vals[1..K], 's));
  if (subst(Dp, 's, ss[K + 1]) != vals[K + 1] || subst(Dp, 's, ss[K + 2]) != vals[K + 2], emit("s check failed: raise K"); return);
  emit(Str("deg D(s) = ", poldegree(Dp)));
  \\ special values: k3 or k4 equal to 1 (triple root), -1, 3 or 0, and k3 = k4
  my(sp = [(1 - c0) / c1, (-1 - c0) / c1, (3 - c0) / c1, -c0 / c1, (1 - d0) / d1, (-1 - d0) / d1, (3 - d0) / d1, -d0 / d1, (d0 - c0) / (c1 - d1)]);
  my(rest = Dp, mults = vector(#sp));
  for (c = 1, #sp, while (subst(rest, 's, sp[c]) == 0, rest = rest \ ('s - sp[c]); mults[c]++));
  emit(Str("multiplicities at k3 = 1, -1, 3, 0; k4 = 1, -1, 3, 0; k3 = k4: ", mults, "; remaining degree ", poldegree(rest)));
  emit(Str("squarefree decomposition of the rest [multiplicity, degree]: ", apply(v -> [v[2], poldegree(v[1])], factorsqrfree(rest))));
}
default(nbthreads, 12);
main();
