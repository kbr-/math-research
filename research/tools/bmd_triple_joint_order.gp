\\ Appell lead entry two (cycle keo, 9 October 2026): joint recurrence order of the three window sequences of U_3.
\\ g_ij(M) = [T^M] P(T) Phi_ij(T), P = prod_l (1+a_l T)^m over the three roots, Phi_ij the weighted pair series
\\ (lem:cube-level-window-reduction).  If one recurrence of order r <= 5 (polynomial coefficients in M, leading one
\\ nonzero on the window) annihilates all three g_ij, a combination vanishing on the five window columns vanishes
\\ identically, forcing rank U_3 = 3.  Finds the least (r, q) such that one recurrence sum_{s<=r} P_s(M) x(M+s) = 0,
\\ deg P_s <= q, holds for all three sequences on M = K0..K1 (exact over Q), at random rational roots.
OUT = getenv("OUT");
emit(s) = print(s); if (OUT != 0 && OUT != "", write(OUT, s));
G(x) = if(x == 1/2, 1, if(x > 1/2, (x - 1) * G(x - 1), G(x + 1) / x));
phi(a, b, m, N) = { my(s = ((1 + a * 'T) * (1 + b * 'T) + O('T^N))^(-3/2)); Ser(vector(N, k, (k - 1)! / G(k - 1 + 5/2 - m) * polcoef(s, k - 1, 'T)), 'T); }
joint(X, K0) = {
  for(tot = 2, 14, for(r = 1, min(tot, 8), my(q = tot - r, nun = (r + 1) * (q + 1), per = nun \ 3 + 8);
    if(K0 + per + r > #X[1], next);
    my(A = matrix(3 * per, nun, i, j, my(w = (i - 1) \ per + 1, k = K0 + (i - 1) % per, s = (j - 1) \ (q + 1), e = (j - 1) % (q + 1)); k^e * X[w][k + s + 1]));
    if(#matker(A) > 0, return([r, q]))));
  [-1, -1];
}
{
  foreach([[2, 5, -3], [1/3, -4, 7/2]], av, for(m = 2, 3,
    my(N = 160, P = prod(l = 1, 3, (1 + av[l] * 'T)^m), pr = [[1, 2], [1, 3], [2, 3]]);
    my(X = vector(3, w, my(S = P * phi(av[pr[w][1]], av[pr[w][2]], m, N)); vector(N, k, polcoef(S, k - 1, 'T))));
    emit(Str("roots ", av, " m=", m, ": least joint (order, degree) of a recurrence for g_12, g_13, g_23: ", joint(X, 3 * m + 5)))));
}
quit;
