\\ Extra limit functions of the (2,n) two-cluster class (30 September 2026; cycle bmd-20260930-zw).
\\ Class: products (1 - b_j eps u1)^(1/2)(1 - c_k eps u2)^(1/2), j = 1, 2, k = 1..n, u_i = 1/(z - p_i), p1 = 0, p2 = 1,
\\ shapes centred (b = (-b, b), sum c = 0; centring moves p_i by O(eps) and does not change the family).
\\ Valuation reduction over Q[[eps]] (as in bmd_cube_two_cluster_limit.gp) in the coordinates u1^a, u2^c (principal
\\ parts at 0 and 1 and the value at infinity).  Prints the reduced eps-orders and, for every limit function of
\\ order >= 2 not in span{1, u1, u2, ..., u2^(n-1)}, its principal-part coefficients, echelonized by order.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
coords(a, c, K) = {
  my(F = 1 / ('z^a * ('z - 1)^c), v = vector(2 * K + 1));
  my(s0 = F + O('z^1)); for (k = 1, K, v[k] = polcoef(s0, -k, 'z));
  my(t = subst(F, 'z, 1 + 'y) + O('y^1)); for (k = 1, K, v[K + k] = polcoef(t, -k, 'y));
  v[2 * K + 1] = if (a + c == 0, 1, 0);
  v;
}
flat(b, c, K) = {
  my(n1 = #b, n2 = #c, D = 2 * K + 1, rows = List(), CO = matrix(K + 1, K + 1));
  for (a = 0, K, for (cc = 0, K - a, CO[a + 1, cc + 1] = coords(a, cc, K)));
  for (j = 1, n1, for (k = 1, n2,
    my(r = vector(D));
    for (a = 0, K, for (cc = 0, K - a, r += binomial(1/2, a) * (-b[j])^a * binomial(1/2, cc) * (-c[k])^cc * 'e^(a + cc) * CO[a + 1, cc + 1]));
    listput(rows, r)));
  my(R = Mat(Vec(rows)~), n = n1 * n2, vals = vector(n), iter = 0);
  while (1, iter++; if (iter > 2000, error("no convergence"));
    for (i = 1, n, vals[i] = vecmin(vector(D, t, if (R[i, t] == 0, oo, valuation(R[i, t], 'e)))));
    my(L = matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e)), ker = matker(L~));
    if (#ker == 0, break);
    my(w = ker[, 1], i0 = 0, best = -oo);
    for (i = 1, n, if (w[i] != 0 && vals[i] > best, best = vals[i]; i0 = i));
    R[i0, ] = sum(i = 1, n, w[i] * 'e^(best - vals[i]) * R[i, ]);
    for (t = 1, D, R[i0, t] = truncate(R[i0, t] + O('e^(K + 1)))));
  [vals, matrix(n, D, i, t, polcoef(R[i, t], vals[i], 'e))];
}
\\ report the limit modulo span{1, u1, u2..u2^(n-1)}: keep coordinates u1^a (a >= 2) and u2^c (c >= n)
report(b, c, K) = {
  my(n = #c, res = flat(b, c, K), vals = res[1], L = res[2], keep = concat(vector(K - 1, a, a + 1), vector(K - n + 1, cc, K + n - 1 + cc)));
  my(ord = vecsort(vals, , 1), rowsL = List());
  emit(Str("b = ", b, ", c = ", c, ": orders ", vecsort(vals)));
  \\ quotient vectors, echelonized from the lowest order upward (a basis of the extra part)
  my(Q = matrix(#vals, #keep, i, t, L[ord[i], keep[t]]), got = 0, Acc = matrix(0, #keep));
  for (i = 1, #vals, my(v = Q[i, ]);
    if (matrank(concat(Acc, v)) > got, got++; Acc = concat(Acc, v);
      my(lab = List()); for (t = 1, #keep, if (v[t] != 0, listput(lab, Str(if (keep[t] <= K, Str("u1^", keep[t]), Str("u2^", keep[t] - K)), ":", v[t]))));
      emit(Str("  order ", vals[ord[i]], ": ", Vec(lab)))));
}
main() = {
  my(K = if (getenv("K"), eval(getenv("K")), 14));
  \\ env CASES: a list of [b, c] pairs replacing the default list (used for the (2,6), (2,7) prediction test)
  if (getenv("CASES"), foreach (eval(getenv("CASES")), bc, report(bc[1], bc[2], K)); return);
  \\ env ISO=1: centred shapes c = (1, w, w^2), w a primitive cube root of unity, so sum c_k^2 = 0 and
  \\ lem:cube-two-n-first-generators has kappa = 0.  Computed over F_p for two primes p = 1 mod 3 (a reduction of the
  \\ characteristic-zero point Q(w), valid for all but finitely many p); control: centred c = (1, 2, -3) mod p.
  if (getenv("ISO"), foreach ([1000033, 1000081], p,
      my(w = Mod(znprimroot(p), p)^((p - 1) / 3), o = Mod(1, p));
      emit(Str("p = ", p, ", w = ", lift(w), ":"));
      report([-o, o], [o, w, w^2], K); report([-o, o], [2 * o, 2 * w, 2 * w^2], K); report([-o, o], [o, 2 * o, -3 * o], K));
    return);
  foreach ([[[-1, 1], [-1, 1]], [[-1, 1], [-2, 2]], [[-1, 1], [-1, 0, 1]], [[-1, 1], [-3, 1, 2]], [[-2, 2], [-1, 0, 1]], [[-1, 1], [-3, -1, 1, 3]], [[-1, 1], [-3, 0, 1, 2]], [[-2, 2], [-3, -1, 1, 3]], [[-1, 1], [-2, -1, 0, 1, 2]]], bc,
    report(bc[1], bc[2], K));
}
main();
quit
