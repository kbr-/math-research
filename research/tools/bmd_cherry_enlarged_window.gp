\\ Enlarged cherry windows (8 October 2026; cycle bmd-20261008-zb).
\\ For M >= 2, d = binom(M,2), R_C = binom(M+2,2) and 1 <= j <= M, the space
\\   V~_j = Pol_(<d) + <(1+T)^(-3)> + (1+T)^(-3/2-j-1) Pol_(<2M+1)    (dimension R_C + 1)
\\ should have nonzero initial Taylor determinant (vanishing orders 0..R_C at T = 0), by the Wronskian exponent count.
\\ Prints that determinant's nonvanishing for M = 2..5, and checks, along the two hyperplane arcs of
\\ ex:cube-single-cherry-slack-two-fails (M = 2), that the limit space L0 lies in V~_1 (the wall between windows 1 and 2).
default(parisizemax, 4 * 10^9); default(seriesprecision, 80);
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
ser(f, K) = vector(K + 1, k, polcoef(f + O('x^(K + 1)), k - 1, 'x));
enl(M, j, K) = { my(d = M * (M - 1) / 2, rows = List());
  for (i = 0, d - 1, listput(rows, ser('x^i, K)));
  listput(rows, ser((1 + 'x + O('x^(K + 1)))^(-3), K));
  for (i = 0, 2 * M, listput(rows, ser((1 + 'x + O('x^(K + 1)))^(-3/2 - j - 1) * 'x^i, K)));
  matrix(#rows, K + 1, a, b, rows[a][b]); }
H(r, s, K) = { my(f = ((1 + r * 'x) * (1 + s * 'x))^(-3/2) + O('x^(K + 1))); vector(K + 1, k, polcoef(f, k - 1, 'x)); }
limitspace(rts, K) = {
  my(n = #rts, R = n * (n - 1) / 2, P = matrix(R, K + 1), r = 0);
  for (i = 1, n, for (j = i + 1, n, r++; my(h = H(rts[i], rts[j], K)); for (k = 1, K + 1, P[r, k] = h[k])));
  for (step = 1, R,
    my(bi = 0, bj = 0, bv = 1e9);
    for (i = step, R, for (j = 1, K + 1, if (P[i, j] != 0, my(vv = valuation(P[i, j], 'e)); if (vv < bv || (vv == bv && j < bj), bv = vv; bi = i; bj = j))));
    my(tmp = P[step, ]); P[step, ] = P[bi, ]; P[bi, ] = tmp;
    P[step, ] = P[step, ] / P[step, bj];
    for (i = 1, R, if (i != step && P[i, bj] != 0, P[i, ] = P[i, ] - P[i, bj] * P[step, ])));
  matrix(R, K + 1, i, j, my(z = P[i, j]); if (z == 0, 0, my(vv = valuation(z, 'e)); if (vv > 0, 0, subst(numerator(z), 'e, 0) / subst(denominator(z), 'e, 0))));
}
{
for (M = 2, 5, my(RC = binomial(M + 2, 2), res = List());
  for (j = 1, M, my(A = enl(M, j, RC)); listput(res, matdet(A) != 0));
  emit(Str("M = ", M, ": initial (R_C+1)-determinant of V~_j nonzero for j = 1..M: ", Vec(res))));
foreach([[1, 1 + 'e + 2 * 'e^2, 'e, -2 * 'e^2], [1, 1 + 2 * 'e^2 + 3 * 'e^5, 2 * 'e^2, -3 * 'e^5], [1, 1 + 3 * 'e, 'e, -2 * 'e^2]], rts,
  my(K = 11, L0 = limitspace(rts, K), contained = vector(2, j, matrank(matconcat([enl(2, j, K); L0])) == matrank(enl(2, j, K))));
  emit(Str("arc ", rts, ": L0 contained in V~_1, V~_2: ", contained)));
}
quit
