\\ Symbolic check of lem:cube-two-n-first-generators (30 September 2026; cycle bmd-20260930-zw).
\\ Class (2,n): span{A, B} * W2, A, B = (1 -+ b v1)^(1/2) (centred pair), W2 = span{(1 - c_k v2)^(1/2)} (centred,
\\ sum c_k = 0), v_i = eps u_i.  With X = v1/S^2, S = (A + B)/2, and the valuation basis h_b = v2^b + O(v2^n) of W2,
\\ it forms
\\   E1 = X h1 - q X h0 + q h1,                                                   q = eps r, r = 1/(p1 - p2),
\\   E  = X h_{n-1} - q^{n-1} X h0 + sum_{i=1}^{n-1} q^{n-i} h_i,
\\   E' = E - eta_{n-1,n} (q^n X h0 - sum_{i=1}^{n-1} q^{n+1-i} h_i),  E'' = E' - (n-1) q^{n-2} E1,
\\ and checks: E1 = O(eps^4) with eps^4 coefficient -r^2 g1 u1^2 + (terms in 1, u1, u2..u2^{n-1}), g1 = b^2/4;
\\ E'' = O(eps^{n+2}) with eps^{n+2} coefficient r^2 kappa u2^n + (such terms), no u1^2 term, and
\\ kappa = -3(2n-3) p2/(4n(n^2-1)), p2 = sum c_k^2.  Here W2's basis is computed from the square roots directly
\\ (symbolic linear solve), not from the recurrence used in the proof.  Series variable eps is x; u1, u2 are
\\ symbols U1, U2 substituted by 1/(z - p1), 1/(z - p2) in the coefficients.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
\\ pole-order profile of a rational function f of z: [coefficient of u1^2, coefficient of u2^n, max pole at p1, max pole at p2]
pp(f, n) = {
  my(s1 = subst(f, 'z, 'p1 + 'y) + O('y), s2 = subst(f, 'z, 'p2 + 'y) + O('y));
  [polcoef(s1, -2, 'y), polcoef(s2, -n, 'y), -valuation(s1, 'y), -valuation(s2, 'y)];
}
run(n) = {
  my(K = n + 3, c = vector(n, k, if (k < n, eval(Str("'c", k)), -sum(j = 1, n - 1, eval(Str("'c", j))))));
  my(sq(w) = sum(a = 0, K, binomial(1/2, a) * w^a) + O(x^(K + 1)));
  my(u1 = 1 / ('z - 'p1), u2 = 1 / ('z - 'p2), r = 1 / ('p1 - 'p2), q = x * r, U(f) = substvec(f, ['U1, 'U2], [u1, u2]));
  my(A = sq(-'b * x * 'U1), B = sq('b * x * 'U1), S = (A + B) / 2, X = x * 'U1 / S^2, g1 = 'b^2 / 4);
  \\ W2 as polynomials in V = v2 (truncated at degree K), valuation basis by a symbolic solve
  my(F = vector(n, k, sum(a = 0, K, binomial(1/2, a) * (-c[k])^a * 'V^a)));
  my(M = matrix(n, n, a, k, polcoef(F[k], a - 1, 'V)));
  my(Mi = M^-1, h = vector(n, b, sum(k = 1, n, Mi[k, b] * F[k])));
  for (b = 1, n, for (a = 0, n - 1, if (polcoef(h[b], a, 'V) != (a == b - 1), error("basis"))));
  my(H(b) = subst(h[b + 1], 'V, x * 'U2) + O(x^(K + 1)));
  my(eta = polcoef(h[n], n, 'V));
  my(E1 = X * H(1) - q * X * H(0) + q * H(1));
  for (k = 0, 3, if (U(polcoef(E1, k)) != 0, emit(Str("n=", n, ": E1 has a nonzero eps^", k, " term")); return));
  my(e4 = pp(U(polcoef(E1, 4)), n));
  emit(Str("n=", n, ": E1 = O(eps^4); u1^2 coefficient of its eps^4 term equals -r^2 g1: ", e4[1] == -r^2 * g1, "; pole orders (", e4[3], ", ", e4[4], ")"));
  my(E = X * H(n - 1) - q^(n - 1) * X * H(0) + sum(i = 1, n - 1, q^(n - i) * H(i)));
  my(E2 = E - eta * (q^n * X * H(0) - sum(i = 1, n - 1, q^(n + 1 - i) * H(i))) - (n - 1) * q^(n - 2) * E1);
  for (k = 0, n + 1, if (U(polcoef(E2, k)) != 0, emit(Str("n=", n, ": E'' has a nonzero eps^", k, " term")); return));
  my(kap = -3 * (2 * n - 3) * sum(k = 1, n, c[k]^2) / (4 * n * (n^2 - 1)), en = pp(U(polcoef(E2, n + 2)), n));
  emit(Str("n=", n, ": E'' = O(eps^", n + 2, "); u2^", n, " coefficient equals r^2 kappa: ", en[2] == r^2 * kap, "; u1^2 coefficient ", en[1], "; pole orders (", en[3], ", ", en[4], ")"));
}
main() = { for (n = 3, 5, run(n)); }
main();
quit
