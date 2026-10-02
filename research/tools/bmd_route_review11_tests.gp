\\ Tests of the route review of 8 October 2026 (cycle bmd-20261008-ze).
\\ (a) Limit pair spaces at roots of unity: a cherry above a tie cluster and a tie with a cherry on one level, with
\\     the tie modulus c0 a primitive cube root of unity or i (number-field coefficients), several rates; prints the
\\     vanishing orders of the limit space at T = 0 and whether the largest is <= R+1.
\\ (The two-variable Schur values s_(l1,l2)(1, c) = c^l2 (1 + c + ... + c^(l1-l2)) vanish only at 0 and roots of unity,
\\ so these moduli are where a leading Schur-type sum at the tie pair could vanish.)
default(parisizemax, 6 * 10^9); default(seriesprecision, 80);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
t = varlower("t");
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
orders(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 1e9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  my(L = matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv > 0, 0, subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0)))));
  my(rk = 0, pv = List()); for (j = 1, K + 1, if (matrank(vecextract(L, "..", [1 .. j])) > rk, rk++; listput(pv, j - 1)));
  Vec(pv);
}
{
my(cs = [["omega", Mod(t, t^2 + t + 1)], ["i", Mod(t, t^2 + 1)]]);
foreach(cs, C, my(c0 = C[2]);
  foreach([[1, 1], [1, 3], [3, 1]], ab, my([a, b] = ab, rts = [1, 1 + 'e^b, c0 * 'e^a, 'e^a, 'e^(a + 2), -3 * 'e^(a + 3)], R = 15, o = orders(rts, R + 3));
    emit(Str("(a) cherry above tie, c0 = ", C[1], ", (a,b) = ", ab, ": orders ", o, "; largest <= R+1: ", vecmax(o) <= R + 1)));
  foreach([[1, 1], [1, 2]], ab, my([a, b] = ab, rts = [1, 1 + 'e^b, c0, 'e^a, -2 * 'e^(a + 1)], R = 10, o = orders(rts, R + 3));
    emit(Str("(a) tie and cherry on one level, c0 = ", C[1], ", (a,b) = ", ab, ": orders ", o, "; largest <= R+1: ", vecmax(o) <= R + 1))));
}
quit
