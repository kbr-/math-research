\\ Vanishing orders of limit pair spaces for cherry combinations (8 October 2026; cycle bmd-20261008-zc).
\\ For each arc (roots as polynomials in eps), the limit L0 of the pair space (rows H_k(r,s) = [T^k]((1+rT)(1+sT))^(-3/2),
\\ columns 0..R+3) by valuation-pivoted elimination over Q(eps); prints its vanishing orders at T = 0 and whether the
\\ largest is <= R+1 (no section of order R+2: the arc avoids the contact locus K = {rank A_(R+1) < R}, and the leading
\\ coordinate lies in columns 0..R+1).  Types: a cherry above a tie cluster, two cherries at different levels, a cherry
\\ above a cherry (nested at different scales), with several tie moduli including c = -1.
default(parisizemax, 6 * 10^9); default(seriesprecision, 80);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
H(r, s, K) = { my(f = ((1 + r * 'x + O('x^(K + 1))) * (1 + s * 'x))^(-3/2)); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
orders(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 1e9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    if (bi == 0, return([-1]));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  my(L = matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv > 0, 0, subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0)))));
  my(rk = 0, pv = List()); for (j = 1, K + 1, if (matrank(vecextract(L, "..", [1 .. j])) > rk, rk++; listput(pv, j - 1)));
  Vec(pv);
}
{
my(arcs = List());
\\ cherry {1, 1+e^b} above a tie cluster x*{c0, 1} over a caterpillar x*{e^2, -3 e^3}: x = e^a
foreach([2, -1, -1/2, 3], c0, foreach([[1, 1], [1, 3], [3, 1]], ab, my([a, b] = ab);
  listput(arcs, [Str("cherry above tie, c0 = ", c0, ", (a,b) = ", ab), [1, 1 + 'e^b, c0 * 'e^a, 'e^a, 'e^(a + 2), -3 * 'e^(a + 3)]])));
\\ two cherries: top cherry {1, 1+e^b}, lower cherry x*{1, 1+e^(b2)} over x*{e^2, -2 e^3}: x = e^a
foreach([[1, 1, 1], [1, 2, 1], [2, 1, 3], [1, 3, 2]], abb, my([a, b, b2] = abb);
  listput(arcs, [Str("two cherries, (a,b,b2) = ", abb), [1, 1 + 'e^b, 'e^a, 'e^a * (1 + 2 * 'e^b2), 'e^(a + 2), -2 * 'e^(a + 3)]]));
\\ tie and cherry on one level: level roots 1 (cherry {1,1+e^b}) and c0, over caterpillar e^a*{1, -2 e}
foreach([2, -1], c0, foreach([[1, 1], [1, 2], [2, 1]], ab, my([a, b] = ab);
  listput(arcs, [Str("tie and cherry on one level, c0 = ", c0, ", (a,b) = ", ab), [1, 1 + 'e^b, c0, 'e^a, -2 * 'e^(a + 1)]])));
foreach(arcs, A, my(rts = A[2], n = #rts, R = n * (n - 1) / 2, ord = orders(rts, R + 3));
  emit(Str(A[1], ": R = ", R, ", vanishing orders ", ord, "; largest <= R+1: ", vecmax(ord) <= R + 1)));
}
quit
