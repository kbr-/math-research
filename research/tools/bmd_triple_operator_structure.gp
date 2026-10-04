\\ Appell lead entry three (cycle keq, 9 October 2026): structure of the order-six joint operator of the triple window's
\\ pair sequences g_ij(M) = [T^M] P Phi_ij (lem:cube-level-window-reduction; window M = w..w+4, w = binomial(m,2)+3m).
\\ Predictions tested, m = 2..5, two root triples, modulo p = 1000003:
\\  (1) the trailing coefficient P_0 (the indicial polynomial at T = infinity) has integer roots exactly 3m-5..3m-1;
\\  (2) the operator holds from some M0 inside that block, and P_6 has no integer root >= M0 (checked to 600);
\\  (3) the window functionals have rank five on the six-dimensional solution space on M >= M0;
\\  (first run, operator-structure.txt: rank three, not five; the rerun also checks the window relations against
\\   the g_ij and prints which P_s vanish at M0..w+4)
\\  (4) no nonzero combination of the three g_ij vanishes on M0+1..M0+40 (independence modulo finite support).
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
default(parisizemax, 2000000000);
p = 1000003;
lam = 3/2;
seqs(av, m, N) = {
  my(P = prod(l = 1, 3, (1 + av[l] * 'T)^m), pr = [[1, 2], [1, 3], [2, 3]]);
  vector(3, w, my(a = av[pr[w][1]], b = av[pr[w][2]], s = ((1 + a * 'T) * (1 + b * 'T) + O('T^N))^(-lam), rho = Mod(1, p), c = vector(N));
    for(k = 0, N - 1, if(k > 0, rho *= Mod(k, p) / Mod(k + lam - m, p)); c[k + 1] = rho * Mod(polcoef(s, k, 'T), p));
    my(S = Mod(1, p) * P * Ser(c, 'T)); vector(N, k, polcoef(S, k - 1, 'T)));
}
op6(X, K0) = {
  for(q = 6, 60, my(r = 6, nun = (r + 1) * (q + 1), per = nun \ 3 + 10);
    my(A = matrix(3 * per, nun, i, j, my(w = (i - 1) \ per + 1, k = K0 + (i - 1) % per, s = (j - 1) \ (q + 1), e = (j - 1) % (q + 1)); Mod(k, p)^e * X[w][k + s + 1]));
    my(K = matker(A)); if(#K, return([q, #K, vector(r + 1, s, Pol(vector(q + 1, e, K[(s - 1) * (q + 1) + q + 2 - e, 1]), 'M))])));
  0;
}
{
  foreach([[2, 5, -3], [1/3, -4, 7/2]], av, for(m = 2, 5,
    my(X = seqs(av, m, 900), K0 = 3 * m + 5, R = op6(X, K0));
    if(R == 0, emit(Str("roots ", av, " m=", m, ": no order-six operator with q <= 60")); next);
    my(q = R[1], Pc = R[3], val(k) = vector(3, w, sum(s = 0, 6, subst(Pc[s + 1], 'M, k) * X[w][k + s + 1])));
    my(M0 = K0); forstep(k = K0 - 1, 0, -1, if(val(k) == [0, 0, 0], M0 = k, break));
    my(ok = 1); for(k = K0, 850, if(val(k) != [0, 0, 0], ok = 0; break));
    my(w = binomial(m, 2) + 3 * m, P0r = select(k -> subst(Pc[1], 'M, k) == 0, vector(601, k, k - 1)), P6r = select(k -> k >= M0 && subst(Pc[7], 'M, k) == 0, vector(601, k, k - 1)));
    \\ fundamental solutions on M >= M0 from unit initial vectors at M0..M0+5
    my(F = matrix(6, w + 5 - M0 + 1));
    for(i = 1, 6, my(x = vector(w + 6 - M0 + 1)); x[i] = Mod(1, p);
      for(k = M0, w + 4 - 6, x[k - M0 + 7] = -sum(s = 0, 5, subst(Pc[s + 1], 'M, k) * x[k - M0 + s + 1]) / subst(Pc[7], 'M, k));
      for(c = 1, #x, if(c <= w + 5 - M0 + 1, F[i, c] = x[c])));
    my(Wn = matrix(6, 5, i, c, F[i, w - M0 + c]), rk = matrank(Wn), Kw = matker(Wn), G = matrix(3, 5, i, c, X[i][w + c]));
    my(cons = (G * Kw == 0), zp = vector(w + 4 - M0 + 1, t, select(s -> subst(Pc[s + 1], 'M, M0 + t - 1) == 0, vector(7, s, s - 1))));
    my(ind = matrank(matrix(3, 40, w0, c, X[w0][M0 + c + 1])));
    emit(Str("roots ", av, " m=", m, ": degree ", q, ", kernel dim ", R[2], "; holds from M0 = ", M0, " (to 850: ", ok, "); window ", w, "..", w + 4,
      "; P_0 integer roots ", P0r, " (predicted ", 3 * m - 5, "..", 3 * m - 1, "); P_6 roots >= M0: ", P6r,
      "; window rank on solutions ", rk, " (its window relations also kill the g_ij: ", cons, "); vanishing P_s at M = M0..w+4: ", zp, "; rank of the g_ij on M0+1..M0+40: ", ind))));
}
quit;
