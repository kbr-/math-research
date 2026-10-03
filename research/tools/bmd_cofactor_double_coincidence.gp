\\ Vanishing of the Taylor cofactor on double coincidences (cycle bmd-20261009-ae, 9 October 2026).
\\ F = p_T0 / Vand^(M-2) (pair span rows [w^t]((1+y_i w)(1+y_j w))^(-3/2)), a polynomial.
\\ Tested statement (candidate): F vanishes whenever two disjoint pairs of roots coincide, for every M >= 4.
\\ F at y = (a + e u1, a, b + e u2, b, y5..yM) is the e^0 value of the exact quotient (symbolic e), at random
\\ rational a, b, y5.. and u1, u2, for M = 4, 5, 6 (three points each). Control: a single coincident pair
\\ (a + e u1, a, y3, ..., yM), where F should be nonzero.
OUT = "research/results/bmd-20261009-ae/cofactor-double-coincidence.txt";
default(parisizemax, 4 * 10^9);
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
Fat(Y) = {
  my(M = #Y, R = M * (M - 1) / 2, P = matrix(R, R), r = 0);
  for (i = 1, M, for (j = i + 1, M, r++; my(h = H(Y[i], Y[j], R - 1)); for (k = 1, R, P[r, k] = h[k])));
  subst(matdet(P) / prod(i = 1, M, prod(j = i + 1, M, Y[i] - Y[j]))^(M - 2), 'e, 0);
};
rr() = (random(200) + 1) / (random(13) + 2);
{
  setrand(20261009);
  foreach([4, 5, 6], M, my(dbl = vector(3), sgl = vector(3));
    for (t = 1, 3, my(a = rr(), b = rr() + 7, rest = vector(M - 4, i, rr() + 20 + 5 * i));
      dbl[t] = Fat(concat([a + 'e * 3, a, b + 'e * 5, b], rest));
      sgl[t] = Fat(concat([a + 'e * 3, a, b, b + 11], rest)));
    write(OUT, "M=", M, ": two disjoint coincident pairs: F = ", dbl, "; one coincident pair (control): F nonzero: ", vector(3, t, sgl[t] != 0)));
}
