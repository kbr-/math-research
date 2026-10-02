\\ Slack of single-cherry clusters (8 October 2026; cycle bmd-20261008-y).
\\ A framed single-cherry cluster: the cherry {1, 1+e} and a caterpillar x*y_q (q = 1..M) below it, with
\\ e = c_e eps^b, x = eps^a, y_q = c_q eps^(v_q), 0 = v_1 < v_2 < ... (integer exponents).  The pair matrix has
\\ R = binom(M+2, 2) rows H_k(r, s) = [T^k] ((1+rT)(1+sT))^(-3/2) and columns 0..R+1.  The invariant (H) of
\\ thm:cube-single-tie-chain-avoidance holds at every column set L of least valuation; its slack is R + 1 - max L.
\\ Prints, for M = 2, 3 and several rate choices (a, b) and leading coefficients: the least valuation, the number of
\\ minimizing sets, and the largest slack among minimizers (>= 1 is what lem:cube-level-step needs for a tie above).
\\ Environment EXT = e extends the columns to 0..R+1+e: (H) needs the least valuation over all subsets of
\\ L u {j > max L}; the slack is still R + 1 - max L of a least set.
default(parisizemax, 4 * 10^9);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
H(r, s, K) = { my(f = ((1 + r * 'x) * (1 + s * 'x))^(-3/2) + O('x^(K + 1))); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
{
my(cases = List());
\\ [M, a, b, v-vector, leading coefficients c_e, c_q]
listput(cases, [2, 1, 1, [0, 1], 3, [1, -2]]); listput(cases, [2, 1, 2, [0, 1], 3, [1, -2]]); listput(cases, [2, 2, 1, [0, 1], 3, [1, -2]]);
listput(cases, [2, 1, 3, [0, 2], -5, [2, 7]]); listput(cases, [2, 3, 1, [0, 2], -5, [2, 7]]);
listput(cases, [3, 1, 1, [0, 1, 2], 3, [1, -2, 5]]); listput(cases, [3, 1, 2, [0, 1, 2], 3, [1, -2, 5]]);
listput(cases, [3, 2, 1, [0, 1, 2], 3, [1, -2, 5]]); listput(cases, [3, 1, 4, [0, 1, 3], -2, [3, 1, -4]]);
EXT = if (getenv("EXT") == 0 || getenv("EXT") == "", 0, eval(getenv("EXT")));
foreach(cases, C, my([M, a, b, v, ce, cq] = C, R = binomial(M + 2, 2), K = R + 1 + EXT, roots, P, vals = List(), best = 1e9, nmin = 0, sl = -1);
  roots = concat([1, 1 + ce * 'e^b], vector(M, q, cq[q] * 'e^(a + v[q])));
  P = matrix(R, K + 1); my(r = 0);
  for (i = 1, M + 2, for (j = i + 1, M + 2, r++; my(h = H(roots[i], roots[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  forsubset([K + 1, R], S, my(dt = matdet(vecextract(P, "..", Vec(S)))); if (dt != 0, my(vv = valuation(dt, 'e));
    if (vv < best, best = vv; nmin = 0; sl = -1);
    if (vv == best, nmin++; sl = max(sl, R + 1 - (vecmax(Vec(S)) - 1)))));
  emit(Str("columns 0..R+1+", EXT, ": M = ", M, ", a = ", a, ", b = ", b, ", v = ", v, ": least valuation ", best, ", minimizing sets ", nmin, ", best slack ", sl)));
}
quit
