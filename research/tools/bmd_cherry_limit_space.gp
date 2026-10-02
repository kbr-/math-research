\\ Limit row spaces of single-cherry clusters (8 October 2026; cycle bmd-20261008-za).
\\ Arcs: roots 1, 1 + c_e eps^b, c_q eps^(a + v_q) (caterpillar below, v_1 = 0 < v_2 < ...), integer rates.  The limit
\\ L0 of the row space of the pair matrix (rows H_k(r, s) = [T^k]((1+rT)(1+sT))^(-3/2), columns 0..K) is computed by
\\ valuation-pivoted elimination over Q(eps) and stored in reduced row echelon form.  Prints, for M = 2 (K = 11) and
\\ M = 3 (K = 13), over several arcs: the vanishing orders of L0 at T = 0 (pivot columns), whether L0 equals the L0 of
\\ the first arc, and whether L0 contains the limit functions (1+T)^(-3) (the cherry pair) and 1 (cluster pairs).
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
H(r, s, K) = { my(f = ((1 + r * 'x) * (1 + s * 'x))^(-3/2) + O('x^(K + 1))); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
ser(f, K) = vector(K + 1, k, polcoef(f + O('x^(K + 1)), k - 1, 'x));
limitspace(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 1e9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  my(L = matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv > 0, 0, if (vv < 0, error("negative valuation"), subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0))))));
  matrref(L);
}
matrref(L) = {
  my(A = L, piv = List(), row = 1, nr = #A[, 1]);
  for (j = 1, #A, if (row > nr, break); my(p = 0); for (i = row, nr, if (A[i, j] != 0, p = i; break));
    if (p, my(t = A[row, ]); A[row, ] = A[p, ]; A[p, ] = t; A[row, ] = A[row, ] / A[row, j];
      for (i = 1, nr, if (i != row && A[i, j] != 0, A[i, ] = A[i, ] - A[i, j] * A[row, ])); listput(piv, j - 1); row++));
  [A, Vec(piv)];
}
contains(A, v) = matrank(matconcat([A; v])) == matrank(A);
{
foreach([[2, 11, [[1, 1, [0, 1], 3, [1, -2]], [1, 2, [0, 1], 3, [1, -2]], [2, 1, [0, 1], 3, [1, -2]], [1, 3, [0, 2], -5, [2, 7]], [3, 1, [0, 2], -5, [2, 7]], [1, 1, [0, 1], 7, [-3, 4]]]],
         [3, 13, [[1, 1, [0, 1, 2], 3, [1, -2, 5]], [1, 2, [0, 1, 2], 3, [1, -2, 5]], [2, 1, [0, 1, 2], 3, [1, -2, 5]], [1, 4, [0, 1, 3], -2, [3, 1, -4]]]]], G,
  my([M, K, arcs] = G, first = 0);
  foreach(arcs, A, my([a, b, v, ce, cq] = A, rts, res, L);
    rts = concat([1, 1 + ce * 'e^b], vector(M, q, cq[q] * 'e^(a + v[q])));
    res = limitspace(rts, K); L = res[1];
    if (first == 0, first = L);
    emit(Str("M = ", M, ", (a, b) = ", [a, b], ", v = ", v, ": vanishing orders ", res[2], "; equal to the first arc's L0: ", L == first,
      "; contains (1+T)^(-3): ", contains(L, ser((1 + 'x)^(-3), K)), ", contains 1: ", contains(L, ser(1, K)),
      ", contains (1+T)^(-3/2): ", contains(L, ser((1 + 'x)^(-3/2), K))))));
}
quit
